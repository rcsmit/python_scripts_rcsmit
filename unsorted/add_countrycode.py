import csv
import pycountry
# url = r"C:\Users\rcxsm\Documents\python_scripts\streamlit_scripts\input\length_male.csv"
url = r"C:\Users\rcxsm\Documents\python_scripts\streamlit_scripts\input\meat_consumption.csv"
# Read the CSV file
with open(url, 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    data = list(reader)

print (data)
# Add a column for alpha3 country codes
for row in data:
    try:
        country_alpha3 = pycountry.countries.lookup(row['\ufeffcountry']).alpha_3
        row['country_alpha3'] = country_alpha3
    except LookupError:
        row['country_alpha3'] = 'Unknown'

# Write the modified data to a new CSV file
fieldnames = reader.fieldnames + ['country_alpha3']

with open('modified_file.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)