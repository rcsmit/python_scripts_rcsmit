# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 11:03:02 2019

@author: rcxsm
"""
import random
import sys

stenen=[]
pot=0

posities= [ False, False, False, False, False]
tactiek = [1,5,1,5,3,3]     # wanneer geef je de beurt door? Als x stenen op het bord liggen.
                            # van 1 tot 5, hoe hoger, hoe riskanter het spel 
                            # 9 is als je random speelt
aantalkeergewonnen = []
gewonnenpercentages = []
stenen.clear()
aantalstenenaanheteind = []
aantalspelers = 6
totaalaantalstenen = 60
aantalspelletjes = 1000
stenenperspeler = totaalaantalstenen/aantalspelers
for n in range (0, aantalspelers):
    stenen.append (stenenperspeler)
    aantalkeergewonnen.append (0)
    gewonnenpercentages.append(0)
    aantalstenenaanheteind.append(0)
    #stenen [n] = stenenperspeler

aantalrondes = 1
aantalbeurten=1
aantalkeergegooid = 0
totaantalkeergegooid = 0
beurt = 0
wieisaandebeurt = 0
beginner = 999 # 99 - random beginner, andere waarde speler 1
aantalstenenophetbord = 0
pot = 0
xxx=4
if xxx==2: 
    print ("aantal spelers")
    print (aantalspelers)
    print (stenenperspeler)
    print (stenen)
    print ("HERE WE GO")

def wiemagbeginnen():
      return (random.randint(0,aantalspelers-1))
      
      
def spelen (wieisaandebeurt):
    global  aantalrondes, beurt, aantalstenenophetbord, pot, aantalbeurten, aantalkerenspelen, aantalkeergegooid,xxx, gewonnenpercentages, aantalbeurten
    speler = wieisaandebeurt
    spelerx = speler + 1
    
    
    #print ("het bord")
    #print (posities)
    
    if xxx==2: 
        print ("===========================")
        print ("SPEL NUMMER "+ str(aantalkerenspelen))
        print ("WORP NUMMER "+ str(aantalkeergegooid))
        print ("BEURT NUMMER "+ str(aantalbeurten))
        print ("RONDE NUMMER "+ str(aantalrondes))
        print ("de beurt is aan " + str(spelerx))
        print ("zijn tactiek is " + str(tactiek[speler]))
          
        print ("stenen per speler " + str(stenen))
        print ("aantal stenen op het bord "+ str(aantalstenentellen()))
        print ("aantal stenen in de pot "+ str(pot))
        
        print (posities)
        print ("------------------")
      
    #voorkomen dat het spelletje eeuwig doorgaat
    if aantalbeurten == 200000:
        sys.exit()
    
    volgendeaandebeurt = speler + 1
             
    #speler rolt dobbelsteen
    number = random.randint(0,5)
    gegooid = number + 1 
    aantalkeergegooid=aantalkeergegooid+1
    
    #number = 1
    if xxx==2:
        print("Speler "+ str(spelerx) + " heeft " + str(gegooid) + " gegeooid")
    #als het zes is: steen gaat in de pot
    if number == 5:
        pot = pot + 1
        stenen [speler] = stenen [speler] - 1
        whattodo(speler)                
    else:
        #checken of de positie is bezet
        if posities[number] == True:
            #speler neemt alle stenen
            if xxx==2:
                print ("speler pakt alle stenen")
            for n in range (0,5):
                if posities[n] == True:
                    stenen [speler]=stenen [speler] +1    
                    posities[n]=False
            aantalstenenophetbord = 0
            #beurt wordt doorgegeven
            if xxx==2:
                print ("speler geeft beurt door")
            aantalbeurten=aantalbeurten+1
            spelen(wieisdevolgende(speler))         
        else:
            #speler plaatst steen
            posities [number]= True
            stenen [speler]= stenen [speler]-1  
            if xxx==2:
                print ("speler "+ str(spelerx) + " plaatst steen")
                print (posities)
            whattodo(speler)
            
def aantalstenentellen():     
#hoeveelstenenliggenophetbord
    aantalstenenophetbord = 0
    for n in range (0,5):
         if posities[n] == True:
             aantalstenenophetbord = aantalstenenophetbord + 1
    return (aantalstenenophetbord)
        
def tactiekbepalen(speler):
    spelerx = speler 
    
    t = tactiek[spelerx]
    if t ==9:
            t = random.randint(1,5)
    return (t)

def wieisdevolgende(speler):
    global  aantalrondes
    volgendeaandebeurt = speler + 1
    
    if (volgendeaandebeurt > (aantalspelers-1)) :
            volgendeaandebeurt = 0
            aantalrondes=aantalrondes+1
            
    return (volgendeaandebeurt)

def whattodo(speler):
        global  aantalrondes, beurt, aantalstenenophetbord, pot,aantalspelers,xxx, totaantalkeergegooid
        spelerx= speler+1
        aantalstenen = aantalstenentellen()
        txx=tactiekbepalen(speler)
       
        if  stenen [speler]> 0:     
            #: speler maakt beslissing aan de hand van aantal stenen dat er al op het bord staat
            if aantalstenen <= txx:
                #speler gooit nog een keer
                if xxx==2:
                    print ("speler gooit nog een keer // " + str(aantalstenen) + " op het bord - vs " + str(txx))
                spelen(speler)
            else:
                #speler geeft de beurt door
                if xxx==2:
                    print ("speler geeft beurt door // " + str(aantalstenen) + " vs " + str(txx))
                spelen(wieisdevolgende(speler))
      
        else:
            if xxx==2: 
                print ("===========================")
                print ("===========================")
                print ("einde spel")
                print ("WINNAAR "+ str(spelerx))
                print ("AANTAL KEER GEGOOID "+ str(aantalkeergegooid))
                
                print ("AANTAL BEURTEN "+ str(aantalbeurten))
                print ("AANTAL RONDES "+ str(aantalrondes))
                
            for n in range (0, aantalspelers):
                    aantalstenenaanheteind[n]=aantalstenenaanheteind[n]+stenen[n]
                
            aantalkeergewonnen[speler]=aantalkeergewonnen[speler]+1
            totaantalkeergegooid = totaantalkeergegooid + aantalkeergegooid
            #print (aantalkeergewonnen)
            # sys.exit("Error message")
            sys.exit
   
def aantalpercentages():
    global aantalkeergewonnen, gewonnenpercentages
    totaal=0
    for n in range (0,aantalspelers):
        totaal=totaal+aantalkeergewonnen[n]
        
    for m in range (0,aantalspelers):
        gewonnenpercentages[m]=round((aantalkeergewonnen[m]/totaal*100),3)
         
def reset():
    global  wieisaandebeurt, aantalrondes, beurt, aantalstenenophetbord, pot, aantalbeurten, aantalkeergegooid,xxx, aantalbeurten

    aantalrondes = 1
    aantalbeurten=1
    aantalkeergegooid = 0
    beurt = 0
    wieisaandebeurt = 0
    aantalstenenophetbord = 0
    pot = 0
    
    stenen.clear()
    
    for n in range (0, aantalspelers):
        stenen.append (stenenperspeler)
      

def main():

    for aantalkerenspelen in range (0, aantalspelletjes):
        if xxx==2: 
            print ("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            
            print (str(aantalkerenspelen))
            print ("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        reset()
        if beginner == 99:
            spelen(wiemagbeginnen())
        else:
            spelen(wieisaandebeurt)
    for n in range (0,aantalspelers):
        aantalstenenaanheteind[n]=round(aantalstenenaanheteind[n]/aantalkerenspelen)
     
    #EINDRAPPORTAGE
    aantalpercentages()
    print ("Aantal spelletjes                      " + str(aantalkerenspelen))
    print ("taktiek                                " + str((tactiek[:aantalspelers])))
    
    print ("Aantal keer gewonnen                   " + str (aantalkeergewonnen))
    print ("Gewonnen in %                          " + str(gewonnenpercentages))
   
        
    print ("Gemiddelde aantal stenen aan het eind  " + str(aantalstenenaanheteind))
    print ("Gemiddelde aantal keer gegooid         " + str(round(totaantalkeergegooid/aantalkerenspelen)))
main()