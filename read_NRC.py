# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 20:23:09 2018

@author: rcxsm
"""

# with help of https://www.dataquest.io/blog/web-scraping-beautifulsoup/


import os
import re
import time
import webbrowser
from urllib.request import urlopen  # python3
from bs4 import BeautifulSoup

def parsepagina (url):
    '''Lets parse the page'''
    try:
        page =  urlopen(url)
    except:
        print ("geef een geldige URL")
        quit()
    # parse the html using beautiful soup and store in variable `soup`
    soup = BeautifulSoup(page, 'html.parser')
    if "nrc" in url:
        search1 = soup.find_all('h1', attrs={'data-flowtype':'headline'})
        titel = re.sub(r'[\\/*?:\'",.<>|]',"",str(search1))
        search1 +=  soup.find_all('div', attrs={'class':'article__intro'})
        search1 += soup.find_all('div', attrs={'class':'article__content'})

    elif "volkskrant" in url:
        search1 = soup.find_all('h1', attrs={'class':'artstyle__header-title'})
        titel = re.sub(r'[\\/*?:\'",.<>|]',"",str(search1))
       

        
        search1 += soup.find_all('div', attrs={'class':'block-content'})

    else:
        print ("Geef een link van NRC of Volkskrant")
        quit()

    if not search1 is None:
        print (search1)
        seconds = str(int(time.time()))
        path = os.path.abspath('NRC_Volkskrant'+ titel + seconds + '.html')
        url = 'file://' + path
        with open(path, 'w') as f:
            f.write(str(search1))
        webbrowser.open(url)
    else:
        print ('NO entry found')
        # sys.exit()

def main():
    '''Lets start'''
    url0 = input ("Geef een URL : ")
    parsepagina(url0)

main()
