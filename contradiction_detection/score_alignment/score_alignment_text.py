# ! /usr/bin/env python
# coding=utf-8
""" process score alignment between two texts : test wmdistance(document1, document2) """

import re
from machine_reading.mrtoneo4j.mrtoneo4j import *
import argparse
from pathlib import Path
from gensim.models.keyedvectors import KeyedVectors
import nltk

def process_alignment_between_cdss(cds1, cds2, model):

    # Some sentences to test.
    sentence_1 = cds1.lower().split()
    sentence_2 = cds2.lower().split()

    # Remove their stopwords.
    stopwords = nltk.corpus.stopwords.words('french')
    sentence_1 = [w for w in sentence_1 if w not in stopwords]
    sentence_2 = [w for w in sentence_2 if w not in stopwords]

    # Compute WMD.
    distance = model.wmdistance(sentence_1, sentence_2)
    print(distance)
    return distance


def process_alignment_between_texts(session, lang, text_name_1, text_name_2, model):

    # clean Alignment, SUM_CDSS, SUM_TEXTS
    delete_query_1 = "MATCH(n: Alignment),(som_cds:SUM_CDSS),(som_text:SUM_TEXTS),(text: TEXT {name: '{name1}'}) DETACH DELETE n,som_cds,som_text"
    delete_query_2 = "MATCH(n: Alignment),(som_cds:SUM_CDSS),(som_text:SUM_TEXTS),(text: TEXT {name: '{name2}'}) DETACH DELETE n,som_cds,som_text"
    feed_dict = {}
    feed_dict["name1"] = text_name_1
    feed_dict["name2"] = text_name_2
    session.run(delete_query_1, feed_dict)
    session.run(delete_query_2, feed_dict)

    # for all cds from text_name_1 and text_name_2 return list(elem1,id1,elem2,id2)
    query_list = "MATCH (text1:TEXT {name:{name1}})-[:cds]->(cds1:CDS)-[:subject|:verb|:object]->(elem1) MATCH (text2:TEXT {name:{name2}})-[:cds]->(cds2:CDS)-[" \
                 ":subject|:verb|:object]->(elem2) RETURN ID(elem1), elem1.normalized as e1, ID(elem2), elem2.normalized as e2, cds1.verbatim as v1, cds2.verbatim as v2, " \
                 "elem1.normalized as normalized1, elem2.normalized as normalized2"
    resultat = session.run(query_list, feed_dict)

    # add alignments between cds elements
    for record in resultat:
        elem1 = record["e1"]
        elem2 = record["e2"]
        id1 = record["ID(elem1)"]
        id2 = record["ID(elem2)"]
        verbatim_cds1 = record["v1"]
        verbatim_cds2 = record["v2"]
        elem1 = re.sub('^le ', '', elem1)
        elem2 = re.sub('^le ', '', elem2)

        try:
            model[elem2]
            model[elem1]
            alignment_score = model.similarity(elem2, elem1)
            #alignment_score = getTermAlignment(elem2, elem1)
        except KeyError:
            print("not in vocabulary")
            alignment_score = 0
        print("%s %s %s %s -> %f" % (elem1, id1, elem2, id2, alignment_score))

        # create node alignment
        if alignment_score != 0:
            query_alignment = "MATCH (n) WHERE ID(n) = " + str(id1) + "  MATCH(m) WHERE ID(m) = " + str(
                id2) + " CREATE (n)<-[:alignment]-(A:Alignment {alignement :" + str(
                alignment_score) + "})-[:alignment]->(m)"
            session.run(query_alignment)

    #sentence can don't have cds
    try:
        verbatim_cds1
        verbatim_cds2
        print("verbatim_cds")
        dist_cdss = process_alignment_between_cdss(verbatim_cds1, verbatim_cds2, model)
    except:
        print("verbatim_cds not defined")
        # print(verbatim_cds2)
        dist_cdss = -1

    feed_dict["dist_cdss"] = dist_cdss
    # add alignments between cdss
    query_alignment_cdss = "MATCH (cds1:CDS)-[:object|subject|verb]->(n)<-[:alignment]-(a:Alignment)-[:alignment]->(m)<-[:object|subject|verb]-(cds2:CDS) \
    MERGE(cds1)-[:SUM_CDSS]->(som_cds:SUM_CDSS {total:{dist_cdss}})<-[:SUM_CDSS]-(cds2) "

    session.run(query_alignment_cdss,feed_dict)


def get_best_alignment_score(session, lang, text_name_1, text_name_2,model):
    process_alignment_between_texts(session, lang, text_name_1, text_name_2,model)

    # add alignments between texts
    query = "MATCH(text1:TEXT {name: 'sentence1'})-[: cds]->(cds1: CDS)-[:SUM_CDSS]->(s:SUM_CDSS) <-[:SUM_CDSS]-(cds2: CDS) < -[: cds]-(text2: TEXT {name: 'sentence2'})" \
        "RETURN MAX(s.total) AS max"
    feed_dict = {}
    feed_dict["name1"] = text_name_1
    feed_dict["name2"] = text_name_2
    resultat = session.run(query, feed_dict)

    for record in resultat:
        return record["max"] if record["max"] != None else 0


def main(argv):
    # default values
    host = "bolt://localhost:7687"
    login = "neo4j"
    password = "synapsedev"
    mr_ws_url = "http://api-synapse-dev.azurewebsites.net/machinereading/extractcds"
    apikey = "HT8R7PP6N8U8h8Bn9hrE5NX2R2cdxt32y58Lzqnc"
    lang = "fr"
    text_1_path = "../../resources/corpora/sample_texts/machine_reading/mrtoneo4j/file_1.txt"
    text_2_path = "../../resources/corpora/sample_texts/machine_reading/mrtoneo4j/file_2.txt"

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", "-loc", help = "Neo4j host. Default to " + host, default = host)
    parser.add_argument("--login", "-log", help = "Login Neo4j. Default to " + login, default = login)
    parser.add_argument("--password", "-psw", help = "Password Neo4j. Default to " + password, default = password)
    parser.add_argument("--url", "-u", help = "Machine Reading endpoint URL. Default to " + mr_ws_url, default = mr_ws_url)
    parser.add_argument("--key", "-k", help = "API key allowing to consume Machine Reading WS.", default = apikey)
    parser.add_argument("--lang", "-l", help = "Language of the texts to be analysed. Possible values: fr for French, en for English. Default to " + lang , default = lang)
    parser.add_argument("--path1", "-p1", help = "Path to the first file containing text to be analysed. Default to " + text_1_path, default = text_1_path)
    parser.add_argument("--path2", "-p2", help = "Path to the second file containing text to be analysed. Default to " + text_2_path, default = text_2_path)
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

    if args.path2 == None or Path(args.path2).exists() == False:
        print("Specified input file 2 does not exist.")
        sys.exit()

    # load content from input files
    files_content = {}
    for f in [args.path1, args.path2]:
        with open(f, "r") as current_file:
            files_content[f] = current_file.read()

    # start connection to Neo4j DB
    driver = GraphDatabase.driver(host, auth=basic_auth(login, password))
    session = driver.session()

    apply_machine_reading(args.host, args.login, args.password, files_content, args.url, args.key, args.lang)
    model = KeyedVectors.load_word2vec_format("twitter_w2v.gensim")
    process_alignment_between_texts(session, args.lang, args.path1, args.path2,model)

    session.close()

if __name__ == "__main__":
	main(sys.argv[1:])