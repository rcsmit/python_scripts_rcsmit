from geopy.geocoders import Nominatim
import pandas as pd

import reverse_geocode
import pandas as pd
import json
import numpy as np
import csv
import os


def save_df(df, name):
    """  _ _ _ """
    name_ =  name + ".csv"
    compression_opts = dict(method=None, archive_name=name_)
    df.to_csv(name_, index=False, compression=compression_opts)

    print("--- Saving " + name_ + " ---")



def geocode():
    list = ["Costa Rica",
    "Croatia",
    "Argentina",
    "Colombia",
    "Scotland",
    "Canada",
    "Peru",
    "Indonesia",
    "Spain",
    "Costa Rica",
    "Denmark",
    "AUSTRALIA",
    "AUSTRALIA",
    "NEW ZEALAND",
    "Costa Rica",
    "USA",
    "India",
    "Egypt",
    "AUSTRALIA"]
    # create a geocoder object
    geolocator = Nominatim(user_agent="Rene_SMIT")
    for l in list:
    # define the location you want to find the coordinates for
        location = l
        try:
            # use geolocator to get the location object
            location_obj = geolocator.geocode(location)

            # extract the latitude and longitude from the location object
            latitude = location_obj.latitude
            longitude = location_obj.longitude

            # print the coordinates
        
            print (f"{l},{longitude},{latitude}")
        except:
            print (f"{l}#None#None")




