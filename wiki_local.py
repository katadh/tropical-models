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

def get_random_wikipedia_article(sim_data):
    #print "getting article"
    wiki_path = "../json_articles/"
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
    #text = wsd.WSD(text, sim_data)
    return (text, title)

#class WikiThread(threading.Thread):
#    articles = list()
#    articlenames = list()
#    lock = threading.Lock()
#
#    def run(self):
#        (article, articlename) = get_random_wikipedia_article()
#        WikiThread.lock.acquire()
#        try:
#            article = wsd.WSD(article)
#            WikiThread.articles.append(article)
#            WikiThread.articlenames.append(articlename)
#        except Exception as ex: #catch and print message for basically anything that's not a system error or keyboard interrupt
#            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
#            message = template.format(type(ex).__name__, ex.args)
#            print message
#        WikiThread.lock.release()

class WikiPool():

    def __init__(self):
        self.sim_data = wnic.ic('ic-bnc-add1.dat')
        self.q = Queue()
        self.p = Process(target=self.start)
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
        #print articles[1]
        return (articles, titles)

    def append_to_queue(self, result):
        self.p_count -= 1
        self.q.put(result)
        #print result
        return

    def start(self):
    
        #print "getting wiki articles"
        pool = Pool(processes=8)

        while self.run:
            if self.p_count < 16:
                #print "starting process"
                self.p_count += 1
                pool.apply_async(get_random_wikipedia_article, args=(self.sim_data,), callback=self.append_to_queue)
            else:
                #print "sleeping"
                time.sleep(1)
                
            #results = [pool.apply_async(get_random_wikipedia_article) for i in range(64)]
            #if self.run:
            #    for res in results:
            #        #print "adding to queue"
            #        self.q.put(res.get())
            #    print "got 64 articles"

        pool.close()
        pool.join()
        
        #articles = []
        #titles = []
        #for res in results:
        #    article, title = res.get()
        #    articles.append(article)
        #    titles.append(title)

        #pool.close()
        #pool.join()

        ##articles = [pair[0] for pair in article_title_pairs]
        ##titles = [pair[1] for pair in article_title_pairs]

        #print "finished getting wiki articles"

        #return (articles, titles)

        ##maxthreads = 8
        ##WikiThread.articles = list()
        ##WikiThread.articlenames = list()
        ##wtlist = list()
        ##for i in range(0, n, maxthreads):
        ##    print 'downloaded %d/%d articles...' % (i, n)
        ##    for j in range(i, min(i+maxthreads, n)):
        ##        wtlist.append(WikiThread())
        ##        wtlist[len(wtlist)-1].start()
        ##    for j in range(i, min(i+maxthreads, n)):
        ##        wtlist[j].join()
        ##return (WikiThread.articles, WikiThread.articlenames)
