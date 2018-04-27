""" Translation of MultuNLI with Google Translate API  """
#!/usr/bin/env python
# coding: utf-8

import sys
import jsonlines
import urllib.request, json, html

key = "AIzaSyAbfqoZWNysTCeGIyzJRZiJICE4EGKSVFg"
source = "en"
target = "fr"

def translate_en_to_fr(texte):
    query_text = urllib.parse.quote(texte)
    google_api = "https://translation.googleapis.com/language/translate/v2?key="+key+"&source="+source+"&target="+target+"&q="+ query_text
    page = urllib.request.urlopen(google_api)
    strpage = page.read()
    datas = json.loads(strpage)
    translatedText = datas["data"]["translations"][0]["translatedText"]
    return html.unescape(translatedText)  # decode HTML (apostrophe)


def display_progress(i):
    sys.stdout.write("\r%d%%" % (i*100))
    sys.stdout.flush()

def write_translated_text():
    for i in range(1, 10000, 1000):
        file_to_translate = "multinli_0.9_dev_matched_%d-%d.jsonl" % (i, i + 999)
        with jsonlines.open(file_to_translate) as reader:
            file_translated = "multinli_0.9_dev_matched_%d-%d_translated.jsonl" % (i, i + 999)
            with open(file_translated, "w", encoding="utf8") as output_file:
                    with jsonlines.Writer(output_file) as writer:
                        dataset_instances = [dataset_instance for dataset_instance in reader]

                        for i, dataset_instance in enumerate(dataset_instances):
                            translated_dataset_instance = {}
                            translated_dataset_instance['annotator_labels'] = dataset_instance["annotator_labels"]
                            translated_dataset_instance['genre'] = dataset_instance["genre"]
                            translated_dataset_instance['gold_label'] = dataset_instance["gold_label"]
                            translated_dataset_instance['pairID'] = dataset_instance["pairID"]
                            translated_dataset_instance['promptID'] = dataset_instance["promptID"]
                            translated_dataset_instance['sentence1'] = translate_en_to_fr(dataset_instance["sentence1"])
                            translated_dataset_instance['sentence2'] = translate_en_to_fr(dataset_instance["sentence2"])

                            writer.write(translated_dataset_instance)

                            display_progress(i/len(dataset_instances))

def main(argv):
    write_translated_text()


if __name__ == "__main__":
	main(sys.argv[1:])