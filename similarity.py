#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): WSD by maximizing similarity
#
# Copyright (C) 2014-2017 alvations
# URL:
# For license information, see LICENSE.md

"""
WSD by maximizing similarity.
"""
import sys
import os
import re

from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic as wnic
from nltk.tokenize import word_tokenize

from pywsd.utils import lemmatize

def similarity_by_path(sense1, sense2, option="path"):
    """ Returns maximum path similarity between two senses. """
    if option.lower() in ["path", "path_similarity"]: # Path similaritys
        return max(wn.path_similarity(sense1,sense2),
                   wn.path_similarity(sense1,sense2))
    elif option.lower() in ["wup", "wupa", "wu-palmer", "wu-palmer"]: # Wu-Palmer
        return wn.wup_similarity(sense1, sense2)
    elif option.lower() in ['lch', "leacock-chordorow"]: # Leacock-Chodorow
        if sense1.pos != sense2.pos: # lch can't do diff POS
            return 0
        return wn.lch_similarity(sense1, sense2)

def similarity_by_infocontent(sense1, sense2, option, data):
    """ Returns similarity scores by information content. """
    if sense1.pos != sense2.pos: # infocontent sim can't do diff POS.
        return 0

    info_contents = ['ic-bnc-add1.dat', 'ic-bnc-resnik-add1.dat',
                     'ic-bnc-resnik.dat', 'ic-bnc.dat',

                     'ic-brown-add1.dat', 'ic-brown-resnik-add1.dat',
                     'ic-brown-resnik.dat', 'ic-brown.dat',

                     'ic-semcor-add1.dat', 'ic-semcor.dat',

                     'ic-semcorraw-add1.dat', 'ic-semcorraw-resnik-add1.dat',
                     'ic-semcorraw-resnik.dat', 'ic-semcorraw.dat',

                     'ic-shaks-add1.dat', 'ic-shaks-resnik.dat',
                     'ic-shaks-resnink-add1.dat', 'ic-shaks.dat',

                     'ic-treebank-add1.dat', 'ic-treebank-resnik-add1.dat',
                     'ic-treebank-resnik.dat', 'ic-treebank.dat']

    if option in ['res', 'resnik']:
        if data == None:
            return wn.res_similarity(sense1, sense2, wnic.ic('ic-bnc-resnik-add1.dat'))
        else:
            return wn.res_similarity(sense1, sense2, data)
    #return min(wn.res_similarity(sense1, sense2, wnic.ic(ic)) \
    #             for ic in info_contents)

    elif option in ['jcn', "jiang-conrath"]:
        if data == None:
            return wn.jcn_similarity(sense1, sense2, wnic.ic('ic-bnc-add1.dat'))
        else:
            return wn.jcn_similarity(sense1, sense2, data)

    elif option in ['lin']:
        if data == None:
            return wn.lin_similarity(sense1, sense2, wnic.ic('ic-bnc-add1.dat'))
        else:
            return wn.lin_similarity(sense1, sense2, data)

def sim(sense1, sense2, option="path", data=None):
    """ Calculates similarity based on user's choice. """
    option = option.lower()
    if sense1 is 0 or sense2 is 0:
        return 0
    if option.lower() in ["path", "path_similarity",
                        "wup", "wupa", "wu-palmer", "wu-palmer",
                        'lch', "leacock-chordorow"]:
        return similarity_by_path(sense1, sense2, option)
    elif option.lower() in ["res", "resnik",
                          "jcn","jiang-conrath",
                          "lin"]:
        return similarity_by_infocontent(sense1, sense2, option, data)

def max_similarity(context_sentence, ambiguous_word, option="path",
                   lemma=True, context_is_lemmatized=False, pos=None, best=True, data=None):
    """
    Perform WSD by maximizing the sum of maximum similarity between possible
    synsets of all words in the context sentence and the possible synsets of the
    ambiguous words (see http://goo.gl/XMq2BI):
    {argmax}_{synset(a)}(\sum_{i}^{n}{{max}_{synset(i)}(sim(i,a))}
    """
    ambiguous_word = lemmatize(ambiguous_word)
    # If ambiguous word not in WordNet return None
    if not wn.synsets(ambiguous_word):
        print("no synsets found in wordnet")
        return None
    # print("its synsets are %s" % wn.synsets(ambiguous_word))
    if context_is_lemmatized:
        context_sentence = word_tokenize(context_sentence)
    else:
        context_sentence = [lemmatize(w) for w in word_tokenize(context_sentence)]
        #print context_sentence

    result = {}
    for i in wn.synsets(ambiguous_word):
        try:
            if pos and pos != str(i.pos()):
                continue
        except:
            if pos and pos != str(i.pos):
                continue

        res = 0
        for j in context_sentence:
            if re.search(r'[a-z]+\.[nvsar]\.[0-9]{2}', j) != None: # if j is already disambiguated
                mysynsets = [wn.synset(j)]
            #elif j is not '.':
            #    mysynsets = wn.synsets(j)
            else:
                mysynsets = wn.synsets(j)

            #print len(mysynsets)
            sims = [0]
            for k in mysynsets:
                sims.append(sim(i,k,option,data))

            res += max(sims)
                        # res += max([sim(i,k,option,data) for k in mysynsets])
                        # result[i] = sum(max([sim(i,k,option,data) for k in wn.synsets(j)]+[0]) \
                            # for j in context_sentence)
        result[i] = res
                        
    if len(result) == 0:
        return None
    # print("printing results")
    #print result.items()
    if option in ["res","resnik"]: # lower score = more similar
        result = sorted([(v,k) for k,v in result.items()])
    else: # higher score = more similar
        result = sorted([(v,k) for k,v in result.items()],reverse=True)
        # print("sorted; printing results again")
    #print result
    if best: return result[0][1];
    return result
    #except Exception as e:
    #    exc_type, exc_obj, exc_tb = sys.exc_info()
    #    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #    print "exception: ", exc_type, fname, exc_tb.tb_lineno
    #    raise

'''
bank_sents = ['I went to the bank to deposit my money',
'The river bank was full of dead fishes']
ans = max_similarity(bank_sents[0], 'bank', pos="n", option="res")
print ans
print ans[0][1].definition
'''
