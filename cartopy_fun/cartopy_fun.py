# Having fun with Cartopy.
# inspired by the work of @pythonmaps on Twitter
# eg. https://twitter.com/PythonMaps/status/1391056641546768388

# Rene Smit, 10th of May 2021, MIT-License

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from numpy import genfromtxt
import time

import cartopy.crs as ccrs # https://www.lfd.uci.edu/~gohlke/pythonlibs/#cartopy
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

def get_data(url,delimiter):
    '''
    Get the data
    '''
    df   = pd.read_csv(url, delimiter=delimiter, low_memory=False)
    return df

def save_df(df, name):
    """  _ _ _ """
    OUTPUT_DIR = ""
    name_ = OUTPUT_DIR + name + ".csv"
    compression_opts = dict(method=None, archive_name=name_)
    df.to_csv(name_, index=False, compression=compression_opts)

    print("--- Saving " + name_ + " ---")

def show_cities():
    '''
    Show fixed points of interest on a map
    '''
    cities = pd.DataFrame({'City': ['Utrecht', 'Amsterdam', 'Rotterdam', 'The Hague', 'Arnhem', 'Hilversum', 'Amersfoort', 'Almere',  'Lelystad', 'Apeldoorn', 'Den Burg', 'Harlingen', 'Zwolle', 'Gorinchem'],
                            'Lon': [5.1214, 4.9041, 4.4777, 4.3007, 5.8987, 5.1669, 5.3878, 5.2647, 5.4714, 5.9699, 4.7997, 5.4252, 6.0830, 4.9758],
                            'Lat': [52.0907, 52.3676, 51.9244, 52.0705, 51.9851, 52.2292, 52.1561, 52.3508, 52.5185, 52.2112, 53.0546, 53.1746, 52.5168, 51.8372]})
    plt.scatter(cities.Lon, cities.Lat, marker = 'o', color = 'red', s = 50)
    for i in range(cities.shape[0]):
        plt.text(cities.Lon[i] + 0.02, cities.Lat[i], cities.City[i], color = 'red')

def show_locations(df, how, cities):
    '''
    Show the locations given in a dataframe
    df = dataframe
    how = points or scatter. The first reads the POI's in a loop, and adds the placename (or whatever field), the second plots
                             a scatter which is (much) faster.

    cities = True/False      Show the fixed POI's on the map

    '''
    df = df[df['type']=="large_airport"]

    fig = plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.stock_img() #show a background
    ax.coastlines()

    if how == "points":
    # PLOTTING AS DIFFERENT POINTS - 12.8sec
        for i in range (0, len(df)):
            plt.plot( df.iloc[i]["longitude_deg"],      df.iloc[i]["latitude_deg"], markersize=1, marker='o', color='red')
            plt.text(df.iloc[i]["longitude_deg"], df.iloc[i]["latitude_deg"] , df.iloc[i]["iata_code"],
                horizontalalignment='left',
                fontsize='smaller',
                transform=ccrs.PlateCarree())
    else:
    # PLOTTING AS SCATTERPOINTS - 5.1 seconds
        plt.scatter(
            x=df["longitude_deg"],
            y=df["latitude_deg"],
            color="red",
            s=1,
            alpha=1,
            transform=ccrs.PlateCarree()
        )
    if cities:
        show_cities()
    plt.title("Large airports in the world")
    plt.show()


