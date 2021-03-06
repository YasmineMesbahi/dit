# ! /usr/bin/env python
# coding=utf-8
""" Contradictions : Feature Negation """

from contradiction_detection.score_alignment.calcul_similarity import *

def read_translated_files(mr, model, name_model, sim, session, lang, mr_url, key ):
    for i in range(1, 1000, 1000):
        file_translated = "../../resources/corpora/multinli/translated/multinli_0.9_dev_matched_%d-%d_translated.jsonl" % (i, i + 999)
        with jsonlines.open(file_translated) as reader:
            print(file_translated)
            for obj in reader:
                sentence1 = obj["sentence1"]
                sentence2 = obj["sentence2"]
                files_content = {"sentence1": sentence1, "sentence2": sentence2}
                score = similarity(mr, model, sim, files_content, session, lang, mr_url, key)
    return score


def count_negation_graph(session,sentence):

    query_graph = "MATCH (t:TEXT  {name:{sentence}})-[:cds]->(cds:CDS)-[:verb]->(n) " \
                     " RETURN cds.negation as n, ID(cds) as id, n.normalized as elem"
    feed_dict = {}
    feed_dict["sentence"] = sentence
    result = session.run(query_graph, feed_dict)

    nb_negation_graph = 0
    for record in result:
        if record["n"] is True:
            id_cds = record["id"]
            pattern = record["elem"]
            nb_negation_graph = nb_negation_graph + 1
            #print(nb_negation_graph)
            #print(record["n"])
            return nb_negation_graph,pattern
        else:
            return 0, record["elem"]


def recognize_pattern(session):
    nb_negation_graph1, pattern1 = count_negation_graph(session, "sentence1")
    print(nb_negation_graph1)
    print(pattern1)
    nb_negation_graph2, pattern2 = count_negation_graph(session, "sentence2")
    print(nb_negation_graph2)
    print(pattern2)

     # compare pattern1 and pattern2
    if nb_negation_graph1 == nb_negation_graph2 == 0:
        print("No negation detected")
    elif nb_negation_graph1 == nb_negation_graph2:
        print("The sentences are both negated >> No negation feature detected")
    else:
        print("There is chances that have negation feature")

        print("Checking recognize patterns negated. If they are same >> feature negation detected")

        if pattern1 == pattern2:
            print("Feature negation detected at the pattern", pattern1)

        else:
            print("Negation is not in the same pattern !>> No feature negation")






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

    model_wikipedia = KeyedVectors.load_word2vec_format(
        "../../resources/lexical_resources/wikifrdict_deserializing.gensim")

    score = read_translated_files(True, model_wikipedia, "wikipedia", "n_similarity", session, args.lang, args.url,
                                  args.key)
    print(score)

    if score > 0:
        print("Score is high >> there are chances to have contradiction ")
        print("Step 4 ", score)
        recognize_pattern(session)
    else:
        print("Score is low >> no contradiction")

    session.close()

if __name__ == "__main__":
	main(sys.argv[1:])