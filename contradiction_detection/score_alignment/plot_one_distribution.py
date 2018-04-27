#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Vizualization of the score distribution in classes """

import matplotlib.pyplot as plt
import csv

# Plot for 1 file

# read TSV file
scores = {'entailment': [], 'neutral': [], 'contradiction': []}
with open('D:/dit/resources/corpora/multinli/score/score_compressed/No_MR/score_1-10000_n_similarity_wikipedia.tsv', 'r') as tsv_file:
    for row in csv.reader(tsv_file, delimiter='\t'):
        label = row[0]
        score = float(row[1])
        if label in ['entailment', 'neutral', 'contradiction']:
            scores[label].append(score)

scores['entailment_contradiction'] = sorted(scores['entailment'] + scores['contradiction'])
scores['neutral'] = sorted(scores['neutral'])


plt.hist([scores['entailment_contradiction'],scores['neutral']],
         bins=50, color=['r','g'], label=["entailment_contradiction","neutral"], histtype="bar",normed = 1)

plt.title("score n_similarity wikipedia")
plt.xlabel('Score value')
plt.ylabel('Number of score')

# for display label
plt.legend()
plt.show()