# extract all categories from a wiki dump, e.g. from https://en.wikipedia.org/wiki/Special:Export
# track articles they come from
# and count em

from collections import deque

import os
import json
import pickle

fn = "/Users/kristen/Box Sync/Semantics/Wikipedia-20170407184627.xml"

def scan_file(fn, cat_dict):
	with open(fn) as f:
		on_art_id = False
		rightns = False
		for line in f:
			if line == "  <page>\n": #track whether we're on first ID in a new page
				on_art_id = True
				#print "saw a page tag; set on_art_id to True"
			elif line.split('>')[0] == "    <ns":
				if line.split('>')[1].split('<')[0] == "0":
					rightns = True
			elif on_art_id and line.split('>')[0] == '    <id':
				curr_id = line.split('>')[1].split('<')[0]
				on_art_id = False #revision IDs will start coming up; ignore those
				#print "just set curr_id to", curr_id
			elif rightns == True and line.split(':')[0] == "[[Category":
				cat=line.split(':')[1].split(']')[0]
				if '|' in cat:
					cat = cat.split('|')[0]
				if cat in cat_dict:
					cat_dict[cat].append(curr_id)
				else:
					cat_dict[cat] = [curr_id]
					#print "added %s to dict" % cat

def handler(files = [fn]):
	cat_dict = dict()
	for filename in files:
		scan_file(filename, cat_dict)
	        #print cat_dict

	biggest = 0
	big_cat = None
	for key in cat_dict:
		if len(cat_dict[key]) > biggest:
			biggest = len(cat_dict[key])
			big_cat = key
	                print "the biggest category is %s with %d items" % (big_cat, biggest)

	return cat_dict

def create_cat_dict(xml_file):
        cat_dict = {}
	with open(xml_file) as f:
		rightns = False
                curr_title = ''
		for line in f:
			if line == "  <page>\n": #track whether we're on first ID in a new page
				on_page = True
                                rightns = False
                        elif line.split('>')[0] == "    <title":
                                curr_title = line.split('>')[1].split('<')[0]
			elif line.split('>')[0] == "    <ns":
				if line.split('>')[1].split('<')[0] == "14":
					rightns = True
                                        curr_title = curr_title.split(':')[1]
                                        if curr_title not in cat_dict:
                                                cat_dict[curr_title] = []
                                        #print "title:", curr_title
			elif rightns == True and line.split(':')[0] == "[[Category":
				cat=line.split(':')[1].split(']')[0]
				if '|' in cat:
					cat = cat.split('|')[0]
				if cat in cat_dict:
					cat_dict[cat].append(curr_title)
				else:
					cat_dict[cat] = [curr_title]
                return cat_dict
        

#wiki_base_url = 'https://en.wikipedia.org'
#
#def get_descendant_categories(url, level, subcats):
#
#    page = urllib2.urlopen(url)
#    soup = BSoup(page.read(), "html5lib")
#
#    subcat_div = soup.find(id='mw-subcategories')
#
#    if subcat_div:
#        child_cats = subcat_div.find_all('a',href=re.compile('/wiki/Category:.*'))
#        for child_cat in child_cats:
#            if child_cat.text not in subcats:
#                #print child_cat.get('href')
#                subcats.add(child_cat.text)
#                print ' ' * level, level, child_cat.text, len(subcats)
#                get_descendant_categories(wiki_base_url + child_cat.get('href'), level + 1, subcats)

def get_descendant_categories(category, cat_dict, max_depth=float('Inf')):
        descendant_cats = set()

        cat_queue = deque()
        cat_queue.append((category, 0))

        while len(cat_queue) > 0:
                next_cat, depth = cat_queue.popleft()
                if next_cat not in descendant_cats:
                        descendant_cats.add(next_cat)
                        if (depth + 1) <= max_depth:
                                for child_cat in cat_dict[next_cat]:
                                        cat_queue.append((child_cat, depth + 1))
        return descendant_cats

def get_article_ids_in_categories(categories, cat_article_dict):
        article_ids = set()

        for cat in categories:
                if cat in cat_article_dict:
                        for article_id in cat_article_dict[cat]:
                                article_ids.add(article_id)
        return article_ids

def pull_articles(article_ids, in_dir, out_path):
        path_modifier = 0
        articles_pulled = 0
        open(out_path+str(path_modifier), 'a').close()
        for folder in os.listdir(in_dir):
                for file_name in os.listdir(in_dir+folder):
                        if os.stat(out_path+str(path_modifier)).st_size > 3200000:
                                path_modifier += 1
                        with open(out_path+str(path_modifier), 'a') as out_file:
                                with open(in_dir+folder+'/'+file_name) as article_file:
                                        for article_line in article_file:
                                                article = json.loads(article_line)
                                                if article['id'] in article_ids:
                                                        articles_pulled += 1
                                                        json.dump(article, out_file)
                                                        out_file.write("\n")
        return articles_pulled

def load_object(file_path):
        with open(file_path) as object_file:
                return pickle.load(object_file)

def save_object(file_path, in_object):
        with open(file_path) as object_file:
                pickle.dump(in_object, object_file)
                
                                                        
                                        
if __name__ == "__main__": 
	handler()
