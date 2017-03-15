# do POS tagging and WSD on a single article
# then throw away the tags and spit back an article with word senses disambiguated

from nltk import word_tokenize, pos_tag

def stripArticleName(pair):
	name = pair[1]
	art = pair[0]
	l = len(name.split())
	if art[:l] == name:
		art = art[l:]
	return (art, name)

def tagPOS(string):
	text = word_tokenize(unicode(string))
	#print text
	tagged = pos_tag(text)
	return tagged


if __name__ == '__main__':
	from wiki_local import get_random_wikipedia_article
	art_pair = stripArticleName(get_random_wikipedia_article())
	tagged = tagPOS(art_pair[0])
	print(tagged)