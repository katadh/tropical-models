# do POS tagging and WSD on a single article
# then throw away the tags and spit back an article with word senses disambiguated

from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet_ic as wnic
#from nltk.wsd import lesk

from allwords_wsd import disambiguate_new
from similarity import max_similarity

def WSD(article, data=None):
        #print "disambiguating article"
	# takes in an article string and outputs a disambiguated article string
	# throws away any words not found in WordNet
	# often changes the word itself -- e.g. disambiguating "involving" in one case yielded "necessitate.v.01"
	# always changes inflected forms of verbs and nouns to the base form
	new_art_string = ''
	art_sents = article.split('.')
	#print "num sents:", len(art_sents)
	for sent in art_sents:
		try:
			sent_str = disambig_sent(sent, data)
		except IndexError:
			sent_str = ''
		new_art_string += sent_str
	return new_art_string[1:]

def disambig_sent(sent, data):
	#print sent
	sent_str = ''
	if sent == '\n':
		return ''
	sent = sent.strip()
	#print sent
	disamb_sent = []
	if data == None:
		disamb_sent = disambiguate_new(sent, algorithm=max_similarity, similarity_option='jcn', keepLemmas=False, similarity_data=wnic.ic('ic-bnc-add1.dat'))
	else:
		#print "disambiguating sentence"
		disamb_sent = disambiguate_new(sent, algorithm=max_similarity, similarity_option='jcn', similarity_data=data)
		#print "finished with sentence"
		for pair in disamb_sent:
			if pair[1] is not None:
				sent_str += ' ' + pair[1].name()
	return sent_str
                                
def stripArticleName(pair):
	# strips off article name from front of article text
	# maybe irrelevant
	name = pair[1]
	art = pair[0]
	l = len(name)
	if art[:l+2] == name + '  ':
		art = art[l+2:] #also remove initial spaces
	return (art, name)

def tagPOS(string):
	# basically irrelevant. 
	# if we want to use this, consider using n-gram taggers rather than just the default here;
	# and/or experiment with other POS tagging packages rather than NLTK default
	text = word_tokenize(unicode(string))
	tagged = pos_tag(text)
	return tagged

if __name__ == '__main__':
	from wiki_local import get_random_wikipedia_article
	art_pair = stripArticleName(get_random_wikipedia_article(1))
	# tagged = tagPOS(art_pair[0])
	new_article = WSD(art_pair[0])
	print(new_article)
