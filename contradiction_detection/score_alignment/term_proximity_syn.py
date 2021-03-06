#! /usr/bin/env python
# coding=utf-8
""" process score alignment between two terms """

import sys
from lxml import etree


def get_score(synonym_node):
    return float(synonym_node.get("proximity", "200")) / 255


def read_data(xml_path):
    tree = etree.parse(xml_path)

    alignments = {}

    for entry_node in tree.xpath("//entry"):
        orth_node = entry_node.find("orth")
        #print(orth_node.text)
        alignments[orth_node.text] = {}
        synonym_nodes = entry_node.findall("gramGrp/gram/sense/syno")
        for synonym_node in synonym_nodes:
            #print(" -> " + synonym_node.text + " - " + str(get_score(synonym_node)))
            alignments[orth_node.text][synonym_node.text] = get_score(synonym_node)

    return alignments


def process_term_proximty_syn_inner(term1, term2):
    if term1 == term2:
        return 1.0
    term1_synonyms = alignments.get(term1, {})
    alignment = term1_synonyms.get(term2, 0)
    return alignment


def process_term_proximty_syn(term1, term2):
    return max(process_term_proximty_syn_inner(term1, term2), process_term_proximty_syn_inner(term2, term1))


alignments = read_data("../../resources/lexical_resources/synonymes_synapse.xml")


def main(argv):
    alignment_score = process_term_proximty_syn('éducation', 'enseignement')
    print(alignment_score)
    assert (alignment_score == 137/255),"process_term_proximty_syn('éducation', 'enseignement') should be " + str(137/255) + ", but was " + str(alignment_score)

    # test simple word
    alignment_score = process_term_proximty_syn('émettre', 'exsuder')
    assert (alignment_score == 68/255),"process_term_proximty_syn('émettre', 'exsuder') should be " + str(68/255) + ", but was " + str(alignment_score)

    # test composed word with -
    alignment_score = process_term_proximty_syn('intention', 'arrière-pensée')
    assert (alignment_score == 91/255),"process_term_proximty_syn('intention', 'arrière-pensée') should be " + str(91/255) + ", but was " + str(alignment_score)

    # test composed word with space
    alignment_score = process_term_proximty_syn('ménager', 'faire le ménage')
    print(alignment_score)
    assert (alignment_score == 216/255),"process_term_proximty_syn('ménager', 'faire le ménage') should be " + str(216/255) + ", but was " + str(alignment_score)

    alignment_score = process_term_proximty_syn('dévorer', 'manger')
    print(alignment_score)


if __name__ == "__main__":
	main(sys.argv[1:])
