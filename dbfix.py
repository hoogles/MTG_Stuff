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
import wordfixing

from datetime import datetime
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


def convert_mtg_df(df):
    
    type_set = set()
    for tlist in df["Type"]:
        type_set.update(tlist)
    # datetime.datetime.strptime(df["Date"][0], "%Y-%m-%d")
    
    
    n = len(df)
    types = set([t.lower().strip(" ") for subtypes in df["Type"] for t in subtypes])
    mainTypes = ["Artifact", "Creature", "Enchantment",  "Instant", "Land", "Planeswalker", "Sorcery"]
    islegend = ["legendary" in subtype  for subtype in df["Type"]]
    df["Is Legendary"] = islegend
    
    boolTypes = np.zeros(len(type_set))
    df["Bool Types"] = [([int(i in df.loc[j]["Type"]) for i in type_set]) for j in df.index]
    
    df.loc[df["Rarity"]== "Common", "Rarity"] = 0
    df.loc[df["Rarity"]== "Uncommon", "Rarity"] = 1
    df.loc[df["Rarity"]== "Rare", "Rarity"] = 2
    df.loc[df["Rarity"]== "Mythic", "Rarity"] = 3
    df.loc[df["Rarity"]== "Special", "Rarity"] = 3
    
    BT = np.array( [i for i in df["Bool Types"]])
    #Tht = (df["Price (USD)"])
    #X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(BT, Tht, test_size=0.33, random_state=42)
    
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
          
    
    
    tx = df["Price (tix)"].to_numpy()
    usd = df["Price (USD)"].to_numpy()
    tp = df["times printed"].to_numpy()
    
    leg = np.array(df["Legality"].to_numpy().tolist())
    r = df["Rarity"].to_numpy()
    
    card_info = []
    for i in range(n):
        
        card = df.iloc[i]
        cr = wordfixing.card_reader(card)
        card_info.append(cr.translated)
    
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


    Timeset = []
    for t in df["Date"]:
        dt = datetime.strptime(t, "%Y-%m-%d")
        tdelta = datetime.now() - dt
        Timeset.append(tdelta.days)
        

    
       
    
    Y = np.array([tx,usd], dtype='f')
    #X = np.array([np.ones(n), tp, leg, r, sts, costs.transpose() ,islegend, BT])
    X = np.array([np.ones(n), tp,  r, islegend, Timeset],dtype="f")
    X = np.vstack((X, sts.transpose()[0].transpose()))
    X = np.vstack((X, sts.transpose()[1].transpose()))
    
    #add the legalities we are ingoring pauper/penny because that will skew data
    X = np.vstack((X, leg.transpose()[0].transpose())) #Standard
    X = np.vstack((X, leg.transpose()[1].transpose())) #Pioneer
    X = np.vstack((X, leg.transpose()[2].transpose())) #Modern
    X = np.vstack((X, leg.transpose()[3].transpose())) #Legacy
    X = np.vstack((X, leg.transpose()[4].transpose())) #Vintage
    X = np.vstack((X, leg.transpose()[5].transpose())) #Commander
    
    X = np.vstack((X, BT.transpose()[0]))
    X = np.vstack((X, BT.transpose()[1]))
    X = np.vstack((X, BT.transpose()[2]))
    X = np.vstack((X, BT.transpose()[3]))
    X = np.vstack((X, BT.transpose()[4]))
    X = np.vstack((X, BT.transpose()[5]))
    X = np.vstack((X, BT.transpose()[6]))
    X = np.vstack((X, costs))
    
    for ct in np.array(card_info).T:
        X = np.vstack((X, ct))        
    return X, Y
#df = pd.read_csv("round2.csv")
df2 = pd.read_pickle("db3.pickle")
n= len(df2)
is_leg = np.zeros(n)
for i in range(n):
    is_leg[i] = sum(df2.iloc[i]["Legality"])>0
df = df2.iloc[is_leg>0] #remove illefgal cards
df = df.loc[df["Price (USD)"]>0]

# dftext =[]
# for i in range(n):
#     ctxt = str(df.iloc[i]["Rules Text"])
#     cname = df.iloc[i]["Name"]
#     dftext.append((ctxt.replace(cname, "Self")))

# tvec = CountVectorizer()
# X = tvec.fit_transform(dftext)
# txtbool = X.toarray()

