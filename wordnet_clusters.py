from nltk.corpus import wordnet as wn

import numpy as np

from matplotlib import pyplot as plt

from sklearn import manifold

from pywsd import disambiguate

import get_topics

# just doing some rudimentary disambiguation wsd so we can see some results
def get_synsets(words):
    sent = ' '.join(words)
    result = disambiguate(sent)

    synsets = []
    for tup in result:
        synset = tup[1]
        if synset is not None:
            if synset.pos() == 'n':
                synsets.append(tup[1])

    return synsets

#def wordnet_distances(words):
#
#    word_dists = {}
#
#    for i in range(len(words)):
#        for j in range(i+1, len(words):
#            word_dists[(words[i], words[j])] = wn.path_similarity(words[i], words[j])

#We want an actual matrix in order to use sklearn MDS
def wordnet_distances(synsets):
    word_dists = np.zeros(len(synsets)**2, dtype='float64').reshape(len(synsets), len(synsets))

    for i in range(len(synsets)):
        for j in range(i+1, len(synsets)):
            sim = wn.path_similarity(synsets[i], synsets[j], simulate_root=True)
            if sim is None:
                print "syn1: " + str(synsets[i]) + " syn2: " + str(synsets[j])
                continue
            word_dists[i, j] = 1.0 / sim
            word_dists[j, i] = 1.0 / sim

    return word_dists

def visualize_distance_matrix(dists):

    nmds = manifold.MDS(n_components=2, metric=False, max_iter=3000, eps=1e-12,
                        dissimilarity="precomputed", random_state=666, n_jobs=-1)
    points = nmds.fit(dists).embedding_

    plt.scatter(points[:, 0], points[:, 1], lw=0)
    plt.show()

def visualize_topics(topics):
    synset_set = set()
    for topic in topics:
        words = [w[0] for w in topic]
        synsets = get_synsets(words)
        for synset in synsets:
            synset_set.add(synset)
    dists = wordnet_distances(list(synset_set))
    visualize_distance_matrix(dists)
    return dists
