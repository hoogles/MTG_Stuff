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





#Data structure
'''
Its a vector because thats the easiest way to do it. 
We got speed,
keywords
how it actiavtes
what it does
who it effects
ie who what when where how (the why is win the game)
size is [speed, keywords, effects, targets, trigger]
'''
class card_reader:





###############################################################################
#                                  Effects                                    #
###############################################################################
    def plusplus(self, x):
        n = 0
        m =0
        try:
            
            n = re.findall("\+(.)\/",x.lower())[0]
            m = re.findall("\/\+(.)",x.lower())[0]
        except:
            n=0
        try:
            n = int(n)
        except:
            n = 1
        try:
            m= int(m)
        except:
            m= 1       
        return [int(n),int(m)]
    def minusminus(self, x):
        n = 0
        m =0
        try:
            
            n = re.findall("\-(.)\/",x.lower())[0]
            m = re.findall("\/\-(.)",x.lower())[0]
        except:
            n=0
        
        try:
            n = int(n)
        except:
            n = 10
        try:
            m= int(m)
        except:
            m= 10
        return [int(n),int(m)]
    
    def life_gain(self, x):
        n = 0
        try:
            n = re.findall ("gain (.*) life", x.lower())[0].split()[-1]
            n = text2int(n)
        except:
            n = 0
        
        return int(n)
    
    def life_loss(self, x):
        
        n = 0
        try:
            n = re.findall ("lose (.*) life", x.lower())[0].split()[-1]
            n = text2int(n)
        except:
            n = 0    
        return int(n)
    
    def get_draw(self, x):
        n = 0
        try:
            n = re.findall("draw (.*) card",x.lower())[0]
            if n=="a" or n=="x":
                n = 1
            elif len(n)>1:
                n = text2int(n)
            
        except:
            n = 0
        return int(n)
    
    def search_lib(self, x):
        n = 0
        try:
            n = re.findall("search (.*?) library",x.lower())[0]
            n = 1
        except:
            n=0
        return int(n)
    
    def landintxt(self, x):
        
        return "forest" in x.lower() or "mountain" in x.lower() or "swamp" in x.lower() or "island" in x.lower() or "plains" in x.lower() or "land" in x.lower()  
        
    
    def land_cheat(self, x):
        n = 0
        try:
            #y = re.findall("play an additional land", x.lower())[0]
            
            a = "additional land" in x.lower()
            b = self.landintxt( x) and "onto the battlefield tapped" in x.lower()
            n = a or b
        except:
            n =0
        
        return n
    
    def damage_effect(self, x):
        
        n=0
        
        try:
            n = int(re.findall("deals (.*?) damage", x.lower())[0])
        except:
            n = 0
        return n
    
    def discard_effect(self, x):
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
    
    def sacrifice_effect(self, x):
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
                eff = re.findall("sacrifices (.*?) perm",x.lower())
                if len(eff)>0:
                    eff =eff[0]
                    if "a" in eff:
                        n=1
                    elif "x" in eff or "half" in eff or "those" in eff:
                        n = 10
                    
                    else:
                        
                        n = text2int(eff)           
                else:
                    n=0
        
        return n
    
    
    def create_tokens(self, x):
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
    
    def add_mana(self, x):
        n = 0
        eff = re.findall("add (.*?) mana",x.lower())
        if len(eff)>0 or "add {" in x.lower():
            n=1
            if "{" in x:
                #count sequential { 
                eff = re.findall("add \{(.*)\}",x.lower())
                if len(eff)>0:
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
        
    def reduce_cost(self, x, cost):
        n=0
        y = x.lower().replace("costs ","cost ")
        eff = re.findall("cost \{(.)\} less", y)
        try:
            if len(eff)>0:
                if eff[0]=="x":
                    n = cost
                else:
                    n=int(eff[0])
        except:
            n=0
        return n
    def increase_cost(self, x):
        n=0
        y = x.lower().replace("costs ","cost ")
        eff = re.findall("cost \{(.)\} more", y)
        if len(eff)>0:
            try:
                n=int(eff[0])
            except:
                n=len(eff[0])
        if n==0:
            
            eff = re.findall("pay \{(.)\}",y)
            if len(eff)>0:
                try:
                    n=int(eff[0])
                except:
                    n=len(eff[0])
           
        return n
    
    def destroy(self, x):
        n=0
        y = x.lower().replace("up to","")
        y = y.replace("any number of", "all")
        y = y.replace("target", "one")
        y=y.replace("each", "all")
        all_num = 15 #arbitrary rn need to calculate average number or change something
        if "destroy" in y:
            n = 1
            eff = re.findall("destroy (.*?) ",y)
            
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
    
    def exile(self, x):
        n=0
        y = x.lower().replace("up to","")
        y = y.replace("any number of", "all")
        y = y.replace("target", "one")
        y=y.replace("each", "all")
        all_num = 15 #arbitrary rn need to calculate average number or change something
        if "exile" in y:
            n = 1
            eff = re.findall("exile (.*?) ",y)
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
    
    
    def counter_spell(self, x):
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
    def no_counter(self,x):
        return " be countered" in x.lower()
    def rez(self, x):
        return " from a graveyard onto the battlefield" in x.lower()
    
    def bounce(self, x):
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
    
    def x_turn(self, x):
        
        eff = re.findall("extra turn", x.lower())
        n = len(eff)>0
        if "extra turns"in x.lower():
            eff = re.findall("take (.*?) extra turns",x.lower())
            for i in eff:
                try:
                    n += text2int(i)
                except:
                    n=1 
            
        
        
        return n
    
    def end_turn(self, x):
        return "end the turn" in x.lower()
    
    def copy_perm(self, x):
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
    
    def copy_spell(self, x):
        n=0
        if "storm" in x.lower():
            n=3
        eff = re.findall("copy target (.*?) spell",x.lower())
        for i in eff:
            n+=1
        return n
    
    def counters(self, x):
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
    
    def mill(self, x):
        n = 0
        eff = re.findall("mill(.*?) card", x.lower())
        for i in eff:
            try:
                n += text2int(i)
            except:
                n+=1
        return n
    
    def win(self, x):
        return "win the game" in x.lower()
    
    def lose(self, x):
        return "lose the game" in x.lower()
    
    def tap(self, x):
        
        return "tap" in x.lower().split() or "tapped" in x.lower().split()
    
    def untap(self, x):
        
        return "untap" in x.lower().split() or "untapped" in x.lower().split()
    
    def wish(self, x):
        
        return "outside the game" in x.lower()
    def cheat_out(self, x):
       
        n = int("without paying" in x.lower())
        eff = re.findall("put (.*?) onto the battlefield", x.lower())
        n+=len(eff)
        
        return n
    
    def doubling(self, x):
        n  = len(re.findall("double", x.lower())) + len(re.findall("twice",x.lower()))
        
        return n
    
    def halving(self, x):
        
        return len(re.findall("half", x.lower())) 
    
    def flicker(self, x):
        substr = "exile (.*?) return (.*?) to the battlefield"
        
        return len(re.findall(substr, x.lower()))
    
    def unblock(self, x):
        
        return ("unblock" in x.lower() or "can’t be blocked" in x.lower()) or "can’t block" in x.lower()
    
    def extrastep(self, x):
        
        return "additional" in x.lower() and "phase" in x.lower()
    
    def stax(self, x):
        #n = int("opponents can’t" in x.lower() or "player's can’t" in x.lower())
        return "can’t" in x.lower() and "prevent" not in x.lower() 
    
    def no_hand_limit(self, x):
        return "hand limit" in x.lower()
    
    def steal(self, x):
        return int("gain control" in x.lower())
    ###############################################################################
    #                             end of effects                                  #
    ###############################################################################
    
    ###############################################################################
    #                             start of triggers                               #
    ###############################################################################
    def on_cast(self, x):
        eff = re.findall("whenever (.*?) cast",x.lower())
        return len(eff)>0
    
    
    def magecraft(self, x):
        eff = re.findall("whenever (.*?) copy", x.lower())
        return len(eff)>0 
    
    def on_etb(self, x):
        eff = re.findall("when (.*?) enters the battlefield",x.lower()) + re.findall("whenever (.*?) enters the battlefield",x.lower())
        return len(eff)>0
    
    def on_death(self, x):
        eff = re.findall("when (.*?) dies",x.lower()) + re.findall("whenever (.*?) dies",x.lower())
        eff +=  re.findall("when (.*?) destroy",x.lower()) + re.findall("whenever (.*?) destroy",x.lower())
        return len(eff)>0 or "afterlife" in x.lower()
    
    def on_discard(self, x):
        n = int("madness" in x.lower())
        n += len(re.findall("when(.*?) discard",x.lower()))
        return n>0
    
    def on_exile(self, x):
        eff = re.findall("when (.*?) exile",x.lower()) + re.findall("whenever (.*?) exile",x.lower())
        return len(eff)>0
    
    def on_draw(self, x):
        eff = re.findall("whenever (.*?) draw",x.lower())
        return len(eff)>0
    
    #might ommit this one, yo can just say "its a PW"
    def loyalty(self, x):
        eff = re.findall("\+.\:", x.lower()) + re.findall("\+.\:", x.lower())
        return len(eff)>0
    
    def passive(self, x):
        when = "when" in x.lower()
        colon = ":" in x
        eot = "end of turn" in x.lower() 
        uk = "at the begin" in x.lower() 
        return not when and not colon and not eot and not uk
    
    def activatable(self, x):
        return ":" in x
    
    def second_spell(self, x):
        
        return "second spell" in x.lower()
    
    #note to self, do better with names
    def on_cost(self, x):
        eff1 = "kicked" in x.lower()
        eff2 = "may pay" in x.lower()
    
        return eff1 or eff2
    
    def on_life_gain(self, x):
        eff = re.findall("when (.*?) gain life",x.lower()) + re.findall("whenever (.*?) gain life",x.lower())
        return len(eff)>0
    
    def on_life_loss(self, x):
        eff1 = "if an opponent lost life" in x.lower()
        eff = re.findall("when (.*?) damage" , x.lower()) + re.findall("whenever (.*?) damage" , x.lower())
        eff2 =  re.findall("life (.*?) lost",x.lower())
        eff += eff2
        #eff = eff2
        return len(eff)>0 or eff1
    
    def on_attack(self, x):
        eff = re.findall("when (.*?) attack",x.lower()) + re.findall("whenever (.*?) attack",x.lower())
        return len(eff)>0
    
    def on_step(self, x):
        abo = "at the beginnning of" in x.lower()
        during = "during" in x.lower()
        step = "step" in x.lower()
        return abo or during or step 


 ###############################################################################
 #                             end of triggers                                 #
 ###############################################################################



 ###############################################################################
 #                             start of targets                                #
 ###############################################################################

    def target_self(self, x):
        return "you" in x.lower()



    def target_spell(self, x):
        return "target spell" in x.lower()

    def target_permanent(self, x):
        n = [0]*5
        x =  x.lower().replace("each", "all")
        if "all" in x.lower() or "target" in x.lower():
            if "permanent" in x.lower().split():
                for i in range(len(n)):
                    n[i] = 1
                if "nonland" in x.lower().split():
                    n[4] =0
                        
            elif "artifact" in x.lower().split():
                n[0] = 1
            elif "creature" in x.lower().split():
                n[1] = 1
            elif "creature" in x.lower().split():
                n[2] = 1
            elif "planeswalker" in x.lower().split():
                n[3] =1    
            elif "land" in x.lower().split():
                n[4] =1  
        
        return n

    def numtargets(self, x):
        n = 0
        x = x.lower().replace("each", "all")
        if "target" in x.lower():
            n =1
        elif "all" in x.lower():
            n = 2
        return n
    

