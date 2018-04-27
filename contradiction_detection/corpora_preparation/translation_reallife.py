""" Translation of real_life_contradiction with Google Translate API """
#!/usr/bin/env python
# coding: utf-8

import urllib.request, json, html
from lxml import etree

key = "AIzaSyAbfqoZWNysTCeGIyzJRZiJICE4EGKSVFg"
target = "fr"
tree = etree.parse("../../resources/corpora/real_life_contradiction.xml")

def translate_en_to_fr(texte):
    query_text = p.find(texte).text
    print(query_text)
    # encode query to pass to url
    query_text = urllib.parse.quote(query_text)
    #print(query_text)
    google_api = "https://translation.googleapis.com/language/translate/v2?key="+key+"&target="+target+"&q="+ query_text    #a = requests.get(google_api)

    # read the web page
    page = urllib.request.urlopen(google_api)
    strpage =page.read()

    # parse the json
    datas = json.loads(strpage) #loads : charger une chaine de car au format JSON
    #print(datas)
    # return the translated text
    for i in datas["data"]["translations"]:
        translatedText = datas["data"]["translations"][0]["translatedText"]
        #ct.write("      <" + texte + ">" + translatedText + "</" + texte + ">\n")
    return html.unescape(translatedText)  # decode HTML (apostrophe)

with open("real_life_contradiction_translated.xml", "w", encoding="utf8") as ct:
    ct.write("<entailment-corpus>\n")
    for p in tree.xpath("//pair"):
        id = p.get("id")
        contradiction = p.get("contradiction")
        type = p.get("type")

        # recuperate properties from english corpora
        ct.write("<pair id ='"+id+"' contradiction = '"+contradiction+"' type ='"+type+"'>\n")

        # translate the pair of contradictions : text and hypothesis

        t = translate_en_to_fr("t")
        h = translate_en_to_fr("h")
        ct.write("      <t>" + t + "</t>\n")
        ct.write("      <h>" + h + "</h>\n")

        ct.write("</pair>\n")
    ct.write("</entailment-corpus>\n")






