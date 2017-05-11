# compare lambda dat files from LDA output

from get_topics import get_topics
from nltk.corpus import wordnet
from numpy import average, median, log
from math import sqrt

import os
import re

TOPIC_LEN = 10

def compare_two_topics(topic1, topic2):
    # takes in 2 topic sets; returns percentage of word overlap
    # assumes provided topics are the same length.
    matches = 0
    for word1 in topic1.keys():
        for word2 in topic2.keys():
            if word1 == word2:
                #print("got a match: %s and %s" % (word1, word2))
                matches += 1
                break
            elif re.search(r'[a-z]+\.[nvsar]\.[0-9]{2}', word1) != None and wordnet.synset(word1) in wordnet.synsets(word2):
                matches += 1
                break
            elif re.search(r'[a-z]+\.[nvsar]\.[0-9]{2}', word2) != None and wordnet.synset(word2) in wordnet.synsets(word1):
                matches += 1
                break
            #elif word1.split('.')[0] == word2:
            #    matches += 1
            #    break
            #elif word2.split('.')[0] == word1:
            #    matches += 1
            #    break
    return matches * 1./ TOPIC_LEN

def compare_topic_sets_best_match(list1, list2):
    best_matches = {}
    for top1 in list1:
        # print("top1:", top1)
        for top2 in list2:
            # print(top2)
            index1 = list1.index(top1)
            index2 = list2.index(top2)
            m = compare_two_topics(top1, top2)
            if index1 in best_matches.keys():
                if m > best_matches[index1][0]:
                    best_matches[index1] = (m, index2)
            else:
                best_matches[index1] = (m, index2)
            # if m != 0:
            #   print("topics: %s\n %s" % (top1, top2))
            #   print("similarity score: %f" % m)
            # if m > 0:
            #   print("got a non-zero score")
    return best_matches

def compare_topic_sets(list1, list2):
    match_totals = []
    for top1 in list1:
        for top2 in list2:
            m = compare_two_topics(top1, top2)
            # if m != 0:
                # print("topics: %s\n %s" % (top1, top2))
                # print("similarity score: %f" % m)
            # if m > 0:
                #print("got a non-zero score")
            match_totals.append(m)
    return match_totals

def strip_synsets(list1):
    new_list = []
    for topic in list1:
        newtop = {}
        for wordsense in topic.keys():
            # todo: handle cases where multiple senses of a word are in a topic
            newtop[wordsense.split('.')[0]] = topic[wordsense]
    return new_list

def add_synsets(list1):
    new_list = []
    for topic in list1:
        newtop = topic
        for word in topic.keys():
            syns = wordnet.synsets(word)
            #if len(syns) == 0:
            #    newtop[word] = topic[word]
            for syn in syns:
                newtop[syn.name()] = topic[word]
        new_list.append(newtop)
        # print("added synsets to turn this topic: \n%s \n\n\n\n" % topic)
        # print("into this topic:\n%s \n\n\n" % newtop)
    return(new_list)

def analyze_match_results(list1=None, list2=None):
    #list1 = get_topics.get_topics('wn_ambiguous.txt', 'wn_ambig_no_stop_8000.dat', TOPIC_LEN)
    if list1 is None:
        list1 = get_topics('wn_ambig_no_stop.txt', 'wn_ambig_no_stop_8000.dat', TOPIC_LEN)
        #list1 = add_synsets(list1)
    if list2 is None:
        list2 = get_topics('synset_dict.txt', '8000_jcn.dat', TOPIC_LEN)
    # list1 = get_topics.get_topics('synset_dict.txt', 'comp1.dat', TOPIC_LEN)
    # list2 = get_topics.get_topics('synset_dict.txt', 'sci_mod.dat', TOPIC_LEN)
    #new_list2 = strip_synsets(list2)
    #match_totals = compare_topic_sets(newlist1, list2)
    #list1 = add_synsets(list1)
    matches = compare_topic_sets_best_match(list1, list2)
    match_totals = [match[0] for match in matches.values()]
    print("length of match_totals is %d" % len(match_totals))
    # print(match_totals)
    #avg = average(match_totals) * sqrt(len(match_totals))
    avg = average(match_totals)
    print("average best match percentage between the two sets times number of topics per set was %f" % avg)
    med = median(match_totals)
    print("median overlap percentage between topics from the two sets provided was %f" % med)
    ma = max(match_totals)
    print("max overlap percentage between two topics was %f" % ma)
    return matches