###############################################################################
#                             end of targets                                  #
###############################################################################


       
    #so this is a bug with spyder or something
    def get_condition(self, card):
        condi = None
        if card["Type"]=="Sorcery" or card["Type"]=="Instant":
            condi = 0 #on cast
        else:
            #now it gets much MUCH harder, permanents can have several abilkities with several conditions
            condi =1
        
        return condi
        


    def addi_cost(self, x):
        cost = 0 
        if "As an additional cost to cast this spell" in x:
            
            #cost = regex("As an additional cost to cast this spell\,(.*?)\.") #not legal fix psudocode
            cost  = re.findall("As an additional cost to cast this spell\,(.*?)\.", x)
        elif ":" in x:
            cost = [re.findall("(.*?):",x)[0]]+re.findall("\.(.*?):",x)
        else:
            cost = 0        
        return cost
    
    def speed(self, x, ctype):
        speed = 0
        if  "Instant" in ctype: 
            speed = 1
            if "split second" in x.lower():
                speed = 2
        else:
            if "flash" in x.lower().split():
                speed = 1
            if "activate only as a sorcery" in x.lower():
                speed = 0
        
        return speed  
    
    
    def __init__(self, card):
        key_words= ["Deathtouch","Defender","Double Strike", "First Strike", "Flash", "Flying", "Haste",
        "Hexproof", "Indestructible", "Lifelink","Menace", "Protection", "Prowess","Reach", "Trample","Vigilance",
        "Infect","Changeling", "Delve","Manifest","Morph", "Suspend", "Shroud"]

        self.rules = card["Rules Text"].split(". ")
        self.translated = [0]*90
        self.translated[-1] = len(self.rules) -1
        spd = self.speed( card["Rules Text"], card["Type"])
        self.translated[0] += spd
        for i in range(len(self.rules)-1):
            x = self.rules[i]
            for j in range(len(key_words)):
                kw = key_words[j]
                self.translated[j+1] += int(kw in x)
            pp =self.plusplus(x)
            self.translated[24] += int(pp[0]+pp[1])
            mm =self.minusminus(x)
            self.translated[25] += int(mm[0]+mm[1])
            self.translated[26] += int(self.life_gain(x))
            self.translated[27] += int(self.life_loss(x))
            self.translated[28] += int(self.land_cheat(x))
            self.translated[29]  += int(self.get_draw(x))
            self.translated[30]  += int(self.search_lib(x))
            self.translated[31]  += int(self.damage_effect(x))
            self.translated[32]  += int(self.sacrifice_effect(x))
            self.translated[33]  += int(self.discard_effect(x))
            self.translated[34]  += int(self.create_tokens(x))
            self.translated[35]  += int(self.add_mana(x))
            
            try:
                card["Mana Cost"][0].sort()
                c = int(card["Mana Cost"][0])
            except:
                c=0
            self.translated[36]  += int(self.reduce_cost(x,c))
            self.translated[37]  += int(self.increase_cost(x))
            self.translated[38]  += int(self.destroy(x))
            self.translated[39]  += int(self.exile(x))
            self.translated[40]  += int(self.counter_spell(x))
            self.translated[41]  += int(self.no_counter(x))
            self.translated[42]  += int(self.x_turn(x))
            self.translated[43]  += int(self.end_turn(x))
            self.translated[44]  += int(self.win(x))
            self.translated[45]  += int(self.lose(x))
            self.translated[46]  += int(self.rez(x))
            self.translated[47]  += int(self.bounce(x))
            self.translated[48]  += int(self.copy_perm(x))
            self.translated[49]  += int(self.copy_spell(x))
            self.translated[50]  += int(self.counters(x))
            self.translated[51]  += int(self.mill(x))
            self.translated[52]  += int(self.tap(x))
            self.translated[53]  += int(self.untap(x))
            self.translated[54]  += int(self.wish(x))
            self.translated[55]  += int(self.cheat_out(x))
            self.translated[56]  += int(self.doubling(x))
            self.translated[57]  += int(self.halving(x))
            self.translated[58]  += int(self.extrastep(x))
            self.translated[59]  += int(self.steal(x))
            self.translated[60]  += int(self.flicker(x))
            self.translated[61]  += int(self.unblock(x))
            self.translated[62]  += int(self.stax(x))
            self.translated[63]  += int(self.no_hand_limit(x))
            self.translated[64]  += int(self.on_cast(x))
            self.translated[65]  += int(self.magecraft(x))
            self.translated[66]  += int(self.on_etb(x))
            self.translated[67]  += int(self.on_death(x))
            self.translated[68]  += int(self.on_discard(x))
            self.translated[69]  += int(self.on_draw(x))
            self.translated[70]  += int(self.on_exile(x))
            self.translated[71]  += int(self.loyalty(x))
            self.translated[72]  += int(self.passive(x))
            self.translated[73]  += int(self.activatable(x))
            self.translated[74]  += int(self.second_spell(x))
            self.translated[75]  += int(self.on_cost(x))
            self.translated[76]  += int(self.on_life_gain(x))
            self.translated[77]  += int(self.on_life_loss(x))
            self.translated[78]  += int(self.on_attack(x))
            self.translated[79]  += int(self.on_step(x))
            self.translated[80]  += int(self.target_self(x))
            self.translated[81]  += int(self.target_spell(x))
            #self.translated[82]  += int(self.target_permanent(x))
            perm = self.target_permanent(x)
            self.translated[82]  += perm[0]
            self.translated[83]  += perm[1]
            self.translated[84]  += perm[2]
            self.translated[85]  += perm[3]
            self.translated[86]  += perm[4]
            self.translated[87] += int("graveyard" in x.lower().split())
            self.translated[88] = self.numtargets(x)

        return None