def show_heatmap_with_histogram2d(df, cities):
    '''
    # turn a CSV file with points of interests into a heatmap.
    # np.histogram2d calculates the number of instances in a certain area

    # Thanks to https://medium.com/analytics-vidhya/custom-strava-heatmap-231267dcd084
    '''
    df = df[df['type']=="large_airport"]

    Z, xedges, yedges = np.histogram2d(np.array(df.longitude_deg, dtype=float),
                                    np.array(df.latitude_deg, dtype=float), bins = 100)

    fig = plt.figure() # I created a new figure and set up its size
    ax = plt.axes(projection=ccrs.PlateCarree())
    #extent = [-10, 30, 35, 75] #  Europe
    extent = [df.longitude_deg.min(),-20, 7,df.latitude_deg.max()] # North America
    ax.set_extent(extent, crs=ccrs.PlateCarree())

    ax.coastlines(resolution='10m', color='black', linewidth=.3)
    heatmap = ax.pcolormesh(xedges, yedges, Z.T, vmin=0, vmax=5, cmap = 'Set1')

    plt.colorbar(heatmap)
    plt.title("Large airports in the world")

    if cities:
        show_cities()
    plt.show()

def show_heatmap_from_values(url, delimiter, resolution, extent, field_lon, field_lat, field_value, value_type,value_process,
                            min_colorbar_std, max_colorbar_std, colorbar_colors, colorbar_nodes, title, log_value, show_colorbar):
    '''
    # turn a CSV file with points of interests into a heatmap.
    # It takes  the average of values or the frequence in a certain area
    # and creates  a pivot table which serves as base for the heatmap

    # inspired by https://twitter.com/PythonMaps/status/1386727574894792707

    parameters :
                URL : URL (string)
                delimiter : the delimiter (string)
                resolution (integer/float)
                extent : the exent of what to slow: lon-left, lon-right, lat-up, lat-down. (list with numbers)
                            Take care : resolution and the extent have to be congruent otherwise there might be unexpected results.
                            Use rounded numbers.
                            If lon-left = -180, lon-right has to be 180, otherwise there might be unexpected results too.
                field_lon, field_lat, field_value : the fieldnames for resp. longitude, latitude and the value. (string)
                value_type : "frequence" -> it adds the a field with the name field_value and fills it with the value 1.0
                                            np.histogram2d could also be used and might be faster.
                            or something else : doesn't matter, it only checks if the value_type is "frequence" (string)
                value_proces : "sum" or "mean" -> calculates the sum or the mean (string)
                min_colorbar_std : for the colorbar: (mean - (min_colorbar_std * std)). Put 999 to set minimum of the colorbar to 0 (integer)
                max : for the colorbar: (mean + (min_colorbar_std * std)) (integer)
                colorbar_colors : colors of the colorbar (list with strings)
                colorbar_nodes :  the nodes of the colorbar (list with strings)
                title : Title of the heatmap (string)
                log_value :  calculate the 10log of the value -> True / False (boolean)
                show_colorbar : show the colorbar? -> True / False (boolean)


    '''
    t1=time.time()
    df = get_data(url,delimiter)

    df = df[df[field_lon]  >= extent[0] ]
    df = df[df[field_lon]  <= extent[1] ]
    df = df[df[field_lat]  >= extent[2] ]
    df = df[df[field_lat]  <= extent[3] ]

    if value_type == "frequence":
        df.loc[:,field_value] = 1

    if log_value:
        df.loc[:,field_value]= np.log10(df.loc[:,field_value])

    df.loc[:, field_lat]= round( df.loc[:,field_lat]/resolution)*resolution
    df.loc[:, field_lon]= round( df.loc[:,field_lon]/resolution)*resolution

    if value_process == "mean":
        df = df.groupby([field_lat, field_lon]).mean()
    else:
        df = df.groupby([field_lat, field_lon]).sum().reset_index()

    if min_colorbar_std == 999:
        min_value = 0
    else:
        min_value =df[field_value].mean() - (min_colorbar_std*df[field_value].std() )
    max_value =df[field_value].mean() + (max_colorbar_std*df[field_value].std() )

    # Make an dataframe with a grid with NaN-values which covers the total
    # area and merge it with your data-dataframe
    row_list = []
    for lon_x in np.arange (extent[0],extent[1]+resolution,resolution):
        for lat_x in np.arange  (extent[3],(extent[2]-resolution),-1*resolution):
            row_list.append([lat_x, lon_x, 0])
    df_temp = pd.DataFrame(row_list, columns=[field_lat, field_lon,field_value])

    df = pd.merge(
        df_temp,
        df,
        how="outer",
        on=[field_lat, field_lon]
        )
    df = df.fillna(0) # I have to fill the NaN, because otherwise I cant merge the two value-fields together
    field_value_x = field_value + "_x"
    field_value_y = field_value + "_y"
    df[field_value]= df[field_value_y] +df[field_value_y]
    df = df.drop(columns=[field_value_x], axis=1)
    df = df.drop(columns=[field_value_y], axis=1)

    # I have to repeat this otherwise I get Nan Values and duplicate columns in my pivot table when resolution<1
    df[field_lat]= round(df[field_lat],2)
    df[field_lon]= round(df[field_lon],2)
    df = df.groupby([field_lat, field_lon]).sum()

    df = df.sort_values(by=[field_lat,field_lon]).reset_index()
    df = df.pivot_table(index=field_lat, columns=field_lon, values=field_value, aggfunc = np.sum)
    df = df.sort_values(by=field_lat, ascending=False)

    df = df.replace(0.0, np.nan) # i don't want a color for 0 or NaN values
    xedges = df.columns.tolist()
    yedges = df.index.tolist()
    values__ = df.to_numpy()

    fig = plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.coastlines(resolution='10m', color='black', linewidth=.3)

    colorbar_cmap = LinearSegmentedColormap.from_list("mycmap", list(zip(colorbar_nodes, colorbar_colors)))
    heatmap = ax.pcolormesh(xedges, yedges, values__, vmin=min_value, vmax=max_value, cmap =  colorbar_cmap)
    if show_colorbar:
        plt.colorbar(heatmap, orientation = 'horizontal')
    plt.title(title)
    t2=time.time()
    print (f"Done in {round(t2-t1,2)} seconds with {title}")
    plt.show()


