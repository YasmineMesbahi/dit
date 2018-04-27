#! /usr/bin/env python
#coding=utf-8
""" Process vector representations of each CDS element term in a given graph """

from neo4j.v1 import GraphDatabase, basic_auth
import nltk
import argparse
from machine_reading.Kmeans.read_fasttext_vectors import *
from pathlib import Path
import os


# creates file word_vectors.npy containing vector representations of each word from the vocabulary of the corpus
def process_and_save_word_vectors(host, login, password, word_vectors_path, normalized):

    V = Path("V.npy")

    if V.is_file() is True:
        os.remove("V.npy")

    # start connection to Neo4j DB
    driver = GraphDatabase.driver(host, auth=basic_auth(login, password))
    session = driver.session()

    # build vocabulary from graph database

    print("get all CDS elements core values")
    all_cores = session.run("MATCH (cds:CDS)-[:subject|:verb|:object|:time|:place]->(elem) "
                            "RETURN elem.core AS core")

    print("build vocabulary")
    vocabulary = set()
    for core in all_cores:
        core_value = core["core"]
        core_tokens = nltk.wordpunct_tokenize(core_value)
        for core_token in core_tokens:
            vocabulary.add(core_token.lower())

    # load word embeddings for each word of the vocabulary
    print("get embeddings for each vocabulary element")

    embedding_dim = 300
    word_vectors = read_word_vectors(word_vectors_path, embedding_dim, vocabulary)

    if normalized:

        for key in word_vectors:

            norm = word_vectors[key] / np.linalg.norm(word_vectors[key])
            word_vectors[key] = norm

        print("save embeddings normalized")
        np.save('word_vectors_normalized.npy', word_vectors)

    else:

        print("save embeddings not normalized")
        np.save('word_vectors.npy', word_vectors)


def get_word_vectors(normalized):


    if normalized:

        word_vectors = np.load('word_vectors_normalized.npy').item()

    else:

        word_vectors = np.load('word_vectors.npy').item()

    return word_vectors


def main(argv):
    # default values
    host = "bolt://localhost:7687"
    login = "neo4j"
    password = "synapsedev"

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", "-loc", help = "Neo4j host. Default to " + host, default = host)
    parser.add_argument("--login", "-log", help = "Login Neo4j. Default to " + login, default = login)
    parser.add_argument("--password", "-psw", help = "Password Neo4j. Default to " + password, default = password)
    args = parser.parse_args()
    print(args)

    # exit script if command line arguments are not valid
    if args.login == None:
        print("Error login.")
        sys.exit()

    if args.password == None:
        print("Error password.")
        sys.exit()

    if args.host == None:
        print("Error host.")
        sys.exit()

    normalized = False

    process_and_save_word_vectors(args.host, args.login, args.password, normalized)
    word_vectors = get_word_vectors(normalized)


if __name__ == "__main__":
	main(sys.argv[1:])
