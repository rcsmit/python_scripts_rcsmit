# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 00:48:07 2020

@author: rcxsm
"""
import collections
from collections import Counter 

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

def Sorting(lst): 
    lst2 = sorted(lst, key=len, reverse=True) 
    print ("gesorteerd")
    return lst2 


def most_frequent(List): 
    occurence_count = Counter(List) 
    return occurence_count.most_common(1)[0][0] 


document = "meditation.txt"
textold = "dropthemosttempleoftemperatureofImakemistakestheEnglishword,droptheinnermosttempleoftemperaturegod,Imakemistakes,offerasknowledge,peacewithin.Ifyouarebeautiful.That'stotallyfine-sixoutnineoutnineeightandcomeintohispresence,ithadadistractionorburdensthatonemorepeacefullifemindinghispresence.Soiftheresomeotherstrongemotionsthatyou'redoingthisabilitytotheshoulderblades,thebreath.Angerislight,letyourwholebodyrecognizetheabilitytothetoesmove.TherhythmandequanimousmindapeacefulandIhavetheseareas.Thatisyourmindisgonnasound,touch,smellstastes,visionsandeverydaytodayyouletthestillnessforthesoftpalate,thebreathandhavereceivedandhonestlyandCenterthequestionaboutaboutyourself,thenhowcandoyourfreefromexternalnoisetherearestrong,youarebeingunhappyorgoofequanimityisconstantlyin-threeyearsofthoughtsthatasthoughyounoticethereisneverhearorGod.Doesn'titreallyunhappy,reallyimportanttobeok.Thankyou.Sometimeswecouldthinkofallbeingsofthingswithanyseedsofpain.Youcannotchangeofyouneedtorunawayfromassigninganyseedsofyourmindfocusedininwerecordedthechannelofthismeditation.Ihopeyoucanbeaquestionthattheyareseedeeplydownintotheinnerawarenessremaincalmandalongyourbody.Inthebeautifulexperiencethemindonearth-eightin-sixphasefourinthebreathasameditationit'snoisythingshappeningthroughouttimeyouknow,Iwearthem,letexhalationeachtime.Fascinatedagain,thereanyonelikeyouandknowingnessthatpersoninourfeelings,butwhenyoumightbeplaysureit'snoisysurroundings,badinthesameseated,poseandobserveitmoreenergyformyvoiceofpeacewithlove.Gentlyallowyourselfconnectedwithrealitysimplyobservethefeelingofwhoyoumindandallowthesolesoftrainingthenexttwointhesixinmindsteadilymakesitselfaround.Youmaynoticethereismuchformyownskin,astheheart,intothebreathsbackwardsfromthemindsisokay.Let'sseesomethingbigstorm,butwithadreadfulwayofthesternumdeeponthepurityandrestandbodyclearthechestsandbegincountingfromthestillness.I'mgonnasaytheheartandyourfieldoftiredness.Youmayalldownattheheartupmentallytellthemtocomeback.Noticetherhythm,theheart.Askyourselfgivingyourwholeworld.Whenyou'regoingonaniceandthenaskinthreein-sixphaseispermanentbridgetotheankles,thepathisalwaysthinkthey'rebeautiful,youtocultivate,what'sreallyupsetandyouknowitwaslookingforourlivesinsidethesignifierofthebreathnaturallyunfoldinginthis"
trump = open(document, encoding='utf8').read()
#corpus = ['drop', 'most']

corpus = trump.split()
corpus3= Sorting(corpus)

#print (corpus3)
print (len(corpus))

numberofwords=0
textnw = "# "
a=0
b=0
#print (corpus)
found = False
gevonden = []

def find_word (textold):
    global a, b, found, textnw, gevonden, i, x
    
    for i in corpus3:
        
        x = len(i)
        y = len (textold)
        if x > 3 :
                     
                
            if left(textold,x) == i:
                #print (i)
                gevonden.append(i)
                found = True
        
    #print (gevonden)
    #print (i)     
    
    if found == True:
        chooseword(textold)
    else:
        cut_letter(textold)
    
    #find_word(textold)

def chooseword(textold):
    global a, b, found, textnw, gevonden, i, x, numberofwords
    foundword= most_frequent(gevonden)    
    y = len(foundword)
    #print (gevonden)        
    textnw = "X" + foundword + " " + i
    #print (textnw)
    #print ("*")
    z = y-x 
    textold = right (textold, z)
    print (f"I chose {foundword}")
    found = True
    numberofwords+=1
    if numberofwords <4 :
        find_word(textold)
  
           
            
def cut_letter(textold):
    global a, b, found, textnw, gevonden, i, x
    z = (len(textold)-1)
    cutoff =left(textold,1)
    print (cutoff)
    textold = right(textold, z)
    find_word(textold)
            
            
        
find_word(textold)
        
        
print (textold)
print (textnw)

##index = corpus3.index('inner')
#print('The index of disney+ is:', index)
    