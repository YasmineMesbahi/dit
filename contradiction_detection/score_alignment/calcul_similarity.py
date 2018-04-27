# ! /usr/bin/env python
# coding=utf-8
""" calcul similarity for each case """

from machine_reading.mrtoneo4j.mrtoneo4j import *
from contradiction_detection.score_alignment.score_alignment_mr import *
from neo4j.v1 import GraphDatabase, basic_auth
from pathlib import Path
from gensim.models.keyedvectors import KeyedVectors
import jsonlines
import nltk
from nltk import word_tokenize
import argparse

def similarity(mr, model, sim, files_content, session, lang, mr_url, key):

    if mr == True:
        apply_machine_reading(session, files_content, mr_url, key, lang)
        distance = process_alignment_between_texts(session, lang, files_content, sim, model)

    else:

        sentence1 = word_tokenize(files_content['sentence1'].lower())
        sentence2 =  word_tokenize(files_content['sentence2'].lower())

        stopwords = nltk.corpus.stopwords.words('french')
        sentence1 = [w for w in sentence1 if w not in stopwords]
        sentence2 = [w for w in sentence2 if w not in stopwords]

        # N_SIMILARITY
        if sim == "n_similarity":
            words1 = [w for w in sentence1 if w in model]
            words2 = [w for w in sentence2 if w in model]

            if words1 == [] or words2 == []:
                distance = 0
            else:
                distance = model.n_similarity(words1, words2)

        # WMDISTANCE
        if sim == "wmdistance":
            distance = model.wmdistance(sentence1, sentence2)
            if distance == float("inf"):
                distance = 0
            else:
                distance = 1 / (1 + distance)

    return distance


def main(argv):
    # default values
    host = "bolt://localhost:7687"
    login = "neo4j"
    password = "synapsedev"
    mr_ws_url = "http://api-synapse-dev.azurewebsites.net/machinereading/extractcds"
    apikey = "HT8R7PP6N8U8h8Bn9hrE5NX2R2cdxt32y58Lzqnc"
    lang = "fr"
    corpora_path = "../../resources/corpora/multinli/translated/multinli_0.9_dev_matched_1-1000_translated.jsonl"

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", "-loc", help = "Neo4j host. Default to " + host, default = host)
    parser.add_argument("--login", "-log", help = "Login Neo4j. Default to " + login, default = login)
    parser.add_argument("--password", "-psw", help = "Password Neo4j. Default to " + password, default = password)
    parser.add_argument("--url", "-u", help = "Machine Reading endpoint URL. Default to " + mr_ws_url, default = mr_ws_url)
    parser.add_argument("--key", "-k", help = "API key allowing to consume Machine Reading WS.", default = apikey)
    parser.add_argument("--lang", "-l", help = "Language of the texts to be analysed. Possible values: fr for French, en for English. Default to " + lang , default = lang)
    parser.add_argument("--path", "-p1", help = "Path to the first file containing text to be analysed. Default to " + corpora_path, default = corpora_path)
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

    if args.path == None or Path(args.path).exists() == False:
        print("Specified input file 1 does not exist.")
        sys.exit()

    # start connection to Neo4j DB
    driver = GraphDatabase.driver(host, auth=basic_auth(login, password))
    session = driver.session()

    model = KeyedVectors.load_word2vec_format("../../resources/lexical_resources/wikifrdict_deserializing.gensim")
    #model = KeyedVectors.load_word2vec_format("../../resources/lexical_resources/twitter_w2v.gensim")

    with jsonlines.open(args.path) as reader:
        for obj in reader:
            sentence1 = obj["sentence1"]
            sentence2 = obj["sentence2"]

            files_content = {"sentence1": sentence1, "sentence2": sentence2}
            print(files_content)

            score = similarity(False, model, "n_similarity",
                               files_content, session, args.lang, args.url, args.key)
            print(score)
            # store scores and classes
            with open("../../resources/corpora/multinli/score/wikipedia/score_wmdistance_MR.tsv", "a+") as f:
                f.write(obj["gold_label"] + "\t" + str(score) + "\n")

    session.close()

if __name__ == "__main__":
	main(sys.argv[1:])