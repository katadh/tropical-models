
import re

def get_word_counts(text, vocab):
    text = text.lower()
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^a-z ]', '', text)
    text = re.sub(r' +', ' ', text)

    word_counts = {}
    words = text.split()
    for word in words:
        if word in vocab:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1
    return word_counts

                
def match_topic(word_counts, topic):
    score = 0
    for word in word_counts.keys():
        if word in topic:
            score += word_counts[word] * topic[word]

    return score


def find_closest_topic(text, vocab, topics):
    word_counts = get_word_counts(text, vocab)

    best_match = {}
    best_match_value = 0
    for topic in topics:
        topic_score = match_topic(word_counts, topic)
        if topic_score > best_match_value:
            best_match = topic
            best_match_value = topic_score

    return best_match

def get_n_best_words(n, topic):
    reverse_dict = {value: key for key, value in topic.iteritems()}
    highest_expts = sorted(reverse_dict.keys(), reverse=True)[:n]
    words = [reverse_dict[expt] for expt in highest_expts]
    return words
