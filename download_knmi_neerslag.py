import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import zipfile
import csv
import polars as pl

"""
DOWNLOADING INFO FROM https://www.knmi.nl/nederland-nu/klimatologie/monv/reeksen

Attention:  Approximately 50 MB across around 675 files. 
            Avoid doing this too frequently, as KNMI may impose restrictions.
"""

def find_links():
    """Step 1:  we read the links in the page Dagwaarden neerslagstations and save it to a file

                After this, I manually removed some internal links etc., so I only kept the .zip files.
                I also added http: in front of the filenames manually

    """    
    
    urls = 'https://www.knmi.nl/nederland-nu/klimatologie/monv/reeksen'
    grab = requests.get(urls)
    soup = BeautifulSoup(grab.text, 'html.parser')
    
    # opening a file in write mode
    f = open("files_knmi_fritsander.csv", "w")
    # traverse paragraphs from soup
    for link in soup.find_all("a"):
        data = link.get('href')
        if data is not None:
            print (data)
            f.write(data)
            f.write("\n")
        
    f.close()


def download_links():
    """step 2:  We download the files.

    Attention:  Attention:  Approximately 50 MB across around 675 files. 
                Avoid doing this too frequently, as KNMI may impose restrictions.
                We copy the files to another directory (manually)

                The data is renewed only once per 10 days anyway.

    """         
    url = r'C:\Users\rcxsm\Documents\python_scripts\files_knmi_fritsander.csv'
    df = pd.read_csv(
        url,
        delimiter=";",
        low_memory=False,
    )
    print (df)

    l = len(df)
    filenames = df["url_file"]
    for i,file_url in enumerate(filenames):
        r = requests.get(file_url, allow_redirects=True)
        if file_url.find('/'):
            filename = file_url.rsplit('/', 1)[1]
        print (f"{i+1} / {l} {filename}")
        open(filename, 'wb').write(r.content)
    
def make_stations_file():
    """Step 3: From the filenames, we extract the stationnumbers and -names to use later.

    The stations are here https://cdn.knmi.nl/knmi/map/page/additional/kaart_neerslagstations_201802.jpg

    TODO: geolocate lat. and lon. for every station
    """    

    # Directory where the files are stored
    directory = r"C:\Users\rcxsm\Documents\python_scripts\in"

    # Output CSV file
    output_csv = 'output.csv'

    # List to store extracted information
    data = []

    # Loop through files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.zip'):
            # Extract the part after 'neerslaggeg_' and split by '_'
            parts = filename.replace('.zip', '').split('_')
            
            # Extract city name (capitalize for consistency)
            city = parts[1].capitalize()
            
            # Extract the numeric value
            number = parts[2]
            
            # Append to data list
            data.append([city, number])

    # Write to CSV file
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['City', 'Number'])  # Write header
        writer.writerows(data)  # Write data rows
       
    print(f'CSV file {output_csv} created successfully.')

def unzip():
    """Step 4: We unzip the files
    """    
    directory = r"C:\Users\rcxsm\Documents\python_scripts\in"
    l = len(os.listdir(directory))
    # Loop through the files in the directory
    for i,filename in enumerate(os.listdir(directory)):
        print (f"{i+1} / {l} {filename}")
        # Create the new filename with "- piano intro" appended
       
        with zipfile.ZipFile(filename, "r") as zfile:
            for name in zfile.namelist():
                zfile.extract(name)
        
        # TODO : DELETE ZIPFILE

def combine_without_spaces():
    """Step 5:  We combine the files into one single file.

                Before combining, we remove the empty lines and comment lines

                I changed manually the headerline of the first file 0STN, .... to avoid this line to be
                removed.

                The result is one file with 16 mln lines of around 200-250 MB. 
    
    """             
  
   # Directory where the .txt files are stored
    directory = r"C:\Users\rcxsm\Documents\python_scripts\fritsander_knmi\txt"
    

    # Output file to store the combined content
    output_file = 'combined_fritz.csv'
 
    # Function to check if a line starts with a number (with or without leading spaces)
    # and doesn't start with "5 spaties"
    
    def is_valid_line(line):
        # Remove at most 2 leading spaces
        line_trimmed = line[1:] if line.startswith(' ') else line  # Remove 1 leading space if present
        line_trimmed = line_trimmed[1:] if line_trimmed.startswith(' ') else line_trimmed  # Remove 2nd leading space if present

        # Check conditions
        return (
            line_trimmed.strip()  # Ensure the line is not just whitespace
            and line_trimmed[0].isdigit()  # First character after trimming is a digit
            and not line_trimmed.startswith('5 spaties')  # Ensure it doesn't start with 5 spaces
        )
     # Function to remove the last comma from a line, if it exists
     # doesnt work well, since a lot of rows end with 2 commas.
    def remove_last_comma(line):
        return line.rstrip(',\n') + '\n' if line.endswith(',\n') else line


    l = len(os.listdir(directory))
        
    # Open the output file for writing
    with open(output_file, 'w') as outfile:
        # Loop through the files in the directory
        for i,filename in enumerate(os.listdir(directory)):
            print (f"{i+1} / {l} {filename}")
            if filename.endswith('.txt'):
                file_path = os.path.join(directory, filename)
                
                # Open and read the content of each .txt file
                with open(file_path, 'r') as infile:
                    for line in infile:
                        # Skip lines starting with "5 spaces" 
                        if is_valid_line(line):
                            # Remove all spaces from the line
                            line_without_spaces = line.replace(' ', '')
                            #line_without_spaces_comma = remove_last_comma(line_without_spaces)
                        
                            outfile.write(line_without_spaces)

    print(f'Files processed and merged into {output_file}.')
