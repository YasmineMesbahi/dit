""" Lemmatisation with syntactictagging """

import requests, sys
import json, csv, re

def read_syntactictagging(text):
  data = {
    "apikey": "HT8R7PP6N8U8h8Bn9hrE5NX2R2cdxt32y58Lzqnc",
    "lang": "fr",
    "text": text
  }
  headers = {
      'Content-type': 'application/json',
      'Accept': 'application/json'
  }
  url = "http://api-synapse-dev.azurewebsites.net/syntax/GetSyntaxAnalysis"
  s = requests.Session()
  response = s.post(url ,data=json.dumps(data), headers=headers)
  analysis = re.sub(r'<[^>]+>', '', response.content.decode())
  return (analysis)


def write_tsv_file(text):
  with open ("output_syntactictagging.tsv", "w", encoding="utf8") as output:
      output.write(read_syntactictagging(text))

def read_tsv_file():
  list =  [] # used as matrix
  with open ("output_syntactictagging.tsv", "r", encoding="utf8") as output:
      reader = csv.reader(output, delimiter='\t')
      for row in reader:
        list.append(row)
      number_header_footer = 7
      number_words = len(list) - number_header_footer  # del header and footer of 1 sentence only (MAUVAIS)


  lemme = 6 # not changed
  list_lemmes = []
  print("Nombre de mots :" ,number_words)
  for word in range(3,number_words+3):
      list_lemmes. append(list[word][lemme])
  print("La liste des lemmes :",list_lemmes)
  return (list_lemmes)


def main(argv):
  write_tsv_file("Le chat mange la souris, mais finalement il n'avait pas très faim.")  # TODO : formater début et fin de phrase
  read_tsv_file()


if __name__ == "__main__":
	main(sys.argv[1:])

