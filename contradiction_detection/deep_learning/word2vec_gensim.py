# ! /usr/bin/env python
# coding=utf-8
""" Creating Word Embeddings with gensim"""
from gensim.models import Word2Vec

# sentence to embedded
sentences = "I had a dog cat mountain half train sorry sorry had had"
#example = [['first'], ['sentence'], ['second'], ['sentence']]

sentences = sentences.split()
list_sentences = []
for i in sentences:
    list_sentences.append([i])

# apply word2vec model
model = Word2Vec(list_sentences, min_count=1)   # in sentences each word/term is a list  min_count = min occurrence of word

# print word vectors
print(model)
print("word2vec \n")
print("sorry >> ",model["dog"]) # dimension 100 (default)
print("cat >> ",model["cat"])
print("mountain >> ",model["mountain"])
print("half >> ",model["half"])
print("train >> ",model["train"])

file = open("word2vec.text", "w")

# save words embedding
for i in list_sentences:
    model[i]
    myfile = str(''.join(i)) + "\t" + str(''.join(str(r)+"\t" for v in  model[i] for r in v)) + "\n"
    file.write(myfile)