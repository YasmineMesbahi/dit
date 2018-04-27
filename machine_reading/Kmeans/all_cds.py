from pathlib import Path
import numpy as np
import pickle
import sys
import argparse
from neo4j.v1 import GraphDatabase, basic_auth



def all_sao(i,myarray,session):
#
     cypher_querys = session.run("MATCH (cds:CDS) "
                                 # "RETURN  cds.verbatim as verbatim",
                                 "OPTIONAL MATCH (cds)-[:subject]->(subj) "
                                 "OPTIONAL MATCH (cds)-[:verb]->(verb) "
                                 "OPTIONAL MATCH (cds)-[:object]->(obj) "
                                 "OPTIONAL MATCH (cds)-[:time]->(time) "
                                 "OPTIONAL MATCH (cds)-[:place]->(place) "
                                 "WITH cds,subj,verb,obj,time,place "
                                 "WHERE cds.embedding = {a} "
                                 "RETURN cds.verbatim as verbatim, subj.core AS subject_core, verb.core AS verb_core, obj.core AS object_core, time.core AS time_core, place.core as place_core",
                                 {"a": str(myarray[i])})
     c = 1

     for cypher_query in cypher_querys:

         if (c==1):

             s = cypher_query["subject_core"]
             a = cypher_query["verb_core"]
             o = cypher_query["object_core"]
             t = cypher_query["time_core"]
             p = cypher_query["place_core"]
             verbatim = cypher_query["verbatim"]
             c=c+1

     return s, a, o, t, p, verbatim


# store all subjects,verbs,objects core and verbatims in a file
def all_cds(localhost, login, password):

    # start connection to Neo4j DB
    driver = GraphDatabase.driver(localhost, auth=basic_auth(login, password))
    session = driver.session()

    matrice = Path("cdss_embeddings.npy")

    if matrice.is_file() is True:
        myarray = np.load('cdss_embeddings.npy')

    all_svo = Path("all_cds.pickle")


    if all_svo.is_file() is False:

        s_all = []
        a_all = []
        o_all = []
        t_all = []
        p_all = []
        verbatim_all = []

        print("store all subjects,verbs,objects core and verbatims in a file, take a long time...")
        for i in range(len(myarray)):
            #
            su, ve, ob, ti, pl, verbatim = all_sao(i, myarray, session)
            s_all.append(su)
            a_all.append(ve)
            o_all.append(ob)
            t_all.append(ti)
            p_all.append(pl)
            verbatim_all.append(verbatim)

        with open("all_cds.pickle", "wb") as fp:  # Pickling
            pickle.dump((s_all, a_all, o_all, t_all, p_all, verbatim_all), fp)


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

    all_cds(host, login, password)


if __name__ == "__main__":
	main(sys.argv[1:])