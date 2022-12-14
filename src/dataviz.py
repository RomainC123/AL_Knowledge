import os

import pandas as pd
from nltk import ngrams
from wordcloud import WordCloud
from collections import Counter

import matplotlib.pyplot as plt
import seaborn as sns

from constants import *

# -----------------------------------------------------------------------------
# Aims to display how the semantic groups are distributed throughout our dataset
# Imports the semantic network

with open(os.path.join(DATA_PATH, "2021AB_SN", "SG"), "r") as f:
    group_df = pd.read_csv(f, sep="|", header=None)

full_names = {}
for abbrev, name in group_df[[0, 1]].itertuples(index=False):
    if abbrev not in full_names.keys():
        full_names[abbrev] = name.upper()

# -----------------------------------------------------------------------------
# Counts every group occurence per document
# Also counts every word, 2-gram and 3-gram

total_distrib = {}
tokens = []
tokens_undef = []
tokens_proc = []
tokens_acti = []

for filename in os.listdir(ARTICLES_PATH):

    with open(os.path.join(ARTICLES_PATH, filename, "entities.csv"), "r") as f:
        entities_df = pd.read_csv(f).drop("Unnamed: 0", axis=1)

    for i, v in entities_df["Type"].value_counts().iteritems():
        if i == "ENTITY":
            i = "UNDEF"
        elif i in full_names.keys():
            i = full_names[i]
        if i not in total_distrib.keys():
            total_distrib[i] = v
        else:
            total_distrib[i] += v

    tokens += list(entities_df["Word"].astype(str).values)
    tokens_undef += list(entities_df.loc[(entities_df["Type"] == "ENTITY") & (entities_df["CUI"] == "UNDEF")]["Word"].astype(str).values)
    tokens_proc += list(entities_df.loc[(entities_df["Type"] == "PROC")]["Word"].astype(str).values)
    tokens_acti += list(entities_df.loc[(entities_df["Type"] == "ACTI")]["Word"].astype(str).values)


# list_distrib = []
# total_v = 0
# undef_v = 0
# for name, v in total_distrib.items():
#     total_v += v
#     list_distrib.append({"group": name, "frequency": v})
#     if name == "UNDEF":
#         undef_v = v
#
# print(undef_v / total_v)

# counted = Counter(tokens)
# counted_2 = Counter(ngrams(tokens, 2))
# counted_3 = Counter(ngrams(tokens, 3))
#
# word_freq = pd.DataFrame(counted.items(), columns=['word', 'frequency']).sort_values(by='frequency', ascending=False)
# word_pairs = pd.DataFrame(counted_2.items(), columns=['pairs', 'frequency']).sort_values(
#     by='frequency', ascending=False)
# trigrams = pd.DataFrame(counted_3.items(), columns=['trigrams', 'frequency']).sort_values(
#     by='frequency', ascending=False)

# -----------------------------------------------------------------------------
# Displays the distribution of semantic groups, words, 2-grams and 3-grams, and
# a wordcloud

# plt.figure(figsize=(9, 5))
# sns.barplot(x='frequency', y='group', data=pd.DataFrame(list_distrib))
#
# plt.figure(figsize=(9, 5))
# sns.barplot(x='frequency', y='word', data=word_freq.head(40))
#
# plt.figure(figsize=(9, 5))
# sns.barplot(x='frequency', y='pairs', data=word_pairs.head(20))
#
# plt.figure(figsize=(9, 5))
# sns.barplot(x='frequency', y='trigrams', data=trigrams.head(20))

clean_words_string = " ".join(tokens)
wordcloud = WordCloud(background_color="white").generate(clean_words_string)

clean_words_string_undef = " ".join(tokens_undef)
wordcloud_undef = WordCloud(background_color="white").generate(clean_words_string_undef)

clean_words_string_proc = " ".join(tokens_proc)
wordcloud_proc = WordCloud(background_color="white").generate(clean_words_string_proc)

clean_words_string_acti = " ".join(tokens_acti)
wordcloud_acti = WordCloud(background_color="white").generate(clean_words_string_acti)


plt.figure(figsize=(12, 8))
plt.imshow(wordcloud)

plt.figure(figsize=(12, 8))
plt.imshow(wordcloud_undef)

plt.figure(figsize=(12, 8))
plt.imshow(wordcloud_proc)

plt.figure(figsize=(12, 8))
plt.imshow(wordcloud_acti)

plt.axis("off")
plt.show()
