import pandas as pd

# create a sample DataFrame with a column of strings
data = {'strings': ['3x2', '1x1', '2x1', '4x1']}
df = pd.DataFrame(data)

# extract the numbers before 'x2' using regular expressions
df['before'] = df['strings'].str.extract(r'^(\d+)x2', expand=False)

# display the result
print(df)