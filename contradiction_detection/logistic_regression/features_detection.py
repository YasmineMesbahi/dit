# ! /usr/bin/env python
# coding=utf-8
""" Contradictions : Features """

from contradiction_detection.score_alignment.calcul_similarity import *
from contradiction_detection.score_alignment.term_proximity_syn import *
import csv

# lemmatisation
def sentence_lemmatized(session, pattern,total_alignment):
    query_sentence = " OPTIONAL MATCH (t1:TEXT  {name:'sentence1'})-[:cds]->(cds1:CDS)-[:SUM_CDSS]-(sum_cds1:SUM_CDSS {total : {total}}) " \
                     " WITH sum_cds1, cds1 " \
                     " OPTIONAL MATCH (t1:TEXT  {name:'sentence1'})-[:cds]->(cds1:CDS)-[:verb]->(v:Verb) " \
                     " OPTIONAL MATCH (t1:TEXT {name:'sentence1'})-[:cds]->(cds1:CDS)-[:subject]->(s:Subject) " \
                     " OPTIONAL MATCH (t1:TEXT {name:'sentence1'})-[:cds]->(cds1:CDS)-[:object]->(o:Object)" \
                     " OPTIONAL MATCH (t1:TEXT {name:'sentence1'})-[:cds]->(cds1:CDS)-[:time]->(t:Time)" \
                     " OPTIONAL MATCH (t2:TEXT  {name:'sentence2'})-[:cds]->(cds2:CDS)-[:SUM_CDSS]-(sum_cds2:SUM_CDSS {total : {total}}) " \
                     " WITH cds2, sum_cds1, s, v, o ,t" \
                     " OPTIONAL MATCH (t2:TEXT  {name:'sentence2'})-[:cds]->(cds2:CDS)-[:verb]->(v2:Verb)" \
                     " OPTIONAL MATCH (t2:TEXT {name:'sentence2'})-[:cds]->(cds2:CDS)-[:subject]->(s2:Subject)" \
                     " OPTIONAL MATCH(t2: TEXT {name: 'sentence2'})-[: cds]->(cds2: CDS)-[: object]->(o2: Object)" \
                     " OPTIONAL MATCH (t2:TEXT {name:'sentence2'})-[:cds]->(cds2:CDS)-[:time]->(t2:Time)" \
                     " RETURN v.normalized as v1, s.normalized as s1, o.normalized as o1, v2.normalized as v2, s2.normalized as s2, o2.normalized as o2, " \
                     " t.normalized as t1, t2.normalized as t2"
    feed_dict = {}
    feed_dict["total"] = total_alignment
    result = session.run(query_sentence, feed_dict)

    for record in result:
        # sentence 1
        s1 = record["s1"]
        s1 if s1 == None else re.sub('^le ', '', s1)
        o1 = record["o1"]
        o1 if o1 == None else re.sub('^le ', '', o1)
        v1 = record["v1"]
        t1 = record["t1"]


        # sentence 2
        s2 = record["s2"]
        s1 if s2 == None else re.sub('^le ', '', s2)
        o2 = record["o2"]
        o2 if o2 == None else re.sub('^le ', '', o2)
        v2 = record["v2"]
        t2 = record["t2"]


    sentence1_lemmatized = {'subject': s1, 'object': o1, 'verb' : v1, 'time' : t1}
    sentence2_lemmatized = {'subject': s2, 'object': o2, 'verb' : v2, 'time' : t2}
    #print(sentence1_lemmatized)
    #print(sentence2_lemmatized)

    # select terms to compare
    term1 = sentence1_lemmatized[pattern]
    term2 = sentence2_lemmatized[pattern]

    return term1, term2

