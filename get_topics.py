import numpy

def get_topics(vocab_file, lambda_file, n):

    vocab = str.split(file(vocab_file).read())
    testlambda = numpy.loadtxt(lambda_file)

    topics = []

    for k in range(0, len(testlambda)):
        lambdak = list(testlambda[k, :])
        lambdak = lambdak / sum(lambdak)
        temp = zip(lambdak, range(0, len(lambdak)))
        temp = sorted(temp, key = lambda x: x[0], reverse=True)
        # feel free to change the "53" here to whatever fits your screen nicely.
        topic_words = {}
        for i in range(0, n):
            topic_words[vocab[temp[i][1]]] = temp[i][0]

        topics.append(topic_words)

    return topics