def geocode():
    import pandas as pd
    # import geopandas
    # import geopy
    from geopy.geocoders import Nominatim


    # https://towardsdatascience.com/pythons-geocoding-convert-a-list-of-addresses-into-a-map-f522ef513fd6
    # https://towardsdatascience.com/geocode-with-python-161ec1e62b89

    # https://rapidapi.com/geoapify-gmbh-geoapify/api/geocode-address-to-location/playground/apiendpoint_8eb61915-984b-41c8-97e6-101b4c294914
    def save_df(df, name):
        """  _ _ _ """
        name_ =  name + ".csv"
        compression_opts = dict(method=None, archive_name=name_)
        df.to_csv(name_, index=False, compression=compression_opts)

        print("--- Saving " + name_ + " ---")


    df = pd.read_csv(r"C:\Users\rcxsm\Documents\python_scripts\fritsander_knmi\stations.csv")
    print (df)
    df['City_']= df['City']
    import requests
    import pandas as pd

   
    # Function to get latitude and longitude from the geocoding API
    def get_lat_lon(city):
        url = "https://geocode-address-to-location.p.rapidapi.com/v1/geocode/autocomplete"
        querystring = {"text": city, "type": "city", "limit": "1", "countrycodes": "nl", "lang": "en"}
        headers = {
            "x-rapidapi-key": "80248646camsh63c71f354bafb81p18d8d1jsnb12ac40ce304",
            "x-rapidapi-host": "geocode-address-to-location.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        
        # Check if the response is valid
        if response.status_code == 200:
            data = response.json()
            if data.get('feautures'):  # Check if there are results
                
                latitude = data['features'][0]['geometry']['coordinates'][1]  # Get latitude
                longitude = data['features'][0]['geometry']['coordinates'][0]  # Get longitude
         
                return latitude, longitude
        return None, None  # Return None if not found

    # Apply the function to get lat and lon for each city
    df[['lat', 'lon']] = df['City'].apply(lambda city: pd.Series(get_lat_lon(city)))

    # Display the DataFrame
    print(df)

    save_df(df, "fritsander_knmi_stations")


def get_data_regen():
    """read the data with Polars

    Returns:
        df: polars dataframe
    """  
    url=r"C:\Users\rcxsm\Documents\python_scripts\python_scripts_rcsmit\combined_fritz.csv"
    df = pl.read_csv(url)
    # df = df.with_columns(
    #     pl.col('YYYYMMDD').cast(pl.String).str.strptime(pl.Datetime, "%Y%m%d"))
    df = df.drop(pl.last())
    df = df.rename({"0TN": "STN"})
   
    return df

def split_and_save_data(station_col="STN", batch_size=125, output_path="output"):
    """Splits dataframe into smaller files based on station numbers and saves them.

    Args:
        df (pl.DataFrame): Polars dataframe to split.
        station_col (str): The name of the station column.
        batch_size (int): The number of stations per file.
        output_path (str): The directory to save the files.
    """
    df= get_data_regen()
    # Rename column '0TN' to 'STN'
    #df = df.rename({"0TN": "STN"})
    
    # Ensure output path exists
    import os
    os.makedirs(output_path, exist_ok=True)
    files =[]
    # Get unique stations and sort them
    unique_stations = df.select(station_col).unique().to_series().sort()

    # Split into batches
    for i in range(0, len(unique_stations), batch_size):
        station_batch = unique_stations[i:i+batch_size]
        df_split = df.filter(pl.col(station_col).is_in(station_batch))
        
        # Save to CSV file
        filename = f"{output_path}/stations_{station_batch[0]}_to_{station_batch[-1]}.csv"
        df_split.write_csv(filename)
        files.append(filename)
        print(f"Saved: {filename}")
    print (files)
def main():

    # GET THE DATA

    #find_links()           # start 1751 - 1800 (9 MIN) // start 1828 finised 1837
    #download_links()       # finised 1843
    #make_stations_file()   # finisehd 1859
    #unzip()                # finised 1853
    #combine_txt()          # finised 1905
    #read_and_save()        # finished 1917 DOESNT WORK< BREAK 1925 (48 MIN) / rstart at 2013. 
    #                       # finished with downloading final version 2036 (23 MIN)
    #combine_without_spaces()
    #geocode()
    split_and_save_data()

if __name__ == "__main__":
    import os
    import datetime
    os.system('cls')
    print(f"--------------{datetime.datetime.now()}-------------------------")
    main()
