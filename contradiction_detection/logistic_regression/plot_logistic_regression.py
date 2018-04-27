# ! /usr/bin/env python
# coding=utf-8
""" Logistic Regression : prediction (contradiction/entailment) """

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


X = np.loadtxt('feature_vector_1.tsv', delimiter='\t', usecols=[1,2,3,4,5,6])
y = np.loadtxt('feature_vector_1.tsv', delimiter='\t', usecols=[0], dtype=np.str)

from sklearn.linear_model import LogisticRegression
logit = LogisticRegression()
model = logit.fit(X, y)
print("score with LogisticRegression: ", model.score(X, y))

pred = model.predict([[0, 0, 1, 0, 0, 1], [0, 0, 1, 1, 0, 0]])

print(pred)

from sklearn.tree import DecisionTreeClassifier
tree = DecisionTreeClassifier()
model = tree.fit(X, y)
print("score with DecisionTreeClassifier: ", model.score(X, y))

from sklearn.ensemble import RandomForestClassifier
forest = RandomForestClassifier(n_estimators=500, criterion='gini', max_depth=None, min_samples_split=2, min_samples_leaf=1,
                                max_features='auto', max_leaf_nodes=None, bootstrap=True, oob_score=True)
model = forest.fit(X,y)
print("score with RandomForestClassifier: ", model.score(X, y))



# Plot the decision boundary. For that, we will assign a color to each
# point in the mesh [x_min, x_max]x[y_min, y_max].
# h = .02
# cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA']) #, '#AAAAFF'])
# cmap_bold = ListedColormap(['#FF0000', '#00FF00', '#0000FF'])
#
# x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
# y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
# xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
#                      np.arange(y_min, y_max, h))
# Z = model.predict(np.c_[xx.ravel(), yy.ravel(),
#                         np.zeros((xx.shape[0], xx.shape[1])).ravel(),
#                         np.zeros((xx.shape[0], xx.shape[1])).ravel(),
#                         np.zeros((xx.shape[0], xx.shape[1])).ravel()])
#
# # Put the result into a color plot
# Z = Z.reshape(xx.shape)
# plt.figure()
# plt.pcolormesh(xx, yy, Z)#, cmap=cmap_light)
#
# # # Plot also the training points
# # plt.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap_bold)
# # plt.xlim(xx.min(), xx.max())
# # plt.ylim(yy.min(), yy.max())
# # plt.title("3-Class classification (k = %i, weights = '%s')"
# #           % (n_neighbors, weights))
#
# plt.show()
#
#
#
# # with open('feature_vector.tsv', 'r') as tsv_file:
# #     rows = tsv_file.readlines()
# #     for row in rows:
# #         data = np.loadtxt(row)
# #
# #     for row in csv.reader(tsv_file, delimiter='\t'):
# #         Y = row[0]
# #         X = str(row[1:][0]).split()
# #
# #         print(X)
# #
# #         #X = X[0]+X[1]+X[2]+X[3]+X[4]
# #
# #
# #         myarray = np.array(X)
# #         print(myarray)
# #         print(type(myarray))
# #         contradiction_logit = logit.fit(myarray, Y)
# #         #
# #         #
# #         # contradiction_logit.coef_
# #         #
# #         #
# #         # print(contradiction_logit)
#
