import threading
import sys
import os
import random
import json
import re

import wsd

def get_random_wikipedia_article():
    wiki_path = "../json_articles/"
    rand_folder = random.choice(os.listdir(wiki_path))
    rand_file = random.choice(os.listdir(wiki_path+rand_folder))

    f = open(wiki_path+rand_folder+'/'+rand_file)

    article = json.loads(random.choice(f.readlines()))
    title = article['title'].encode('ascii', 'ignore')
    text = article['text'].encode('ascii', 'ignore')
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^A-z .]+', '', text)
    #text = re.sub(r' +', ' ', text)
    #print text
    #print text
    #text = wsd.WSD(text)
    return (text, title)

class WikiThread(threading.Thread):
    articles = list()
    articlenames = list()
    lock = threading.Lock()

    def run(self):
        (article, articlename) = get_random_wikipedia_article()
        WikiThread.lock.acquire()
        try:
            article = wsd.WSD(article)
            WikiThread.articles.append(article)
            WikiThread.articlenames.append(articlename)
        except Exception as ex: #catch and print message for basically anything that's not a system error or keyboard interrupt
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print message
        WikiThread.lock.release()

def get_random_wikipedia_articles(n):
    maxthreads = 8
    WikiThread.articles = list()
    WikiThread.articlenames = list()
    wtlist = list()
    for i in range(0, n, maxthreads):
        print 'downloaded %d/%d articles...' % (i, n)
        for j in range(i, min(i+maxthreads, n)):
            wtlist.append(WikiThread())
            wtlist[len(wtlist)-1].start()
        for j in range(i, min(i+maxthreads, n)):
            wtlist[j].join()
    return (WikiThread.articles, WikiThread.articlenames)
