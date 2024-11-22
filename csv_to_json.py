import pandas as pd

# Read the CSV file (replace 'path/to/your/file.csv' with the path to your CSV file)
df = pd.read_csv(r"C:\Users\rcxsm\Downloads\Thai Alphabet - op_alfabet.csv")

# Convert the DataFrame to JSON
json_result = df.to_json(orient='records', force_ascii=False)

# Save the JSON to a file
with open(r'C:\Users\rcxsm\Downloads\Thai Alphabet - op_alfabet.json', 'w', encoding='utf-8') as file:
    file.write(json_result)

print("JSON conversion complete!")