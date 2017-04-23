import threading
import sys
import os
import random
import json
import re
import time

from multiprocessing import Pool, Queue, Process

from nltk.corpus import wordnet_ic as wnic

import wsd

def get_precleaned_file(file_path):
    with open(file_path) as f:
        text = f.readline()
        return (text, file_path)

def get_wikipedia_articles_in_file(file_path, sim_data):
    results = []
    #print "opening:", file_path
    with open(file_path) as f:
        for article_line in f:
            article = json.loads(article_line)
            title = article['title'].encode('ascii', 'ignore')
            #print title
            text = article['text'].encode('ascii', 'ignore')
            text = text.lower()
            text = re.sub(r'[\n\- ]+', ' ', text)
            text = re.sub(r'[^a-z .]+', '', text)
            #text = re.sub(r' +', ' ', text)
            text = re.sub(r'[ .]+\.', '.', text)
            #print text
            #text = wsd.WSD(text, data=sim_data)
            results.append((text, title))
            #print "finished article"
    #print "returning results"
    return results

def get_random_wikipedia_article(sim_data):
    #print "getting random article"
    wiki_path = "../json_all_pages/"
    rand_folder = random.choice(os.listdir(wiki_path))
    rand_file = random.choice(os.listdir(wiki_path+rand_folder))

    f = open(wiki_path+rand_folder+'/'+rand_file)

    article = json.loads(random.choice(f.readlines()))
    title = article['title'].encode('ascii', 'ignore')
    text = article['text'].encode('ascii', 'ignore')
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^A-z .]+', '', text)
    text = re.sub(r' +', ' ', text)
    #print text
    text = wsd.WSD(text, data=sim_data)
    #print "returning result"
    return (text, title)

class WikiPool():

    def __init__(self):
        self.sim_data = wnic.ic('ic-bnc-add1.dat')
        self.q = Queue()
        self.run = True
        #self.p = Process(target=self.start_random)
        self.p = Process(target=self.start_sequential)
        self.p_count = 0
        self.p.start()

    def end(self):
        self.run = False
        self.p.join()
        
    def get_random_wikipedia_articles(self, n):
        articles = []
        titles = []
        #print "getting articles"
        for i in range(n):
            article, title = self.q.get()
            articles.append(article)
            titles.append(title)
        #print "finished getting articles:", titles
        return (articles, titles)

    def append_to_queue(self, result):
        self.p_count -= 1
        self.q.put(result)
        #print result

    def append_multiple_to_queue(self, results):
        #print "appending to queue"
        self.p_count -= 1
        for result in results:
            self.q.put(result)

    def start_sequential(self):
        print "starting sequential"
        pool = Pool(processes=8)

        wiki_path = '../ground_truth/disambig/'
        file_names = os.listdir(wiki_path)
        #print file_names
        i = 0
        while self.run:
            #if self.p_count < 16 and self.q.qsize() < 264 and i < len(file_names):
            if self.p_count < 16 and self.q.qsize() < 1280 and i < len(file_names):
                self.p_count += 1
                #print file_names[i]
                #pool.apply_async(get_wikipedia_articles_in_file, args=(wiki_path+file_names[i], self.sim_data), callback=self.append_multiple_to_queue)
                pool.apply_async(get_precleaned_file, args=(wiki_path+file_names[i],), callback=self.append_to_queue)
                i += 1
            else:
                time.sleep(1)
                #time.sleep(5)

        print "closing/joining pool"
        pool.close()
        pool.join()
                    
    def start_random(self):
    
        print "starting process pool"
        pool = Pool(processes=8)

        while self.run:
            if self.p_count < 16:
                #print "starting process"
                self.p_count += 1
                pool.apply_async(get_random_wikipedia_article, args=(self.sim_data,), callback=self.append_to_queue)
            else:
                #print "sleeping"
                time.sleep(1)
                
        pool.close()
        pool.join()
        
