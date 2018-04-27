#! /usr/bin/env python
# coding=utf-8
""" Evaluation of summarization with graph alignment """

# Score Baseline = 0.73
# Score SomBasic = 0.7691105996009

from neo4j.v1 import GraphDatabase, basic_auth
import argparse
from pathlib import Path
from gensim.models.keyedvectors import KeyedVectors
from utils.browse_files import get_filenames_recursively
from machine_reading.mrtoneo4j.mrtoneo4j import apply_machine_reading
from machine_reading.baseline.baseline import perform_baseline
from machine_reading.SumBasic.sumbasic import perform_sumbasic
from contradiction_detection.score_alignment.calcul_similarity import similarity
from contradiction_detection.score_alignment.score_alignment_mr import *

# manual summarization
def manual_summarization_txt_to_cds(session, text_summarized, mr_url,key,lang):
     apply_machine_reading(session, text_summarized, mr_url, key, lang)

     # récupérer le name text
     name_text = "MATCH (n:TEXT) SET n.name = 'node_manual' RETURN n.name as name, n.verbatim as verbatim"
     resultat1 = session.run(name_text)

     for record in resultat1:
          name = record["name"]
          verbatim = record["verbatim"]

     return name


# automatic summarization
def automatic_summarization_cds_baseline(host, login, password, files_content, url, key, lang,summary_output_filepath, session):
    perform_baseline(host, login, password, files_content, url, key, lang,summary_output_filepath)

    # return CDS duplicate = Le résumé automatique !
    cdss_duplicate = "MATCH (cds1:CDS)-[r:duplicate]->() "\
                    " WITH(cds1) MATCH(cds1)-[:subject|object|verb|place|time]->(s)"\
                    " RETURN cds1, s, ID(cds1) as id,cds1.verbatim as verbatim"

    resultat2 = session.run(cdss_duplicate)
    id_list = []
    verbatims = []
    for record in resultat2:
        id_cds = record["id"]
        verbatim = record["verbatim"]
        verbatims.append(verbatim)
        id_list.append(id_cds)

    create_node = " CREATE (r:TEXT {name:'node_automatic'}) RETURN ID(r) as id"
    resultat = session.run(create_node)
    for record in resultat:
        id_text = record["id"]

        for id in id_list:
             create_text = " MATCH(cds: CDS) WHERE ID(cds) = "+str(id)+ \
                           " MATCH (r:TEXT {name:'node_automatic'}) WHERE ID(r) = "+str(id_text) + \
                           " WITH cds,r MERGE(cds)<-[:cds]-(r) " \
                           " RETURN cds,r, r.name as name, cds.verbatim as verbatim"
             session.run(create_text)
        resultat3 = session.run(create_text)
        for record in resultat3:
            name = record["name"]

        return name

# automatic summarization
def automatic_summarization_cds_sumbasic(host, login, password, files_content, url, key, lang,summary_output_filepath, session):

    verbatims = perform_sumbasic(host, login, password, files_content, url, key, lang, summary_output_filepath)
    print("VERBATIMS ",verbatims)
    # return Le résumé automatique !
    create_node = " CREATE (r:TEXT {name:'node_automatic'}) RETURN ID(r) as id"
    resultat = session.run(create_node)
    for record in resultat:
       id_text = record["id"]

       for i in verbatims:
           feed_dict = {}
           feed_dict["verbatim"] = i
           create_text = " MATCH(cds: CDS)-[:subject|object|verb|place|time]->(element) WHERE cds.verbatim = {verbatim} " \
                          " MATCH (r:TEXT {name:'node_automatic'}) WHERE ID(r) = " + str(id_text) + \
                          " WITH cds,r MERGE(cds)<-[:cds]-(r) " \
                          " RETURN cds,r, r.name as name, cds.verbatim as verbatim"

           resultat3 = session.run(create_text, feed_dict)
       for record in resultat3:
            name = record["name"]

    print(name)

    return name