def show_heatmap_from_array():
    '''
    Show a heatmap, generated from an array
    # thanks to https://stackoverflow.com/a/44952031/4173718
    '''
    extent = [-180, 180, -90, 90]

    # CH4 IN THE AIR
    # heat_data = genfromtxt('https://raw.githubusercontent.com/rcsmit/cartopy_fun/main/MOD_LSTD_M_2021-04-01_rgb_360x180.CSV', delimiter=',')
    # heat_data = genfromtxt('C:\\Users\\rcxsm\\Documents\\phyton_scripts\\MOD_LSTD_M_2021-04-01_rgb_1440x720.CSV', delimiter=',')
    # source : https://neo.sci.gsfc.nasa.gov/view.php?datasetId=MOD_LSTD_M - april 2021, csv, 1.0 degree

    # heat_data[heat_data == 99999.0] = np.nan # filter out the seas and ocean

    # POPULATION COUNT
    #heat_data = genfromtxt('C:\\Users\\rcxsm\\Documents\\phyton_scripts\\gpw_v4_population_count_rev11_2020_1_deg.csv', delimiter=',')
    #heat_data = genfromtxt('C:\\Users\\rcxsm\\Documents\\phyton_scripts\\gpw_v4_population_count_rev11_2020_15_min.asc', delimiter=' ')

    heat_data = genfromtxt('gpw_v4_population_count_rev11_2020_2pt5_min.asc', delimiter=' ')

    # https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-count-rev11/data-download
    # 30 Second (approx. 1km)
    # 2.5 Minute (approx. 5km)
    # 15 Minute (approx. 30km)
    # 30 Minute (approx. 55km)
    # 60 Minute/1 Degree (approx. 110km)

    heat_data[heat_data == -9999] = np.nan # filter out the seas and ocean


    heat_data = np.flip(heat_data)      #no idea why I have to flip the data twice
    heat_data = np.flip(heat_data,1)
    #heat_data = np.log10(heat_data)
    print (heat_data)

    #std = np.matrix.std(heat_data)
    #print (f"{mean} {std}")
    mean = np.nanmean(heat_data)
    std = np.nanstd(heat_data)
    print (mean)
    fig, ax = plt.subplots()
    ax = plt.axes(projection=ccrs.PlateCarree())
    #ax.stock_img()
    ax.coastlines(resolution='10m', color='black', linewidth=.3, alpha=.5)
    lon = np.linspace(extent[0],extent[1],heat_data.shape[1])
    lat = np.linspace(extent[2],extent[3],heat_data.shape[0])

    Lon, Lat = np.meshgrid(lon,lat)

    neo_colors = [ "white", "cyan","blue", "purple", "magenta", "red", "orange", "yellow", "lightyellow"]
    nodes =      [0.0,           0.125,   0.25,  0.375,   0.5,       0.625,  0.75,    0.825,  1.0]
    neo_cmap = LinearSegmentedColormap.from_list("mycmap", list(zip(nodes, neo_colors)))

    #heatmap = ax.pcolormesh(Lon,Lat,(heat_data) ,vmin=-25, vmax=50, cmap = neo_cmap)
    heatmap = ax.pcolormesh(Lon,Lat,(heat_data), vmin=0, vmax=(mean+(1*std)), cmap =  'YlOrBr')
    plt.colorbar(heatmap)
    plt.title("LAND SURFACE TEMPERATURE [DAY] \nHeatmap based on a np.array from a CSV file")
    plt.show()

