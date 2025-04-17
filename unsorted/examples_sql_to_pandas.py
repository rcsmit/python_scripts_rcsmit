import pandas as pd

df = forbes_global_2010_2014[['company', 'sector', 'continent', 'profits']]

# Selecting Financials sector
df = df[df['sector'] == 'Financials'].sort_values('profits', ascending = False)

# Assigning rank for profits column
df['profits_rank'] = df['profits'].rank(method = 'dense', ascending = False)

# Selecting the most profitable company
df = df[df['profits_rank'] == 1]

# Output required columns
df[['company', 'continent']]
###############################################
# Import your libraries
import pandas as pd

# Start writing code
df=forbes_global_2010_2014
df.query('sector=="Financials" & rank==1')[['company','continent']]