# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 22:08:53 2019

@author: rcxsm
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 20:23:09 2018

@author: rcxsm
"""

# with help of https://www.dataquest.io/blog/web-scraping-beautifulsoup/

# import libraries
from urllib.request import Request, urlopen #python3
from bs4 import BeautifulSoup
import sys
import os, time, csv
from datetime import datetime

import pandas as pd

def parsepagina (url, t):
    
   
    # Workbook is created / add_sheet is used to create sheet.
    
    #wb = Workbook() 

    #sheet1 = wb.add_sheet('Sheet 1')   
    #sheet1 = wb.sheet_by_index(0)
   
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
              
    page =  urlopen(req).read() 
    page_html = BeautifulSoup(page, 'html.parser') 
    mv_containers = page_html.find_all('div', class_ = 'comment__body')
    print (mv_containers)
    
    
            
def main():
    #url0 = 'https://www.zoover.nl/italie/lazio-latium/rome/village-fabulous/camping'
    #url0='https://www.happycow.net/reviews/goodsouls-kitchen-chiang-mai-107183'
    url0="https://www.happycow.net/reviews/reform-kafe-chiang-mai-84403"
    parsepagina(url0, 1)
    
main()

