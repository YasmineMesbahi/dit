#! /usr/bin/env python
# coding=utf-8
""" produces a summary of a set of texts in the form of CDSs """

import os
import sys
import argparse
import pickle
import time
from neo4j.v1 import GraphDatabase, basic_auth
from datetime import datetime
from pathlib import Path
from utils.browse_files import get_filenames_recursively
from machine_reading.mrtoneo4j.mrtoneo4j import apply_machine_reading
from machine_reading.Kmeans.word2vec import process_and_save_word_vectors, get_word_vectors
from machine_reading.Kmeans.add_vect_cds import add_embedding_cds
from machine_reading.Kmeans.plot_clustering import plot_clustering
from machine_reading.Kmeans.add_kmeans_to_graph import add_kmeans_to_graph
from machine_reading.Kmeans.all_cds import all_cds


def perform_corpus_summarization(host, login, password, files_content, mr_ws_url, mr_apikey, lang, override_word_vectors, word_vectors_path, word_vect_normalized, summary_output_filepath):

    # start connection to Neo4j DB
    driver = GraphDatabase.driver(host, auth=basic_auth(login, password))
    session = driver.session()

    if override_word_vectors:
        apply_machine_reading(session, files_content, mr_ws_url, mr_apikey, lang, clear_graph=True)
        process_and_save_word_vectors(host, login, password, word_vectors_path, word_vect_normalized)

    word_vectors = get_word_vectors(word_vect_normalized)
    add_embedding_cds(host, login, password, word_vectors, word_vect_normalized)
    add_kmeans_to_graph(host, login, password, word_vect_normalized)
    #all_cds(host, login, password)
    #plot_clustering()

    with open("svo_centers.pickle", "rb") as fp:  # Unpickling list of all svo
        (subject_center, verb_center, object_center, time_center, place_center, verbatim_centers, cdss_summary) = pickle.load(fp)

    text_summary = verbatim_centers

    # write summary result in graph DB
    create_node = " CREATE (r:TEXT {name:'node_automatic'}) RETURN ID(r) as id"
    session.run(create_node)

    for id_cds in cdss_summary:
        # TODO: use only one query (without for loop) with an array containing all ids
        feed_dict = {}
        feed_dict["cds_id"] = id_cds
        create_text = " MATCH(cds: CDS) WHERE ID(cds) = {cds_id} " \
                      " MATCH (r:TEXT {name:'node_automatic'}) " \
                      " CREATE (r)-[:cds]->(cds) "

        session.run(create_text, feed_dict)

    text_file = open(summary_output_filepath, "w")

    for entry in verbatim_centers:
        text_file.write("%s" % entry)
        text_file.write("%s" % '\n')

    return cdss_summary, text_summary


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')



def main(argv):

    start_time = datetime.now()
    # default values
    host = "bolt://localhost:7687"
    login = "neo4j"
    password = "synapsedev"
    mr_ws_url = "http://api-synapse-dev.azurewebsites.net/machinereading/extractcds"
    apikey = "HT8R7PP6N8U8h8Bn9hrE5NX2R2cdxt32y58Lzqnc"
    lang = "fr"
    input_path = "../../resources/corpora/sample_texts/machine_reading/summarization/Corpus_RPM2/Corpus_RPM2_documents"
    override_word_vectors = False
    word_vect_normalized = False


    word_vectors_path = os.path.join("D:\\", "wiki.fr.vec")

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", "-loc", help = "Neo4j host. Default to " + host, default=host)
    parser.add_argument("--login", "-log", help = "Login Neo4j. Default to " + login, default=login)
    parser.add_argument("--password", "-psw", help = "Password Neo4j. Default to " + password, default=password)
    parser.add_argument("--url", "-u", help = "Machine Reading endpoint URL. Default to " + mr_ws_url, default=mr_ws_url)
    parser.add_argument("--key", "-k", help = "API key allowing to consume Machine Reading WS.", default=apikey)
    parser.add_argument("--lang", "-l", help = "Language of the texts to be analysed. Possible values: fr for French, en for English. Default to " + lang , default=lang)
    parser.add_argument("--inputpath", "-i", help = "Path to the file containing text to be analysed, or folder containing several files. Default to " + input_path, default=input_path)
    parser.add_argument("--wordvectorspath", "-w", help = "Path to the file containing fastText word vectors. Default to " + word_vectors_path, default=word_vectors_path)
    parser.add_argument("--overridewv", "-owv", type=str2bool, nargs='?', const=True, default=override_word_vectors, help="Whether the word vectors should be reprocessed or not. Default to " + str(override_word_vectors))
    parser.add_argument("--wvnormalized", "-wvn", type=str2bool, nargs='?', const=True, default=word_vect_normalized, help="Whether the word vectors should be normalized or not. Default to " + str(word_vect_normalized))
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

    if args.inputpath == None or Path(args.inputpath).exists() == False:
        print("Specified input file/folder does not exist.")
        sys.exit()

    for thematic in range(1, 21):
        for cluster in range(1, 3):
            file_start = "../../resources/corpora/sample_texts/machine_reading/summarization/Corpus_RPM2/Corpus_RPM2_documents\T"+ str(thematic).zfill(2) +"_C" + str(cluster) #
            print(file_start)

            summary_output_filepath = "../Rouge/test-summarization/system\T" + str(thematic).zfill(2) + "C" + str(cluster) + "_kmeans.txt" #

            # load content from input file(s)
            filenames = get_filenames_recursively(args.inputpath)
            files_content = {}
            for filename in filenames:
                if filename.startswith(file_start) and filename.endswith('.txt'):
                    with open(filename, "r") as current_file:
                        files_content[filename] = current_file.read()

            perform_corpus_summarization(args.host, args.login, args.password, files_content, args.url, args.key, args.lang, args.overridewv, args.wordvectorspath, args.wvnormalized, summary_output_filepath)

            try:
                os.remove("D:\dit\machine_reading\Kmeans\cdss_embeddings.npy")
            except OSError:
                pass


    # load content from input file(s)
    # filenames = get_filenames_recursively(args.inputpath)
    # files_content = {}
    # for filename in filenames:
    #
    #         if filename.startswith('../../resources/corpora/sample_texts/machine_reading/summarization/Corpus_RPM2/Corpus_RPM2_documents\T10_C2') and filename.endswith('.txt'):
    #             with open(filename, "r") as current_file:
    #                 files_content[filename] = current_file.read()
    #
    # perform_corpus_summarization(args.host, args.login, args.password, files_content, args.url, args.key, args.lang,args.overridewv, args.wordvectorspath, args.wvnormalized)

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))


if __name__ == "__main__":

	main(sys.argv[1:])
