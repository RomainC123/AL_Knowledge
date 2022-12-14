import os
import time
import pandas as pd
from datetime import datetime

import pickle

import requests
from bs4 import BeautifulSoup

import networkx as nx
from pyvis.network import Network

from tqdm.auto import tqdm

from constants import *

search_terms = ["anastomotic", "leak"]
max_page_num = None

OVERWRITE = True

# -----------------------------------------------------------------------------
# Adding all relevant utilities


def _pget(url, stream=False):
    """
    Acounts for network errors in   getting a request (Pubmed often appears offline, but not for long periods of time)
    Retries every 2 seconds for 60 seconds and then gives up
    """
    downloaded = False
    count = 0

    while not downloaded and count < 60:
        try:
            page = requests.get(url, stream=stream)
            downloaded = True
        except:
            print(url + f" - Network error, retrying... ({count + 1})")
            time.sleep(2)
            count += 1

    if page != None:
        return page
    else:
        raise ValueError

# -----------------------------------------------------------------------------


# Option to not re-download all search results every time as it takes a while
if OVERWRITE:
    # Filtering out every non English match
    search_url = "https://pubmed.ncbi.nlm.nih.gov/?term=" + '+'.join(search_terms) + '&filter=lang.english'
    full_search_ids = []

    # Grabs every page
    page_num = 0
    while (max_page_num and page_num < max_page_num) or not max_page_num:
        page_num += 1
        if page_num != 1:
            page_url = search_url + "&page=" + str(page_num)
        else:
            page_url = search_url
        try:
            page = _pget(page_url)
            page_soup = BeautifulSoup(page.text, features="lxml")
            page_ids = page_soup.find("div", {"class": "search-results-chunk results-chunk"}
                                      ).get("data-chunk-ids").split(",")
            full_search_ids += page_ids
        except AttributeError:
            break

    with open(os.path.join(LOGS_PATH, "full_search_ids_anastomotic_leak.pkl"), "wb") as f:
        pickle.dump(full_search_ids, f)

else:
    with open(os.path.join(LOGS_PATH, "full_search_ids_anastomotic_leak_full.pkl"), "rb") as f:
        full_search_ids = pickle.load(f)

articles_list = []

for article_id in tqdm(full_search_ids):

    url = "https://pubmed.ncbi.nlm.nih.gov/" + str(article_id)

    with _pget(url) as r:
        soup = BeautifulSoup(r.text, "html.parser")

    # Getting title
    title_soup = soup.find("head").find("title")
    title = title_soup.text[:-9]

    # Getting author names
    try:
        author_names = []
        authors_soup_list = soup.find("div", {"class": "inline-authors"}
                                      ).find_all("span", {"class": "authors-list-item"})
        for author_soup in authors_soup_list:
            author_soup = author_soup.find("a", {"class": "full-name"})
            author_names.append(author_soup["data-ga-label"])
    except:
        author_names = []

    # Getting publication date
    try:
        date_text = soup.find("div", {"class": "article-source"}).find("span", {"class": "cit"}).text.split(";")[0]
        date_text = " ".join(date_text.split(" ")[:2])
        date = datetime.strptime(date_text, "%Y %b")
    except:
        date = "Undef"

    # Getting all citations mentionned in the Cited By section on pubmed
    citations_ids = []
    citedby = soup.find("div", {"class": "citedby-articles"})
    if citedby:
        for a in citedby.find_all("a", {"class": "docsum-title"}):
            citations_ids.append(a["data-ga-action"])

    articles_list.append({"ID": article_id,
                          "Title": title,
                          "Authors": author_names,
                          "Date": date,
                          "Citations": citations_ids})

articles_df = pd.DataFrame(articles_list).set_index("ID")

# -----------------------------------------------------------------------------
# Saving everything for later use, then building the networkx object
# The network takes forever to display and is betetr seen with physics off

with open(os.path.join(DATA_PATH, "articles_infos.csv"), "w") as f:
    articles_df.to_csv(f, sep="|")

with open(os.path.join(DATA_PATH, "articles_infos.pkl"), "wb") as f:
    pickle.dump(articles_df, f)

G = nx.DiGraph()

for i, c in articles_df["Citations"].iteritems():
    G.add_node(i)
    for c2 in c:
        G.add_edge(c2, i)

net = Network(height='600px', width='50%', directed=True)
net.show_buttons(filter_=['physics'])
net.from_nx(G)
net.toggle_physics(False)
net.show(os.path.join(DATA_PATH, "citations_graph.html"))
