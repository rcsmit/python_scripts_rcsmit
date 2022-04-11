import pandas as pd
import geopandas
import geopy
from geopy.geocoders import Nominatim


# https://towardsdatascience.com/pythons-geocoding-convert-a-list-of-addresses-into-a-map-f522ef513fd6
# https://towardsdatascience.com/geocode-with-python-161ec1e62b89

def save_df(df, name):
    """  _ _ _ """
    name_ =  name + ".csv"
    compression_opts = dict(method=None, archive_name=name_)
    df.to_csv(name_, index=False, compression=compression_opts)

    print("--- Saving " + name_ + " ---")


df = pd.read_csv("C:\\Users\\rcxsm\\Documents\\spiritual places peggy anke.csv")
print (df)
df['Naam_']= df['Naam']
from geopy.extra.rate_limiter import RateLimiter
locator = Nominatim(user_agent="myGeocoder")

# 1 - conveneint function to delay between geocoding calls
geocode = RateLimiter(locator.geocode, min_delay_seconds=1)
# 2- - create location column

df['location'] = df['Naam'].apply(geocode)
# 3 - create longitude, laatitude and altitude from location column (returns tuple)
df['point'] = df['location'].apply(lambda loc: tuple(loc.point) if loc else None)
# 4 - split point column into latitude, longitude and altitude columns
df[['latitude', 'longitude', 'altitude']] = pd.DataFrame(df['point'].tolist(), index=df.index)

#df = df.drop([‘Address1’, ‘Address3’, ‘Address4’, ‘Address5’,’Telefon’, ‘ADDRESS’, ‘location’, ‘point’], axis=1)
df.head()
save_df(df, "peggytest")