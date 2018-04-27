#! /usr/bin/env python
#coding=utf-8
""" Add vecteur to CDS """


import nltk
from machine_reading.Kmeans.all_cds import *
from sklearn.manifold import TSNE
import numpy as np
import os
from machine_reading.Kmeans.word2vec import get_word_vectors


np.seterr(divide='ignore', invalid='ignore')
tsne = TSNE(n_components=2, random_state=0, verbose=1)
np.set_printoptions(suppress=True)


# process and store embeddings for each CDS
def process_term_vector(term, word_vectors):

    vector_sum = np.zeros(300)
    vectors_count = 0

    stopwords = nltk.corpus.stopwords.words('french')
    stopwords.append("'")
    stopwords.append('"')
    stopwords.append("les")
    stopwords.append("a")
    stopwords.append("cet")
    stopwords.append("elles")
    stopwords.append(",")
    stopwords.append("-")

    for token in term:

        if token not in stopwords:

            if token in word_vectors:
                vector_sum += word_vectors[token]
                vectors_count += 1

    return vector_sum
    #term_vector = vector_sum / vectors_count
    #return term_vector

def process_cds_vector(subject_core, verb_core, object_core, time_core, place_core, word_vectors):
    # TODO:
    # calculer embedding de subject_core
    # calculer embedding de verb_core
    # calculer embedding de object_core
    # concaténer les trois embedding et retourner le résultat

    # embedding de subject_core

    if subject_core==None:
        subject_vector = np.zeros(300)
    else:
        subject_vector = process_term_vector(nltk.wordpunct_tokenize(subject_core.lower()), word_vectors)

    # embedding de verb_core
    if verb_core==None:
        verb_vector = np.zeros(300)
    else:
        verb_vector = process_term_vector(nltk.wordpunct_tokenize(verb_core.lower()), word_vectors)

    # embedding de object_core
    if object_core==None:
        object_vector = np.zeros(300)
    else:
        object_vector = process_term_vector(nltk.wordpunct_tokenize(object_core.lower()), word_vectors)

    # embedding de time_core
    if time_core == None:
            time_vector = np.zeros(300)
    else:
            time_vector = process_term_vector(nltk.wordpunct_tokenize(time_core.lower()), word_vectors)

    # embedding de place_core
    if place_core == None:
        place_vector = np.zeros(300)
    else:
        place_vector = process_term_vector(nltk.wordpunct_tokenize(place_core.lower()), word_vectors)


    cds_concatenate_vector = np.concatenate((subject_vector, verb_vector, object_vector,time_vector,place_vector))

    return cds_concatenate_vector


def add_cds_vector_to_graph(cds_id, vector, session):
    session.run("MATCH (cds:CDS) WHERE ID(cds) = {cds_id} SET cds.embedding = {cds_vector}",
                {"cds_id": cds_id, "cds_vector": str(vector)})


def delete_cdsvectors_duplicate(array):

    array_sorted=array[np.lexsort(np.fliplr(array).T)]

    Y = array_sorted[0]

    for i in range(len(array_sorted)):

        if i < (len(array_sorted) - 1):

            if (array_sorted[i] == array_sorted[i + 1]).all():

                nothing = 0

            else:

                Y = np.vstack((Y, array_sorted[i + 1]))

    return Y


