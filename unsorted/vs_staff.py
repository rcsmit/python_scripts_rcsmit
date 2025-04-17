import pandas as pd
import matplotlib.pyplot as plt


def read(sheet_id, sheet_name):  
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url, delimiter=',')
    return df

def read_x():
    sheet_id = "1Lqddg3Rsq0jhFgL5U-HwvDdo0473QBZtjbAp9ol8kcg"
    sheet_name = "gegevens"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

    #url = "C:\\Users\\rcxsm\\Documents\\pyhton_scripts\\in\\schoonmaaktijden.csv",
    df = pd.read_csv(url, delimiter=',')
    #df = df[:-1]  #remove last row which appears to be a Nan

    df["Datum"] = pd.to_datetime(df["Datum"], format="%d-%m-%Y")

    return df

def plot(df, what, jaar):
    # df = df.groupby([what]).sum() # .plot(kind='pie', y=what,  autopct='%1.0f%%',)
    # print (df)

    # plot = df.plot.pie(y=what, figsize=(5, 5))


   
    plt.figure()
    title = f"Verdeling {jaar}"
    plt.pie(sources, labels = index)
    #fig = plt.gcf()
    plt.show()

def get_data_for_plot (df, what):
    a = df[what].value_counts()
    index = a.index
    sources = a.values
    return index, sources

def two_plots(df2021, df2022):
        
    fig, (ax0, ax1) = plt.subplots(nrows=1, ncols=2,)

    index, sources = get_data_for_plot(df2021, "hoofdsectie")
    ax0.set_title('2021')
    ax0.pie(sources, labels = index,autopct='%1.1f%%', )
       
    index, sources = get_data_for_plot(df2022, "hoofdsectie")
    ax1.set_title('2022')
    ax1.pie(sources, labels = index,autopct='%1.1f%%', )
    fig.suptitle('_')
    plt.show()

def main():
    sheet_id = "1vpp8VkFqwMSY3rWyRBdS9HU5BxtwcuFU"
    sheet_name = "2022"
    df2021= read(sheet_id,"2021_")
   
    df2022= read(sheet_id,"2022")
    
    # fig, axs = plt.subplots(2, 1)

    # plot(df2021, "hoofdsectie", 2021)
    # plot(df2022, "hoofdsectie", 2022)
    two_plots(df2021, df2022)
  
main()