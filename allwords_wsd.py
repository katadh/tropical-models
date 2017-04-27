#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD): all-words WSD
#
# Copyright (C) 2014-2017 alvations
# URL:
# For license information, see LICENSE.md

from string import punctuation

from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords

from lesk import simple_lesk, original_lesk
from similarity import max_similarity
from utils import lemmatize, lemmatize_sentence

"""
This is a module for all-words full text WSD
(modified for use in tropical_models framework)

This would involve:
Step 1: First tokenize your text such that each token is separated by whitespace
Step 2: Iterates through the tokens and only disambiguate the content words.
"""

stopwords = stopwords.words('english') + list(punctuation)

def disambiguate(sentence, algorithm=simple_lesk,
                 context_is_lemmatized=False, similarity_option='path',
                 keepLemmas=False, prefersNone=True, similarity_data=None):
    tagged_sentence = []
    # Pre-lemmatize the sentnece before WSD
    if not context_is_lemmatized:
        surface_words, lemmas, morphy_poss = lemmatize_sentence(sentence, keepWordPOS=True)
        lemma_sentence = " ".join(lemmas)
    else:
        lemma_sentence = sentence # TODO: Miss out on POS specification, how to resolve?
    for word, lemma, pos in zip(surface_words, lemmas, morphy_poss):
        if lemma not in stopwords: # Checks if it is a content word
            try:
                wn.synsets(lemma)[0]
                if algorithm == original_lesk: # Note: Original doesn't care about lemmas
                    synset = algorithm(lemma_sentence, lemma)
                elif algorithm == max_similarity:
                    synset = algorithm(lemma_sentence, lemma, pos=pos, option=similarity_option, data=similarity_data)
                else:
                    synset = algorithm(lemma_sentence, lemma, pos=pos, context_is_lemmatized=True)
            except: # In case the content word is not in WordNet
                synset = '#NOT_IN_WN#'
        else:
            synset = '#STOPWORD/PUNCTUATION#'
        if keepLemmas:
            tagged_sentence.append((word, lemma, synset))
        else:
            tagged_sentence.append((word, synset))
    # Change #NOT_IN_WN# and #STOPWORD/PUNCTUATION# into None.
    if prefersNone and not keepLemmas:
        tagged_sentence = [(word, None) if str(tag).startswith('#')
                           else (word, tag) for word, tag in tagged_sentence]
    if prefersNone and keepLemmas:
        tagged_sentence = [(word, lemma, None) if str(tag).startswith('#')
                           else (word, lemma, tag) for word, lemma, tag in tagged_sentence]
    return tagged_sentence


def disambiguate_new(sentence, algorithm=simple_lesk, extra_words=None,
                 context_is_lemmatized=False, similarity_option='path',
                 keepLemmas=False, prefersNone=True, similarity_data=None):
    # adds option of extra words, e.g. from LDA output, though not required
    # also checks if a word has 0 or 1 synsets, and doesn't run WSD in those cases
    tagged_sentence = []
    # Pre-lemmatize the sentence before WSD
    if not context_is_lemmatized:
        surface_words, lemmas, morphy_poss = lemmatize_sentence(sentence, keepWordPOS=True)
        lemma_sentence = " ".join(lemmas)
    else:
        lemma_sentence = sentence # TODO: Miss out on POS specification, how to resolve?
    # print lemma_sentence
    if extra_words:
        # print("changing sentence to add LDA words:")
        # print(lemma_sentence)
        lemma_sentence = lemma_sentence.rstrip('.') + ' ' + " ".join(extra_words)
        # print(lemma_sentence)
    for word, lemma, pos in zip(surface_words, lemmas, morphy_poss):
        if lemma not in stopwords: # Checks if it is a content word
            try:
                if '.' in lemma: # lemma is already disambiguated
                    synset = wn.synset(lemma)
                    # print("single synset for %s" % lemma)
                else:
                    syns = wn.synsets(lemma)
                    if len(syns) == 0:
                        # print("no synsets for %s; returning None" % lemma)
                        synset = None
                    elif len(syns) == 1:
                        # print("just one synset for %s; returning %s" % (lemma, syns[0]))
                        synset = syns[0]
                    elif algorithm == original_lesk: # Note: Original doesn't care about lemmas
                        # print("running original_lesk on %s" % lemma)
                        synset = algorithm(lemma_sentence, lemma)
                        # print("succeeded; returning %s" % synset)
                    elif algorithm == max_similarity:
                        # print("running max_similarity on %s" % lemma)
                        synset = algorithm(lemma_sentence, lemma, pos=pos, option=similarity_option, data=similarity_data)
                        # print("succeeded at max_sim; returning %s" % synset)
                    else:
                        # print("running alg %s on %s" % (algorithm.__name__, lemma))
                        synset = algorithm(lemma_sentence, lemma, pos=pos, context_is_lemmatized=True)
                        # print("succeeded; returning %s" % synset)
            except: # In case the content word is not in WordNet
                synset = '#NOT_IN_WN#'
                # print("\ntry/except caught %s while trying alg %s and is returning #NOT_IN_WN#\n" % (lemma, algorithm.__name__))
        else:
            synset = '#STOPWORD/PUNCTUATION#'
        if keepLemmas:
            tagged_sentence.append((word, lemma, synset))
        else:
            tagged_sentence.append((word, synset))
        # print word, synset
    # Change #NOT_IN_WN# and #STOPWORD/PUNCTUATION# into None.
    if prefersNone and not keepLemmas:
        tagged_sentence = [(word, None) if str(tag).startswith('#')
                           else (word, tag) for word, tag in tagged_sentence]
    if prefersNone and keepLemmas:
        tagged_sentence = [(word, lemma, None) if str(tag).startswith('#')
                           else (word, lemma, tag) for word, lemma, tag in tagged_sentence]
    return tagged_sentence