# Feature antonym
def is_antonym(session, total_alignment):
    patterns = ["verb", "subject", "object"]
    for pattern in patterns:
        term1, term2 = sentence_lemmatized(session, pattern, total_alignment)
        print(term1)
        print(term2)

        if term1 == term2:
            print("The terms are equals")
            print("Feature antonym :", 0, 0)
            return 0, 0, "", ""
        else:
            synonym_list = []
            antonym_indirect_list = []
            antonym_direct_list = []
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
                        if antonym_direct_node.text != None:
                            # plusieurs anto direct
                            antonym_direct_list.append(antonym_direct_node.text)
                            for ant in antonym_direct_list:
                                if ant == term2:
                                    print("There is a direct antonym ! >> %s" % term2)
                                    print("Feature antonym detected")
                                    antonym_direct = 1
                                    antonym_indirect = 0
                                    print("Feature antonym :", antonym_direct, antonym_indirect)
                                    return antonym_direct, antonym_indirect, term1, term2

                    # Test antonym indirect
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
                                if antonym_direct_node2.text != None:
                                    print("antonym of " + orth + " is: " + antonym_direct_node2.text)
                                    antonym_indirect_list.append(antonym_direct_node2.text)
            print(antonym_indirect_list)
            antonym_feature = False
            for ant in antonym_indirect_list:
                if ant == term2:
                    # if antonym_direct_node2.text == sentence2:
                    antonym_feature = True

            if antonym_feature is True:
                print("There is an indirect antonym ! >> %s" % term2)
                print("Feature antonym detected")
                antonym_direct = 0
                antonym_indirect = 1
                print("Feature antonym :", antonym_direct, antonym_indirect)
                return antonym_direct, antonym_indirect, term1, term2
            else:
                print("There is no indirect antonym !!!!!!! >> %s" % term2)
                print("Feature antonym not detected")
                print("Feature antonym :", 0)
                return 0, 0, "", ""


# Feature negation
def count_negation_graph(session,sentence, total_alignment):

    query_graph = " MATCH (t:TEXT  {name:{sentence}})-[:cds]->(cds1:CDS)-[:SUM_CDSS]-(sum_cds1:SUM_CDSS {total : {total}}) " \
                  " WITH sum_cds1, cds1 " \
                  " MATCH (cds1:CDS)-[:verb]->(n) " \
                  " RETURN cds1.negation as n, ID(cds1) as id, n.normalized as elem"
    feed_dict = {}
    feed_dict["total"] = total_alignment
    feed_dict["sentence"] = sentence
    result = session.run(query_graph, feed_dict)
    nb_negation_graph = 0
    if total_alignment != 0:
        for record in result:
            if record["n"] is True:
                pattern = record["elem"]
                nb_negation_graph = nb_negation_graph + 1
                #print(nb_negation_graph)
                #print(record["n"])
                print("Feature amount of negation :", nb_negation_graph)
                return nb_negation_graph, pattern
            else:
                print("Feature amount of negation :", 0)
                return 0, record["elem"]
    else: # one CDS not found
        return 0, ""


def is_negation(session, total_alignment): # recognize pattern
    nb_negation_graph1, pattern1 = count_negation_graph(session, "sentence1", total_alignment)
    print(nb_negation_graph1)
    print(pattern1)
    nb_negation_graph2, pattern2 = count_negation_graph(session, "sentence2", total_alignment)
    print(nb_negation_graph2)
    print(pattern2)
    print("Feature amount of negation :",max(nb_negation_graph1, nb_negation_graph2))

     # compare pattern1 and pattern2
    if nb_negation_graph1 == nb_negation_graph2 == 0:
        print("No negation detected")
        return 0, 0, ""
    elif nb_negation_graph1 > 0 and nb_negation_graph2 > 0:
        print("The sentences are both negated >> No negation feature detected")
        return 0, nb_negation_graph1+nb_negation_graph2, ""
    else:
        print("There is chances that have negation feature")

        print("Checking recognize patterns negated. If they are same >> feature negation detected")

        if pattern1 == pattern2:
            print("Feature negation detected at the pattern", pattern1)
            print("Feature negation :", 1)
            return 1, nb_negation_graph1+nb_negation_graph2, pattern1

        else:
            print("Negation is not in the same pattern !>> No feature negation")
            print("Feature negation :", 0)
            return 0, nb_negation_graph1+nb_negation_graph2, ""


# Feature switch
def is_switch(session, total_alignment):

    # select terms to compare
    subject_term1, subject_term2  = sentence_lemmatized(session, 'subject', total_alignment)
    object_term1, object_term2 = sentence_lemmatized(session, 'object', total_alignment)

    if (subject_term1 and subject_term2 and object_term1 and object_term2) != None and (subject_term1 and subject_term2 and object_term1 and object_term2) != "" : # if CDS None
        if subject_term1 == object_term2 and subject_term2 == object_term1:
            print("There is switch object/subject contradiction !")
            print("Feature switch :", 1)
            return 1, subject_term1, object_term1
        else:
            print("There is no switch object/subject")
            print("Feature switch :", 0)
            return 0, "", ""
    else:
        print("je dois être là")
        return 0, "", ""

