# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 12:52:45 2022

@author: Hart
"""
"""
List of keywords:
    Deathtouch
    Defender
    Double Strike
    First Strike
    Flash
    Flying
    Haste
    Hexproof
    Indestructible
    Lifelink
    Menace
    Protection
    Prowess
    Reach
    Trample
    Vigilance
    Infect
    Changeling
    Delve
    Manifest
    Morph
    

List of things to check:
    +x/+x 
    -x/-x 
    gain life
    lose life
    draw x cards
    search library
    put land on
    damage
    discard
    sacrifice
    tokens
    add mana
    reduce cost
    increase cost
    exile
    counter
    reanimate 
    bounce
    extra turn
    end turn
    clone
    copy
    counters
    mill
    win the game
    lose the game
    tap
    untap
    destroy
    exile
    wish effect
    put on to battlefield from hand
    doubling effects
    halving effects
    flicker
    cant be blocked
    target vs all 
    opponent vs you
    hand limit
    extra steps
    denial effects like that asshole white card from Ikoria. Drannith Magistrate.
    cant be regenerated
    
For permanents I need to check the when effect triggers. 
List of triggers:
    on cast
    other cast
    copy
    mana cost
    tap
    sacrifice
    life gain
    life loss
    death
    etb
    remove a counter
    add counter
    discard
    exile
    exile top card, play it
    ignore mana cost
    during step
    attack
    damage
    passive effect
    loyalty
    second spell
    lesser stuff like the raccoon barrell
    additional costs... ugh
    
Finally targets
    for all, none, you control and opponent controls
    creature
    artifact
    planeswalker
    enchantment
    player
    
Also need to determine Speed


