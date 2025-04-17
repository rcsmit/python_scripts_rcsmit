import pandas as pd
from datetime import datetime
# Load the CSV files into dataframes
url = r"C:\Users\rcxsm\Documents\inventaris accomodaties VS.csv"
df =  pd.read_csv(url, sep=";")
df['ID_rene_original'].fillna(0, inplace=True)
df1 = df[df["ID_rene_original"] ==0]
df2 =  df[df["ID_rene_original"] !=0]
df1['NL'] = df1['NL'].str.lower()
df2['NL'] = df2['NL'].str.lower()



df1= df1[["ID_oude_layout","id_nieuwe_layout","NL","EN","DU","FR","IT","ES","DK","HU","PL","NAV + SAH (up to 2022)","NAV + SAH (FROM 2022)","KAL (up to 2022)","KAL (from 2022)","SER (up to 2022)","SER (from 2022)","MH(up to 2016)","MH(2017 up to 2021)","MH (from 2022)"]]
df2= df2[["ID_rene_original","cat_rene_original","sub_id_rene_orig","rubriek","NL","EN","DU","FR","IT","ES","DK","HU","PL" ,"Waikiki","Bali","Sahara","Kalahari 1","Kalahari 2","Serengeti XL","Serengetti L","€","bron prijs","remarks"]]


print ("DF1")
print (df1)
print ("DF2")
print(df2)

# Merge the dataframes (assuming you want to concatenate them)
merged_df = pd.merge(df1, df2, on='NL', how='outer')  # Adjust 'how' as needed (inner, outer, left, right)
desired_columns = ["ID_rene_original","cat_rene_original","sub_id_rene_orig","rubriek"]

# Reorder the columns in the DataFrame
merged_df = merged_df[desired_columns + [col for col in merged_df.columns if col not in desired_columns]]

# Save the merged dataframe as a new CSV file

merged_df = merged_df.sort_values(by=["ID_rene_original", "id_nieuwe_layout", "ID_oude_layout"])


# Get the current date and time
current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# Construct the new filename with the timestamp
new_filename = f'merged_data_{current_datetime}.csv'

merged_df.to_csv(new_filename, index=False, sep=";",encoding='utf-8')  # Replace 'merged_data.csv' with your desired file name
print ("Merged DF")
print (merged_df)


# Find articles in df but not in df2
df_not_in_df2 = df1.merge(df2, on='NL', how='left', indicator=True).loc[lambda x: x['_merge'] == 'left_only']

# Find articles in df2 but not in df
df2_not_in_df = df2.merge(df1, on='NL', how='left', indicator=True).loc[lambda x: x['_merge'] == 'left_only']

# Display the results
print("Articles in df but not in df2:")
print(df_not_in_df2[["NL"]])

print("\nArticles in df2 but not in df:")
print(df2_not_in_df[["NL"]])
