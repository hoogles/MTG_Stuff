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
import datetime


class mtg_df:
     
    
    def get_legality(self, txt):
        
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
    def get_times_printed(self, url, cname):
        n=1
        cnamemod = "-".join(cname.split())

        url_mod = "https://scryfall.com/search?as=grid&order=released&q=%21%22"+cnamemod+"%22+include%3Aextras&unique=prints"
        
        resp = requests.get(url_mod)
        
        if resp.status_code==200:
            soup = BS(resp.text, 'html.parser')
            y = soup.find("div",{"class":"search-info"})
            n = int(y.find("strong").text.split()[0])
            
        return n
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
            
            cprice = float(re.findall("usd\">(.*?)<",x)[0].strip("$"))
            try:
                cpricetx = float(re.findall("tix\">(.*?)<",x)[0].strip("$").strip(","))
            except:
                cpricetx = 0
            cname = ctext.find("span", {"class":"card-text-card-name"}).text.strip("\n ")
            ctype = ctext.find("p", {"class":"card-text-type-line"}).text.strip("\n ")
            cstats = ""
            try:
                cstats = soup.find("div", {"class":"card-text-stats"}).text.strip("\n ")
            except: #tbh theres so many exceptions to the rule "only creatures have power" that it's an exception in the code too. 
                cstats = "0/0"
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
            clegality = self.get_legality(ctext)
            
            is_reserved = len(soup.findAll("p", {"class":"card-text-artist"}))==2
            is_basic = ctype_list.count("Basic")==1
            #omitting reserve lists and basic lands since one is arbitrarily low and basic lands are considered free
            if is_reserved==False and is_basic == False:
                try:
                    camount = self.get_times_printed(url, cname)
                except:
                    camount = 1
                op.append(cname)
                op.append(ccost_list)
                op.append(ctype_list)
                op.append(crules)
                op.append(crarity)
                op.append(cprice)
                op.append(cstats)
                op.append(camount)
                op.append(clegality)
                op.append(cpricetx)
        return op
            
    
    
    def pull_set(self, url):
        resp = requests.get(url)
        if resp.status_code==200:
            x = resp.text
            soup = BS(x, 'html.parser')
            date_released = soup.find("p", {"class","set-header-title-subline"}).text.split()[-1]
        
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

                        self.df.loc[cdata[0]] = {'Name': cdata[0],'Mana Cost':cdata[1], 
                                                 'Type':cdata[2], 'Rules Text':cdata[3], 
                                                 'Rarity':cdata[4], 'Price (USD)':cdata[5], 
                                                 'stats':cdata[6], 'times printed':cdata[7], 
                                                 "Date":date_released, "Legality":cdata[8], 
                                                 "Price (tix)":cdata[9]}
                    else:
                        self.df.loc[cdata[0]] =  {'Name': cdata[0],'Mana Cost':cdata[1], 
                                                 'Type':cdata[2], 'Rules Text':cdata[3], 
                                                 'Rarity':cdata[4], 'Price (USD)':cdata[5], 
                                                 'stats':cdata[6], 'times printed':cdata[7], 
                                                 "Date":date_released, "Legality":cdata[8], 
                                                 "Price (tix)":cdata[9]}
    
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
                if ncards>150 and sname.find("Promo")==-1 and sname.find("Historic")==-1 and sname.find("Tokens")==-1 and sname.find("Cube")==-1 and sname.find("Arena")==-1 and sname.find("Alchemy")==-1 and sname.find("Secret Lair")==-1:
                    try:
                        self.pull_set(url)
                    except:
                        print("failed" + url)
        
                
    def __init__(self):
        self.df = pd.DataFrame(columns={'Name','Mana Cost', 'Type', 'Rules Text', 'stats', 'Rarity', 'Price (USD)','Price (tix)', 'times printed', 'Date',"Legality"})
        self.df.set_index('Name')
        #self.pull_sets()
        
        
dataset = mtg_df()
#df.df.to_csv("out.csv")
