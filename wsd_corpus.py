import os
import re

import xml.etree.ElementTree as et

from nltk.corpus import wordnet as wn


def pull_files(in_path, out_path, nwm, ambig=True):
    dir_contents = os.listdir(in_path)
    for f in dir_contents:
        if f != 'simple-wsd-doc.dtd':
            if os.path.isdir(in_path+'/'+f):
                pull_files(in_path+'/'+f, out_path, nwm, ambig)
            elif os.path.isfile(in_path+'/'+f):
                if ambig:
                    pull_file(in_path+'/'+f, out_path+'/'+f, nwm)
                else:
                    pull_file(in_path+'/'+f, out_path+'/'+f, nwm, ambig=False)


def pull_file(file_path, out_file_path, nwm, ambig=True):
    tree = et.parse(file_path)
    root = tree.getroot()
    with open(out_file_path, 'w') as out_file:
        for word_elem in root.findall('word'):
            sense = word_elem.get("sense")
            if ambig != True and sense != None and sense in nwm:
                synset_name = nwm[sense]
                out_file.write(synset_name + ' ')
            else:
                word = word_elem.get("text").lower()
                word = re.sub(r'[^a-z]+', '', word)
                if word != '':
                    out_file.write(word + ' ')


def get_noad_wordnet_map(manual_map, auto_map):
    nwm = {}
    with open(manual_map) as map1:
        mappings = map1.readlines()
        for mapping in mappings:
            noad, wn_key = mapping.split()
            wn_key = wn_key.split(',')[0]
            try:
                synset_name = wn.lemma_from_key(wn_key).synset().name()
                nwm[noad] = synset_name
            except:
                print wn_key

    with open(auto_map) as map2:
        mappings = map2.readlines()
        for mapping in mappings:
            noad, wn_key = mapping.split()
            if noad not in nwm:
                try:
                    synset_name = wn.lemma_from_key(wn_key).synset().name()
                    nwm[noad] = synset_name
                except:
                    print wn_key
    return nwm
                
    
