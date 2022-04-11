# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 17:34:44 2020

@author: rcxsm
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pylab as plt

# Use 2 decimal places in output display
pd.options.display.float_format = '{:.2f}'.format
# Don't wrap repr(DataFrame) across additional lines
pd.set_option("display.expand_frame_repr", False)

def f(x):
    #https://stackoverflow.com/a/9574948/2901002
    d = pd.Timestamp(1899, 12, 30)
    timedeltas = pd.to_timedelta(x, unit='d', errors='coerce')
    dates = pd.to_datetime(x, errors='coerce')
    return (timedeltas + d).fillna(dates)
def read_csv():
    global df
    df = pd.read_csv(
                "runninggeschiedeniscompleet3.csv",
                #names=["datum","afstand", "tijd", "snelheid"],
                names = ["Activiteittype","datum","Datum2","Titel","afstand","Tijd","km_u","Kolom8","Kolom9","Kolom10","Kolom11","Kolom12","Kolom13"],
                delimiter=';',
                parse_dates=["datum"],
                encoding='latin-1'  ,
                dayfirst=True
            )
    bewerk()

def read():
    filetype = 'xls'
    #file = 'C:\Users\rcxsm\Documents\pyhton_scripts'
    sheet = 'Sheet01'
    global df

    df = pd.read_excel ('input\\runninggeschiedeniscompleet.xlsx',
                        sheet_name= sheet,
                        header=1,
                        usecols= "b,e,f,g",
                        names=["datum","afstand", "tijd", "snelheid"],)
    bewerk()
def bewerk():
    global df
    #print (df)
    df.datum=pd.to_datetime(df.datum, dayfirst=True)
    df['jaar']=df['datum'].dt.strftime('%Y')
    df['maand']=df['datum'].dt.strftime('%m')
    df['jaarmaanddag']=df['datum'].dt.strftime('%d-%m-%Y')

    #print ("========= DATAFRAME ===========")
    #print (df)
    #print (f"---------- {len(df)}  regels --------")

def print_perdag():
    global rapport
    print ("========= AFSTAND PER DAG ===========")
    rapport = df.groupby("jaarmaanddag")["afstand"].sum()
    print (rapport)
    #fig, ax = plt.subplots(figsize=(8,6))
    #df.groupby('jaarmaanddag').plot(kind='scatter', x = "jaarmaanddag", y = "afstand", ax=ax)
    #sns.regplot(x=rapport["jaarmaanddag"], y=rapport["afstand"])
    #sns.regplot(data=df, x="jaarmaanddag", y="afstand")
    #sns.plt.show()
    print ("Lets plot!!!!")
    print (df)
    df.plot(kind='scatter', x = "datum", y = "afstand")
    #df.groupby('jaar').plot(kind='scatter', x = "jaarmaanddag", y = "afstand")
    #plt.show
    plt.show(block=False)
    input('press <ENTER> to continue')


    #sns.regplot(data=rapport, x="jaarmaanddag", y="afstand")
    #sns.plt.show()
def print_permaand():
    print ("========= PER MAAND ===========")
    df['datum'] = pd.to_datetime(df['datum'],format='%d-%m-%Y')
    rapport2 = df.groupby(df['jaarmaand'])['bedrag'].sum()
    print(rapport2)


def print_kruistabel_jaar():
    print ("========= KRUISTABEL PER JAAR ===========")
    df.datum=pd.to_datetime(df.datum)
    df.datum=df['datum'].dt.strftime('%Y')
    table = (pd.pivot_table(df, values='bedrag', index=['hoofdrub'],
            columns=['jaar'], aggfunc=np.sum,fill_value='', margins=True))
    print (table)

def print_kruistabel_maand():
    global table

    print ("========= KRUISTABEL PER MAAND ===========")
    df.datum=pd.to_datetime(df.datum)
    df.datum=df['datum'].dt.strftime('%Y-%m')

    table = (pd.pivot_table(df, values='bedrag', index=['jaarmaand'],
            columns=['hoofdrub'], aggfunc=np.sum,fill_value='', margins=True))

    return table

def print_kruistabel_maand_hoofdrub(hr):
    global table
    try:
        found = df[df['hoofdrub'].str.contains(hr)]
    except:
        print ("error2")
    if len(found) ==  0:
            print ("VALUE DOESNT EXIST")

    else:
        print (f"========= KRUISTABEL PER MAAND / {hr} ===========")
        df.datum=pd.to_datetime(df.datum)
        df.datum=df['datum'].dt.strftime('%Y-%m')
        #df_gt_hr = df[df['hoofdrub'] == hr]
        df_gt_hr =df[df['hoofdrub'].str.contains(hr)]
        print (df_gt_hr)
        table = (pd.pivot_table(df_gt_hr, values='invbedrag', index=['jaarmaand'],
                columns=['hoofdrub'], aggfunc=np.sum,fill_value='', margins=False))
        print (table)
        table.plot(kind='bar', stacked = True)
        return (table)


def plotafstanddag():
    # use the function regplot to make a scatterplot
    sns.regplot(x=rapport["jaarmaanddag"], y=rapport["afstand"])
    sns.plt.show()



def main():
    read_csv()
    #print_rub()

    print_perdag()
    #plotafstanddag()

    #print_kruistabel_jaar()
    #print(print_kruistabel_maand())

main()
