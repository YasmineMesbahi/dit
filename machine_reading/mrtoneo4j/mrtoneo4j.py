""" Machine Reading to Neo4j """
#! /usr/bin/env python
#coding=utf-8

import sys, re
import requests
import json
from neo4j.v1 import GraphDatabase, basic_auth
import datetime
import hashlib
import argparse
from pathlib import Path
from utils.browse_files import get_filenames_recursively


list_properties = ["syntacticType", "human", "gender", "number", "groupType", "namedEntityType", "core", "normalized"]


def augment_feeddict_with_cdsg(feed_dict, cds_g, end_value):
    for property in list_properties:
        property_end = property + end_value  # end_value is a character added to property in order to distinguish values in query (if not, values will crush)
        feed_dict[property_end] = cds_g[property]


def call_machine_reading_ws(url, key, lang, text):
    data = {
        "apikey": key,
        "lang": lang,
        "text": re.sub('[«»]', '',re.sub('2.o', '2.0',text))
    }
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json'
    }
    s = requests.Session()
    response = s.post(url, data=json.dumps(data), headers=headers)
    return json.loads(response.content.decode())


def apply_machine_reading(session, text_contents, mr_ws_url, mr_apikey, lang, clear_graph=True):

    # clean Neo4j DB
    if clear_graph:
        session.run("MATCH (n) DETACH DELETE n")

    # analyse all texts from text_content
    for text_name, text_content in text_contents.items():
        print("text " + text_name)
        analysis = call_machine_reading_ws(mr_ws_url, mr_apikey, lang, text_content)

        # commit text node in Neo4j DB
        version = analysis["output"]["version"]
        pseudo_key = str(datetime.datetime.utcnow()) + text_name + text_content + version   # pseudo_key is a string that is created in order to disinguish text
        pseudo_key = hashlib.sha256(pseudo_key.encode(encoding='UTF-8')).hexdigest()
        cypher_query_text = "CREATE (texte:TEXT {content: {content}, version: {version}, name : {path}, pseudokey: {pseudokey}})"
        feed_dict = {}
        feed_dict["content"] = text_content
        feed_dict["version"] = version
        feed_dict["path"] = text_name
        feed_dict["pseudokey"] = pseudo_key
        session.run(cypher_query_text, feed_dict)

        cdss = analysis["output"]["cdss"]

        # Read and commit CDSs
        print(str(len(cdss)) + " cdss found")
        for cds in cdss:
            offset_start = int(cds["offsets"]["start"])
            offset_end = int(cds["offsets"]["end"])
            cypher_query = "CREATE (cds:CDS {offsetStart: {offsetStart}, offsetEnd: {offsetEnd}, question: {question}, modal: {modal}, negation: {negation}, verbatim: {verbatim}})"
            cypher_query = cypher_query + "\n  WITH (cds) MATCH(cds), (b:TEXT {pseudokey: {pseudokey}}) CREATE (cds)<-[:cds]-(b),"
            feed_dict = {}
            feed_dict["pseudokey"] = pseudo_key
            feed_dict["offsetStart"] = offset_start
            feed_dict["offsetEnd"] = offset_end
            feed_dict["question"] = cds["question"]
            feed_dict["modal"] = cds["modifiers"]["modal"]
            feed_dict["negation"] = cds["modifiers"]["negation"]
            feed_dict["verbatim"] = text_content[offset_start:offset_end]

            # ADVERBS
            for id_node, node in enumerate(cds["modifiers"]["adverbs"]):
                try:
                    normalized = node["normalized"]
                    advNameKey = "advName_" + str(id_node)
                    advTitleKey = "advTitle_" + str(id_node)
                    cypher_query = cypher_query + "\n (cds)-[:adverb]->(adv:Adverbs {name: {" + advNameKey + "}, title: {" + advTitleKey + "}, syntacticType: {syntacticTypeAdv}, human: {humanAdv}, gender: {genderAdv}, number: {numberAdv}, groupType: {groupTypeAdv}, namedEntityType: {namedEntityTypeAdv}, core: {coreAdv}, normalized: {normalizedAdv}}),"
                    augment_feeddict_with_cdsg(feed_dict, node, "Adv")
                    feed_dict[advNameKey] = normalized
                    feed_dict[advTitleKey] = normalized
                except:
                    pass

            # ACTION
            try:
                verb = cds["action"]["normalized"]
                node = cds["action"]
                cypher_query = cypher_query + "\n(cds)-[:verb]->(v:Verb {name: {verbName}, title: {verbTitle},syntacticType: {syntacticTypeV}, human: {humanV},gender: {genderV},number: {numberV},groupType: {groupTypeV},namedEntityType: {namedEntityTypeV},core: {coreV} ,normalized: {normalizedV}}),"
                augment_feeddict_with_cdsg(feed_dict, node, "V")
                feed_dict["verbName"] = verb
                feed_dict["verbTitle"] = verb
            except:
                pass

            # SUBJECT
            try:
                subject =  cds["subject"]["normalized"]
                node = cds["subject"]
                cypher_query = cypher_query + "\n(cds)-[:subject]->(s:Subject {name: {subjName}, title: {subjTitle},syntacticType: {syntacticTypeS}, human: {humanS},gender: {genderS},number: {numberS},groupType: {groupTypeS},namedEntityType: {namedEntityTypeS},core: {coreS} ,normalized: {normalizedS}}),"
                augment_feeddict_with_cdsg(feed_dict, node, "S")
                feed_dict["subjName"] = subject
                feed_dict["subjTitle"] = subject
            except:
                pass

            # OBJECT
            try:
                objects = cds["object"]["normalized"]
                node = cds["object"]
                cypher_query = cypher_query + "\n(cds)-[:object]->(o:Object {name: {objName}, title: {objTitle},syntacticType: {syntacticTypeO}, human: {humanO},gender: {genderO},number: {numberO},groupType: {groupTypeO},namedEntityType: {namedEntityTypeO},core: {coreO} ,normalized: {normalizedO}}),"
                augment_feeddict_with_cdsg(feed_dict, node, "O")
                feed_dict["objName"] = objects
                feed_dict["objTitle"] = objects
            except:
                pass

            # IO
            try:
                io = cds["io"]["normalized"]
                node = cds["io"]
                cypher_query = cypher_query + "\n(cds)-[:io]->(io:IO {name: {ioName}, title: {ioTitle},syntacticType: {syntacticTypeIO}, human: {humanIO},gender: {genderIO},number: {numberIO},groupType: {groupTypeIO},namedEntityType: {namedEntityTypeIO},core: {coreIO} ,normalized: {normalizedIO}}),"
                augment_feeddict_with_cdsg(feed_dict, node, "IO")
                feed_dict["ioName"] = io
                feed_dict["ioTitle"] = io
            except:
                pass

            # TIME
            try:
                time = cds["time"]["normalized"]
                node = cds["time"]
                cypher_query = cypher_query + "\n(cds)-[:time]->(t:Time {name: {timeName}, title: {timeTitle},syntacticType: {syntacticTypeT}, human: {humanT},gender: {genderT},number: {numberT},groupType: {groupTypeT},namedEntityType: {namedEntityTypeT},core: {coreT} ,normalized: {normalizedT}}),"
                augment_feeddict_with_cdsg(feed_dict, node, "T")
                feed_dict["timeName"] = time
                feed_dict["timeTitle"] = time
            except:
                pass

            # PLACE
            try:
                 place = cds["place"]["normalized"]
                 node = cds["place"]
                 cypher_query = cypher_query + "\n(cds)-[:place]->(p:Place {name: {placeName}, title: {placeTitle},syntacticType: {syntacticTypeP}, human: {humanP},gender: {genderP},number: {numberP},groupType: {groupTypeP},namedEntityType: {namedEntityTypeP},core: {coreP} ,normalized: {normalizedP}}),"
                 augment_feeddict_with_cdsg(feed_dict, node, "P")
                 feed_dict["placeName"] = place
                 feed_dict["placeTitle"] = place
            except:
                pass

            # MANNER
            try:
                manner = cds["manner"]["normalized"]
                node = cds["manner"]
                cypher_query = cypher_query + "\n(cds)-[:manner]->(m:Manner {name: {mannerName}, title: {mannerTitle},syntacticType: {syntacticTypeM}, human: {humanM},gender: {genderM},number: {numberM},groupType: {groupTypeM},namedEntityType: {namedEntityTypeM},core: {coreM} ,normalized: {normalizedM}}),"
                augment_feeddict_with_cdsg(feed_dict, node, "M")
                feed_dict["mannerName"] = manner
                feed_dict["mannerTitle"] = manner
            except:
                pass

            # Save in DB Neo4j
            cypher_query = cypher_query[:-1]    # Delete the last char ','
            session.run(cypher_query, feed_dict)



