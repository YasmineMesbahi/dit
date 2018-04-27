# ! /usr/bin/env python
# coding=utf-8
""" Contradiction detection : antonym from Cordial synonymes  (original code not used with MR) """

import sys
from lxml import etree

# Step 1 : lemmatisation
# Step2 : nature of node
# Step 3 : test synsets
    # is elem1 antonym of elem2 ?

def main(argv):
    sentence1 = "vocal"
    type_node = "v"
    sentence2 = "écrit"
    synonym_list = []
    antonym_list = []
    tree = etree.parse("../../resources/lexical_resources/synonymes_synapse.xml")
    for entry_node in tree.xpath("//entry"):
            orth_node = entry_node.find("orth")

            # Search antonyms if node == sentence 1
            if orth_node.text == sentence1:
                print("Sentence 1 : "+orth_node.text)

                # Test direct antonym
                antonym_direct_nodes = entry_node.findall("gramGrp/gram/sense/anto")

                for antonym_direct_node in antonym_direct_nodes:
                    # direct antonym
                    if antonym_direct_node.text == sentence2:
                        print("There is a direct antonym ! >> %s" % sentence2)
                        print("Feature antonym detected")

                    else:
                        # Test indirect antonym
                        print("There is a no direct antonym ! We searching for indirect antonym")
                        # antonyms of synonyms
                        # Search synonym of sentence 1
                        synonym_nodes = entry_node.findall("gramGrp/gram/sense/syno")
                        print("Synonyms of " + sentence1 + " :")
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
                            print("antonym of "+orth+" is: "+antonym_direct_node2.text)
                            antonym_list.append(antonym_direct_node2.text)
    print(antonym_list)
    antonym_feature = False
    for ant in antonym_list:
        if ant == sentence2:
        # if antonym_direct_node2.text == sentence2:
            antonym_feature = True

    if antonym_feature is True:
        print("There is an indirect antonym ! >> %s" % sentence2)
        print("Feature antonym detected")
    else:
        print("There is no indirect antonym !!!!!!! >> %s" % sentence2)
        print("Feature antonym not detected")

if __name__ == "__main__":
	main(sys.argv[1:])