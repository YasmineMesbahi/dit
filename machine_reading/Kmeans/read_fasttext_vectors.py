import numpy as np
import sys


def read_word_vector(file_line, embedding_dim):
    split_line = file_line.split()
    word, vector = split_line[0], split_line[1:]
    try:
        vector = np.asarray([float(num) for num in vector], dtype='float32')
        return word, vector
    except:
        # print(file_line)
        return word, np.random.randn(embedding_dim)*0.2


def read_word_vectors(file_name, embedding_dim, word_set):
    word_vectors = {}
    print("-")
    for word_vector in open(file_name, encoding='utf8'):
        word, vector = read_word_vector(word_vector, embedding_dim)
        if word in word_set:
            word_vectors[word] = vector
    return word_vectors


def main(argv):
    word_vectors_path = "wiki.fr.vec"
    embedding_dim = 300
    vocabulary = ["avion", "hydravion"] #ensemble ou liste des mots dont on veut les word vectors
    vocab_size = len(vocabulary)
    word_vectors = read_word_vectors(word_vectors_path, embedding_dim, vocabulary)
    for word_value, vector in word_vectors.items():
        print(word_value, " -> ", vector)


if __name__ == "__main__":
    main(sys.argv[1:])
