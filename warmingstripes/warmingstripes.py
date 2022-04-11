# MAKE A PLOT OF WARMING STRIPES and a LINEPLOT of the TEMPERATURE
# ON A CERTAIN DATE OR THE YEAR AVERAGE

# RENE SMIT
# Based on code of Sebastian Beyer

# License to be confirmed


import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

def main():
    # the colors in this colormap come from http://colorbrewer2.org
    # the 8 more saturated colors from the 9 blues / 9 reds
    # https://matplotlib.org/matplotblog/posts/warming-stripes/
    cmap = ListedColormap([
        '#08306b', '#08519c', '#2171b5', '#4292c6',
        '#6baed6', '#9ecae1', '#c6dbef', '#deebf7',
        '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a',
        '#ef3b2c', '#cb181d', '#a50f15', '#67000d',
    ])

    # Bewerkt van
    # https://www.knmi.nl/nederland-nu/klimatologie/daggegevens
    # https://cdn.knmi.nl/knmi/map/page/klimatologie/gegevens/daggegevens/etmgeg_260.zip
    url1 = 'C:\\Users\\rcxsm\\Documents\\phyton_scripts\\debilt.csv'
    #url1 = 'C:\\Users\\rcxsm\\Documents\\phyton_scripts\\arcen.csv'
    #url1 = 'https://raw.githubusercontent.com/rcsmit/warmingstrips/main/debilt.csv'

    mode = "period" # / "year_avg" / # "spec_day"
    day = 5 # day to show in spec_day mode
    month = 5 # month to show in spec_day mode
    month1 = 4 #first month in period mode
    month2 = 5 # last month  in period mode
    PLAATS = "De Bilt"
    months = ["January", "February",  "March", "April", "May", "June",
            "July", "August", "September", "Oktober", "November", "December"]
    day_in_words = str(day) + "th of " + months[month-1]



    df   = pd.read_csv(url1,
                        delimiter=",",
                        low_memory=False)

    df["date"]= pd.to_datetime(df["YYYYMMDD"], format="%Y%m%d")
    df["YYYY"]= df['date'].dt.year

    if mode == "year_avg":
        df_jaar = df.groupby(["YYYY"], sort=True).mean().reset_index()
    elif mode == "spec_day":
        df_jaar = df[(df['date'].dt.month==month) & (df['date'].dt.day==day)]
    elif mode == "period":

        df = df[(df['date'].dt.month>=month1)  & (df['date'].dt.month<=month2)   ]  # & df[(df['date'].dt.month<=month2)]
        df_jaar = df.groupby(["YYYY"], sort=True).mean().reset_index()
        df_jaar = df_jaar[['YYYY', "TX", "TN", "TG"]]

    # SHOW ONLY LAST xx YEARS
    how_many_years_from_now = 120
    df_jaar =df_jaar[(len(df_jaar.index) - how_many_years_from_now):]

    FIRST = df_jaar["YYYY"].min()
    LAST = df_jaar["YYYY"].max()


    # UNCOMMENT what you want to see / ... day temperature

    which_column = "TN"
    what_is = "Minimum"

    which_column = "TG"
    what_is = "Average"

    # which_column = "TX"
    # what_is = "Maximum"

    toshow = ["TN", "TG", "TX"]
    what_is_ = [ "Minimum", "Average day", "Maximum"]
    colors = ["blue", "orange", "red"]


    jaren = df_jaar["YYYY"].tolist()

    if mode == "year_avg":
        # remove last year (not finished) (in casu 2021)
        # TODO: also remove the last year if the chosen day is after the current day
        del temperatures[-1]
        del jaren[-1]

    # SHOW BARCODE

    barcode = False
    if barcode :
        # https://github.com/sebastianbeyer/warmingstripes/blob/master/warmingstripes.py
        stacked_temps = np.stack((temperatures, temperatures))
        plt.figure(figsize=(4,18))
        img = plt.imshow(stacked_temps, cmap=cmap, aspect=40, )
        plt.gca().set_axis_off()

        plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
                    hspace = 0, wspace = 0)
        plt.margins(0,0)
        if mode == "year_avg":
            plt.title(f"{what_is} temperature Barcode of average year-temperature {FIRST} - {LAST-1}")
        elif mode == "spec_day":
            plt.title(f"{what_is} temperature Barcode of {day_in_words} {FIRST} - {LAST}")

        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.show()


    # MAKE LINE GRAPH
    # TODO: Horizontal line @ average
    plt.figure(figsize=(4,18))

    for i, ts in enumerate(toshow):
        df_jaar["temperatures_"]= df_jaar[ts]/10   # TG = average / TN = min of the day / TX = max of the day
        temperatures = df_jaar['temperatures_'].tolist()
        avg_temperatures = sum(temperatures)/ len(temperatures)

        plt.plot(jaren,temperatures, label = f"{what_is_[i]} temperature", color = colors[i])
        #plt.hlines(avg_temperatures, FIRST, LAST, colors = "#000000", linestyles = "dotted", label = "Average")

        # Calculate rolling average
        # https://stackoverflow.com/a/44797397/4173718
        N = 1
        cumsum, temperatures_rolling_avg = [0], []
        for i, x in enumerate(temperatures, 1):
            cumsum.append(cumsum[i-1] + x)
            if i>=N:
                moving_ave = (cumsum[i] - cumsum[i-N])/N
                #can do stuff with moving_ave here
                temperatures_rolling_avg.append(moving_ave)
            else:
                temperatures_rolling_avg.append(None)

        #plt.plot(jaren,temperatures_rolling_avg, alpha = 0.5, label = f"Rolling average ({N}) ")
    if mode == "year_avg":
        plt.ylabel("Average Temperature of the year\nin degrees Celcius")
    elif mode == "spec_day":
        plt.ylabel(f"Temperatures at {day_in_words} in {PLAATS}\nin degrees Celcius")
    if mode == "year_avg":
        plt.title(f"average year-temperature {FIRST} - {LAST-1}")
    elif mode == "spec_day":
        plt.title(f"Daytemperature of {day_in_words} in {PLAATS} {FIRST} - {LAST}")
    elif mode == "period":
        plt.title(f"Average daytemperature of {months[month1-1]} to {months[month2-1]} in {PLAATS} {FIRST} - {LAST}")
    plt.grid( linestyle='--', alpha = 0.5)
    plt.legend()
    plt.show()

    df_jaar = df_jaar.sort_values(by=['TG'])
    print (df_jaar)


if __name__ == "__main__":
    main()
