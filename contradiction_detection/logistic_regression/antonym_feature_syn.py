# ! /usr/bin/env python
# coding=utf-8
""" Contradictions : Feature Antonym """

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

# lemmatisation
def sentence_lemmatized(session, pattern):
    query_sentence = " OPTIONAL MATCH (t1:TEXT  {name:'sentence1'})-[:cds]->(cds1:CDS)-[:verb]->(v:Verb) " \
                     " OPTIONAL MATCH (t1:TEXT {name:'sentence1'})-[:cds]->(cds1:CDS)-[:subject]->(s:Subject) " \
                     " OPTIONAL MATCH (t1:TEXT {name:'sentence1'})-[:cds]->(cds1:CDS)-[:object]->(o:Object)" \
                     " OPTIONAL MATCH (t2:TEXT  {name:'sentence2'})-[:cds]->(cds2:CDS)-[:verb]->(v2:Verb)" \
                     " OPTIONAL MATCH (t2:TEXT {name:'sentence2'})-[:cds]->(cds2:CDS)-[:subject]->(s2:Subject)" \
                     " OPTIONAL MATCH(t2: TEXT {name: 'sentence2'})-[: cds]->(cds2: CDS)-[: object]->(o2: Object)" \
                     " RETURN v.normalized as v1, s.normalized as s1, o.normalized as o1, v2.normalized as v2, s2.normalized as s2, o2.normalized as o2"
    result = session.run(query_sentence)

    list_verb1 = []
    list_subject1 = []
    list_object1 = []
    list_verb2 = []
    list_subject2 = []
    list_object2 = []

    for record in result:
        # sentence 1
        s1 = re.sub('^le ', '',record["s1"])
        o1 = re.sub('^le ', '', record["o1"])

        list_verb1.append(record["v1"])
        list_subject1.append(s1)
        list_object1.append(o1)

        # sentence 2
        s2 = re.sub('^le ', '', record["s2"])
        o2 = re.sub('^le ', '', record["o2"])

        list_verb2.append(record["v2"])
        list_subject2.append(s2)
        list_object2.append(o2)

    sentence1_lemmatized = {'verb': list(set(list_verb1)), 'subject': list(set(list_subject1)), 'object': list(set(list_object1)) }
    sentence2_lemmatized = {'verb': list(set(list_verb2)), 'subject': list(set(list_subject2)), 'object': list(set(list_object2)) }
    print(sentence1_lemmatized)
    print(sentence2_lemmatized)

    # select terms to compare
    term1 = sentence1_lemmatized[pattern][0]
    term2 = sentence2_lemmatized[pattern][0]

    return term1, term2

def compare_sentences(session):
    patterns = ["verb", "subject", "object"]
    for pattern in patterns:
        term1, term2 = sentence_lemmatized(session, pattern)
        print(term1)
        print(term2)

        if term1 == term2:
            print("The terms are equals")
        else:
            synonym_list = []
            antonym_list = []
            tree = etree.parse("../../resources/lexical_resources/synonymes_synapse.xml")
            for entry_node in tree.xpath("//entry"):

                orth_node = entry_node.find("orth")

                # Search antonyms if node == sentence 1
                if orth_node.text == term1:
                    print("Sentence 1 : " + orth_node.text)

                    # Test antonym direct
                    antonym_direct_nodes = entry_node.findall("gramGrp/gram/sense/anto")

                    for antonym_direct_node in antonym_direct_nodes:
                        # direct antonym
                        if antonym_direct_node.text == term2:
                            print("There is a direct antonym ! >> %s" % term2)
                            print("Feature antonym detected")

                        else:
                            # Test antonym inbdirect
                            print("There is a no direct antonym ! We searching for indirect antonym")
                            # antonyms of synonyms

                            # Search synonym of sentence 1
                            synonym_nodes = entry_node.findall("gramGrp/gram/sense/syno")
                            print("Synonyms of " + term1 + " :")
                            for synonym_node in synonym_nodes:
                                synonym_list.append(synonym_node.text)

                            print(synonym_list)
                            break

            for entry_node_anto in tree.xpath("//entry"):
                # antonym of synonyms
                orth_node_anto = entry_node_anto.find("orth")
                for syno in synonym_list:

                    for orth in orth_node_anto.text.split("\n"):
                        if syno == orth:
                            # print(orth)
                            # Test antonym direct
                            antonym_direct_nodes2 = entry_node_anto.findall("gramGrp/gram/sense/anto")

                            for antonym_direct_node2 in antonym_direct_nodes2:
                                # direct antonym
                                print("antonym of " + orth + " is: " + antonym_direct_node2.text)
                                antonym_list.append(antonym_direct_node2.text)
            print(antonym_list)
            antonym_feature = False
            for ant in antonym_list:
                if ant == term2:
                    # if antonym_direct_node2.text == sentence2:
                    antonym_feature = True

            if antonym_feature is True:
                print("There is an indirect antonym ! >> %s" % term2)
                print("Feature antonym detected")
            else:
                print("There is no indirect antonym !!!!!!! >> %s" % term2)
                print("Feature antonym not detected")


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

    model_wikipedia = KeyedVectors.load_word2vec_format("../../resources/lexical_resources/wikifrdict_deserializing.gensim")

    score = read_translated_files(True, model_wikipedia, "wikipedia", "n_similarity", session, args.lang, args.url, args.key)
    print(score)

    if score > 3:
        print("Score is high >> there are chances to have contradiction ")
        print("Step 4 ", score)
        compare_sentences(session)
    else:
        print("Score is low >> no contradiction")

    session.close()

if __name__ == "__main__":
	main(sys.argv[1:])