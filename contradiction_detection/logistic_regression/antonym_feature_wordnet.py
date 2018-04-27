# ! /usr/bin/env python
# coding=utf-8
""" Contradiction detection : antonym from WordNet (original mthod)"""

import sys
from nltk.corpus import wordnet as wn

def main(argv):

    sentence1 = "fall"
    type_node = "v"
    sentence2 = "rise"

    # lemmatize 4 parts
    sentence1 = wn.synset(sentence1+'.'+type_node+'.01')
    print(sentence1)
    sentence1_antonyms = sentence1.lemmas()[0].antonyms()

    # direct antonym
    if sentence1_antonyms != []:
        print("There is a direct antonym ! %s" %sentence1_antonyms)

    # indirect antonym
    else:
        print("There is no direct antonym !")

        print("We searching for synonyms")
        sentence1_syn = wn.synsets('fall')

        if sentence1_syn == []:
            print("There is no synonyms")
            print("No antonym found !")

        else:
            print(sentence1_syn)
            print("We searching for antonyms of synonyms")
            # if sentence2 in antonyms then true feature
            for synonym in sentence1_syn:
                sentence1_antonyms_in_synonyms = synonym.lemmas()[0].antonyms()

                if sentence1_antonyms_in_synonyms != []:
                    for antonym_synonym in sentence1_antonyms_in_synonyms:
                        if sentence2 in str(antonym_synonym):
                            print("Then sentences have an indirect antonym ! It is %s" %antonym_synonym)

if __name__ == "__main__":
	main(sys.argv[1:])