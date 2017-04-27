# compare lambda dat files from LDA output

import get_topics
from nltk.corpus import wordnet
from numpy import average, median
from math import sqrt

TOPIC_LEN = 10

def compare_two_topics(topic1, topic2):
	# takes in 2 topic sets; returns percentage of word overlap
	# assumes provided topics are the same length.
	matches = 0
	for word1 in topic1.keys():
		for word2 in topic2.keys():
			if word1 == word2:
				#print("got a match: %s and %s" % (word1, word2))
				matches += 1
			elif word1.split('.')[0] == word2:
				matches += 1
			elif word2.split('.')[0] == word1:
				matches += 1
	return matches * 1./ TOPIC_LEN

def compare_topic_sets(list1, list2):
	match_totals = []
	for top1 in list1:
		for top2 in list2:
			m = compare_two_topics(top1, top2)
			# if m != 0:
				# print("topics: %s\n %s" % (top1, top2))
				# print("similarity score: %f" % m)
			# if m > 0:
				#print("got a non-zero score")
			match_totals.append(m)
	return match_totals

def strip_synsets(list1):
	new_list = []
	for topic in list1:
		newtop = {}
		for wordsense in topic.keys():
			# todo: handle cases where multiple senses of a word are in a topic
			newtop[wordsense.split('.')[0]] = topic[wordsense]
	return new_list

def add_synsets(list1):
	new_list = []
	for topic in list1:
		newtop = {}
		for word in topic.keys():
			syns = wordnet.synsets(word)
			if len(syns) == 0:
				newtop[word] = topic[word]
			for syn in syns:
				newtop[syn.name()] = topic[word]
		new_list.append(newtop)
		# print("added synsets to turn this topic: \n%s \n\n\n\n" % topic)
		# print("into this topic:\n%s \n\n\n" % newtop)
	return(new_list)

def analyze_match_results():
	#list1 = get_topics.get_topics('wn_ambiguous.txt', 'wn_ambig_no_stop_8000.dat', TOPIC_LEN)
	list1 = get_topics.get_topics('wn_ambig_no_stop.txt', 'wn_ambig_no_stop_8000.dat', TOPIC_LEN)
	list2 = get_topics.get_topics('synset_dict.txt', '8000_jcn.dat', TOPIC_LEN)
	# list1 = get_topics.get_topics('synset_dict.txt', 'comp1.dat', TOPIC_LEN)
	# list2 = get_topics.get_topics('synset_dict.txt', 'sci_mod.dat', TOPIC_LEN)
	#new_list2 = strip_synsets(list2)
	newlist1 = add_synsets(list1)
	match_totals = compare_topic_sets(newlist1, list2)
	print("length of match_totals is %d" % len(match_totals))
	avg = average(match_totals) * sqrt(len(match_totals))
	print("average overlap percentage between the two sets times number of topics per set was %f" % avg)
	med = median(match_totals)
	print("median overlap percentage between topics from the two sets provided was %f" % med)
	ma = max(match_totals)
	print("max overlap percentage between two topics was %f" % ma)

if __name__ == '__main__':
	analyze_match_results()

"""
version using dicts that could work with expectation
def compare_two_topics(topic1, topic2):
	# takes in 2 topic sets; returns percentage of word overlap
	# assumes provided topics are the same length.
	matches = 0
	for word1 in topic1.keys():
		for word2 in topic2.keys():
			if word1 == word2:
				#print("got a match: %s and %s" % (word1, word2))
				matches += 1
			elif word1.split('.')[0] == word2:
				matches += 1
			elif word2.split('.')[0] == word1:
				matches += 1
	return matches * 1./ TOPIC_LEN
"""
