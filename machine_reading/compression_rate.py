from utils.browse_files import get_filenames_recursively
import numpy as np
import argparse

input_path = "../../resources/corpora/sample_texts/machine_reading/summarization/Corpus_RPM2/Corpus_RPM2_documents"

M = np.zeros(40)

i = 0
for thematic in range(1, 21):
    for cluster in range(1, 3):
        file_start = "../../resources/corpora/sample_texts/machine_reading/summarization/Corpus_RPM2/Corpus_RPM2_documents\T" + str(thematic).zfill(2) + "_C" + str(cluster)
        print(file_start)

        # load content from input file(s)
        filenames = get_filenames_recursively(input_path)
        files_content = {}

        for filename in filenames:
            if filename.startswith(file_start) and filename.endswith('.txt'):
                with open(filename, "r") as current_file:

                    M[i] += len(current_file.read())

        i = i+1

input_path = "../../resources/corpora/sample_texts/machine_reading/summarization/system"

B = np.zeros(40)

i = 0

for thematic in range(1, 21):
    for cluster in range(1, 3):
        file_start = "../../resources/corpora/sample_texts/machine_reading/summarization/system\T" + str(thematic).zfill(2) + "C" + str(cluster)

        # load content from input file(s)
        filenames = get_filenames_recursively(input_path)
        files_content = {}

        for filename in filenames:
            if filename.startswith(file_start) and filename.endswith('sumbasictfidf.txt'):
                with open(filename, "r") as current_file:
                    B[i] = len(current_file.read())

        i=i+1

print(B)
print(M)
CR_K = np.divide(B,M)

CR_K.tolist()

thefile = open('cr_sumbasic.txt', 'w')

for item in CR_K:

    thefile.write("%s\n" % item)

