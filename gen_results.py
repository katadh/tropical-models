import xml.etree.ElementTree as et

from allwords_wsd import disambiguate

from nltk.corpus import wordnet as wn
from nltk import word_tokenize

import re

def disambig_documents(doc_path, out_path):
    tree = et.parse(doc_path)
    root = tree.getroot()

    all_results = []
    for doc in root.findall('text'):
        doc_results = disambig_document(doc)
        all_results.append((doc.get('id'), doc_results)) 

    with open(out_path, 'w') as out_file:
        for doc_id, doc_results in all_results:
            for result in doc_results:
                out_file.write(doc_id + ' ' + result[0] + ' ' + result[1] + '\n')

#takes in the document xml tree
def disambig_document(doc):
    sents = []
    word_locs = []
    for sent_tree in doc.findall('s'):
        sent, sent_word_locs = get_sentence(sent_tree)
        sents.append(sent)
        word_locs.append(sent_word_locs)

    #do topic matching here

    results = []
    for sent, sent_word_locs in zip(sents, word_locs):
        #print sent
        #print sent_word_locs
        disambig_sent = disambiguate_sentence(sent)
        #print disambig_sent
        index = 0
        for word, synset in disambig_sent:
            #print word
            if index in sent_word_locs:
                if synset is None:
                    synset = wn.synsets(word)[0]
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

def disambiguate_sentence(sent):
    return disambiguate(sent)
