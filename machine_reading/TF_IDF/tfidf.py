from sklearn.feature_extraction.text import CountVectorizer
import argparse
from neo4j.v1 import GraphDatabase, basic_auth
from machine_reading.mrtoneo4j.mrtoneo4j import apply_machine_reading
from pathlib import Path
from utils.browse_files import get_filenames_recursively
import sys
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import numpy as np

rm_stopunctuation = True

def clean_sentence(tokens):
    file = open("stop_punctuation.txt", "r")
    stopunctuation = file.read()
    tokens = [t.lower() for t in tokens]
    if rm_stopunctuation : tokens = [t for t in tokens if t not in stopunctuation]
    return tokens

def perform_sumbasic_tfidf(localhost, login, password, mr_ws_url, mr_apikey, lang):
    driver = GraphDatabase.driver(localhost, auth=basic_auth(login, password))
    session = driver.session()
    for thematic in range(1, 21):
        for cluster in range(1, 3):
            input_path = "../../resources/corpora/sample_texts/machine_reading/summarization/Corpus_RPM2/Corpus_RPM2_documents"
            file_start = "../../resources/corpora/sample_texts/machine_reading/summarization/Corpus_RPM2/Corpus_RPM2_documents\T" + str(thematic).zfill(2) + "_C" + str(cluster)
            summary_output_filepath = "../Rouge/test-summarization/system\T" + str(thematic).zfill(2) + "C" + str(cluster) + "_sumbasictfidf.txt"
            filenames = get_filenames_recursively(input_path)
            corpus = []
            files_content = {}
            for filename in filenames:
                if filename.startswith(file_start) and filename.endswith('.txt'):
                    with open(filename, "r") as current_file:
                        files_content[filename] = current_file.read()
                        corpus.append(files_content[filename])

            vectorizer = CountVectorizer(min_df=1)
            X = vectorizer.fit_transform(corpus)
            transformer = TfidfTransformer(smooth_idf=False)
            tfidf = transformer.fit_transform(X)
            tfidf_sum = tfidf.toarray().sum()
            apply_machine_reading(session,files_content, mr_ws_url, mr_apikey, lang)
            all_cdss = session.run("MATCH (cds:CDS) "
                               "OPTIONAL MATCH (cds)-[:subject]->(subj) "
                               "OPTIONAL MATCH (cds)-[:verb]->(verb) "
                               "OPTIONAL MATCH (cds)-[:object]->(obj) "
                               "OPTIONAL MATCH (cds)-[:time]->(time) "
                               "OPTIONAL MATCH (cds)-[:place]->(place) "
                               "RETURN subj.core AS subject_core, verb.core AS verb_core, obj.core AS object_core, cds.verbatim as verbatim, time.core AS time_core, place.core as place_core")

            count = session.run("MATCH (cds:CDS) "
                            "RETURN count(cds) as count_cds")
            for c in count:
                conta = c['count_cds']

    # print(type(C))
            dictlist = list({} for i in range(conta))
            i = 0
            for cds in all_cdss:
                dictlist[i]['subject'] = cds["subject_core"]
                dictlist[i]['verb'] = cds["verb_core"]
                dictlist[i]['object'] = cds["object_core"]
                dictlist[i]['time'] = cds["time_core"]
                dictlist[i]['place'] = cds["place_core"]
                dictlist[i]['verbatim'] = cds["verbatim"]
                i=i+1
            print("ciao")

            for k in range(len(dictlist)):

                # Subject
                if dictlist[k]['subject'] is not None:
                    tokens = nltk.word_tokenize(dictlist[k]['subject'])
                    dictlist[k]['subject'] = clean_sentence(tokens)

                # Verb
                if dictlist[k]['verb'] is not None:
                    tokens = nltk.word_tokenize(dictlist[k]['verb'])
                    dictlist[k]['verb'] = clean_sentence(tokens)

                # Object
                if dictlist[k]['object'] is not None:
                    tokens = nltk.word_tokenize(dictlist[k]['object'])
                    dictlist[k]['object'] = clean_sentence(tokens)

                # Time
                if dictlist[k]['time'] is not None:
                    tokens = nltk.word_tokenize(dictlist[k]['time'])
                    dictlist[k]['time'] = clean_sentence(tokens)

                # Place
                if dictlist[k]['place'] is not None:
                    tokens = nltk.word_tokenize(dictlist[k]['place'])
                    dictlist[k]['place'] = clean_sentence(tokens)

        # for term in dictlist[k]['subject']:
        #
        #     doc = Path("doc.txt")
        #     text_file = open(doc, "w")
        #     text_file.write("%s" % term )

            word_ps = {}


    # for i in range (len(vectorizer.get_feature_names())):
    #
    #     if vectorizer.get_feature_names()[i] == 'libÃ©rer':
    #
    #         print(i)
    #
    # print(tfidf.toarray().sum(axis=0)[714]/tfidf.toarray().sum())

            for k in range(len(dictlist)):
                dictlist[k]['subject_ps'] = 0.
                dictlist[k]['verb_ps'] = 0.
                dictlist[k]['object_ps'] = 0.
                dictlist[k]['time_ps'] = 0.
                dictlist[k]['place_ps'] = 0.
                dictlist[k]['sentence_ps'] = 0.
                for i in range (len(vectorizer.get_feature_names())):
                    if dictlist[k]['subject'] is not None:
                        if vectorizer.get_feature_names()[i] in dictlist[k]['subject']:
                            dictlist[k]['subject_ps'] += tfidf.toarray().sum(axis=0)[i]
                    if dictlist[k]['verb'] is not None:
                        if vectorizer.get_feature_names()[i] in dictlist[k]['verb']:
                            dictlist[k]['verb_ps'] += tfidf.toarray().sum(axis=0)[i]
                    if dictlist[k]['object'] is not None:
                        if vectorizer.get_feature_names()[i] in dictlist[k]['object']:
                            dictlist[k]['object_ps'] += tfidf.toarray().sum(axis=0)[i]
                    if dictlist[k]['time'] is not None:
                        if vectorizer.get_feature_names()[i] in dictlist[k]['time']:
                            dictlist[k]['time_ps'] += tfidf.toarray().sum(axis=0)[i]
                    if dictlist[k]['place'] is not None:
                        if vectorizer.get_feature_names()[i] in dictlist[k]['place']:
                            dictlist[k]['place_ps'] += tfidf.toarray().sum(axis=0)[i]


            print("ciao2")
            for k in range(len(dictlist)):
                dictlist[k]['sentence_ps'] = 0
                if dictlist[k]['subject'] is not None:
                    dictlist[k]['subject_ps'] = dictlist[k]['subject_ps']/(tfidf_sum*len(dictlist[k]['subject']))
                if dictlist[k]['verb'] is not None:
                    dictlist[k]['verb_ps'] = dictlist[k]['verb_ps'] / (tfidf_sum*len(dictlist[k]['verb']))
                if dictlist[k]['object'] is not None:
                    dictlist[k]['object_ps'] = dictlist[k]['object_ps'] / (tfidf_sum*len(dictlist[k]['object']))
                if dictlist[k]['time'] is not None:
                    dictlist[k]['time_ps'] = dictlist[k]['time_ps'] / (tfidf_sum*len(dictlist[k]['time']))
                if dictlist[k]['place'] is not None:
                    dictlist[k]['place_ps'] = dictlist[k]['place_ps'] / (tfidf_sum*len(dictlist[k]['place']))
                dictlist[k]['sentence_ps'] = (dictlist[k]['subject_ps'] + dictlist[k]['verb_ps'] + dictlist[k]['object_ps'] + dictlist[k]['time_ps'] + dictlist[k]['place_ps'])/5.
            print("ciao3")


            n_sentences = 7
            max_score = 0.
            j = 0
            summary = []
            while j < n_sentences:
                for k in range(len(dictlist)):
                    if dictlist[k]['sentence_ps'] > max_score:
                        max_score = dictlist[k]['sentence_ps']
                        pos_max = k
                summary.append(dictlist[pos_max]['verbatim'])
                dictlist[pos_max]['sentence_ps'] = -1

                j += 1
                max_score = 0.
            print(summary)

            text_file = open(summary_output_filepath, "w")
            for entry in summary:
                text_file.write("%s \n" % entry)


