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

def get_wikipedia_articles_in_file(file_path, sim_data):
    results = []
    with open(file_path) as f:
        for article_line in f:
            article = json.loads(article_line)
            title = article['title'].encode('ascii', 'ignore')
            text = article['text'].encode('ascii', 'ignore')
            text = re.sub(r'\n', ' ', text)
            text = re.sub(r'[^A-z .]+', '', text)
            text = re.sub(r' +', ' ', text)
            #print text
            text = wsd.WSD(text, data=sim_data)
            results.append((text, title))
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
        self.p = Process(target=self.start_random)
        #self.p = Process(target=self.start_sequential)
        self.p_count = 0
        self.run = True
        self.p.start()

    def end(self):
        self.run = False
        self.p.join()
        
    def get_random_wikipedia_articles(self, n):
        articles = []
        titles = []
        print "getting articles"
        for i in range(n):
            article, title = self.q.get()
            articles.append(article)
            titles.append(title)
        print "finished getting articles:", len(titles)
        return (articles, titles)

    def append_to_queue(self, result):
        self.p_count -= 1
        self.q.put(result)
        #print result

    def append_multiple_to_queue(self, results):
        self.p_count -= 1
        for result in results:
            self.q.put(result)

    def start_sequential(self):

        pool = Pool(processes=8)

        wiki_path = '../ecology_articles/'
        for file_name in os.listdir(wiki_path):
            while self.run:
                if self.p_count >= 16:
                    self.p_count += 1
                    pool.apply_async(get_wikipedia_articles_in_file, args=(wiki_path+file_name, self.sim_data), callback=self.append_multiple_to_queue)
                else:
                    time.sleep(1)
                    
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
        