def reverse_geocode_x():
    list_=[]
    locator = Nominatim(user_agent="Rene SMIT")
    list_coordinates = ["-16.4462964, -152.2542742",
            "22.0964396, -159.5261238",
            "16.4533691, -85.8844404",
            "15.9721198, -86.475644",
            "20.5071703, -86.9446237",
            "12.0479159, 102.3234816",
            "11.6680759, 102.5642261",
            "10.7290832, 103.2317225",
            "1.1367041, 104.4257533",
            "9.4462305, 118.3929417",
            "-9.6993439, 119.9740534",
            "11.1999448, 123.7405967",
            "43.0602104, 16.1828781",
            "34.8346879, 24.084637",
            "39.2645095, 26.2777073",
            "9.0926343, 98.2951581",
            "9.7368141, 98.4019754",
            "9.5268343, 99.6842603",
            "37.995443, -105.6991929",
            "37.2769484, -107.8766",
            "61.0666922, -107.991707",
            "33.7497366, -117.76858968767132",
            "34.0897, -118.6029649",
            "44.7816915, -121.9764106",
            "47.420875949999996, -122.47370525466893",
            "49.2608724, -123.113952",
            "40.866517, -124.08284",
            "28.2935785, -16.621447121144122",
            "27.74350835, -18.038179618209902",
            "56.7861112, -4.1140518",
            "37.8845813, -4.7760138",
            "-0.936423, -48.280254",
            "-34.9964963, -64.9672817",
            "-41.9649027, -71.5348197",
            "4.099917, -72.9088133",
            "-6.8699697, -75.0458515",
            "9.3040623, -82.12848154978464",
            "35.6009498, -82.5540161",
            "10.2735633, -84.0739102",
            "13.1303252, -84.1248894",
            "37.7274692, -89.216655",
            "38.4601765, -9.195120495540346",
            "15.6631437, -96.5205344",
            "9.734950300000001, 100.0305710845208",
            "-2.4833826, 117.8902853",
            "45.3658443, 15.6575209",
            "43.1837325, 16.5972359",
            "-8.4939889, 115.2654386",
            "39.613432, 2.8829026938823548",
            "39.3858103, 20.1129375",
            "40.086, 22.3585",
            "39.672853, 26.7637243",
            "51.3112589, 3.1323429",
            "37.872734, 32.4924376",
            "28.4963633, 34.5145652",
            "29.035, 34.661667",
            "-3.15073925, 39.67507159193717",
            "39.94918695, 4.0529515568716175",
            "32.26309405, 77.18812183241408",
            "40.9623396, 8.1988519",
            "40.0912813, 9.0305773",
            "100.921822, 9.983953617562140",
            "39.7837304, -100.445882",
            "40.0149856, -105.270545",
            "33.2579507, -115.462841",
            "45.3735129, -121.695878",
            "49.2694099, -123.155267",
            "57.6591141, -3.6107041",
            "-14.2266964, -39.0060954",
            "39.3260685, -4.8379791",
            "10.303688000000001, -68.69984511211467",
            "37.3179725, -8.5558655",
            "10.2735633, -84.0739102",
            "10.2735633, -84.0739102",
            "10.2735633, -84.0739102",
            "20.6308643, -87.0779503",
            "14.68014625, -91.18616099752487",
            "55.670249, 10.3333283",
            "5.91574635, 102.71964491129607",
            "10.631475, 104.132637",
            "-8.8016023, 115.2312006",
            "-8.58356375, 116.35808185429117",
            "9.7391661, 118.759057",
            "52.1567263, 12.5935216",
            "13.5498206, 121.07583852654",
            "52.5170365, 13.3888599",
            "-24.7761086, 134.755",
            "-24.7761086, 134.755",
            "-24.7761086, 134.755",
            "36.0467778, 14.25825649123654",
            "-37.8142176, 144.9631608",
            "-28.3267617, 153.3971541",
            "-41.5000831, 172.8344077",
            "35.308495199999996, 24.46334231842296",
            "49.123317, 24.7299495",
            "26.2540493, 29.2675469",
            "28.4963633, 34.5145652",
            "1.4419683, 38.4313975",
            "14.5439629, 74.3184418",
            "11.0018115, 76.9628425",
            "32.0104317, 77.3166036",
            "10.216793, 77.4847285",
            "27.5753726, 77.6938045",
            "22.3511148, 78.6677428",
            "5.9493634, 80.4558128",
            "25.3356491, 83.0076292",
            "5.0585562, 95.389178",
            "50.82253, -0.137163",
            "-12.5958826, -41.4974246",
            "-14.1312468, -47.5209318",
            "36.0143209, -5.6044497",
            "37.31657, -8.7992645",
            "7.432407, -80.1955268",
            "9.28517, -83.777863",
            "14.6906713, -91.2025207",
            "14.7239015, -91.2590198",
            "38.9067339, 1.4205983",
            "-8.6478175, 115.1385192",
            "-8.5068536, 115.2624778",
            "31.236913, 34.422839",
            "-14.0152408, 34.8507927",
            "32.095838, 34.952177",
            "32.4728028, 34.9742001",
            "30.176442, 35.016722",
            "52.4889466, 5.4942672",
            "6.1394676, 80.1062861",
            "6.8379771, 81.8251687",
            "28.2095831, 83.9855674",
            "27.7172453, 85.3239605",
            "19.3582191, 98.4404863",
            "18.7883439, 98.9853008",
            "9.7513418, 99.9817202",
            "19.8967662, -155.5827818",
            "28.1033035, -17.2193578",
            "51.14804, -2.716577",
            "57.65199, -3.5920868",
            "50.433741, -3.685797",
            "37.2202482, -6.5152587",
            "-6.4824784, -76.3726891",
            "42.441713, -76.5420994",
            "38.1128515, -8.528624",
            "35.5198647, -82.203256",
            "8.7812248, -83.2111258",
            "51.517083, 0.578411",
            "42.7635254, 11.1123634",
            "43.252288, 11.130646",
            "55.673412, 12.5964061",
            "41.7453958, 13.6366557",
            "59.6012139, 13.7004975",
            "-26.7818209, 152.7168632",
            "38.904177, 23.055011",
            "39.1479685, 25.948056",
            "32.9729728, 35.2160224",
            "47.4790491, 7.6170412",
            "45.4174773, 7.7477771",
            "6.7319696, 79.9654564",
            "46.1584, 8.76314",
            "40.7886448, -119.2030177",
            "39.976314, -7.180722",
            "53.3059197, 12.750133",
            "46.7525477, 18.3908146",
            "53.2165157, 5.886514",
            "26.2389469, 73.0243094",
            "24.585445, 73.712479",
            "18.5204303, 73.8567437",
            "27.0238036, 74.2179326",
            "26.4885822, 74.5509422",
            "26.9124336, 75.7872709",
            "10.8505159, 76.2710833",
            "8.7378685, 76.7163359",
            "27.1751448, 78.0421422",
            "25.3176452, 82.9739144",
            "51.341447, -1.144678",
            "22.756817, -102.321713",
            "40.014986, -105.270545",
            "20.868926, -105.440702",
            "36.407238, -105.573285",
            "37.347655, -108.626085",
            "34.86796, -111.761716",
            "34.342782, -112.100631",
            "34.44805, -119.242889",
            "43.97928, -120.737257",
            "39.261561, -121.016059",
            "41.40919, -122.194953",
            "38.440492, -122.714105",
            "44.050505, -123.095051",
            "49.303961, -123.156683",
            "49.261407, -123.261801",
            "48.829667, -123.515161",
            "49.152964, -125.904708",
            "28.400377, -14.00487",
            "20.802957, -156.310683",
            "21.394833, -157.729891",
            "28.286399, -16.796012",
            "28.115981, -17.318794",
            "40.068116, -2.134824",
            "36.72103, -2.193233",
            "51.453802, -2.597298",
            "36.900494, -3.423876",
            "-6.22898, -35.04901",
            "-14.214498, -38.994711",
            "-14.214168, -38.997791",
            "51.859126, -4.311591",
            "52.214003, -4.360321",
            "-12.827727, -41.427712",
            "-12.639166, -41.576256",
            "-22.971974, -43.1843",
            "-22.794007, -43.18841",
            "-23.401147, -45.001301",
            "-23.433162, -45.083415",
            "-27.5973, -48.54961",
            "-15.969457, -5.712944",
            "-23.508137, -53.728537",
            "-34.402852, -53.782501",
            "-30.857208, -64.52632",
            "-21.699514, -64.621458",
            "-30.777933, -64.637126",
            "-22.910832, -68.200138",
            "40.240453, -7.45298",
            "42.61946, -7.863112",
            "-33.553253, -70.582463",
            "-13.388385, -71.82642",
            "-39.273117, -71.97776",
            "-13.22928, -72.264668",
            "6.266563, -72.541311",
            "40.646766, -73.157059",
            "-40.581228, -73.17812",
            "-12.901939, -73.207068",
            "11.268184, -74.190815",
            "-7.847686, -75.017824",
            "6.252594, -75.166883",
            "4.594612, -75.555564",
            "42.439604, -76.496802",
            "37.714283, -8.51493",
            "37.540858, -8.767857",
            "37.433225, -8.770199",
            "37.042143, -8.895396",
            "7.265326, -80.486565",
            "-1.67744, -80.812349",
            "9.625074, -82.620446",
            "38.478414, -82.637939",
            "8.668342, -82.798462",
            "9.738481, -82.840763",
            "10.454131, -84.009661",
            "9.871429, -84.302626",
            "9.913432, -84.924778",
            "11.475207, -85.540671",
            "11.498308, -85.625452",
            "9.979955, -85.652837",
            "10.034637, -85.708621",
            "17.092016, -88.611896",
            "38.83556, -9.352225",
            "30.544722, -9.709128",
            "30.841899, -9.819964",
            "14.72645, -91.265581",
            "16.683547, -92.615518",
            "15.662144, -96.512976",
            "15.667588, -96.553655",
            "15.869333, -97.072643",
            "29.882644, -97.940583",
            "18.75, -99.0",
            "18.991496, -99.102545",
            "24.460334, -99.884448",
            "38.706391, 1.433527",
            "39.028297, 1.557856",
            "55.686724, 12.570072",
            "52.140562, 12.586587",
            "10.977686, 123.152392",
            "9.905138, 126.051189",
            "-23.880765, 148.062341",
            "11.361771, 15.190144",
            "-28.594046, 153.222975",
            "-28.548333, 153.501111",
            "-28.648333, 153.617778",
            "43.173981, 16.556472",
            "40.262824, 17.898418",
            "-41.271085, 173.283676",
            "39.591337, 19.859619",
            "39.569582, 2.650074",
            "37.724369, 23.493811",
            "35.157388, 24.45663",
            "40.451154, 25.585657",
            "39.169957, 25.933736",
            "40.000677, 3.835597",
            "39.26022, 32.021126",
            "35.123553, 33.293156",
            "28.496363, 34.514565",
            "-3.150739, 39.675072",
            "36.4112312, 30.4705477",
            "15.69097, 73.703635",
            "15.009308, 74.024229",
            "14.997108, 74.033829",
            "15.350319, 74.101782",
            "32.214304, 76.319672",
            "15.3358, 76.46102",
            "30.108654, 78.291619",
            "30.488531, 79.625267",
            "12.005421, 79.8111",
            "42.33053, 9.415112",
            "39.924752, -7.24159",
            "40.118167, -7.316315",
            "39.908356, -7.337264",
            "40.5765, -7.448994",
            "39.414618, -7.454066",
            "40.137963, -7.501077",
            "40.321867, -7.612967",
            "40.320654, -7.615107",
            "40.614033, -7.844066",
            "38.015304, -7.862731",
            "40.791109, -7.883833",
            "41.552567, -7.921201",
            "40.231745, -7.94579",
            "37.137919, -8.020216",
            "40.218499, -8.053791",
            "40.203314, -8.410257",
            "37.135663, -8.451723",
            "39.856267, -8.460304",
            "40.762231, -8.475844",
            "37.317988, -8.556171",
            "38.197451, -8.56264",
            "41.150387, -8.594836",
            "37.235932, -8.601222",
            "37.597231, -8.636685",
            "37.594377, -8.641201",
            "37.596408, -8.641991",
            "37.717275, -8.662822",
            "37.715551, -8.663502",
            "37.102788, -8.673028",
            "37.137473, -8.682355",
            "37.31657, -8.799264",
            "37.140741, -8.86161",
            "38.552722, -8.932952",
            "38.539404, -8.940489",
            "9.9621, -84.496654",
            "38.822855, -9.434862",
            "39.412896, -9.513123",
            "-11.6384466, -77.2164443",
            "37.718615, -8.5206002",
            "10.0348382, -85.706404",
            "20.2114185, -87.4653502",
            "52.6894, 11.1434201"]
    for coordinates in list_coordinates:
        try:
        #coordinates = "53.480837, -2.244914"  #lat, lon
            location = locator.reverse(coordinates)
            lat= location.raw['lat']
            lon = location.raw['lon']
            city = location.raw['address']['city']
            state = location.raw['address']['state']
            
            country = location.raw['address']['country']
            print (country)
        except:

            lat= location.raw['lat']
            lon = location.raw['lon']
            city,state,country = "unknown", "unknown","unknown"
        cx = [lat, lon, city, state, country]
        list_.append(cx)
    columns =  ["lat", "lon", "city", "state", "country"]

    total_df = pd.DataFrame(list_, columns=columns)
    print (total_df)
    save_df(total_df, "geocodes_adresses")

