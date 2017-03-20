# do POS tagging and WSD on a single article
# then throw away the tags and spit back an article with word senses disambiguated

from nltk import word_tokenize, pos_tag
#from nltk.wsd import lesk
from pywsd import disambiguate
from pywsd.similarity import max_similarity

def WSD(article):
	# takes in an article string and outputs a disambiguated article string
	# throws away any words not found in WordNet
	# often changes the word itself -- e.g. disambiguating "involving" in one case yielded "necessitate.v.01"
	# always changes inflected forms of verbs and nouns to the base form
	new_art_string = ''
	art_sents = article.split('.')
	for sent in art_sents:
		sent_str = ''
		if sent == '\n':
			continue
                sent = sent.strip()
		#print sent
		disamb_sent = disambiguate(sent)
		for pair in disamb_sent:
			if pair[1] is not None:
				sent_str += ' ' + pair[1].name()
		new_art_string += sent_str + '.'
	return new_art_string

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

#if __name__ == '__main__':
#	from wiki_local import get_random_wikipedia_article
#	art_pair = stripArticleName(get_random_wikipedia_article())
#	# tagged = tagPOS(art_pair[0])
#	new_article = WSD(art_pair[0])
#	# print(new_article)