# #dftext = [str(df["Rules Text"][i]) for i in range(n)]

# text_dataset = tf.data.Dataset.from_tensor_slices(dftext)
# max_features = 70000  # Maximum vocab size.
# max_len = 3  # Sequence length to pad the outputs to.

# vectorize_layer = tf.keras.layers.TextVectorization(

#  output_mode='int')

# SEED = 42
# AUTOTUNE = tf.data.AUTOTUNE
# vectorize_layer.adapt(text_dataset)
# vocabulary_size = vectorize_layer.vocabulary_size()
# vocab_size = vocabulary_size

# text_ds = tf.data.TextLineDataset("rulesonly.csv").filter(lambda x: tf.cast(tf.strings.length(x), bool))
# text_vector_ds = text_ds.batch(1024).prefetch(AUTOTUNE).map(vectorize_layer).unbatch()
# sequences = list(text_vector_ds.as_numpy_iterator())
# targets, contexts, labels = generate_training_data(
#     sequences=sequences,
#     window_size=2,
#     num_ns=4,
#     vocab_size=vocab_size,
#     seed=SEED
#     )
# targets = np.array(targets)
# contexts = np.array(contexts)[:,:,0]
# labels = np.array(labels)

# dataset = tf.data.Dataset.from_tensor_slices(((targets, contexts), labels))

# dataset = dataset.cache().prefetch(buffer_size=AUTOTUNE)

# dataset = dataset.shuffle(10000).batch(1024, drop_remainder=True)
# cvec = sklearn.feature_extraction.text.CountVectorizer()
# X = cvec.fit_transform(dftext)
# X2 = X.toarray()


    
def get_legality( txt):
        
        legality = [0]*8 #we care about Standard, Pioneer, Modern, Legacy, Vintage and Commander. Added Pauper and Penny to test that my NLP works
        lgls = txt.find("dl", {"class":"card-legality"})
        lgls2 = lgls.text.split("\n")
        
        i0 = lgls2.index("Standard")+1
        i1 = lgls2.index("Pioneer")+1
        i2 = lgls2.index("Modern")+1
        i3 = lgls2.index("Legacy")+1
        i4 = lgls2.index("Vintage")+1
        i5 = lgls2.index("Commander")+1
        i6 = lgls2.index("Pauper")+1
        i7 = lgls2.index("Penny")+1
        
        legality[0]  = int(lgls2[i0]=="Legal")
        legality[1]  = int(lgls2[i1]=="Legal")
        legality[2]  = int(lgls2[i2]=="Legal")
        legality[3]  = int(lgls2[i3]=="Legal")
        legality[4]  = int(lgls2[i4]=="Legal")
        legality[5]  = int(lgls2[i5]=="Legal")
        legality[6]  = int(lgls2[i6]=="Legal")
        legality[7]  = int(lgls2[i7]=="Legal")  
        
        
        return legality
    
def clean_cost( cost):
    
    templist = cost.replace("{", " ").replace("}", " ").split()
    uniques = set(templist)
    cleaned = []
    for i in uniques:
        n = templist.count(i)
        x = i
        if n>1:
           x = str(n)+x 
        cleaned.append(x)
    
    return cleaned
    

    

X, Y =  convert_mtg_df(df)
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X.T, Y[1], random_state=1)


from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor(n_estimators=1000)
model.fit(X_train,y_train)
#model.fit(X.T,Y[1]) overfit, aka goal
class skipgraming:
    
    
    
    def get_skipgrams(dftext):
        vocab = {}
        index = 1
        vocab['<pad>'] = 0
        for rules in dftext:
            tokens = list(rules.lower().split())
            for token in tokens:
                if token not in vocab:
                    vocab[token] = index
                    index += 1
        inverse_vocab = {index: token for token, index in vocab.items()}
        example_sequence = []
        vocab_size = len(vocab)
        for rules in dftext:
            tokens = list(rules.lower().split())
            seq = [vocab[word] for word in tokens]
            example_sequence = example_sequence + seq
        window_size = 3
        positive_skip_grams, _ = tf.keras.preprocessing.sequence.skipgrams(
              example_sequence,
              vocabulary_size=vocab_size,
              window_size=window_size,
              negative_samples=0)