Ignoring jank effects like Aeon Engine or draft stuff 
"""
import re 
#https://stackoverflow.com/questions/493174/is-there-a-way-to-convert-number-words-to-integers thank you 
def text2int(textnum, numwords={}):
    if not numwords:
      units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]

      tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

      scales = ["hundred", "thousand", "million", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current


key_words= ["Deathtouch","Defender","Double Strike", "First Strike", "Flash", "Flying", "Haste",
    "Hexproof", "Indestructible", "Lifelink","Menace", "Protection", "Prowess","Reach", "Trample","Vigilance",
    "Infect","Changeling", "Delve","Manifest","Morph", "Suspend", "Shroud"]



###############################################################################
#                                  Effects                                    #
###############################################################################
def plusplus(x):
    n = 0
    m =0
    try:
        
        n = re.findall("\+(.)\/",x.lower())[0]
        m = re.findall("\/\+(.)",x.lower())[0]
    except:
        n=0
    
    return [int(n),int(m)]
def minusminus(x):
    n = 0
    m =0
    try:
        
        n = re.findall("\-(.)\/",x.lower())[0]
        m = re.findall("\/\-(.)",x.lower())[0]
    except:
        n=0
    
    return [int(n),int(m)]

def life_gain(x):
    n = 0
    try:
        n = re.findall ("gain(.*) life", x.lower())[0].split()[-1]
    except:
        n = 0
    
    return int(n)

def life_loss(x):
    
    n = 0
    try:
        n = re.findall ("lose(.*) life", x.lower())[0].split()[-1]
    except:
        n = 0    
    return int(n)

def get_draw(x):
    n = 0
    try:
        n = re.findall("draw (.*) card",x.lower())[0]
        if n=="a":
            n = 1
        elif len(n)>1:
            n = text2int(n)
        
    except:
        n = 0
    return int(n)

def search_lib(x):
    n = 0
    try:
        n = re.findall("search (.*?) library",x.lower())[0]
        n = 1
    except:
        n=0
    return int(n)

def landintxt(x):
    
    return "forest" in x.lower() or "mountain" in x.lower() or "swamp" in x.lower() or "island" in x.lower() or "plains" in x.lower() or "land" in x.lower()  
    

def land_cheat(x):
    n = 0
    try:
        #y = re.findall("play an additional land", x.lower())[0]
        
        a = "additional land" in x.lower()
        b = landintxt(x) and "onto the battlefield tapped" in x.lower()
        n = a or b
    except:
        n =0
    
    return n

def damage_effect(x):
    
    n=0
    
    try:
        n = int(re.findall("deals (.*?) damage", x.lower())[0])
    except:
        n = 0
    return n

def discard_effect(x):
    n = 0
    
    try:
        eff = re.findall("discard(.*?) card",x.lower())[0]
        n =1 #at minimum
        if "hand" in eff:
            n = 7 #max handsize
        else:
            try:
                n = int(text2int(eff.split()[-1]))
            except:
                n=1
        
    except:
        n=0
    return n

def sacrifice_effect(x):
    n=0
    try:
        if "sacrifice" in x.lower():
            n = 1
            eff = re.findall("sacrifices (.*?) creature",x.lower())[0]
            if "a"==eff:
                n=1
            elif "x" in eff or "half" in eff:
                n = 10
            else:
                n = text2int(eff)
    except:
        if "sacrifice" in x.lower():
            n = 1
            eff = re.findall("sacrifices (.*?) perm",x.lower())[0]
            if "a"==eff:
                n=1
            elif "x" in eff or "half" in eff:
                n = 10
            else:
                n = text2int(eff)           
    
    return n


def create_tokens(x):
    n=0
    
    if "token" in x.lower():
        n=1
        try:
            y = x.lower()
            y = y.replace("put a", "create") #cover errataed effects
            y = y.replace("puts", "create")
            
            eff = re.findall("create (.*?) token",y)[0]
            n2 = eff.split()
            if  "x" in n2 or "number" in eff:
                n= 5
            elif n2[0] == "a":
                n=1
            else:
                n= text2int(n2[0])
        except:
            n=1
    
    return n

def add_mana(x):
    n = 0
    eff = re.findall("add (.*?) mana",x.lower())
    if len(eff)>0 or "add {" in x.lower():
        n=1
        if "{" in x:
            #count sequential { 
            eff = re.findall("add \{(.*)\}",x.lower())[0]
            n=0
            for i in eff:
                if i !="{" and i!="}":
                    try:
                        n+=int(i)
                    except:
                        n+=1
            
        else:
            try:
                
                y = eff[0][0]
                if y=="s":
                    y == eff[0][1]
                
                n = text2int(y)
            except:
                n = 1 #TODO make this accruate
        
    return n
    
def reduce_cost(x):
    n=0
    y = x.lower().replace("costs ","cost ")
    eff = re.findall("cost \{(.)\} less", y)
    if len(eff)>0:
        n=int(eff[0])
    
    return n
def increase_cost(x):
    n=0
    y = x.lower().replace("costs ","cost ")
    eff = re.findall("cost \{(.)\} more", y)
    if len(eff)>0:
        n=int(eff[0])
    if n==0:
        eff = re.findall("pay \{(.)\}",y)
        n= int(eff[0])
    return n

def destroy(x):
    y = x.lower().replace("up to","")
    y = y.replace("any number of", "all")
    y = y.replace("target", "one")
    y=y.replace("each", "all")
    all_num = 15 #arbitrary rn need to calculate average number or change something
    if "destroy" in y:
        n = 1
        eff = re.replace("destroy (.*?) ",y)
        
        #if all
        if "all" in eff or "overload" in x:
            n= all_num
        else:
            try:
                n =0
                for i in eff:
                    n += text2int(i)
            except:
                n=1
    return n

def exile(x):
    y = x.lower().replace("up to","")
    y = y.replace("any number of", "all")
    y = y.replace("target", "one")
    y=y.replace("each", "all")
    all_num = 15 #arbitrary rn need to calculate average number or change something
    if "exile" in y:
        n = 1
        eff = re.replace("exile (.*?) ",y)
        if "return" in x.lower():
            n = -1
        #if all
        elif "you may cast" in x.lower():
            n=-2
        elif "all" in eff or "overload" in x:
            n= all_num
        
        else:
            try:
                n =0
                for i in eff:
                    n += text2int(i)
            except:
                n=1
    return n


def counter_spell(x):
    n=0
    
    eff = re.findall("counter (.*?) spell", x.lower())
    for i in eff:
        if i=="target":
            n += 2
        else:
            n+=1
            
    eff = re.findall("counter (.*?) ability", x.lower())
    for i in eff:
        if i=="target":
            n += 2
        else:
            n+=1    
    return n

def rez(x):
    return " from a graveyard onto the battlefield" in x.lower()

def bounce(x):
    n=0
    eff = re.findall("return (.*?) to it", x.lower())
    for i in eff:
        if "creature" in i:
            n+=1
        elif "nonland" in i:
            n+=2
        elif "permanent" in i:
            n+=3
    return n

def x_turn(x):
    
    eff = re.findall("extra turn", x.lower())
    n = len(eff)>0
    if "extra turns"in x.lower():
        eff = re.findall("take (.*?) extra turns")
        for i in eff:
            try:
                n += text2int(i)
            except:
                n=1 
        
    
    
    return n

def end_turn(x):
    return "end the turn" in x.lower()

def copy_perm(x):
    n=0
    
    
    eff = re.findall("copy (.*?) creature",x.lower())
    n += len(eff)
    eff = re.findall("copy (.*?) artifact",x.lower())
    n += len(eff)
    eff = re.findall("copy (.*?) enchantment",x.lower())
    n += len(eff)    
    eff = re.findall("copy (.*?) planeswalker",x.lower())
    n += len(eff)       
    
    
    
    return n

def copy_spell(x):
    n=0
    if "storm" in x.lower():
        n=3
    eff = re.findall("copy target (.*?) spell",x.lower())
    for i in eff:
        n+=1
    return n

def counters(x):
    n=0
    y= x.lower().replace("a","one")
    if "proliferate" in y:
        n+=1
    eff = re.findall("put (.*) counter",y)    
    for i in eff:
        try:
            j = i.split()
            i+=text2int(j[0])
        except:
            n+=1
            
    return n

def mill(x):
    n = 0
    eff = re.findall("mill(.*?) card", x.lower())
    for i in eff:
        try:
            n += text2int(i)
        except:
            n+=1
    return n

def win(x):
    return "win the game" in x.lower()

def lose(x):
    return "lose the game" in x.lower()

def tap(x):
    
    return "tap" in x.lower().split() or "tapped" in x.lower().split()

def untap(x):
    
    return "untap" in x.lower().split() or "untapped" in x.lower().split()

def wish(x):
    
    return "outside the game" in x.lower()
def cheat_out(x):
   
    n = int("without paying" in x.lower())
    eff = re.findall("put (.*?) onto the battlefield", x.lower())
    n+=len(eff)
    
    return n

def doubling(x):
    n  = len(re.findall("double", x.lower())) + len(re.findall("twice",x.lower()))
    
    return n

def halving(x):
    
    return len(re.findall("half", x.lower())) 

def flicker(x):
    substr = "exile (.*?) return (.*?) to the battlefield"
    
    return len(re.findall(substr, x.lower()))

def unblock(x):
    
    return ("unblock" in x.lower() or "can’t be blocked" in x.lower()) or "can’t block" in x.lower()

def extrastep(x):
    
    return "additional" in x.lower() and "phase" in x.lower()

def stax(x):
    #n = int("opponents can’t" in x.lower() or "player's can’t" in x.lower())
    return "can’t" in x.lower() and "prevent" not in x.lower() 

def no_hand_limit(x):
    return "hand limit" in x.lower()
###############################################################################
#                             end of effects                                  #
###############################################################################

###############################################################################
#                             start of triggers                               #
###############################################################################


###############################################################################
#                             end of triggers                                 #
###############################################################################



###############################################################################
#                             start of targets                                #
###############################################################################


###############################################################################
#                             end of targets                                  #
###############################################################################


def get_condition(card):
    condi = None
    if card["Type"]=="Sorcery" or card["Type"]=="Instant":
        condi = 0 #on cast
    else:
        #now it gets much MUCH harder, permanents can have several abilkities with several conditions
        condi =1
    
    return condi

def addi_cost(x):
    cost = 0 
    if "As an additional cost to cast this spell" in x:
        
        #cost = regex("As an additional cost to cast this spell\,(.*?)\.") #not legal fix psudocode
        cost  = re.findall("As an additional cost to cast this spell\,(.*?)\.", x)
    elif ":" in x:
        cost = [re.findall("(.*?):",x)[0]]+re.findall("\.(.*?):",x)
    else:
        cost = 0        
    return cost


def speed(x, ctype):
    speed = 0
    if ctype =="Instant": 
        speed = 1
    else:
        if "Flash" in x:
            speed = 1
        if "Activate only as a sorcery" in x:
            speed = 0
    return speed


class card_reader:
    
    
    
    def __init__(self):
        
        
        return 0