def rasterio_and_geotiff():
    # https://geoscripting-wur.github.io/PythonRaster/
    # under construction
    pass


def main():
    # url = 'C:\\Users\\rcxsm\\Documents\\phyton_scripts\\airports.csv'  #10 mb big file, takes a lot of time to process !
    # url = "https://ourairports.com/data/airports.csv" #10 mb big file, takes a lot of time to process !
    # url = 'https://raw.githubusercontent.com/rcsmit/python_scripts_rcsmit/cartopy_fun/main/airports2.csv'
    # df = get_data(url,",")

    # SHOW THE LOCATIONS ON A MAP
    # show_locations(df, "points", False) # show the airports on a map

    # GENERATE A HEATMAP WITH A GENERATED HISTOGRAM 

    #show_show_heatmap_with_histogram2d(df, False) # number of airports in a certain area
    
    # GENERATE A HEATMAP FROM AN ARRAY WITH VALUES
    #show_heatmap_from_array() # land temperatures

    # GENERATE A HEATMAP FROM VALUES (more flexible)
    show_heatmap_from_values( "C:\\Users\\rcxsm\\Documents\\phyton_scripts\\ch4.csv", ";",
                                # source: https://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/EDGAR/datasets/v50_GHG/CH4/TOTALS/v50_CH4_2015.zip
                                # via https://edgar.jrc.ec.europa.eu/index.php/dataset_ghg50#p2 ->
                                # via https://edgar.jrc.ec.europa.eu/gallery?release=v50&substance=CH4&sector=TOTALS
                        0.25, [-10, 30, 30, 80] ,
                        "lon", "lat", "emission",
                        "value","mean",
                        2,2,
                         [ "white", "cyan","blue", "purple", "red"],
                        [0.0,       0.25,    0.5,    0.75,     1.0],
                        "CH4 emission",
                        True,
                        False)


    show_heatmap_from_values( 'C:\\Users\\rcxsm\\Documents\\phyton_scripts\\airports.csv', ",",
                        # source : "https://ourairports.com/data/airports.csv" #10 mb big file, takes a lot of time to process !
                        1, [-170, 30, 30, 80] ,
                        "longitude_deg", "latitude_deg", "count",
                        "frequence","sum",
                        999,2,
                         [ "white","orange"],
                        [0.0,        1.0],
                        "aiports",
                        False,
                        True)

if __name__ == "__main__":
    main()