def main(argv):
    # default values
    host = "bolt://localhost:7687"
    login = "neo4j"
    password = "synapsedev"
    mr_ws_url = "http://api-synapse-dev.azurewebsites.net/machinereading/extractcds"
    apikey = "HT8R7PP6N8U8h8Bn9hrE5NX2R2cdxt32y58Lzqnc"
    lang = "fr"
    input_path = "../../resources/corpora/sample_texts/machine_reading/summarization/example" #Corpus_RPM2/Corpus_RPM2_documents"

    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", "-loc", help = "Neo4j host. Default to " + host, default = host)
    parser.add_argument("--login", "-log", help = "Login Neo4j. Default to " + login, default = login)
    parser.add_argument("--password", "-psw", help = "Password Neo4j. Default to " + password, default = password)
    parser.add_argument("--url", "-u", help = "Machine Reading endpoint URL. Default to " + mr_ws_url, default = mr_ws_url)
    parser.add_argument("--key", "-k", help = "API key allowing to consume Machine Reading WS.", default = apikey)
    parser.add_argument("--lang", "-l", help = "Language of the texts to be analysed. Possible values: fr for French, en for English. Default to " + lang , default = lang)
    parser.add_argument("--path", "-f", help = "Path to the file containing text to be analysed, or folder containing several files. Default to " + input_path, default = input_path)
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
        print("Specified input file/folder does not exist.")
        sys.exit()

    # load content from input file(s)

    filenames = get_filenames_recursively(args.path)
    text_contents = {}
    for filename in filenames:
        with open(filename, "r") as current_file:
            text_contents[filename] = current_file.read()

    # start connection to Neo4j DB
    driver = GraphDatabase.driver(args.host, auth=basic_auth(args.login, args.password))
    session = driver.session()

    apply_machine_reading(session, text_contents, args.url, args.key, args.lang)

    session.close()

if __name__ == "__main__":
	main(sys.argv[1:])
