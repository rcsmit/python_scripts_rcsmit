import pandas as pd

# Specify the path to your Excel file
excel_file_path = r"C:\Users\rcxsm\Documents\xls\gasstanden95xxCN5.xlsx"
# Read the Excel file into a Pandas DataFrame
df = pd.read_excel(excel_file_path)

# Now, 'df' contains the data from the Excel file