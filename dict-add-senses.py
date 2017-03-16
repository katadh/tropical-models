from nltk.corpus import words
from nltk.corpus import wordnet
path_to_dict_in = '/Users/kristen/Documents/Semantics/tropical-models/dict-ldavb-7k.txt'
new_dict_path = '/Users/kristen/Documents/Semantics/tropical-models/expanded-ldavb-7k-dict.txt'

def addSenses(inname = path_to_dict_in, outname = new_dict_path):
	lines = []
	with open(inname) as f:
		lines = f.readlines()

	all_eng_words = set(words.words()) #from nltk
	new_dict = []

	for word in lines:
		clean = word.strip()
		print "word: %s" % word
		if clean in all_eng_words:
			all_synonyms = wordnet.synsets(clean)
			for item in all_synonyms:
				nm = item.name()
				#print nm.split('.')[0]
				if nm.split('.')[0] == clean:
					new_dict.append(nm)
					#print "sense: %s" % nm

	with open(outname, 'w') as file_handler:
		for item in new_dict:
			file_handler.write("{}\n".format(item))
	print "wrote a new dict with all the word senses to %s" % (outname)
	return

if __name__ == '__main__':
	addSenses()