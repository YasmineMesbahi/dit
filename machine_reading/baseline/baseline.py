from neo4j.v1 import GraphDatabase, basic_auth
import argparse
import sys
from pathlib import Path
from utils.browse_files import get_filenames_recursively
from machine_reading.mrtoneo4j.mrtoneo4j import apply_machine_reading


def perform_baseline(localhost, login, password,  files_content, mr_ws_url, mr_apikey, lang, summary_output_filepath):

    driver = GraphDatabase.driver(localhost, auth=basic_auth(login, password))
    session = driver.session()

    apply_machine_reading(session, files_content, mr_ws_url, mr_apikey, lang)

    all_cdss = session.run("MATCH (subj1) <-[:subject]-(cds1:CDS)-[:object]->(obj1) "
                           "MATCH (subj2) <-[:subject]-(cds2:CDS)-[:object]->(obj2) "
                           "MATCH (cds1:CDS)-[:verb]->(verb1) "
                           "MATCH (cds2:CDS)-[:verb]->(verb2) "
                           "MATCH (subj1) <--(cds1:CDS)<--(text) "
                           "MATCH (subj2) <--(cds2:CDS)<--(text) "
                           "where subj1.normalized=subj2.normalized " 
                           "and obj1.normalized=obj2.normalized and verb1.normalized=verb2.normalized "
                           "and cds1<>cds2 "
                           "create (cds1)-[r:duplicate]->(cds2) "
                           "return distinct cds2.verbatim as verbatim "
                           "LIMIT 7")

    # return one CDS from 2 CDSS duplicate
    query_summary = session.run(" MATCH (cds1:CDS)-[r:duplicate]->(cds2:CDS) " \
                                " WHERE ID(cds1) < ID(cds2) " \
                                " RETURN cds1, ID(cds1) as id, cds1.verbatim as verbatim ")


    text_summary = []
    cdss_summary = []
    for cds in query_summary:
        text_summary.append(cds["verbatim"])
        cdss_summary.append(cds)


    # write summary result in graph DB
    create_node = " CREATE (r:TEXT {name:'node_automatic'}) RETURN ID(r) as id"
    session.run(create_node)

    for cds in cdss_summary:
        # TODO: use only one query (without foor loop) with an array containing all ids
        feed_dict = {}
        feed_dict["cds_id"] = cds["id"]
        create_text = " MATCH(cds: CDS) WHERE ID(cds) = {cds_id} " \
                      " MATCH (r:TEXT {name:'node_automatic'}) " \
                      " CREATE (r)-[:cds]->(cds) "

        session.run(create_text, feed_dict)



    text_file = open(summary_output_filepath, "w")
    for entry in text_summary:
        text_file.write("%s" % entry)
        text_file.write("%s" % '\n')

    return text_summary, cdss_summary

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
    parser.add_argument("--host", "-loc", help = "Neo4j host. Default to " + host, default=host)
    parser.add_argument("--login", "-log", help = "Login Neo4j. Default to " + login, default=login)
    parser.add_argument("--password", "-psw", help = "Password Neo4j. Default to " + password, default=password)
    parser.add_argument("--url", "-u", help = "Machine Reading endpoint URL. Default to " + mr_ws_url, default=mr_ws_url)
    parser.add_argument("--key", "-k", help = "API key allowing to consume Machine Reading WS.", default=apikey)
    parser.add_argument("--lang", "-l", help = "Language of the texts to be analysed. Possible values: fr for French, en for English. Default to " + lang , default=lang)
    parser.add_argument("--inputpath", "-i", help = "Path to the file containing text to be analysed, or folder containing several files. Default to " + input_path, default=input_path)
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

    # load content from input file(s)
    for thematic in range(1, 21):
        for cluster in range(1, 3):
            file_start = "../../resources/corpora/sample_texts/machine_reading/summarization/Corpus_RPM2/Corpus_RPM2_documents\T" + str(thematic).zfill(2) + "_C" + str(cluster)
            print(file_start)

            summary_output_filepath = "../Rouge/test-summarization/system\T" + str(thematic).zfill(2) + "C" + str(cluster) + "_baseline.txt"

            # load content from input file(s)
            filenames = get_filenames_recursively(args.inputpath)
            files_content = {}
            for filename in filenames:
                if filename.startswith(file_start) and filename.endswith('.txt'):
                        with open(filename, "r") as current_file:
                            files_content[filename] = current_file.read()

            perform_baseline(args.host, args.login, args.password, files_content, args.url, args.key, args.lang, summary_output_filepath)



if __name__ == "__main__":
    main(sys.argv[1:])