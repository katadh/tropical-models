import xml.etree.ElementTree as et

from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic as wnic
from nltk import word_tokenize

import re
import random

from allwords_wsd import disambiguate, disambiguate_new
from similarity import max_similarity
import baseline

import topic_fitting
import get_topics

sim_data = wnic.ic('ic-bnc-add1.dat')

def get_vocab(vocab_path):
    with open(vocab_path) as vocab_file:
        vocab = vocab_file.readlines()
        vocab = [v.strip() for v in vocab]
        return vocab

def disambig_documents(doc_path, out_path):
    tree = et.parse(doc_path)
    root = tree.getroot()

    vocab = get_vocab('wn_ambig_no_stop.txt')
    topics = get_topics.get_topics('wn_ambig_no_stop.txt', 'wn_ambig_no_stop_8000.dat', 150)

    all_results = []
    for doc in root.findall('text'):
        doc_results = disambig_document(doc, vocab, topics)
        all_results.append((doc.get('id'), doc_results)) 

    with open(out_path, 'w') as out_file:
        for doc_id, doc_results in all_results:
            for result in doc_results:
                out_file.write(doc_id + ' ' + result[0] + ' ' + result[1] + '\n')

#takes in the document xml tree
def disambig_document(doc, vocab, topics):
    sents = []
    word_locs = []
    for sent_tree in doc.findall('s'):
        sent, sent_word_locs = get_sentence(sent_tree)
        sents.append(sent)
        word_locs.append(sent_word_locs)

    doc_text = ''
    for sent in sents:
        doc_text += ' ' + sent

    extra_words = []
    best_topic = topic_fitting.find_closest_topic(doc_text, vocab, topics)
    extra_words = topic_fitting.get_n_best_words(30, best_topic)
    print extra_words

    results = []
    for sent, sent_word_locs in zip(sents, word_locs):
        #print sent
        #print sent_word_locs
        disambig_sent = disambiguate_sentence(sent, extra_words)
        #print disambig_sent
        index = 0
        for word, synset in disambig_sent:
            #print word
            if index in sent_word_locs:
                if synset is None:
                    synset = baseline.max_lemma_count(word)
                if sent_word_locs[index][1] != word:
                    print "Incorrect matching!"
                word_id = 'eng-30-' + str(synset.offset()).zfill(8) + '-' + synset.pos()
                word_loc = sent_word_locs[index][0]
                results.append((word_loc, word_id))
            index += 1
    return results

def get_sentence(sent_tree):
    sentence = sent_tree.text
    sentence = word_tokenize(sentence)
    word_locs = {}
    index = len(sentence)
    for wsd_word in sent_tree.findall('head'):
        word_locs[index] = [wsd_word.get('id'), wsd_word.text]
        sentence.append(wsd_word.text)

        tail_words = wsd_word.tail
        tail_words = word_tokenize(tail_words) 
        sentence.extend(tail_words)
        index += len(tail_words) + 1

    #print sentence
    #print word_locs
    return ' '.join(sentence), word_locs

def disambiguate_sentence(sent, extras):
    return disambiguate_new(sent, extra_words=extras, algorithm=max_similarity, similarity_option='jcn', similarity_data=sim_data)
    #return disambiguate_new(sent, extra_words=extras)

#def disambiguate_sentence(sent):
#    result = []
#    for word in sent.split():
#        synsets = wn.synsets(word)
#
#        if len(synsets) > 0:
#            res = random.choice(synsets)
#        else:
#            res = None
#
#        result.append((word, res))
#    return result

#def disambiguate_sentence(sent):
#    results = []
#    for word in sent.split():
#        if len(wn.synsets(word)) > 0:
#            results.append((word, baseline.max_lemma_count(word)))
#        else:
#            results.append((word, None))
#    return results
