import pandas as pd
import colorsys
import pyperclip
import json

# TOOL TO CONVERT GOOGLE MAPS JSON to MAPERATIVE RULES
# FIND GOOGLE MAPS JSON AT eg. snazzymaps.com/
# https://developers.google.com/maps/documentation/javascript/style-reference


def adjust_saturation(hex_color, saturation):
    # Convert hex color to RGB
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Normalize RGB values to the range 0-1
    rgb = [x / 255.0 for x in rgb]
    
    # Convert RGB to HLS
    h, l, s = colorsys.rgb_to_hls(*rgb)
    
    # Adjust the saturation
    s = saturation / 100.0
    
    # Convert HLS back to RGB
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    
    # Normalize RGB values to the range 0-255 and convert to integers
    r, g, b = [int(x * 255) for x in (r, g, b)]
    
    # Convert RGB to hex
    new_hex_color = f"#{r:02x}{g:02x}{b:02x}"
    
    return new_hex_color

def adjust_lightness(hex_color, lightness):
    # Convert hex color to RGB
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Normalize RGB values to the range 0-1
    rgb = [x / 255.0 for x in rgb]
    
    # Convert RGB to HLS
    h, l, s = colorsys.rgb_to_hls(*rgb)
    
    # Adjust the lightness
    l = lightness / 100.0
    
    # Convert HLS back to RGB
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    
    # Normalize RGB values to the range 0-255 and convert to integers
    r, g, b = [int(x * 255) for x in (r, g, b)]
    
    # Convert RGB to hex
    new_hex_color = f"#{r:02x}{g:02x}{b:02x}"
    
    return new_hex_color

def calculate_new_color_column(df, color_col, lightness_col, saturation_col):
    """
    Calculate a new column based on color, lightness, and saturation columns.
    
    Parameters:
    df (DataFrame): Input DataFrame.
    color_col (str): Name of the color column.
    lightness_col (str): Name of the lightness column.
    saturation_col (str): Name of the saturation column.
    
    Returns:
    DataFrame: DataFrame with the new column added.
    """
    
    
   # Initialize an empty list to store new column values
    new_column_values = []
    
    # Iterate over DataFrame rows
    for index, row in df.iterrows():
        color = row[color_col]
        
        # Adjust lightness and saturation if a value is provided
        # Try/except to catch the empty fields

        if lightness_col != None:
            lightness = row[lightness_col]
            
            try:
                color = adjust_lightness(color, float(lightness))
            except:
                pass

        if saturation_col !=None:
            saturation = row[saturation_col]
        
            try:
                color = adjust_saturation(color, float(saturation))
            except:
                pass
        # Append the adjusted color to the list of new column values
        new_column_values.append(color)
    
    # Add the new column to the DataFrame
    df['real_color'] = new_column_values
   
    
    return df

def split_geometry_column(df):
    """
    Split the geometry column into fill-color and line-color columns.
    
    Parameters:
    df (DataFrame): Input DataFrame.
    
    Returns:
    DataFrame: DataFrame with fill-color and line-color columns.
    """
    # Create fill-color and line-color columns and initialize with None
    df['fill-color'] = None
    df['line-color'] = None
    print (df)
    # Iterate over DataFrame rows
    for index, row in df.iterrows():
        element_type = row['elementType']
        
        # Check if elementType is 'geometry'
        if element_type == 'geometry':
            df.at[index, 'line-color'] = row["real_color"]
            df.at[index, 'fill-color'] = row["real_color"]
        elif element_type == 'all':
            df.at[index, 'line-color'] = row["real_color"]
            df.at[index, 'fill-color'] = row["real_color"]
        elif element_type == 'geometry.fill':
            df.at[index, 'fill-color'] = row["real_color"]
        elif element_type == 'geometry.stroke':
            df.at[index, 'line-color'] = row["real_color"]
        elif element_type == 'labels':
            df.at[index, 'line-color'] = row["real_color"]
        elif element_type == 'labels.icon':
            df.at[index, 'line-color'] = row["real_color"]
        elif element_type == 'labels.text.fill':
            df.at[index, 'line-color'] = row["real_color"]
    return df

