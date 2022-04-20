# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 13:14:36 2022

@author: Hart Ramsey

Generates a pandas database of all MTG cards from scryfall based off of my needs for analytics. 

Set up with 3 main functions that are all sub fuctions to be more readable and modular
"""


import requests
import pandas as pd
from bs4 import BeautifulSoup as BS 
import re #for find and replace that soup isnt good for



class mtg_df:
     
    
    def clean_cost(self, cost):
        
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
    
    def pull_card(self, url):
        resp = requests.get(url)
        op = []
        if resp.status_code==200: #good to go
            x = resp.text
            soup = BS(x, 'html.parser')
            ctext = soup.find("div",{"class":"card-text"})
            camount = 1
            
            cprice = float(re.findall("Nonfoil: (.*?)\,",x)[0].strip("$").strip(","))
            cname = ctext.find("span", {"class":"card-text-card-name"}).text.strip("\n ")
            ctype = ctext.find("p", {"class":"card-text-type-line"}).text.strip("\n ")
            cstats = ""
            try:
                cstats = soup.find("div", {"class":"card-text-stats"}).text.strip("\n ")
            except: #tbh theres so many exceptions to the rule "only creatures have power" that it's an exception in the code too. 
                cstats = ""
            ccost = 0
            ccost_list = []
            try:
                ccost = ctext.find("span", {"class":"card-text-mana-cost"}).text
                ccost_list = self.clean_cost(ccost)
            except:
                ccost = 0
                ccost_list = [0]
            crules = ""
            try:
                crules = ctext.find("div", {"class":"card-text-oracle"}).text.replace('\n', ' ')
            except:
                crules = ""
            crarity = ""
            try:
                crarity = soup.find("span", {"class":"prints-current-set-details"}).text.strip("\n ").split()[2]
            except:
                crarity = ""
            ctype_list = ctype.replace("—", "").split()
            
            
            is_reserved = len(soup.findAll("p", {"class":"card-text-artist"}))==2
            is_basic = ctype_list.count("Basic")==1
            #omitting reserve lists and basic lands since one is arbitrarily low and basic lands are considered free
            if is_reserved==False and is_basic == False:
                try:
                    void_var = df[cname]
                    cammount = df[cname][8]+1
                except:
                    cammount = 1
                op.append(cname)
                op.append(ccost_list)
                op.append(ctype_list)
                op.append(crules)
                op.append(crarity)
                op.append(cprice)
                op.append(cstats)
                op.append(camount)
            
        return op
            
    
    
    def pull_set(self, url):
        resp = requests.get(url)
        if resp.status_code==200:
            x = resp.text
            soup = BS(x, 'html.parser')
            grid = soup.find("div", {"class":"card-grid"}) #only finds the first
            n= int(soup.find("span",{"class":"card-grid-header-content"}).text.split()[-2])
            for i in range(n):
                #url = str(grid.findAll("a")[i]).replace("=", " ").split()[4].split("\"")[1]
                cdata =[]
                #if url=="card-grid-item-card":
                url = str(grid.findAll("a")[i]).split("href=\"")[1].split("\"")[0]
                try:
                    cdata = self.pull_card(url)
                except:
                    print(str(i) + " failed " + url)
                if len(cdata)>0:
                    if cdata[7]>1:
                        price1 = cdata[5]
                        price2 = df.loc[cdata[0], "Price (USD)"]
                        price = min(price1,price2)
                        self.df.loc[cdata[0]] = {'Name': cdata[0],'Mana Cost':cdata[1], 'Type':cdata[2], 'Rules Text':cdata[3], 'Rarity':cdata[4], 'Price (USD)':price, 'stats':cdata[6], 'times printed':cdata[7]}
                    else:
                        self.df.loc[cdata[0]] = {'Name': cdata[0],'Mana Cost':cdata[1], 'Type':cdata[2], 'Rules Text':cdata[3], 'Rarity':cdata[4], 'Price (USD)':cdata[5], 'stats':cdata[6], 'times printed':cdata[7]}
    
    def pull_sets(self):
        
        base_url = "https://scryfall.com/sets"
        resp = requests.get(base_url)
        if resp.status_code==200:
            x = resp.text
            soup = BS(x, 'html.parser')    
            tbl = soup.find("table", {"class":"checklist"}).findAll("td", {"class":"flexbox"})
            n = len(tbl)
            for i in range(1,n):
                s =str(tbl[i].find("a"))
                sname = tbl[i].find("a").text.strip("\n ")
                ncards= int(soup.findAll("tr")[i+1].findAll("td")[1].text.strip("\n"))
                url = s.replace("=", " ").split()[2].split("\"")[1]
                if ncards>150 and sname.find("Promo")==-1 and sname.find("Tokens")==-1 and sname.find("Cube")==-1 and sname.find("Arena")==-1 and sname.find("Alchemy")==-1 and sname.find("Secret Lair")==-1:
                    try:
                        self.pull_set(url)
                    except:
                        print("failed" + url)
        
                
    def __init__(self):
        self.df = pd.DataFrame(columns={'Name','Mana Cost', 'Type', 'Rules Text', 'stats', 'Rarity', 'Price (USD)', 'times printed'})
        self.df.set_index('Name')
        #self.pull_sets()
        
        
df = mtg_df()
df.df.to_csv("out.csv")