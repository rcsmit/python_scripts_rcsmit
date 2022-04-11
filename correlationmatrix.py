# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 12:07:40 2020

@author: rcxsm
"""


import pandas as pd
import numpy as np
import seaborn as sn
import matplotlib.pyplot as plt

#%matplotlib inline


#https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7444648/#!po=71.8750


# Use 2 decimal places in output display
pd.options.display.float_format = '{:.2f}'.format
# Don't wrap repr(DataFrame) across additional lines
pd.set_option("display.expand_frame_repr", False)

def read():
    filetype = 'csv'
    #file = 'C:\Users\rcxsm\Documents\pyhton_scripts'
    #sheet = 'Blad1'
    global df
    
    if filetype == 'csv':
        #adapted to the export of excel
        try:
            df = pd.read_csv(
                "waitingbus2016.csv",
                delimiter=';',
                decimal=",",
                encoding='utf-8-sig'  ,
                            )
         
        
        except:
            print ("error met laden")
 
def corr():
    corrMatrix = df.corr()
    print (corrMatrix)
    sn.heatmap(corrMatrix, annot=True)
    plt.show()
    
def plot(a,b):
    bplot= sn.scatterplot(x=a,y=b,data=df)
    bplot.axes.set_title(a+" vs "+b+ ": Scatter Plot",
                        fontsize=16)
    bplot.set_xlabel(a, 
                    fontsize=16)
    bplot.set_ylabel(b, 
                    fontsize=16)
    
    
    
read()
corr()
plot('D','X')


 
#print (df)
#print (vars(df))