def process_data(data):
    """Process the JSON data

    Args:
        data (json): json with the data

    Returns:
        df: dataframe with the converted data
    """    
    processed = []
    for entry in data:
        featureType = entry.get('featureType', None)
        elementType = entry.get('elementType', "geometry")
        for styler in entry.get('stylers', []):
            processed.append({
                'featureType': featureType,
                'elementType': elementType,
                **styler
            })
    df = pd.DataFrame(processed)
    print (df)
    try:
        df["lightness"] = df["lightness"].astype(float)
        l = "lightness"
    except:
        l = None
    try:
        df["saturation"] = df["saturation"].astype(float)
        s= "saturation"
    except:
        s = None
    combined_df = combine_rows(df)
    combined_df = calculate_new_color_column(combined_df, "color", l,s)
    combined_df = do_replacements(combined_df)

    combined_df = combined_df.rename(columns={"weight":"line-width"})
        
    combined_df=split_geometry_column(combined_df)
    try:
        combined_df=combined_df[[ "featureType","elementType", "visibility", "fill-color", "line-color", "line-width"]]
    except:
        combined_df=combined_df[[ "featureType","elementType", "visibility", "fill-color", "line-color"]]
        
    return combined_df

def combine_rows(df):
    """Combine rows with the same featureType and elementType.
    
    Args:
        df (_type_): _description_

    Returns:
        _type_: _description_
    """    
    combined = df.groupby(['featureType', 'elementType'], dropna=False).agg(lambda x: ', '.join(x.dropna().astype(str))).reset_index()
    return combined
def do_replacements(df):

    # administrative selects all administrative areas. 
    # Styling affects only the labels of administrative areas, not the geographical borders or fill.
    # administrative.country selects countries.
    # administrative.land_parcel selects land parcels.
    # administrative.locality selects localities.
    # administrative.neighborhood selects neighborhoods.
    # administrative.province selects provinces.
    # landscape selects all landscapes.
    # landscape.man_made selects man-made features, such as buildings and other structures.
    # landscape.natural selects natural features, such as mountains, rivers, deserts, and glaciers.
    # landscape.natural.landcover selects land cover features, the physical material that covers the earth's surface, such as forests, grasslands, wetlands, and bare ground.
    # landscape.natural.terrain selects terrain features of a land surface, such as elevation, slope, and orientation.
    # poi selects all points of interest.
    # poi.attraction selects tourist attractions.
    # poi.business selects businesses.
    # poi.government selects government buildings.
    # poi.medical selects emergency services, including hospitals, pharmacies, police, doctors, and others.
    # poi.park selects parks.
    # poi.place_of_worship selects places of worship, including churches, temples, mosques, and others.
    # poi.school selects schools.
    # poi.sports_complex selects sports complexes.
    # road selects all roads.
    # road.arterial selects arterial roads.
    # road.highway selects highways.
    # road.highway.controlled_access selects highways with controlled access.
    # road.local selects local roads.
    # transit selects all transit stations and lines.
    # transit.line selects transit lines.
    # transit.station selects all transit stations.
    # transit.station.airport selects airports.
    # transit.station.bus selects bus stops.
    # transit.station.rail selects rail stations.
    # water selects bodies of water.
    replacements = [
                    ["poi.park", "park"],
                    ["administrative","administrative"],
                    ["administrative.country","country"],
                    ["administrative.land_parcel","land_parcel"],
                    ["administrative.locality","locality"],
                    ["administrative.neighborhood","neighbourhoood"],
                    ["administrative.province","province"],
                    ["landscape","landuse"],
                    ["landscape.man_made","building"],
                    ["landscape.natural","nature reserve"],
                    ["landscape.natural.landcover","forest"],
                    ["landscape.natural.terrain","natural"],
                    ["poi","poi"],
                    ["poi.attraction","attraction"],
                    ["poi.business","commercial area"],
                    ["poi.government",""],
                    ["poi.medical","hospital"],
                    ["poi.park","park"],
                    ["poi.place_of_worship","church"],
                    ["poi.school","school"],
                    ["poi.sports_complex","leisure stadium"],
                    ["road","road"],
                    ["road.arterial", "major road"],
                    ["road.highway","motor way" ],
                    ["road.local", "minor road"],
                    
                    ["road.highway.controlled_access","motor way"],
                    
                    ["transit", "railway"],
                    
                    ["transit.line","railway"],
                    ["transit.station","railway station"],
                    ["transit.station.airport","airport"],
                    ["transit.station.bus","bus stop"],
                    ["transit.station.rail","railway station"],
                    ["water","water"]
                    ]
    for c in replacements:
            df = df.replace(c[0],c[1])
    return df


