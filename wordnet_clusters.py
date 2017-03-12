from nltk.corpus import wordnet as wn

def word_distances(words):

    word_dists = {}

    for i in range(len(words)):
        for j in range(i+1, len(words)):
            word_dists[(words[i], words[j])] = wn.path_similarity(words[i], words[j])
