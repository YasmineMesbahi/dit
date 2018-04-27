#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Vizualization of the score distribution in classes """

import matplotlib.pyplot as plt
import csv


# import numpy as np
# x = np.linspace(0, 2 * np.pi, 400)
# y = np.sin(x ** 2)
# f, axarr = plt.subplots(2, 2)
# axarr[0, 0].plot(x, y)
# axarr[0, 0].set_title('Axis [0,0]')
# axarr[0, 1].scatter(x, y)
# axarr[0, 1].set_title('Axis [0,1]')
# axarr[1, 0].plot(x, y ** 2)
# axarr[1, 0].set_title('Axis [1,0]')
# axarr[1, 1].scatter(x, y ** 2)
# axarr[1, 1].set_title('Axis [1,1]')
# # Fine-tune figure; hide x ticks for top plots and y ticks for right plots
# plt.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False)
# plt.setp([a.get_yticklabels() for a in axarr[:, 1]], visible=False)
#
# plt.show()




sources = [ {'file_path': 'No_MR/score_1-10000_n_similarity_twitter.tsv',
            'title': 'score_n_similarity twitter'},
           {'file_path': 'No_MR/score_1-10000_n_similarity_wikipedia.tsv',
            'title': 'score_n_similarity wikipedia'},

            {'file_path': 'MR/score_1-10000_n_similarity_twitter.tsv',
            'title': 'score_n_similarity twitter MR'},
           {'file_path': 'MR/score_1-10000_n_similarity_wikipedia.tsv',
            'title': 'score_n_similarity wikipedia MR'},

            {'file_path': 'No_MR/score_1-10000_wmdistance_twitter.tsv',
             'title': 'score_wmdistance twitter'},
            {'file_path': 'No_MR/score_1-10000_wmdistance_wikipedia.tsv',
             'title': 'score_wmdistance wikipedia'},

           {'file_path': 'MR/score_1-10000_wmdistance_twitter.tsv',
            'title': 'score_wmdistance twitter MR'},
           {'file_path': 'MR/score_1-10000_wmdistance_wikipedia.tsv',
            'title': 'score_wmdistance wikipedia MR'},

           {'file_path': 'MR/score_1-10000_synonym_.tsv',
            'title': 'score_synonym_MR'}
           ]

f, axarr = plt.subplots(3, 3)

for ids, source in enumerate(sources):
    current_plt = axarr[ids // 3, ids % 3]

    # read TSV file
    scores = {'entailment': [], 'neutral': [], 'contradiction': []}
    with open('../../resources/corpora/multinli/score/score_compressed/' + source['file_path'], 'r') as tsv_file:
        for row in csv.reader(tsv_file, delimiter='\t'):
            label = row[0]
            score = float(row[1])
            if label in ['entailment', 'neutral', 'contradiction']:
                scores[label].append(score)

    scores['entailment_contradiction'] = sorted(scores['entailment'] + scores['contradiction'])
    scores['neutral'] = sorted(scores['neutral'])

    current_plt.hist([scores['entailment_contradiction'],scores['neutral']],
             bins=50, color=['r','g'], label=["entailment_contradiction","neutral"], histtype="bar", normed = 1)

    current_plt.set_title(source['title'])
    
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.4)
    # current_plt.xlabel('Score value')
    # current_plt.ylabel('Number of score')

    # for display label
    #current_plt.legend()

plt.show()

i=2