# coding: utf-8

import pandas as pd
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
from keras.utils.np_utils import to_categorical
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.metrics import classification_report
from sklearn.decomposition import TruncatedSVD
import gensim
from sklearn.preprocessing import normalize
from tqdm import tqdm
from nltk.tokenize import word_tokenize as tokenizer
from scipy import stats

#get_ipython().magic('matplotlib inline')
import matplotlib.pyplot as plt

#from __future__ import print_function
import numpy as np
import datetime, time, json
from keras.models import Sequential, Model
from keras.layers import Embedding, Dense, Dropout, Reshape, Merge, BatchNormalization, TimeDistributed, Lambda, Input
from keras.regularizers import l2
from keras.callbacks import Callback, ModelCheckpoint
from keras import backend as K
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.model_selection import cross_val_score


config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.7
set_session(tf.Session(config=config))

import jsonlines

path = "../../resources/corpora/multinli/translated/multinli_0.9_dev_matched_1-10000_translated.jsonl"

l=list()
with jsonlines.open(path) as reader:
    for obj in reader:
        sentence1 = obj["sentence1"]
        sentence2 = obj["sentence2"]
        y         = obj["gold_label"]
        l.append([sentence1, sentence2, y])


df = pd.DataFrame(l).sample(frac=1.0)
df.columns = ["s1", "s2", "y"]
df.head()


# # Preprocess

index_shift=10
vocab_size=5000
vectorizer = TfidfVectorizer(max_features=vocab_size-index_shift-1)
vectorizer

df_mnli = df
vectorizer.fit(pd.concat([df_mnli.s1, df_mnli.s2]))
len(vectorizer.vocabulary_)

token_to_index = {k:v+index_shift for k, v in vectorizer.vocabulary_.items()}

_unk = "[unk]"
_start1 = "[start1]"
_pad = "[pad]"
_end2 = "[end2]"
_go = "[go]"
_dropped = "[dropped]"

token_to_index[_pad] = 0
token_to_index[_start1] = 2
token_to_index[_go] = 1
token_to_index[_end2] = 4
token_to_index[_unk] = 5
token_to_index[_dropped] = 6

index_to_token = {v:k for k, v in token_to_index.items()}

seq_length = 25

def vectorize_input(texts, seq_length=seq_length):
    X=[]
    for sentence in texts:
        sentence = str(sentence).lower()
        sen = [token_to_index.get(word, token_to_index[_unk]) for word in tokenizer(sentence)[:seq_length]]
        pad = [0]*(seq_length - len(sen)) 
        X +=  [pad + sen ] 
        
    return np.array(X)


# # Learning

word_vectors_path = "../../resources/wordembeddings/wiki.fr.vec"
embedding_dim = 300

def read_glove_vector(file_line):
    split_line = file_line.split()
    word, vector = split_line[0], split_line[1:]
    try:
        vector = np.asarray([float(num) for num in vector], dtype='float32')
        return word, vector
    except:
        #print(file_line)
        return word, np.random.randn(embedding_dim)*0.2

        
def read_glove_vectors(file_name, word_set):
    for word_vector in open(file_name, encoding='utf8'):
        word, vector = read_glove_vector(word_vector)
        if word in word_set:
            yield word, vector

word_vectors = read_glove_vectors(word_vectors_path, token_to_index.keys())

word_weights = 0*np.random.randn(vocab_size, embedding_dim)*0.2

i=0
for word, vector in word_vectors:
    word_weights[token_to_index[word]]=vector
    i+=1
word_weights.shape, i

word_vectors = read_glove_vectors(word_vectors_path, token_to_index.keys())
l = list(word_vectors)

voc_emb = {a for (a,b) in l}

len(voc_emb)

H = word_weights

Q1_train = vectorize_input(df["s1"])
Q2_train = vectorize_input(df["s2"])
y_train = df["y"].rank(method="dense").astype(int)
df["y"]


state_size=200
embedding_dim = 300


from keras.layers import Lambda
from keras import backend as K
from numpy import newaxis
from keras.models import Model

from keras.optimizers import Adam
from keras.utils import np_utils

y_train = np_utils.to_categorical(y_train-1)

class NBatchLogger(Callback):
    def __init__(self,display=100):
        '''
        display: Number of batches to wait before outputting loss
        '''
        self.seen = 0
        self.display = display
        self.loss = []
        self.acc = []
        self.epoch_time_start = time.time()
        self.loss_ = []
        self.acc_ = []
        self.times=[]
    def on_epoch_end(self, batch, logs={}):
        self.times.append(time.time() - self.epoch_time_start)
        
    def on_batch_end(self,batch,logs={}):
        self.seen += logs.get('size', 0)
        self.loss += [logs.get('loss')]
        self.acc += [logs.get('acc')]
        if self.seen % self.display == 0:
            self.loss_+=[np.mean(self.loss)]
            self.acc_+=[np.mean(self.acc)]
            print(self.seen,self.params['nb_sample'], np.mean(self.loss), np.mean(self.acc))
            loss=[]
            acc=[]

import keras.layers as lyr
from keras.models import Model

input1_tensor = lyr.Input(Q1_train.shape[1:])
input2_tensor = lyr.Input(Q2_train.shape[1:])

words_embedding_layer = lyr.Embedding(vocab_size, embedding_dim, weights=[H])
words_embedding_layer.trainable=False
gru = lyr.GRU(state_size, activation='tanh', dropout_U=0.4, dropout=0.4, return_sequences=False)

input1_tensor_masked = lyr.Masking(mask_value=0)(input1_tensor)
input2_tensor_masked = lyr.Masking(mask_value=0)(input2_tensor)

h1 = gru(words_embedding_layer(input1_tensor_masked))
h2 = gru(words_embedding_layer(input2_tensor_masked))

left  = lyr.Dense(state_size, activation='linear')(h1)
right = h2

merge_prod = lyr.merge([left, right], mode="mul")

ouput_layer = lyr.Dense(4, activation='softmax')(merge_prod)

model = Model([input1_tensor, input2_tensor], ouput_layer)
model.compile(loss='categorical_crossentropy', optimizer=Adam(lr=1e-4, clipvalue=1.0), metrics=['acc'])


callbacks = [NBatchLogger(500)]

for i in range(10):
    h = model.fit([Q1_train, Q2_train], y_train, validation_split=0.1, nb_epoch=1, verbose=0, batch_size=64,
                  callbacks=[])
    print(h.history)

n = int(len(Q1_train )*0.9)
y_pred = model.predict([Q1_train[n:], Q2_train[n:]])

y_pred.argmax(axis=1)

model.summary()

from sklearn.decomposition import PCA

rep = model.layers[-1].get_weights()[0].T

rep = rep-np.mean(rep,axis=0)
print(rep.shape)
viz = PCA(n_components=2)
H = viz.fit_transform(rep)
print(viz.explained_variance_ratio_)

x,y = H[:,0], H[:,1]

fig, ax = plt.subplots()
ax.scatter(x, y)

df.groupby("y").count()