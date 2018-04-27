# ! /usr/bin/env python
# coding=utf-8
""" calcul similarity if MR = True """

from contradiction_detection.score_alignment.term_proximity_syn import *
import re, nltk
from nltk import word_tokenize

def process_alignment_between_texts(session, lang, files_content, sim_mr, model):

    # clean Alignment, SUM_CDSS, SUM_TEXTS
    delete_query_1 = "MATCH(n: Alignment),(som_cds:SUM_CDSS),(som_text:SUM_TEXTS),(text: TEXT {name: '{name1}'}) DETACH DELETE n,som_cds,som_text"
    delete_query_2 = "MATCH(n: Alignment),(som_cds:SUM_CDSS),(som_text:SUM_TEXTS),(text: TEXT {name: '{name2}'}) DETACH DELETE n,som_cds,som_text"
    feed_dict = {}
    feed_dict["name1"] = 'sentence1'
    feed_dict["name2"] = 'sentence2'
    session.run(delete_query_1, feed_dict)
    session.run(delete_query_2, feed_dict)

    query_list = "MATCH (text1:TEXT {name:{name1}})-[:cds]->(cds1:CDS)-[:subject|:verb|:object]->(elem1) MATCH (text2:TEXT {name:{name2}})-[:cds]->" \
                 "(cds2:CDS)-[:subject|:verb|:object]->(elem2) RETURN ID(elem1), elem1.normalized as e1, ID(elem2), elem2.normalized as e2"
    resultat = session.run(query_list, feed_dict)

    # add alignments between cds elements

    if sim_mr == "synonym":
        def process_term_proximity(term1, term2):
            return process_term_proximty_syn(re.sub('^le ', '', term1), re.sub('^le ', '', term2))

    elif sim_mr == "n_similarity":
        def process_term_proximity(term1, term2):
            words1 = word_tokenize(term1.lower())
            words2 = word_tokenize(term2.lower())

            words1 = [w for w in words1 if w in model]
            words2 = [w for w in words2 if w in model]

            return 0 if words1 == [] or words2 == [] else model.n_similarity(words1, words2)

    elif sim_mr == "wmdistance":
        def process_term_proximity(term1, term2):
            words1 = word_tokenize(term1.lower())
            words2 = word_tokenize(term2.lower())
            distance = model.wmdistance(words1, words2)
            return 0 if distance == float("inf") else 1/(1+distance)



    for record in resultat:
        term1 = record["e1"]
        term2 = record["e2"]
        id1 = record["ID(elem1)"]
        id2 = record["ID(elem2)"]

        alignment_score = process_term_proximity(term1, term2)
        print(" %s %s -> %f" % (term1, term2, alignment_score))

        # create node alignment
        if alignment_score != 0:
            query_alignment = "MATCH (n) WHERE ID(n) = " + str(id1) + "  MATCH(m) WHERE ID(m) = " + str(
                id2) + " CREATE (n)<-[:alignment]-(A:Alignment {alignement :" + str(
                alignment_score) + "})-[:alignment]->(m)"
            session.run(query_alignment)

    # add alignments between cdss
    query_alignment_cdss = "MATCH (cds1:CDS)-[:object|subject|verb]->(n)<-[:alignment]-(a:Alignment)-[:alignment]->(m)<-[:object|subject|verb]-(cds2:CDS) \
    WITH cds1,cds2,SUM(a.alignement) AS total \
    MERGE(cds1)-[:SUM_CDSS]->(som_cds:SUM_CDSS {total:total, name :'total_alignment'})<-[:SUM_CDSS]-(cds2) \
    RETURN total,cds1,cds2,ID(cds1),ID(cds2) "
    session.run(query_alignment_cdss)

    # trait case where we have 0 in all alignments
    best_alignment_score = get_best_alignment_score(session, lang, files_content)
    return best_alignment_score if best_alignment_score is not None else 0


def get_best_alignment_score(session, lang, files_content):

    # add alignments between texts
    query = "MATCH(text1:TEXT {name: {name1}})-[: cds]->(cds1: CDS)-[:SUM_CDSS]->(sum:SUM_CDSS) " \
            "<-[:SUM_CDSS]-(cds2: CDS) < -[: cds]-(text2: TEXT {name: {name2}}) " \
            "WITH MAX(sum.total) AS max, (text1), (text2) " \
            "CREATE (text1)-[:score]->(s:score {name: max})<-[:score]-(text2)" \
            "RETURN max"
    feed_dict = {}
    feed_dict["name1"] = 'sentence1'
    feed_dict["name2"] = 'sentence2'
    resultat = session.run(query, feed_dict)

    for record in resultat:
        return record["max"] if record["max"] != None else 0