def comp(list1, list2):
    for val in list1:
        if val in list2:
            return val
    return False

# Feature numeric
def is_numeric(session, total_alignment):
    list_cardinal = []
    list_ordinal = []
    # same entity
    subject_term1, subject_term2 = sentence_lemmatized(session, 'subject', total_alignment)
    object_term1, object_term2 = sentence_lemmatized(session, 'object', total_alignment)
    if (subject_term1 and subject_term2 ) != None:
        if subject_term1 == subject_term2:
            # test if objects are numeric
            with open('numeric_cardinal_ordinal.tsv','r', encoding="utf8") as tsv_file:
                for row in csv.reader(tsv_file, delimiter='\t'):
                    list_cardinal.append(row[0])
                    list_ordinal.append(row[1])

            if (object_term1 and object_term2 ) != None and (object_term1 and object_term2 ) != "":
                object_term1 = object_term1.split()
                object_term2 = object_term2.split()

                object_term1_cardinal = comp(object_term1, list_cardinal)  # test objects are numeric cardinal
                object_term2_cardinal = comp(object_term2, list_cardinal)
                object_term1_ordinal = comp(object_term1, list_ordinal)  # test objects are numeric ordinal
                object_term2_ordinal = comp(object_term2, list_ordinal)

                if (object_term1_cardinal and object_term2_cardinal) != False: # same value
                        if object_term1_cardinal != object_term2_cardinal:
                            print("There is numeric cardinal contradiction !")
                            return 1, object_term1_cardinal, object_term2_cardinal, subject_term1
                        else:
                            return 0, "", "", ""

                if (object_term1_ordinal and object_term2_ordinal) != False:
                    if object_term1_ordinal != object_term2_ordinal:
                        print("There is numeric ordinal contradiction !")
                        return 1, object_term1_ordinal, object_term2_ordinal, subject_term1
                    else:
                        return 0, "", "", ""
                else:
                    return 0,"", "", ""
            else:
                return 0, "", "", ""
        else:
            return 0, "", "", ""

    else:
        return 0, "", "", ""


# Feature time
def time(session, total_alignment):
    # select terms to compare
    time1, time2 = sentence_lemmatized(session, 'time', total_alignment)
    subject_term1, subject_term2 = sentence_lemmatized(session, 'subject', total_alignment)
    if subject_term1 and subject_term2 != None:
        if subject_term1 == subject_term2:
            if time1 != time2:
                print("Features time :", 1)
                return 1, time1, time2
            else:
                print("Features time :", 0)
                return 0,"",""
        else:
            print("Features time :", 0)
            return 0, "", ""
    else:
        print("Features time :", 0)
        return 0, "", ""

# Feature distance
def distance_term1_term2(session, total_alignment, model):
    subject_term1, subject_term2 = sentence_lemmatized(session, 'subject', total_alignment)
    object_term1, object_term2 = sentence_lemmatized(session, 'object', total_alignment)
    verb_term1, verb_term2 = sentence_lemmatized(session, 'verb', total_alignment)
    print("sujet1 : %s, sujet2 : %s, objet1: %s, objet2: %s, verb1: %s, verb2: %s" %(subject_term1,subject_term2, object_term1, object_term2, verb_term1,
                                                           verb_term2))
    distance1 = model.wmdistance(subject_term1,subject_term2) if (subject_term1 and subject_term2) != None and (subject_term1 and subject_term2) != "" else 100

    distance2 = model.wmdistance(object_term1, object_term2) if (object_term1 and object_term2) != None and (object_term1 and object_term2) != "" else 100

    distance3 = model.wmdistance(subject_term1, object_term2) if (subject_term1 and object_term2) != None and (subject_term1 and object_term2) != "" else 100

    distance4 = model.wmdistance(subject_term2, object_term1) if (subject_term2 and object_term1) != None and (subject_term2 and object_term1) != "" else 100

    distance5 =  model.wmdistance(verb_term1, verb_term2) if (verb_term1 and verb_term2) != None and (verb_term1 and verb_term2) != "" else 100

    print("Features distance :",distance1, distance2, distance3, distance4, distance5)
    return distance1, distance2, distance3, distance4, distance5

