from neo4j.v1 import GraphDatabase, basic_auth
import nltk
import argparse
import sys
from pathlib import Path
from utils.browse_files import get_filenames_recursively
from machine_reading.mrtoneo4j.mrtoneo4j import apply_machine_reading
import fnmatch
import os

stopwords = nltk.corpus.stopwords.words('french')
stopwords.append("'")
stopwords.append('"')
stopwords.append("les")
stopwords.append("a")
stopwords.append("cet")
stopwords.append("elles")
stopwords.append(",")
stopwords.append("-")


def clean_sentence(tokens, use_stopwords=True):
    tokens = [t.lower() for t in tokens]
    if use_stopwords:
        tokens = [t for t in tokens if t not in stopwords]
    return tokens


def update_counts(cds_desc_element, word_ps, token_count):
    if cds_desc_element is not None:
        tokens = nltk.wordpunct_tokenize(cds_desc_element)
        cds_desc_element = clean_sentence(tokens)
        token_count += len(cds_desc_element)
        for token in cds_desc_element:
            if token not in word_ps:
                word_ps[token] = 1
            else:
                word_ps[token] += 1
    return cds_desc_element, word_ps, token_count


def perform_sumbasic(localhost, login, password,  files_content, mr_ws_url, mr_apikey, lang, summary_output_filepath, n_sentences=7):

    driver = GraphDatabase.driver(localhost, auth=basic_auth(login, password))
    session = driver.session()

    apply_machine_reading(session, files_content, mr_ws_url, mr_apikey, lang, clear_graph=True)

    all_cdss = session.run("MATCH (cds:CDS) "
                       "OPTIONAL MATCH (cds)-[:subject]->(subj) "
                       "OPTIONAL MATCH (cds)-[:verb]->(verb) "
                       "OPTIONAL MATCH (cds)-[:object]->(obj) "
                       "OPTIONAL MATCH (cds)-[:time]->(time) "
                       "OPTIONAL MATCH (cds)-[:place]->(place) "
                       "RETURN ID(cds) AS cds_id, subj.core AS subject_core, verb.core AS verb_core, obj.core AS object_core, cds.verbatim as verbatim, time.core AS time_core, place.core as place_core")

    count = session.run("MATCH (cds:CDS) "
                    "RETURN count(cds) as count_cds")
    for c in count:
        conta = c['count_cds']

    all_cdss_desc = []
    for cds in all_cdss:
        cds_desc = {}
        cds_desc['id'] = cds["cds_id"]
        cds_desc['subject'] = cds["subject_core"]
        cds_desc['verb'] = cds["verb_core"]
        cds_desc['object'] = cds["object_core"]
        cds_desc['time'] = cds["time_core"]
        cds_desc['place'] = cds["place_core"]
        cds_desc['verbatim'] = cds["verbatim"]
        all_cdss_desc.append(cds_desc)

    word_ps = {}
    token_count = 0

    for cds_desc in all_cdss_desc:
        cds_desc['subject'], word_ps, token_count = update_counts(cds_desc['subject'], word_ps, token_count)
        cds_desc['verb'],    word_ps, token_count = update_counts(cds_desc['verb'],    word_ps, token_count)
        cds_desc['object'],  word_ps, token_count = update_counts(cds_desc['object'],  word_ps, token_count)
        cds_desc['time'],    word_ps, token_count = update_counts(cds_desc['time'],    word_ps, token_count)
        cds_desc['place'],   word_ps, token_count = update_counts(cds_desc['place'],   word_ps, token_count)

    for word_p in word_ps:
            word_ps[word_p] = word_ps[word_p] / float(token_count)

    pos_max = 0
    j = 0
    text_summary = []
    cdss_summary = []

    while j < n_sentences:

        for cds_desc in all_cdss_desc:

            cds_desc['subject_ps'] = 0.
            cds_desc['verb_ps'] = 0.
            cds_desc['object_ps'] = 0.
            cds_desc['time_ps'] = 0.
            cds_desc['place_ps'] = 0.
            cds_desc['sentence_ps'] = 0.

        for word_p in word_ps:
            for cds_desc in all_cdss_desc:
                if cds_desc['subject'] is not None:
                    if word_p in cds_desc['subject']:
                        cds_desc['subject_ps'] += word_ps[word_p]
                if cds_desc['verb'] is not None:
                    if word_p in cds_desc['verb']:
                        cds_desc['verb_ps'] += word_ps[word_p]
                if cds_desc['object'] is not None:
                    if word_p in cds_desc['object']:
                        cds_desc['object_ps'] += word_ps[word_p]
                if cds_desc['time'] is not None:
                    if word_p in cds_desc['time']:
                        cds_desc['time_ps'] += word_ps[word_p]
                if cds_desc['place'] is not None:
                    if word_p in cds_desc['place']:
                        cds_desc['place_ps'] += word_ps[word_p]

        max_score = 0.

        for cds_desc in all_cdss_desc:
            if cds_desc['subject'] is not None:
                if len(cds_desc['subject']) != 0:
                    cds_desc['subject_ps'] = cds_desc['subject_ps']/len(cds_desc['subject'])
            if cds_desc['verb'] is not None:
                if len(cds_desc['verb']) != 0:
                    cds_desc['verb_ps'] = cds_desc['verb_ps'] / len(cds_desc['verb'])
            if cds_desc['object'] is not None:
                if len(cds_desc['object']) != 0:
                    cds_desc['object_ps'] = cds_desc['object_ps'] / len(cds_desc['object'])
            if cds_desc['time'] is not None:
                if len(cds_desc['time']) != 0:
                    cds_desc['time_ps'] = cds_desc['time_ps'] / len(cds_desc['time'])
            if cds_desc['place'] is not None:
                if len(cds_desc['place']) != 0:
                    cds_desc['place_ps'] = cds_desc['place_ps'] / len(cds_desc['place'])
            cds_desc['sentence_ps'] = (cds_desc['subject_ps']+cds_desc['verb_ps']+cds_desc['object_ps']+cds_desc['time_ps']+cds_desc['place_ps'])/5.
            if cds_desc['sentence_ps'] > max_score:
                max_score = cds_desc['sentence_ps']
                cds_score_max = cds_desc

        # update weight of tokens used in selected CDS (to prevent redundancy)
        for word_p in word_ps:
            if cds_score_max['subject'] is not None:
                if word_p in cds_score_max['subject']:
                    word_ps[word_p] = word_ps[word_p] ** 2
            if cds_score_max['verb'] is not None:
                if word_p in cds_score_max['verb']:
                    word_ps[word_p] = word_ps[word_p] ** 2
            if cds_score_max['object'] is not None:
                if word_p in cds_score_max['object']:
                    word_ps[word_p] = word_ps[word_p] ** 2
            if cds_score_max['time'] is not None:
                if word_p in cds_score_max['time']:
                    word_ps[word_p] = word_ps[word_p] ** 2
            if cds_score_max['place'] is not None:
                if word_p in cds_score_max['place']:
                    word_ps[word_p] = word_ps[word_p] ** 2

        # TODO: clarify C usage
        C = True

        for sentence in text_summary:
            if cds_score_max['verbatim'] == sentence:
                n_sentences += 1
                C = False

        if C:
            cdss_summary.append(cds_score_max)
            text_summary.append(cds_score_max['verbatim'])
            print(cds_score_max)
            j += 1

        all_cdss_desc.remove(cds_score_max)

    print(text_summary)

    # write summary result in graph DB

    create_node = " CREATE (r:TEXT {name:'node_automatic'}) RETURN ID(r) as id"
    session.run(create_node)

    for cdss_desc in cdss_summary:
        # TODO: use only one query (without foor loop) with an array containing all ids
        feed_dict = {}
        feed_dict["cds_id"] = cdss_desc["id"]
        create_text = " MATCH(cds: CDS) WHERE ID(cds) = {cds_id} " \
                      " MATCH (r:TEXT {name:'node_automatic'}) " \
                      " CREATE (r)-[:cds]->(cds) "

        session.run(create_text, feed_dict)

    # No comment, occur error on cds_score_max!
    text_file = open(summary_output_filepath, "w")
    for entry in text_summary:
        text_file.write("%s" % entry)
        text_file.write("%s" % '\n')

    return cdss_summary, text_summary

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

            summary_output_filepath = "../Rouge/test-summarization/system\T" + str(thematic).zfill(2) + "C" + str(cluster) + "_sumbasic.txt"

            # load content from input file(s)
            filenames = get_filenames_recursively(args.inputpath)
            files_content = {}
            for filename in filenames:
                if filename.startswith(file_start) and filename.endswith('.txt'):
                    with open(filename, "r") as current_file:
                        files_content[filename] = current_file.read()

            perform_sumbasic(args.host, args.login, args.password, files_content, args.url, args.key, args.lang, summary_output_filepath)


if __name__ == "__main__":
    main(sys.argv[1:])

# Add return summary for alignment graph evaluation