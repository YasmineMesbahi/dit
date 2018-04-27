# ! /usr/bin/env python
# coding=utf-8
""" Main program : automatiser le calcul de scores pour tous les fichiers : 10.000 paires * 9 cas"""

from contradiction_detection.score_alignment.calcul_similarity import *


def read_translated_files(mr, model, name_model, sim, session, lang, mr_url, key ):
    for i in range(1, 10000, 1000):
        file_translated = "../../resources/corpora/multinli/translated/multinli_0.9_dev_matched_%d-%d_translated.jsonl" % (i, i + 999)
        with jsonlines.open(file_translated) as reader:
            print(file_translated)
            for obj in reader:
                sentence1 = obj["sentence1"]
                sentence2 = obj["sentence2"]

                files_content = {"sentence1": sentence1, "sentence2": sentence2}

                score = similarity(mr, model, sim, files_content, session, lang, mr_url, key)
                print(score)

                # store scores and classes
                if mr == True:
                    with open("../../resources/corpora/multinli/score/score_10000/MR/score_%d-%d_%s_%s.tsv" % (i, i + 999, sim, name_model), "a+") as f:
                        f.write(obj["gold_label"] + "\t" + str(score) + "\n")
                else:
                    with open("../../resources/corpora/multinli/score/score_10000/No_MR/score_%d-%d_%s_%s.tsv" % (i, i + 999, sim, name_model), "a+") as f:
                        f.write(obj["gold_label"] + "\t" + str(score) + "\n")



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
    parser.add_argument("--host", "-loc", help="Neo4j host. Default to " + host, default=host)
    parser.add_argument("--login", "-log", help="Login Neo4j. Default to " + login, default=login)
    parser.add_argument("--password", "-psw", help="Password Neo4j. Default to " + password, default=password)
    parser.add_argument("--url", "-u", help="Machine Reading endpoint URL. Default to " + mr_ws_url, default=mr_ws_url)
    parser.add_argument("--key", "-k", help="API key allowing to consume Machine Reading WS.", default=apikey)
    parser.add_argument("--lang", "-l",
                        help="Language of the texts to be analysed. Possible values: fr for French, en for English. Default to " + lang,
                        default=lang)
    parser.add_argument("--path", "-p1",
                        help="Path to the first file containing text to be analysed. Default to " + corpora_path,
                        default=corpora_path)
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
        print("Specified input file 1 does not exist.")
        sys.exit()

    # start connection to Neo4j DB
    driver = GraphDatabase.driver(host, auth=basic_auth(login, password))
    session = driver.session()

    model_wikipedia = KeyedVectors.load_word2vec_format("../../resources/lexical_resources/wikifrdict_deserializing.gensim")
    model_twitter = KeyedVectors.load_word2vec_format("../../resources/lexical_resources/twitter_w2v.gensim")

    similarity_function = { 'MRTrue' : ['n_similarity','wmdistance', 'synonym'], 'MRFalse' : ['n_similarity', 'wmdistance']}

    if similarity_function.get("MRTrue") is not None:
        for func_mr in similarity_function["MRTrue"]:
            read_translated_files(True, model_wikipedia, "wikipedia", func_mr , session, args.lang, args.url, args.key)
            read_translated_files(True, model_twitter, "twitter", func_mr, session, args.lang, args.url, args.key)

    if similarity_function.get("MRFalse") is not None:
        for func_no_mr in similarity_function["MRFalse"]:
            read_translated_files(False, model_wikipedia,"wikipedia",func_no_mr, session, args.lang, args.url, args.key)
            read_translated_files(False, model_twitter, "twitter",func_no_mr, session, args.lang, args.url, args.key)

    session.close()

if __name__ == "__main__":
	main(sys.argv[1:])