def main(argv):
    # default values
    host = "bolt://localhost:7687"
    login = "neo4j"
    password = "synapsedev"
    mr_ws_url = "http://api-synapse-dev.azurewebsites.net/machinereading/extractcds"
    apikey = "HT8R7PP6N8U8h8Bn9hrE5NX2R2cdxt32y58Lzqnc"
    lang = "fr"
    path_automatic = "D:/dit/resources/file/automatic_to_summarized"  # Corpus_RPM2/Corpus_RPM2_documents"
    path_manual = "D:/dit/resources/file/manual_summarized"  # Corpus_RPM2/Corpus_RPM2_documents"

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", "-loc", help="Neo4j host. Default to " + host, default=host)
    parser.add_argument("--login", "-log", help="Login Neo4j. Default to " + login, default=login)
    parser.add_argument("--password", "-psw", help="Password Neo4j. Default to " + password, default=password)
    parser.add_argument("--url", "-u", help="Machine Reading endpoint URL. Default to " + mr_ws_url, default=mr_ws_url)
    parser.add_argument("--key", "-k", help="API key allowing to consume Machine Reading WS.", default=apikey)
    parser.add_argument("--lang", "-l", help="Language of the texts to be analysed. Possible values: fr for French, en for English. Default to " + lang, default=lang)
    parser.add_argument("--path1", "-f1", help="Path to the file containing text to be analysed, or folder containing several files. Default to " + path_automatic, default=path_automatic)
    parser.add_argument("--path2", "-f2",help="Path to the file containing text to be analysed, or folder containing several files. Default to " + path_manual, default=path_manual)
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

    if args.path1 == None or Path(args.path1).exists() == False:
        print("Specified input file/folder does not exist.")
        sys.exit()

    if args.path2 == None or Path(args.path2).exists() == False:
        print("Specified input file/folder does not exist.")
        sys.exit()

    summary_output_filepath = "aa.txt"

    # load content from input file(s)

    filenames1 = get_filenames_recursively(args.path1)
    text_contents = {}
    for filename in filenames1:
        with open(filename, "r") as current_file:
            text_contents[filename] = current_file.read()

    filenames2 = get_filenames_recursively(args.path2)
    text_contents2 = {}
    for filename in filenames2:
        with open(filename, "r") as current_file:
            text_contents2[filename] = current_file.read()

    # start connection to Neo4j DB
    driver = GraphDatabase.driver(args.host, auth=basic_auth(args.login, args.password))
    session = driver.session()



    #name_sentence1 = manual_summarization_txt_to_cds(session, text_contents2, args.url, args.key, args.lang)

    #name_sentence2 = automatic_summarization_cds_baseline(args.host, args.login, args.password, text_contents, args.url, args.key, args.lang, summary_output_filepath, session)

    #name_sentence2 = automatic_summarization_cds_sumbasic(host, login, password, text_contents, args.url, args.key, lang, summary_output_filepath, session)


    # # delete_not_summarized = " MATCH(n: TEXT) WHERE " \
    # # " n.name <> 'node_automatic' and n.name <> 'node_manual' " \
    # # " DELETE n"
    # # session.run(delete_not_summarized)

    model_wikipedia = KeyedVectors.load_word2vec_format("D:/dit/resources/lexical_resources/wikifrdict_deserializing.gensim")
    # # # # model_twitter = KeyedVectors.load_word2vec_format("D:/dit/resources/lexical_resources/twitter_w2v.gensim")
    # #
    files_content_global = {"sentence1": "node_manual", "sentence2": "node_automatic"}
    # #
    # # # # evaluation (manual_summarization, automatic_summarization)
    # # # # score_n_similarity = similarity(False, model_wikipedia, "n_similarity", files_content_global, session, args.lang, args.url, args.key)
    # # # #         #score_wmdistance = similarity(False, model_wikipedia, "wmdistance", files_content_global, session, args.lang, args.url,args.key)
    # #
    # #
    score_n_similarity_MR = process_alignment_between_texts(session, lang, files_content_global, "n_similarity", model_wikipedia)
    # #
    print("Le score MR :",score_n_similarity_MR)



    # print(score_n_similarity)
    # # print(score_n_similarity)
    # # print(score_wmdistance)
    # # print(score_n_similarity_MR)



    session.close()

if __name__ == "__main__":
	main(sys.argv[1:])