def main(argv):
    # default values
    host = "bolt://localhost:7687"
    login = "neo4j"
    password = "synapsedev"
    mr_ws_url = "http://api-synapse-dev.azurewebsites.net/machinereading/extractcds"
    apikey = "HT8R7PP6N8U8h8Bn9hrE5NX2R2cdxt32y58Lzqnc"
    lang = "fr"
    input_path = "../../resources/corpora/sample_texts/machine_reading/summarization/Corpus_RPM2/Corpus_RPM2_documents"

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", "-loc", help="Neo4j host. Default to " + host, default=host)
    parser.add_argument("--login", "-log", help="Login Neo4j. Default to " + login, default=login)
    parser.add_argument("--password", "-psw", help="Password Neo4j. Default to " + password, default=password)
    parser.add_argument("--url", "-u", help="Machine Reading endpoint URL. Default to " + mr_ws_url, default=mr_ws_url)
    parser.add_argument("--key", "-k", help="API key allowing to consume Machine Reading WS.", default=apikey)
    parser.add_argument("--lang", "-l",help="Language of the texts to be analysed. Possible values: fr for French, en for English. Default to " + lang,default=lang)
    parser.add_argument("--path", "-f", help="Path to the file containing text to be analysed, or folder containing several files. Default to " + input_path,default=input_path)
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

    if args.lang == None or (args.lang != "fr" and args.lang != "en"):
        print("Supported languages are French and English.")
        sys.exit()

    if args.path == None or Path(args.path).exists() == False:
        print("Specified input file/folder does not exist.")
        sys.exit()

    # load content from input file(s)
    # for thematic in range(1, 21):
    #     for cluster in range(1, 3):
    #         file_start = "../../resources/corpora/sample_texts/machine_reading/summarization/Corpus_RPM2/Corpus_RPM2_documents\T" + str(thematic).zfill(2) + "_C" + str(cluster)
    #         print(file_start)
    #
    #         summary_output_filepath = "../Rouge/test-summarization/system\T" + str(thematic).zfill(2) + "C" + str(cluster) + "_sumbasic.txt"
    #
    #         # load content from input file(s)
    #         filenames = get_filenames_recursively(args.inputpath)
    #         files_content = {}
    #         for filename in filenames:
    #             if filename.startswith(file_start) and filename.endswith('.txt'):
    #                 with open(filename, "r") as current_file:
    #                     files_content[filename] = current_file.read()

    perform_sumbasic_tfidf(args.host, args.login, args.password, args.url, args.key,args.lang)


if __name__ == "__main__":
    main(sys.argv[1:])