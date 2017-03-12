from nltk.corpus import wordnet as wn

import numpy as np

from matplotlib import pyplt as plt

from sklearn import manifold

#def wordnet_distances(words):
#
#    word_dists = {}
#
#    for i in range(len(words)):
#        for j in range(i+1, len(words)):
#            word_dists[(words[i], words[j])] = wn.path_similarity(words[i], words[j])

#We want an actual matrix in order to use sklearn MDS
def wordnet_distances(words):
    word_dists = np.zeros(len(words)**2, dtype='float64').reshape(len(words), len(words))

    for i in range(len(words)):
        for j in range(i+1, len(words)):
            dist = wn.path_similarity(words[i], words[j])
            word_dists[i, j] = dist
            word_dists[j, i] = dist

def visualize_distance_matrix(dists):

    nmds = manifold.MDS(n_components=2, metric=False, max_iter=3000, eps=1e-12,
                        dissimilarity="precomputed", random_state=666, n_jobs=-1)
    points = nmds.fit(dists).embedding_