def reverse_geocode2():
    
    coords = [(37.8845813, -4.7760138),
        (38.440492, -122.714105),
        (-34.9964963, -64.9672817),
        (-41.9649027, -71.5348197),
        (-30.777933, -64.637126),
        (-21.699514, -64.621458),
        (-30.857208, -64.52632),
        (-37.8142176, 144.9631608),
        (-28.3267617, 153.3971541),
        (-24.7761086, 134.755),
        (-24.7761086, 134.755),
        (-24.7761086, 134.755),
        (-28.548333, 153.501111),
        (-28.594046, 153.222975),
        (-28.648333, 153.617778),
        (51.3112589, 3.1323429),
        (-22.971974, -43.1843),
        (-22.794007, -43.18841),
        (38.4601765, -9.195120495540346),
        (-14.2266964, -39.0060954),
        (-12.827727, -41.427712),
        (-23.401147, -45.001301),
        (22.756817, -102.321713),
        (-27.5973, -48.54961),
        (-14.1312468, -47.5209318),
        (-12.639166, -41.576256),
        (-23.433162, -45.083415),
        (-23.508137, -53.728537),
        (10.631475, 104.132637),
        (49.2608724, -123.113952),
        (49.2694099, -123.155267),
        (48.829667, -123.515161),
        (49.261407, -123.261801),
        (-41.271085, 173.283676),
        (61.0666922, -107.991707),
        (49.152964, -125.904708),
        (28.2935785, -16.621447121144122),
        (-33.553253, -70.582463),
        (-40.581228, -73.17812),
        (-22.910832, -68.200138),
        (-39.273117, -71.97776),
        (4.099917, -72.9088133),
        (-15.969457, -5.712944),
        (11.268184, -74.190815),
        (17.092016, -88.611896),
        (4.594612, -75.555564),
        (6.252594, -75.166883),
        (10.2735633, -84.0739102),
        (10.2735633, -84.0739102),
        (10.2735633, -84.0739102),
        (10.454131, -84.009661),
        (10.977686, 123.152392),
        (37.347655, -108.626085),
        (6.266563, -72.541311),
        (8.668342, -82.798462),
        (9.625074, -82.620446),
        (9.738481, -82.840763),
        (9.871429, -84.302626),
        (9.913432, -84.924778),
        (9.979955, -85.652837),
        (10.0348382, -85.706404),
        (45.3658443, 15.6575209),
        (43.1837325, 16.5972359),
        (55.686724, 12.570072),
        (55.670249, 10.3333283),
        (40.068116, -2.134824),
        (-1.67744, -80.812349),
        (-12.901939, -73.207068),
        (24.460334, -99.884448),
        (29.035, 34.661667),
        (28.4963633, 34.5145652),
        (28.4963633, 34.5145652),
        (26.2540493, 29.2675469),
        (28.496363, 34.514565),
        (52.1567263, 12.5935216),
        (52.5170365, 13.3888599),
        (39.3858103, 20.1129375),
        (39.2645095, 26.2777073),
        (35.308495199999996, 24.46334231842296),
        (40.451154, 25.585657),
        (35.123553, 33.293156),
        (35.157388, 24.45663),
        (37.724369, 23.493811),
        (39.169957, 25.933736),
        (39.591337, 19.859619),
        (14.68014625, -91.18616099752487),
        (29.882644, -97.940583),
        (37.872734, 32.4924376),
        (20.802957, -156.310683),
        (11.0018115, 76.9628425),
        (25.3356491, 83.0076292),
        (18.5204303, 73.8567437),
        (25.3176452, 82.9739144),
        (26.9124336, 75.7872709),
        (26.2389469, 73.0243094),
        (27.1751448, 78.0421422),
        (24.585445, 73.712479),
        (32.214304, 76.319672),
        (32.26309405, 77.18812183241408),
        (14.5439629, 74.3184418),
        (32.0104317, 77.3166036),
        (22.3511148, 78.6677428),
        (10.216793, 77.4847285),
        (27.5753726, 77.6938045),
        (10.303688000000001, -68.69984511211467),
        (10.8505159, 76.2710833),
        (26.4885822, 74.5509422),
        (27.0238036, 74.2179326),
        (8.7378685, 76.7163359),
        (12.005421, 79.8111),
        (14.997108, 74.033829),
        (15.009308, 74.024229),
        (15.3358, 76.46102),
        (15.350319, 74.101782),
        (15.69097, 73.703635),
        (30.108654, 78.291619),
        (30.488531, 79.625267),
        (-8.4939889, 115.2654386),
        (-2.4833826, 117.8902853),
        (-8.58356375, 116.35808185429117),
        (5.0585562, 95.389178),
        (-8.8016023, 115.2312006),
        (30.176442, 35.016722),
        (31.236913, 34.422839),
        (32.9729728, 35.2160224),
        (40.262824, 17.898418),
        (40.9623396, 8.1988519),
        (40.0912813, 9.0305773),
        (-3.150739, 39.675072),
        (-3.15073925, 39.67507159193717),
        (-14.0152408, 34.8507927),
        (5.91574635, 102.71964491129607),
        (36.0467778, 14.25825649123654),
        (30.841899, -9.819964),
        (20.6308643, -87.0779503),
        (16.683547, -92.615518),
        (15.6631437, -96.5205344),
        (15.662144, -96.512976),
        (15.667588, -96.553655),
        (15.869333, -97.072643),
        (18.75, -99.0),
        (18.991496, -99.102545),
        (20.868926, -105.440702),
        (20.2114185, -87.4653502),
        (1.4419683, 38.4313975),
        (30.544722, -9.709128),
        (42.33053, 9.415112),
        (28.2095831, 83.9855674),
        (-41.5000831, 172.8344077),
        (13.1303252, -84.1248894),
        (11.361771, 15.190144),
        (11.475207, -85.540671),
        (11.498308, -85.625452),
        (9.3040623, -82.12848154978464),
        (7.265326, -80.486565),
        (-6.8699697, -75.0458515),
        (-7.847686, -75.017824),
        (-13.22928, -72.264668),
        (-13.388385, -71.82642),
        (13.5498206, 121.07583852654),
        (9.7391661, 118.759057),
        (-0.936423, -48.280254),
        (37.3179725, -8.5558655),
        (37.31657, -8.7992645),
        (39.976314, -7.180722),
        (37.042143, -8.895396),
        (37.433225, -8.770199),
        (37.540858, -8.767857),
        (37.714283, -8.51493),
        (38.83556, -9.352225),
        (40.791109, -7.883833),
        (40.321867, -7.612967),
        (37.135663, -8.451723),
        (40.137963, -7.501077),
        (40.320654, -7.615107),
        (37.31657, -8.799264),
        (37.137919, -8.020216),
        (37.715551, -8.663502),
        (39.908356, -7.337264),
        (37.235932, -8.601222),
        (40.231745, -7.94579),
        (37.717275, -8.662822),
        (38.539404, -8.940489),
        (41.150387, -8.594836),
        (39.414618, -7.454066),
        (37.137473, -8.682355),
        (41.552567, -7.921201),
        (38.822855, -9.434862),
        (38.552722, -8.932952),
        (40.118167, -7.316315),
        (9.9621, -84.496654),
        (40.614033, -7.844066),
        (38.015304, -7.862731),
        (37.594377, -8.641201),
        (39.856267, -8.460304),
        (37.597231, -8.636685),
        (38.197451, -8.56264),
        (37.102788, -8.673028),
        (40.762231, -8.475844),
        (40.218499, -8.053791),
        (40.5765, -7.448994),
        (39.924752, -7.24159),
        (40.203314, -8.410257),
        (37.317988, -8.556171),
        (37.596408, -8.641991),
        (37.140741, -8.86161),
        (39.412896, -9.513123),
        (56.7861112, -4.1140518),
        (57.6591141, -3.6107041),
        (38.706391, 1.433527),
        (39.94918695, 4.0529515568716175),
        (39.613432, 2.8829026938823548),
        (27.74350835, -18.038179618209902),
        (39.3260685, -4.8379791),
        (49.123317, 24.7299495),
        (38.9067339, 1.4205983),
        (28.1033035, -17.2193578),
        (28.400377, -14.00487),
        (39.569582, 2.650074),
        (28.115981, -17.318794),
        (28.286399, -16.796012),
        (36.72103, -2.193233),
        (36.900494, -3.423876),
        (40.000677, 3.835597),
        (42.61946, -7.863112),
        (5.9493634, 80.4558128),
        (9.734950300000001, 100.0305710845208),
        (100.921822, 9.983953617562140),
        (19.3582191, 98.4404863),
        (9.7513418, 99.9817202),
        (9.905138, 126.051189),
        (39.672853, 26.7637243),
        (40.086, 22.3585),
        (36.4112312, 30.4705477),
        (39.26022, 32.021126),
        (50.82253, -0.137163),
        (50.433741, -3.685797),
        (51.14804, -2.716577),
        (51.341447, -1.144678),
        (52.214003, -4.360321),
        (-23.880765, 148.062341),
        (-34.402852, -53.782501),
        (35.6009498, -82.5540161),
        (37.2769484, -107.8766),
        (40.0149856, -105.270545),
        (38.478414, -82.637939),
        (47.420875949999996, -122.47370525466893),
        (44.7816915, -121.9764106),
        (33.7497366, -117.76858968767132),
        (40.866517, -124.08284),
        (34.0897, -118.6029649),
        (37.995443, -105.6991929),
        (37.7274692, -89.216655),
        (33.2579507, -115.462841),
        (45.3735129, -121.695878),
        (39.7837304, -100.445882),
        (19.8967662, -155.5827818),
        (39.261561, -121.016059),
        (51.453802, -2.597298),
        (51.859126, -4.311591),
        (21.394833, -157.729891),
        (36.407238, -105.573285),
        (40.014986, -105.270545),
        (44.050505, -123.095051),
        (34.342782, -112.100631),
        (34.44805, -119.242889),
        (34.86796, -111.761716),
        (40.646766, -73.157059),
        (41.40919, -122.194953),
        (42.439604, -76.496802),
        (43.97928, -120.737257),
        (-26.7818209, 152.7168632),
        (49.303961, -123.156683),
        (55.673412, 12.5964061),
        (-16.4462964, -152.2542742),
        (42.7635254, 11.1123634),
        (20.5071703, -86.9446237),
        (52.4889466, 5.4942672),
        (53.2165157, 5.886514),
        (-6.4824784, -76.3726891),
        (51.517083, 0.578411),
        (9.5268343, 99.6842603),
        (9.0926343, 98.2951581),
        (11.1999448, 123.7405967),
        (1.1367041, 104.4257533),
        (15.9721198, -86.475644),
        (16.4533691, -85.8844404),
        (34.8346879, 24.084637),
        (22.0964396, -159.5261238),
        (12.0479159, 102.3234816),
        (11.6680759, 102.5642261),
        (9.7368141, 98.4019754),
        (10.7290832, 103.2317225),
        (9.4462305, 118.3929417),
        (-9.6993439, 119.9740534),
        (43.0602104, 16.1828781),
        (10.2735633, -84.0739102),
        (32.095838, 34.952177),
        (9.28517, -83.777863),
        (14.6906713, -91.2025207),
        (14.7239015, -91.2590198),
        (6.8379771, 81.8251687),
        (-8.6478175, 115.1385192),
        (18.7883439, 98.9853008),
        (6.1394676, 80.1062861),
        (27.7172453, 85.3239605),
        (32.4728028, 34.9742001),
        (7.432407, -80.1955268),
        (36.0143209, -5.6044497),
        (-8.5068536, 115.2624778),
        (-12.5958826, -41.4974246),
        (59.6012139, 13.7004975),
        (47.4790491, 7.6170412),
        (35.5198647, -82.203256),
        (42.441713, -76.5420994),
        (45.4174773, 7.7477771),
        (8.7812248, -83.2111258),
        (57.65199, -3.5920868),
        (38.904177, 23.055011),
        (37.2202482, -6.5152587),
        (43.252288, 11.130646),
        (38.1128515, -8.528624),
        (46.1584, 8.76314),
        (39.1479685, 25.948056),
        (6.7319696, 79.9654564),
        (41.7453958, 13.6366557),
        (40.7886448, -119.2030177),
        (53.3059197, 12.750133),
        (46.7525477, 18.3908146),
        (-14.214168, -38.997791),
        (-14.214498, -38.994711),
        (-6.22898, -35.04901),
        (10.034637, -85.708621),
        (14.72645, -91.265581),
        (39.028297, 1.557856),
        (40.240453, -7.45298),
        (43.173981, 16.556472),
        (52.140562, 12.586587),
        (-11.6384466, -77.2164443),
        (52.6894, 11.1434201),
        (37.718615, -8.5206002)]
    reversed = reverse_geocode.search(coords)
    print (reversed)
    np.savetxt('reversed.csv', 
          reversed,
          encoding="UTF-8",
           delimiter = ", ",
           fmt = '% s')
    

#reverse_geocode2()
x = 36.988287
y = 35.272027
coordinates = [(x,y)]
data = reverse_geocode.search(coordinates)
print (data)