def main(argv):
    # default values
    host = "bolt://localhost:7687"
    login = "neo4j"
    password = "synapsedev"
    mr_ws_url = "http://api-synapse-dev.azurewebsites.net/machinereading/extractcds"
    apikey = "HT8R7PP6N8U8h8Bn9hrE5NX2R2cdxt32y58Lzqnc"
    lang = "fr"

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", "-loc", help = "Neo4j host. Default to " + host, default = host)
    parser.add_argument("--login", "-log", help = "Login Neo4j. Default to " + login, default = login)
    parser.add_argument("--password", "-psw", help = "Password Neo4j. Default to " + password, default = password)
    parser.add_argument("--url", "-u", help = "Machine Reading endpoint URL. Default to " + mr_ws_url, default = mr_ws_url)
    parser.add_argument("--key", "-k", help = "API key allowing to consume Machine Reading WS.", default = apikey)
    parser.add_argument("--lang", "-l", help = "Language of the texts to be analysed. Possible values: fr for French, en for English. Default to " + lang , default = lang)
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


    # start connection to Neo4j DB
    driver = GraphDatabase.driver(host, auth=basic_auth(login, password))
    session = driver.session()

    model_wikipedia = KeyedVectors.load_word2vec_format("../../resources/lexical_resources/wikifrdict_deserializing.gensim")

    for i in range(1, 10000, 1000):
            file_translated = "../../resources/corpora/multinli/translated/multinli_0.9_dev_matched_%d-%d_translated.jsonl" % (
            i, i + 999)
            with jsonlines.open(file_translated) as reader:
                print(file_translated)
                for obj in reader:
                    sentence1 = obj["sentence1"]
                    sentence2 = obj["sentence2"]
                    label = obj["gold_label"]
                    pairID = obj["pairID"]
                    files_content = {"sentence1": sentence1, "sentence2": sentence2}
                    if label != "neutral" and label != "-":
                        # calcul similarity with MR
                        score = similarity(True, model_wikipedia, "n_similarity", files_content, session, args.lang, args.url, args.key)
                        total_alignment = score
                        print(score)

                        # if score > 0.60: # seuil établi par la meilleure distance
                        print("Score is high >> there are chances to have contradiction ")
                        print("Step 4 ", score)
                        feature_score = 1
                        antonym_direct, antonym_indirect, pattern_1_antonym, pattern_2_antonym = is_antonym(session, total_alignment)
                        feature_negation, feature_amount_negation, pattern_negation = is_negation(session,total_alignment)
                        feature_switch, pattern_subj, pattern_obj = is_switch(session, total_alignment)
                        feature_numeric, object_num1, object_num2, entity = is_numeric(session, total_alignment)
                        feature_time, time1, time2 = time(session, total_alignment)
                        distance1, distance2, distance3, distance4, distance5 = distance_term1_term2(session, total_alignment, model_wikipedia)

                        vect = str(antonym_direct) + "\t" + str(antonym_indirect) + "\t" + str(feature_switch) + "\t" + str(feature_score) + "\t" + str(feature_negation) + "\t" + \
                               str(feature_amount_negation) +"\t" + str(feature_numeric) + "\t" + str(feature_time) + "\t" + str(distance1) + "\t" + str(distance2) + "\t" + str(distance3) + "\t" + \
                               str(distance4) + "\t" + str(distance5)
                        print(vect)
                        with open("13_feature_vector_corrected.tsv", "a+", encoding="utf8") as f:
                                f.write(label + "\t" + vect + "\t" + pairID +"\t" + str(pattern_1_antonym) + "\t" + str(pattern_2_antonym) + str( pattern_subj) + "\t" + str(pattern_obj) + "\t"
                                        + str(pattern_negation)+ "\t" + str(object_num1) + "\t" + str(object_num2) + "\t" + str(entity) + "\n")
                        # else:
                        #     print("Score is low >> no contradiction")
                    else:
                        pass

    session.close()

if __name__ == "__main__":
	main(sys.argv[1:])