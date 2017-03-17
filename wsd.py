# do POS tagging and WSD on a single article
# then throw away the tags and spit back an article with word senses disambiguated

from nltk import word_tokenize, pos_tag
#from nltk.wsd import lesk
from pywsd import disambiguate
from pywsd.similarity import max_similarity

def stripArticleName(pair):
	name = pair[1]
	art = pair[0]
	l = len(name)

	if art[:l+2] == name + '  ':
		art = art[l+2:] #also remove initial spaces

	return (art, name)

def tagPOS(string):
	# still TODO: use n-gram taggers rather than just the default here;
	# experiment with other POS tagging packages rather than NLTK default
	text = word_tokenize(unicode(string))
	#print text
	tagged = pos_tag(text)
	return tagged

def WSD(article):
	# it looks like we will have to translate the POS tags generated above
	#   to the ones lesk likes.
	# potentially after turning unicode back to normal string format.
	# after that, just iterate through all words in each sentence to get the sense
	#   and then return the word from the resulting synset -- synset.name()
	new_art_string = ''
	art_sents = article.split('.')
	for sent in art_sents:
		sent_str = ''
		if sent == '\n':
			continue
		print sent
		disamb_sent = disambiguate(sent)
		for pair in disamb_sent:
			if pair[1] is not None:
				sent_str += ' ' + pair[1].name()
		new_art_string += sent_str + '.'
	return new_art_string

if __name__ == '__main__':
	from wiki_local import get_random_wikipedia_article
	art_pair = stripArticleName(get_random_wikipedia_article())
	#tagged = tagPOS(art_pair[0])
	new_article = WSD(art_pair[0])
	# print(new_article)