# Function to format each row according to the specified format
def convert_df_to_rules(df):
    """turn dataframe to maperative rules file

    Args:
        df (_type_): _description_

    Returns:
        _type_: _description_
    """    
    print (df)
    try:
        landscape_fill_color = df.loc[df['featureType'] == 'landuse', 'fill-color'].values[0]
    except:
        landscape_fill_color = "*NOT SPECIFIED*"
    try:
        water_fill_color = df.loc[df['featureType'] == 'water', 'fill-color'].values[0]
    except:
        water_fill_color = "*NOT SPECIFIED*"

    # Replace 'none' with 1 for rows where feature type is 'road'
    conditions = (df['featureType'].isin(['road', 'major road', 'motor way']) & (df['line-width'] == ''))
    df.loc[conditions, 'line-width'] = '1'

    formatted_output = ["// ALWAYS TEST AND CHECK"]
    formatted_output.append(f"features")
    formatted_output.append(f"\tlines")
    #formatted_output.append(f"\t\tall lines : ")
    formatted_output.append(f"\t\tmotor way : highway=motorway OR highway=motorway_link OR highway=trunk OR highway=trunk_link")
    formatted_output.append(f"\t\tmajor road : highway=primary_link OR highway=primary")
    formatted_output.append(f"\t\tminor road : highway=secondary OR highway=tertiary OR highway=unclassified OR highway=residential OR highway=service OR highway=living_street")
		
    formatted_output.append(f"\tareas")
    formatted_output.append(f"\t\tall areas : ")
    formatted_output.append(f"\t\twater : natural=water OR waterway=riverbank OR waterway=dock OR waterway=river OR waterway=stream OR waterway=canal OR waterway=drain")
    formatted_output.append(f"\t\tcoast : natural=coastline")
    formatted_output.append(f"\t\tbuildings : building")
    formatted_output.append(f"\t\tlanduse : landuse OR boundary OR natural OR leisure")
    formatted_output.append(f"\t\tamenity : amenity OR aeroway")
    formatted_output.append(f"properties")
    formatted_output.append(f"\tmap-background-color : {landscape_fill_color}")
    formatted_output.append(f"\tmap-sea-color : {water_fill_color}")
    formatted_output.append(f"rules")
    #formatted_output.append(f"\ttarget : all areas")
    #formatted_output.append(f"\t\tdefine")
    #formatted_output.append(f"\t\t\tfill-color : green")
    #formatted_output.append(f"\t\t\tfill-opacity : 0.1")
    #formatted_output.append(f"\t\tdraw : fill")
    formatted_output.append(f"\ttarget : all lines")
    formatted_output.append(f"\t\tdefine")
    formatted_output.append(f"\t\t\tline-color : lightgray")
    formatted_output.append(f"\t\t\tline-width : 0.5")
    formatted_output.append(f"\t\tdraw : line")
    last_feature_type = None
    #formatted_output.append("rules")
    first= False
    d=""
    for _, row in df.iterrows():
        current_feature_type = row['featureType'] or 'None'
        
        # if current_feature_type != last_feature_type:
        #     if first==True:
        #         formatted_output.append(d)
        #     first = True    
        #     formatted_output.append(f"\ttarget : {current_feature_type}")
        #     formatted_output.append("\t\tdefine")

        
        
        if row['visibility'] != 'off':
            #formatted_output.append(d)
            formatted_output.append(f"\ttarget : {current_feature_type}")
            formatted_output.append(f"\t//{row['elementType']} - visibility:{row['visibility']}")
            formatted_output.append("\t\tdefine")
            
            define_lines = [
                f"\t\t\t{k.replace('_', '-')}: {v}"
                for k, v in row.items()
                if k not in ['featureType', 'elementType',  'visibility'] and v
            ]
            # Add the visibility line only if it's not 'off'
        
            formatted_output.extend(define_lines)

        # formatted_output.extend(define_lines)
        print (f"{_} {row["visibility"]}")
        if (row["elementType"] =='labels') and (row["visibility"] != "off"):
            d = "\t\tdraw : text"  # \n\t\tdraw : shape\n"
        if (row["elementType"] =='all') and (row["visibility"] != "off"):
            d = "\t\tdraw : text\n\t\tdraw : line\n\t\tdraw : fill" # \n\t\tdraw : shape\n"
        if (row["elementType"] =='geometry') and (row["visibility"] != "off"):
            d = "\t\tdraw : line\n\t\tdraw : fill" # \n\t\tdraw : shape\n"
        if (row["elementType"] =='geometry.fill') and (row["visibility"] != "off"):
            d = "\t\tdraw : fill\" #n\t\tdraw : shape\n"
        
        last_feature_type = current_feature_type
        formatted_output.append(d)
        d=""
    return "\n".join(formatted_output)
    
def main():
    # Process the JSON data
    # Load data from JSON file
    file_path = 'C:\\Users\\rcxsm\\Documents\\python_scripts\\python_scripts_rcsmit\\googlemaps.json'
    with open(file_path, 'r') as file:
        data = json.load(file)

    df = process_data(data)
    # Apply formatting to each row
    print (df)
    maperative_rules = convert_df_to_rules(df)


    # Print the formatted output
    print(maperative_rules)
    pyperclip.copy(maperative_rules)
if __name__ == "__main__":
    main()