#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" find threshold maximizing the accuracy """

import matplotlib.pyplot as plt
import csv
import numpy as np

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

num_entailment_contradiction = len(scores['entailment_contradiction'])
num_neutral = len(scores['neutral'])

def get_accuracy_for_threshold_value(threshold):
    num_ent_cont_accurate = sum(float(score) >= threshold for score in scores['entailment_contradiction'])
    num_neutral_accurate = sum(float(score) < threshold for score in scores['neutral'])
    return (num_ent_cont_accurate / num_entailment_contradiction + num_neutral_accurate / num_neutral) / 2


thresholds = np.arange(0, 1, .001)
acurracies = []

for threshold in thresholds:
    acurracies.append(get_accuracy_for_threshold_value(threshold))



# find threshold values maximizing the accuracy
acurracy_max = max(acurracies)
indices_acurracy_max = [i for i, acurracy in enumerate(acurracies) if acurracy == acurracy_max]
best_thresholds = [thresholds[i] for i in indices_acurracy_max]

print("threshold values maximizing the accuracy:")
print(best_thresholds)

# plot accuracies according to threshold values

# plt.hist([scores['entailment_contradiction'],scores['neutral']],
#          bins=50, color=['r','g'], label=["entailment_contradiction","neutral"], histtype="bar",normed = 1)
#
# plt.title("score n_similarity wikipedia")
# plt.xlabel('Score value')
# plt.ylabel('Number of score')
#
# # for display label
# plt.legend()


plt.plot(thresholds, acurracies)

plt.xlabel('threshold value')
plt.ylabel('acurracy')
plt.grid(True)

plt.show()