def topic_coherence(topic_words, doc_freqs, doc_co_freqs):
    coherence = 0
    for i in range(len(topic_words)):
        for j in range(i+1, len(topic_words)):
            if frozenset([topic_words[i], topic_words[j]]) in doc_co_freqs and topic_words[j] in doc_freqs:
                coherence += log((doc_co_freqs[frozenset([topic_words[i], topic_words[j]])] + 1.0) / doc_freqs[topic_words[j]])

    return coherence

def average_coherence(topic_list, corpus_path):
    batch_size = 100
    topic_words = []
    topics_batch = []
    coherences = []
    for i in range(len(topic_list)):
        topic_words.extend(topic_list[i].keys())
        topics_batch.append(topic_list[i].keys())
        if i % batch_size == 0:
            #not enough memory to compute all document co frequencies ahead of time
            doc_freqs, doc_co_freqs = document_freqs(topic_words, corpus_path)
            coherences.extend([topic_coherence(topic, doc_freqs, doc_co_freqs) for topic in topics_batch])
            topic_words = []
            topics_batch = []
    
    #For cases where # of topics isn't divisible by batch size
    doc_freqs, doc_co_freqs = document_freqs(topic_words, corpus_path)
    coherences.extend([topic_coherence(topic, doc_freqs, doc_co_freqs) for topic in topics_batch])
    topic_words = []
    topics_batch = []

    c = sum(coherences)
    return c*1./len(topic_list)

def match_vs_disambig_words(best_matches, disambig_topics):
    match_vs_disambig = []
    for match in best_matches.items():
        match_percent = match[1][0]
        topic = disambig_topics[match[1][1]]
        num_disambig = 0
        for word in topic.keys():
            if re.search(r'[a-z]+\.[nvsar]\.[0-9]{2}', word) != None:
                num_disambig += 1
        match_vs_disambig.append(match_percent, num_disambig)

    return match_vs_disambig
        

def document_freqs(topic_words, corpus_path):
    doc_freqs = {}
    doc_co_freqs = {}
    topic_words = set(topic_words)
    doc_names = os.listdir(corpus_path)
    for doc_name in doc_names:
        with open(corpus_path + '/' + doc_name) as doc:
            # print len(doc_freqs)
            # print len(doc_co_freqs)
            words = list(set([word for line in doc for word in line.split()]))
            for i in range(len(words)):
                if words[i] in topic_words:
                    if words[i] in doc_freqs:
                        doc_freqs[words[i]] += 1
                    else:   
                        doc_freqs[words[i]] = 1
                for j in range(i+1, len(words)):
                    if words[i] != words[j] and words[i] in topic_words and words[j] in topic_words:
                        if frozenset([words[i], words[j]]) in doc_co_freqs:
                            doc_co_freqs[frozenset([words[i], words[j]])] += 1
                        else:
                            doc_co_freqs[frozenset([words[i], words[j]])] = 1
    return doc_freqs, doc_co_freqs

def ambig_v_disambig(top_len=TOPIC_LEN):
    lst = ['30','100','250','500','750','1000']
    for fn in lst:
        name1 = 'gt_ambig/gt_ambig_' + fn + '.dat'
        name2 = 'gt_disambig/gt_disambig_' + fn + '.dat'
        print("comparing ambig and disambig for %s topics" % fn)
        t1 = get_topics.get_topics('mixed_wn_dict.txt', name1, top_len)
        t2 = get_topics.get_topics('mixed_wn_dict.txt', name2, top_len)
        analyze_match_results(t1,t2)

def ecology_coherence(top_len=TOPIC_LEN):
    cpath = '../ecology_articles2/'
    tamb = get_topics.get_topics('wn_ambig_no_stop.txt', 'wn_ambig_no_stop_8000.dat', top_len)
    print("average coherence for ambig ecology articles:", average_coherence(tamb, cpath))
    tdisamb = get_topics.get_topics('synset_dict.txt', '8000_jcn.dat', top_len)
    print("average coherence for disambig ecology articles:", average_coherence(tdisamb, cpath))

if __name__ == '__main__':
    # analyze_match_results()
    # ambig_v_disambig()
    ecology_coherence()

"""
version using dicts that could work with expectation
def compare_two_topics(topic1, topic2):
    # takes in 2 topic sets; returns percentage of word overlap
    # assumes provided topics are the same length.
    matches = 0
    for word1 in topic1.keys():
        for word2 in topic2.keys():
            if word1 == word2:
                #print("got a match: %s and %s" % (word1, word2))
                matches += 1
            elif word1.split('.')[0] == word2:
                matches += 1
            elif word2.split('.')[0] == word1:
                matches += 1
    return matches * 1./ TOPIC_LEN
"""
