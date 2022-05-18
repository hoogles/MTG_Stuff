# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 18:51:57 2022

@author: Hart
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup as BS 
import re #for find and replace that soup isnt good for
import numpy as np
import sklearn 
from sklearn import model_selection #it wont load it if i dont do this. thnks conda
import tensorflow as tf
from word2vec import Word2Vec
from word2vec import generate_training_data
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline



def sigmoid(x):
    return 1/(1 + np.exp(-x))

def binification(X):
    y = []
    n = len(X)
    m = max(X)+1
    for i in range(n):
        z = [0]*m
        j = X[i]
        z[j]=1
        y.append(z)
    
    
    return y
df = pd.read_csv("round2.csv")
df = pd.read_pickle("round2.pickle")
n= len(df)
is_leg = np.zeros(n)
for i in range(n):
    is_leg[i] = sum(df.iloc[i]["Legality"])>0
df = df.iloc[is_leg>0] #remove illefgal cards
    
types = set([t.lower().strip(" ") for subtypes in df["Type"] for t in subtypes])
mainTypes = ["artifact", "creature", "enchantment",  "instant", "land", "planeswalker", "sorcery"]
islegend = ["legendary" in subtype  for subtype in df["Type"]]
df["Is Legendary"] = islegend

boolTypes = np.zeros(len(mainTypes))
df["Bool Types"] = [([int(i in df.loc[j]["Type"]) for i in mainTypes]) for j in df.index]

df.loc[df["Rarity"]== "Common", "Rarity"] = 0
df.loc[df["Rarity"]== "Uncommon", "Rarity"] = 1
df.loc[df["Rarity"]== "Rare", "Rarity"] = 2
df.loc[df["Rarity"]== "Mythic", "Rarity"] = 3
df.loc[df["Rarity"]== "Special", "Rarity"] = 3

BT = np.array( [i for i in df["Bool Types"]])
Tht = (df["Price (USD)"])
X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(BT, Tht, test_size=0.33, random_state=42)

n = len(BT)

costs = np.zeros((8,n)) #[W U B R G C generic X]


for i in range(n):
    cost_s = df.iloc[i]["Mana Cost"]
    if cost_s != [0]:
        for cost in cost_s:
            
                
            if "H" in cost:
                costs[0,i] = -1
            elif "W" in cost:
                if cost=="W" or "/" in cost:
                    costs[0,i] = 1 
                else:
                    costs[0, i] = int(cost.replace("W", ""))
    
            elif "U" in cost:
                if cost=="U" or "/" in cost:
                    costs[1,i] += 1
                else:
                    costs[1,i] += int(cost.replace("U", ""))
            elif "B" in cost :
                if cost=="B" or "/" in cost:
                    costs[2,i] = 1
                else:
                    costs[2,i] = int(cost.replace("B", ""))
            elif "R" in cost:
                if cost=="R" or "/" in cost:
                    costs[3,i] = 1
                else:
    
                    costs[3,i] = int(cost.replace("R", ""))
            elif "G" in cost :
                if cost=="G" or "/" in cost:
                    costs[4,i] = 1
                else:
    
                    costs[4,i] = int(cost.replace("G", ""))
            elif "C" in cost or "S"  in cost:
                if cost=="C" or cost =="S":
                    costs[5,i] = 1
                else:
    
                    costs[5,i] = int(cost.replace("C", "").replace("S", ""))
            elif "X" in cost:
                costs[7,i] +=1
    
            else:
                costs[6,i] = int(cost)
      
dftext =[]
for i in range(n):
    ctxt = str(df.iloc[i]["Rules Text"])
    cname = df.iloc[i]["Name"]
    dftext.append((ctxt.replace(cname, "Self")))

tvec = CountVectorizer()
X = tvec.fit_transform(dftext)
txtbool = X.toarray()

#dftext = [str(df["Rules Text"][i]) for i in range(n)]

text_dataset = tf.data.Dataset.from_tensor_slices(dftext)
max_features = 70000  # Maximum vocab size.
max_len = 3  # Sequence length to pad the outputs to.

vectorize_layer = tf.keras.layers.TextVectorization(

 output_mode='int')

SEED = 42
AUTOTUNE = tf.data.AUTOTUNE
vectorize_layer.adapt(text_dataset)
vocabulary_size = vectorize_layer.vocabulary_size()
vocab_size = vocabulary_size

text_ds = tf.data.TextLineDataset("rulesonly.csv").filter(lambda x: tf.cast(tf.strings.length(x), bool))
text_vector_ds = text_ds.batch(1024).prefetch(AUTOTUNE).map(vectorize_layer).unbatch()
sequences = list(text_vector_ds.as_numpy_iterator())
targets, contexts, labels = generate_training_data(
    sequences=sequences,
    window_size=2,
    num_ns=4,
    vocab_size=vocab_size,
    seed=SEED
    )
targets = np.array(targets)
contexts = np.array(contexts)[:,:,0]
labels = np.array(labels)

dataset = tf.data.Dataset.from_tensor_slices(((targets, contexts), labels))

dataset = dataset.cache().prefetch(buffer_size=AUTOTUNE)

dataset = dataset.shuffle(10000).batch(1024, drop_remainder=True)
cvec = sklearn.feature_extraction.text.CountVectorizer()
X = cvec.fit_transform(dftext)
X2 = X.toarray()



tx = df["Price (tix)"].to_numpy()
usd = df["Price (USD)"].to_numpy()

leg = df["Legality"].to_numpy()
sts = np.zeros([n,2])
for i in range(n):
    stat = df.iloc[i]["stats"]
    a =0
    b =0
    if "Loyalty" in stat:
        a= (stat.split(":")[-1].strip(" "))
        if "*" in a or "X" in a:
            a = -1
        else:
            a = int(a)
        b=a
    else:
        a = (stat.split("/")[0])
        b = (stat.split("/")[1])
        if "*" in a or "X" in a:
            a = -1
        if "*" in b or "X" in b:
            b = -1
    sts[i,0] = int(a)
    sts[i,1]= int(b)
    
