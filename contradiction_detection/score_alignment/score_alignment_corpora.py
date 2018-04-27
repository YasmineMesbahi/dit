#!/usr/bin/env python
# coding: utf-8

from contradiction_detection.score_alignment.score_alignment_text import *
from contradiction_detection.score_alignment.WS_syntactictagging import *
from machine_reading.mrtoneo4j.mrtoneo4j import *
import argparse
from pathlib import Path

myfile = '../../resources/corpora/multinli/translated/multinli_0.9_dev_matched_1-1000_translated.jsonl'

# default values
host = "bolt://localhost:7687"
login = "neo4j"
password = "synapsedev"
mr_ws_url = "http://api-synapse-dev.azurewebsites.net/machinereading/extractcds"
apikey = "HT8R7PP6N8U8h8Bn9hrE5NX2R2cdxt32y58Lzqnc"
driver = GraphDatabase.driver(host, auth=basic_auth(login, password))
session = driver.session()


def main(argv):
    # default values
    host = "bolt://localhost:7687"
    login = "neo4j"
    password = "synapsedev"
    mr_ws_url = "http://api-synapse-dev.azurewebsites.net/machinereading/extractcds"
    apikey = "HT8R7PP6N8U8h8Bn9hrE5NX2R2cdxt32y58Lzqnc"
    lang = "fr"

    pair_1_path = "../../resources/corpora/multinli/translated/multinli_0.9_dev_matched_1-1000_translated.jsonl"
    #text_2_path = "../../resources/corpora/sample_texts/machine_reading/mrtoneo4j/file_2.txt"
    driver = GraphDatabase.driver(host, auth=basic_auth(login, password))
    session = driver.session()

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", "-loc", help = "Neo4j host. Default to " + host, default = host)
    parser.add_argument("--login", "-log", help = "Login Neo4j. Default to " + login, default = login)
    parser.add_argument("--password", "-psw", help = "Password Neo4j. Default to " + password, default = password)
    parser.add_argument("--url", "-u", help = "Machine Reading endpoint URL. Default to " + mr_ws_url, default = mr_ws_url)
    parser.add_argument("--key", "-k", help = "API key allowing to consume Machine Reading WS.", default = apikey)
    parser.add_argument("--lang", "-l", help = "Language of the texts to be analysed. Possible values: fr for French, en for English. Default to " + lang , default = lang)
    parser.add_argument("--path1", "-p1", help = "Path to the first file containing text to be analysed. Default to " + pair_1_path, default = pair_1_path)
    #parser.add_argument("--path2", "-p2", help = "Path to the second file containing text to be analysed. Default to " + text_2_path, default = text_2_path)
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

    if args.url == None:
        print("No endpoint URL has been specified.")

    if args.key == None:
        print("No API key has been specified.")
        sys.exit()

    if args.lang == None or (args.lang != "fr" and args.lang != "en") :
        print("Supported languages are French and English.")
        sys.exit()

    if args.path1 == None or Path(args.path1).exists() == False:
        print("Specified input file 1 does not exist.")
        sys.exit()


    model = KeyedVectors.load_word2vec_format("twitter_w2v.gensim")

    # load content from input files (jsonl format)
    sentence1_model = []
    sentence2_model = []
    with jsonlines.open(args.path1) as reader:
        for obj in reader:
            sentence1 = obj["sentence1"].lower().split()
            sentence2 = obj["sentence2"].lower().split()

            stopwords = nltk.corpus.stopwords.words('french')
            sentence1 = [w for w in sentence1 if w not in stopwords]
            sentence2  = [w for w in sentence2 if w not in stopwords]

            # Compute WMD.
            distance = model.wmdistance(sentence1, sentence2)
            print("%s %s > %f" %( sentence1, sentence2, distance ))

            # Compute n_similarity
            # for i in sentence1:
            #     if i in model:
            #         sentence1_model.append(i)
            # for i in sentence2:
            #     if i in model:
            #         sentence2_model.append(i)
            #
            # print(sentence1_model)
            # print(sentence2_model)
            # distance = model.n_similarity(sentence1_model, sentence2_model)
            # print(" > %f" % distance)

            # print(obj["gold_label"] + "\t" + str(best_alignment_score))

            # store scores and classes
            with open("../../resources/corpora/multinli/score/test.tsv","a+") as f:
                 f.write(obj["gold_label"] + "\t" + str(distance) + "\n")

if __name__ == "__main__":
	main(sys.argv[1:])