# add vector embedding to cds(in neo4j graph) and store all vectors embedding in cdss_embeddings.npy and 2D projection in V.npy
def add_embedding_cds(localhost, login, password, word_vectors,normalized):

    # start connection to Neo4j DB
    driver = GraphDatabase.driver(localhost, auth=basic_auth(login, password))
    session = driver.session()

    all_cdss = session.run("MATCH (cds:CDS) "
                       "OPTIONAL MATCH (cds)-[:subject]->(subj) "
                       "OPTIONAL MATCH (cds)-[:verb]->(verb) "
                       "OPTIONAL MATCH (cds)-[:object]->(obj) "
                       "OPTIONAL MATCH (cds)-[:time]->(time) "
                       "OPTIONAL MATCH (cds)-[:place]->(place) "
                       "RETURN ID(cds) AS cds_id, subj.core AS subject_core, verb.core AS verb_core, obj.core AS object_core, time.core AS time_core, place.core as place_core")
    if normalized:

        emb_not_norm = Path("cdss_embeddings.npy")

        if emb_not_norm.is_file() is True:

            os.remove("cdss_embeddings.npy")

        matrice = Path("cdss_embeddings_normalized.npy")

        if matrice.is_file() is True:

            print("matrix cds.embedding normalized already exists and graph Neo4j already updated with cds.embedding")
            #myarray = np.load('cdss_embeddings_normalized.npy')
            # V = np.load('V.npy')

        else:

            list_word_vec = []
            print("process and store embeddings normalized for each CDS")
            print("add cds.embedding normalized to Neo4j graph")

            for cds in all_cdss:
                subject_core = cds["subject_core"]
                verb_core = cds["verb_core"]
                object_core = cds["object_core"]
                time_core = cds["time_core"]
                place_core = cds["place_core"]
                cds_id = cds["cds_id"]

                vector = process_cds_vector(subject_core, verb_core, object_core,time_core,place_core, word_vectors)

                add_cds_vector_to_graph(cds_id, vector, session)

                # list of vectors word
                if np.any(np.isnan(vector)):

                    n = 0

                else:

                    list_word_vec.append(vector)

            print("store all cds.embedding normalized in a matrix")
            myarray = np.asarray(list_word_vec)
            print("delete dupliactes vectors in the matrix")
            myarray = delete_cdsvectors_duplicate(myarray)
            print("save matrix in a numpy file")
            np.save('cdss_embeddings_normalized.npy', myarray)

            V = tsne.fit_transform(myarray)  # Fit myarray into an embedded space and return that transformed output.
            np.save('V.npy', V)



    else:

        emb_norm = Path("cdss_embeddings_normalized.npy")

        if emb_norm.is_file() is True:

            os.remove("cdss_embeddings_normalized.npy")

        matrice = Path("cdss_embeddings.npy")

        if matrice.is_file() is True:

            print("matrix cds.embedding already exists and graph Neo4j already updated with cds.embedding")
            #myarray = np.load('cdss_embeddings.npy')
            # V = np.load('V.npy')

        # else:

            list_word_vec = []
            print("process and store embeddings for each CDS")
            print("add cds.embedding to Neo4j graph")

            for cds in all_cdss:
                subject_core = cds["subject_core"]
                verb_core = cds["verb_core"]
                object_core = cds["object_core"]
                time_core = cds["time_core"]
                place_core = cds["place_core"]
                cds_id = cds["cds_id"]

                vector = process_cds_vector(subject_core, verb_core, object_core, time_core, place_core, word_vectors)

                add_cds_vector_to_graph(cds_id, vector, session)

                # list of vectors word
                if np.any(np.isnan(vector)):

                    n = 0

                else:

                    list_word_vec.append(vector)

            print("store all cds.embedding in a matrix")
            myarray = np.asarray(list_word_vec)
            print("delete duplicates vectors in the matrix")
            myarray = delete_cdsvectors_duplicate(myarray)
            print("save matrix in a numpy file")
            np.save('cdss_embeddings.npy', myarray)

            V = tsne.fit_transform(myarray)  # Fit myarray into an embedded space and return that transformed output.
            np.save('V.npy', V)





    # print("Matrix cds.embedding shape:")
    #     print(myarray.shape) #shape after deleting duplicates

    session.close()



########################################################################################################################

def main(argv):
    # default values
    host = "bolt://localhost:7687"
    login = "neo4j"
    password = "synapsedev"

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", "-loc", help = "Neo4j host. Default to " + host, default = host)
    parser.add_argument("--login", "-log", help = "Login Neo4j. Default to " + login, default = login)
    parser.add_argument("--password", "-psw", help = "Password Neo4j. Default to " + password, default = password)
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

    normalized = False
    word_vectors = get_word_vectors(normalized)


    add_embedding_cds(host, login, password, word_vectors,normalized)


if __name__ == "__main__":
	main(sys.argv[1:])



