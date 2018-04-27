import pickle
from sklearn.cluster import KMeans
import numpy as np
from neo4j.v1 import GraphDatabase, basic_auth
import sys
from pathlib import Path
import argparse


def find_cds(indice,array, session, s, a, o, t, p, verbatim, id_cds):

    cypher_querys = session.run("MATCH (cds:CDS) "
                                "OPTIONAL MATCH (cds)-[:subject]->(subj) "
                                "OPTIONAL MATCH (cds)-[:verb]->(verb) "
                                "OPTIONAL MATCH (cds)-[:object]->(obj) "
                                "OPTIONAL MATCH (cds)-[:time]->(time) "
                                "OPTIONAL MATCH (cds)-[:place]->(place) "
                                "WITH cds,subj,verb,obj,time,place "
                                "WHERE cds.embedding = {a} "
                                # "RETURN DISTINCT cds.verbatim as verbatim" ,
                                "RETURN  cds.verbatim as verbatim, subj.core AS subject_core, verb.core AS verb_core, obj.core AS object_core,time.core AS time_core, place.core as place_core,"
                                " ID(cds) as id_cds ",{"a": str(array[indice])})
    c = 1

    for cypher_query in cypher_querys:

                if c == 1:

                    s = cypher_query["subject_core"]
                    a = cypher_query["verb_core"]
                    o = cypher_query["object_core"]
                    t = cypher_query["time_core"]
                    p = cypher_query["place_core"]
                    verbatim = cypher_query["verbatim"]
                    id_cds = cypher_query["id_cds"]
                    c = c + 1

    return s, a, o, t, p, verbatim, id_cds


# add Kmeans to graph and find the cdss closest to the cluster centers
def add_kmeans_to_graph(localhost, login, password,normalized):

    # start connection to Neo4j DB
    driver = GraphDatabase.driver(localhost, auth=basic_auth(login, password))
    session = driver.session()

    # Kmeans clustering

    print("Applying Kmeans to cdss_embeddings.npy")

    if normalized:

        matrice = Path("cdss_embeddings_normalized.npy")

        if matrice.is_file() is True:

            print("load cdss_embeddings_normalized ")

            myarray = np.load('cdss_embeddings_normalized.npy')

    else:

        matrice = Path("cdss_embeddings.npy")

        if matrice.is_file() is True:

            myarray = np.load('cdss_embeddings.npy')


    print(myarray.shape)
    kmeans = KMeans(n_clusters=7).fit(myarray)
    clusters = kmeans.labels_

    print("save cluster labels in a file")
    with open("clusters.pickle", "wb") as fp: #Pickling
            pickle.dump(clusters, fp)

    print("add Kmeans to Neo4j graph")
    #add kmeans to Neo4j Graph
    for j in range (len(myarray)):
        session.run("MATCH (cds:CDS) WHERE cds.embedding = {b} SET cds.KmeansLabel = {label} ",
                {"b": str(myarray[j]), "label": str(clusters[j])})

    # find the 100 indices of myarray closest to cluster centers

    print("looking for the n indices of cdss_embeddings closest to cluster centers")
    list_ind = []

    print(len(kmeans.cluster_centers_))
    for j in range (len(kmeans.cluster_centers_)):
        # the distance to the j-th centroid for each point in the array myarray is:
        d = kmeans.transform(myarray)[:, j]
        # the indice of the closest one to centroid j is:
        ind = np.argsort(d)[::][:1]

        k = 1
        while (np.count_nonzero(myarray[ind])<900):
             ind = np.argsort(d)[::][k:k+1]
            # # print(ind)
             k=k+1

        # save indices in a list
        list_ind.append(ind)


    # convert indices list in array
    list_ind_arr = np.asarray(list_ind)

    verbatim_centers = []
    id_cds_centers = []
    subject_center = []
    verb_center = []
    object_center = []
    time_center = []
    place_center = []

    for j in range (len(list_ind_arr)):

        i = int(list_ind_arr[j])
        s = " "
        a = " "
        o = " "
        t = " "
        p = " "
        verbatim = " "
        id_cds = " "
        su_c, ve_c, ob_c, ti_c, pl_c, verbatim, id_cds_c = find_cds(i, myarray, session, s, a, o, t, p, verbatim, id_cds)

        subject_center.append(su_c)
        verb_center.append(ve_c)
        object_center.append(ob_c)
        time_center.append(ti_c)
        place_center.append(pl_c)
        id_cds_centers.append(id_cds_c)
        verbatim_centers.append(verbatim)
        #findCds(i,myarray,session)

    print("store subject,verb,object,time,place cores and verbatims closest to cluster centers")

    print(verbatim_centers)
    print(id_cds_centers)

    with open("svo_centers.pickle", "wb") as fp: #Pickling
           pickle.dump((subject_center, verb_center, object_center, time_center, place_center, verbatim_centers, id_cds_centers), fp)


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
    add_kmeans_to_graph(host, login, password,normalized)


if __name__ == "__main__":
	main(sys.argv[1:])