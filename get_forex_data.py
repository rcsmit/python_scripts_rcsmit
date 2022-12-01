"""Read historical forex (currency) information from yfinance and put it in a dataframe with
a column for each currency
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
    currs = ["INR","THB", "MYR",  "IDR", "NPR","LKR", "VND"]
   
    for ix, c in enumerate(currs):
        print (f"-----------------{c} ({ix+1}/{len(currs)+1}) -------------")
        
        df_currency = get_data(c, "1D")
        if ix==0:
            df_totaal = df_currency
        else:
            df_totaal = pd.merge(df_totaal, df_currency, on="Date", how="outer")
    
    df_totaal = fill_up_weekend_days(df_totaal)
    print (df_totaal)
    save_df(df_totaal, "currencydata_2016_2022")

    # we unpack the table so we can merge it with our expenses-sheet
    df_totaal_unpacked = df_totaal.melt(
        "Date", var_name="currency", value_name="rate"
    )
    print (df_totaal_unpacked)
    save_df(df_totaal_unpacked, "currencydata_2016_2022_unpacked")

if __name__ == "__main__":
    main()
