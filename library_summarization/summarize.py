from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
# from sumy.summarizers.lsa import LsaSummarizer as Summarizer
# from sumy.summarizers.lex_rank import LexRankSummarizer as Summarizer
#from sumy.summarizers.kl import KLSummarizer as Summarizer
from sumy.summarizers.text_rank import TextRankSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from utils.browse_files import get_filenames_recursively



# from utils.browse_files import get_filenames_recursively
#
#
input_path = "../resources/corpora/sample_texts/machine_reading/summarization/Corpus_RPM2/Corpus_RPM2_documents"

LANGUAGE = "french"
SENTENCES_COUNT = 7

for thematic in range(1, 21):
    for cluster in range(1, 3):

        file_start = input_path + "\T" + str(thematic).zfill(2) + "_C" + str(cluster)
        print(file_start)

        clusterContent = ""

        # load content from input file(s)
        filenames = get_filenames_recursively(input_path)
        files_content = {}
        for filename in filenames:
            if filename.startswith(file_start) and filename.endswith('.txt'):
                with open(filename, "r") as current_file:
                    clusterContent = clusterContent + current_file.read() + "\n\n\n"

        # print(clusterContent)
        # print("\n\n\n==================\n\n\n")

        parser = PlaintextParser.from_string(clusterContent, Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)

        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)

        summary = ""
        for sentence in summarizer(parser.document, SENTENCES_COUNT):
            summary = summary + str(sentence) + "\n"

        summary_output_filepath = "../machine_reading/Rouge/test-summarization/system\T" + str(thematic).zfill(2) + "C" + str(cluster) + "_summy-textr.txt"
        with open(summary_output_filepath, "w") as text_file:
            text_file.write(summary)


