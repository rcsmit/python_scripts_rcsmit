"""
Adapted script to replicate error in Yahoo Finance for the EUR to IDR


Read historical forex (currency) information from yfinance and put it in a dataframe with
a column for each currency


Wrong lines


Date,IDR
2022-08-19,4.0
2016-08-05,14.5600004196167
2017-05-18,14.869999885559082
2021-12-03,16.26099967956543
2021-01-20,17.027999877929688
2017-09-26,36.0
2016-06-02,151.0
2017-04-14,1070.0
2022-10-21,1414.0
2016-05-09,1512.0
2020-03-06,1570.0
2021-12-02,1625.0
2021-03-12,1723.0


"""

import pandas as pd
import yfinance as yf
import numpy as np


def save_df(df, name):
    """Saves the dataframe to a file

    Args:
        df : the dataframe
        name : the name of the file (.csv is added by the script)
    """    
    OUTPUT_DIR = (
        "C:\\Users\\rcxsm\\Documents\\python_scripts\\"
    )
    name_ = OUTPUT_DIR + name + ".csv"
    compression_opts = dict(method=None, archive_name=name_)
    df.to_csv(name_, index=False, compression=compression_opts)

    print("--- Saving " + name_ + " ---")

def fill_up_weekend_days(df):
    """In the data there are no rates for the weekend. We generate extra rows and fill up 
    the saturday and sunday with the values of Friday

    Args:
        df : the dataframe

    Returns:
        df : the dataframe
    """
    # https://stackoverflow.com/questions/70486174/insert-weekend-dates-into-dataframe-while-keeping-prices-in-index-location
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df = df.reindex(pd.date_range(df.index.min(), df.index.max())).sort_index(ascending=True).reset_index().rename(columns={'index': 'Date'})
    columns = df.columns.tolist()
    df = df.fillna(0)
    for i in range(len(df)):
        for c in columns:
            if df.at[i,c] == 0:
                 df.at[i,c] = df.at[i-1,c]
    return df

def get_data( choice,  interval):
    """Get the data from yfinance

    Args:
        choice (string): the currency you want to retrieve
        interval (string): the interval

    Returns:
        df : dataframe with the close-rates
    """    
    ticker = f'EUR{choice}%3DX'
    """Retreat the data from Yahoo Finance
    """
    df_currency = pd.DataFrame()
    data = yf.download(tickers=(ticker), start="2016-01-01",interval=interval, group_by='ticker',auto_adjust=True,prepost=False)
    df = pd.DataFrame(data)

    if len(df) == 0:
        print(f"No data or wrong input - {choice}")
        df = None
    else:
        df['rownumber'] = np.arange(len(df))
    
    df = df.reset_index()
    
    df_currency["Date"] = df["Date"]
    df_currency[choice] = df["Close"]
    
    return df_currency

def main():
    currs = ["IDR"]
   
    for ix, c in enumerate(currs):
        df_currency = get_data(c, "1D")
        if ix==0:
            df_totaal = df_currency
        else:
            df_totaal = pd.merge(df_totaal, df_currency, on="Date", how="outer")
    
    # df_totaal = fill_up_weekend_days(df_totaal)
    df_totaal.sort_values(by=['IDR'], inplace=True) 
    print (df_totaal)
    save_df(df_totaal, "currencydata_2016_2022_IDR")

   

if __name__ == "__main__":
    main()
