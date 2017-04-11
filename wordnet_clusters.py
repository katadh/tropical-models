from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic as wnic

import numpy as np

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from sklearn import manifold
from sklearn.decomposition import PCA

from allwords_wsd import disambiguate
from similarity import max_similarity

import get_topics

# just doing some rudimentary disambiguation wsd so we can see some results
def get_synsets(words, disambiguated, data=None):
    if disambiguated:
        return get_synsets_from_labels(words)
    else:
        return get_synsets_from_words(words, data)

def get_synsets_from_labels(labels):
    synsets = []
    for label in labels:
        synsets.append(wn.synset(label))

    return synsets

def get_synsets_from_words(words, data=None):
    sent = ' '.join(words)
    if data == None:
        result = disambiguate(sent, algorithm=max_similarity, similarity_option='jcn', similarity_data=wnic.ic('ic-bnc-add1.dat'))
    else:
        result = disambiguate(sent, algorithm=max_similarity, similarity_option='jcn', similarity_data=data)
    #print result

    synsets = []
    for tup in result:
        synset = tup[1]
        if synset is not None:
            if synset.pos() == 'n':
                synsets.append(synset)

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
    print "calculating distances"
    word_dists = np.zeros(len(synsets)**2, dtype='float64').reshape(len(synsets), len(synsets))

    sim_data = wnic.ic('ic-bnc-add1.dat')
    for i in range(len(synsets)):
        for j in range(i+1, len(synsets)):
            sim = wn.jcn_similarity(synsets[i], synsets[j], sim_data)
            if sim is None:
                print "syn1: " + str(synsets[i]) + " syn2: " + str(synsets[j])
                continue
            word_dists[i, j] = 1.0e+300 - sim
            word_dists[j, i] = 1.0e+300 - sim

    return word_dists

def visualize_distance_matrix3d(dists, topic_lengths):

    nmds = manifold.MDS(n_components=3, metric=False, max_iter=10000, eps=1e-25,
                        dissimilarity="precomputed", n_jobs=-1, n_init=10)
    points = nmds.fit(dists).embedding_
    #clf = PCA(n_components=2)
    #points = clf.fit_transform(points)
    #print points

    coloring = []
    num_topics = len(topic_lengths)
    for i in range(num_topics):
        coloring += [(i+1.0) / (num_topics + 1.0)] * topic_lengths[i]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], c=coloring, lw=0)
    plt.show()

def visualize_distance_matrix(dists, topic_lengths):

    print "starting graph generation"
    nmds = manifold.MDS(n_components=2, metric=False, max_iter=10000, eps=1e-25,
                        dissimilarity="precomputed", n_jobs=-1, n_init=10)
    points = nmds.fit(dists).embedding_
    #clf = PCA(n_components=2)
    #points = clf.fit_transform(points)
    #print points

    coloring = []
    num_topics = len(topic_lengths)
    for i in range(num_topics):
        coloring += [(i+1.0) / (num_topics + 1.0)] * topic_lengths[i]

    fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    plt.scatter(points[:, 0], points[:, 1], c=coloring, lw=0)
    plt.show()

def visualize_topics(topics, dim=2, disambiguated=False):
    all_synsets = []
    topic_lengths = []
    sim_data = wnic.ic('ic-bnc-add1.dat')
    for topic in topics:
        words = topic.keys()
        synsets = get_synsets(words, disambiguated, data=sim_data)
        print len(synsets)
        topic_lengths.append(len(synsets))
        all_synsets += synsets
        
    dists = wordnet_distances(all_synsets)
    print dists.shape
    if dim == 3:
        visualize_distance_matrix3d(dists, topic_lengths)
    elif dim == 2:
        visualize_distance_matrix(dists, topic_lengths)
    return dists

def avg_wn_dist_topic(topic, disambiguated, sim_data):
    words = [w[0] for w in topic]
    synsets = get_synsets(words, disambiguated, data=sim_data)
    
    total_dist = 0.0
    for i in range(len(synsets)):
        for j in range(i+1, len(synsets)):
            sim = wn.jcn_similarity(synsets[i], synsets[j], sim_data)
            if sim is None:
                print "syn1: " + str(synsets[i]) + " syn2: " + str(synsets[j])
                continue
            total_dist += 1.0e+300 - sim

    num_comparisons = (len(synsets) * (len(synsets) - 1) / 2.0)
    return total_dist / num_comparisons, num_comparisons

def avg_wn_dist_topics(topics, disambiguated):

    sim_data = wnic.ic('ic-bnc-add1.dat')

    #doing a weighted average based on the number of words we actually get the dist for
    averages = []
    num_samples = []
    for topic in topics:
        average_dist, samples = avg_wn_dist_topic(topic, disambiguated, sim_data)
        #print average_dist
        averages.append(average_dist)
        num_samples.append(samples)

    total_samples = sum(num_samples)
    total_average = 0.0
    for avg, samples in zip(averages, num_samples):
        total_average += avg * samples / total_samples

    return total_average

def avg_wn_dist_dict(dict_file, disambiguated):
    sim_data = wnic.ic('ic-bnc-add1.dat')
    
    words = file(dict_file).readlines()
    synsets = get_synsets(words, disambiguated, data=sim_data)

    total_dist = 0.0
    num_synsets = len(synsets) / 3
    for i in range(num_synsets):
        for j in range(i+1, num_synsets):
            sim = wn.jcn_similarity(synsets[i], synsets[j], sim_data)
            total_dist += 1.0e+300 - sim
            
    return total_dist / (num_synsets * (num_synsets - 1) / 2.0)

    
