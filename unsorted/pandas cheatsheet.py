Python for Data Analysis
https://wesmckinney.com/book/

https://jakevdp.github.io/PythonDataScienceHandbook/


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



# Python For Data Science Cheat Sheet: Pandas Basics
# https://levelup.gitconnected.com/pandas-basics-cheat-sheet-2023-python-for-data-science-b59fb7786b4d
import pandas as pd


# A one-dimensional labeled array capable of holding any data type
s = pd.Series([3, -5, 7, 4],  index=['a',  'b',  'c',  'd'])

## A two-dimensional labeled data structure with columns of potentially different types
data = {'Country': ['Belgium',  'India',  'Brazil'],
'Capital': ['Brussels',  'New Delhi',  'Brasilia'],
'Population': [11190846, 1303171035, 207847528]} 
df = pd.DataFrame(data,columns=['Country',  'Capital',  'Population'])

#Asking For Help
help(pd.Series.loc)

# I/O
# Read and Write to CSV
pd.read_csv('file.csv', header=None, nrows=5)
df.to_csv('myDataFrame.csv')

#Read multiple sheets from the same file
xlsx = pd.ExcelFile('file.xls')
df = pd.read_excel(xlsx,  'Sheet1')

#Read and Write to Excel
pd.read_excel('file.xlsx')
df.to_excel('dir/myDataFrame.xlsx',  sheet_name='Sheet1')

#Read and Write to SQL Query or Database Table
# (read_sql()is a convenience wrapper around read_sql_table() and read_sql_query())
from sqlalchemy import create_engine
engine = create_engine('sqlite:///:memory:')
pd.read_sql(SELECT * FROM my_table;, engine)
pd.read_sql_table('my_table', engine)
pd.read_sql_query(SELECT * FROM my_table;', engine)
df.to_sql('myDf', engine)

#Selection
#Get one element
s['b']
-5

#Get subset of a DataFrame
df[1:]

#Selecting', Boolean Indexing and Setting
#By Position
#Select single value by row and and column
df.iloc([0], [0])
df.iat([0], [0])

#By Label
#Select single value by row and column labels
df.loc([0],  ['Country'])
df.at([0],  ['Country'])

#By Label/Position
#Select single row of subset of rows
df.ix[2]

#Select a single column of subset of columns
df.ix[:, 'Capital']

#Select rows and columns
df.ix[1, 'Capital']

#Boolean Indexing
#Series s where value is not >1
s[~(s > 1)]

#s where value is <-1 or >2
s[(s < -1) | (s > 2)]

#Use filter to adjust DataFrame
df[df['Population']>1200000000]

#Setting
#Set index a of Series s to 6
s['a'] = 6

#Dropping
#Drop values from rows (axis=0)
s.drop(['a',  'c'])

#Drop values from columns(axis=1)
df.drop('Country', axis=1) 

#Sort and   ORDER
#Sort by labels along an axis
df.sort_index()

#Sort by the values along an axis ORDER BY
df.sort_values(by='Country') 

#Assign ranks to entries
df.rank()

#Retrieving Series/DataFrame Information
#Basic Information
#(rows, columns)
df.shape

#Describe index
df.index

#Describe DataFrame columns
df.columns

#Info on DataFrame
df.info()

#Number of non-NA values
df.count()

#Summary
#Sum of values
df.sum()

#Cumulative sum of values
df.cumsum()

#Minimum/maximum values
df.min()/df.max()

#Minimum/Maximum index value
df.idxmin()/df.idxmax() 

#Summary statistics
df.describe()

#Mean of values
df.mean()

#Median of values
df.median()

#Applying Functions
f = lambda x: x*2

#Apply function
df.apply(f)

#Apply function element-wise
df.applynap(f) 

#Internal Data Alignment
#NA values are introduced in the indices that don't overlap:
s3 = pd.Series([7, -2, 3],  index=['a',  'c',  'd'])
s + s3

#Arithmetic Operations with Fill Methods
#You can also do the internal data alignment yourself with the help of the fill methods:
s.add(s3, fill_value=0)
s.sub(s3, fill_value=2)
s.div(s3, fill_value=4)
s.mul(s3, fill_value=3)

#pivot
df.pivot_table(index='foo', columns='bar', values='baz',  aggfunc='sum')

# filter on list
# https://stackoverflow.com/questions/59275119/how-can-i-filter-single-column-in-a-dataframe-on-multiple-values
selection_list_accos = ["WAKIKI", "BALI"]
df_all_years = df_all_years[df_all_years["acco_type"].isin(selection_list_accos)]

#PIVOT TABLE UITPAKKEN
df_prijzen_stacked = df_prijzen.melt(
        "acco_type", var_name="maand_int", value_name="price_per_night"
    )

# MAKE DF CREATE
total_df = pd.DataFrame(list_, columns=columns)

# GROUPBY
df_grouped = df.groupby([df[valuefield]], sort=True).sum().reset_index()

df = (df.groupby('Name', as_index=False)
       .agg({'Missed':'sum', 'Credit':'sum','Grade':'mean'})
       .rename(columns={'Missed':'Sum1', 'Credit':'Sum2','Grade':'Average'}))

#MERGE
 df  = pd.merge(
                df_data, df_pop, how="outer", on="Agegroup"
            )
#COLUMNS TO LIST
columns = df.columns.tolist()

# VALUES IN COLUMN TO LIST
list_of_accotypes_ = df.acco_type.unique()

#RENAME COLUMNS
df.rename(columns={"A": "a", "B": "c"})

# SMA
df[col_sma] =  df[col].rolling(window = 3, center = False).mean()

df__["jaar_week"] = df__["jaar"].astype(str)  +"_" + df__["weeknr"].astype(str).str.zfill(2)

# COLUMN TO UPPERCASE
data['Name'] = data['Name'].str.upper()

# IGNORE SETCOPYWARNING
pd.options.mode.chained_assignment = None  # default='warn'

def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]


def mid(s, offset, amount):
    return s[offset-1:offset+amount-1]


# date
df['Date'] = pd.to_datetime(df['Date'])

* Series.dt.strftime() function to convert the dates in the given series object to the specified date format.

Python Strftime Format
The strftime converts date object to a string date.


Strptime python is used to convert string to datetime object.
strptime("9/23/20", "%d/%m/%y")

# SLICES

a[start:stop]  # items start through stop-1
a[start:]      # items start through the rest of the array
a[:stop]       # items from the beginning through stop-1
a[:]           # a copy of the whole array
There is also the step value, which can be used with any of the above:

a[start:stop:step] # start through not past stop, by step
The key point to remember is that the :stop value represents the first value that is not in the selected slice. So, the difference between stop and start is the number of elements selected (if step is 1, the default).

The other feature is that start or stop may be a negative number, which means it counts from the end of the array instead of the beginning. So:

a[-1]    # last item in the array
a[-2:]   # last two items in the array
a[:-2]   # everything except the last two items
Similarly, step may be a negative number:

a[::-1]    # all items in the array, reversed
a[1::-1]   # the first two items, reversed
a[:-3:-1]  # the last two items, reversed
a[-3::-1]  # everything except the last two items, reversed


#PLOTLY PROBLEM
plotly.offline.init_notebook_mode(connected=True)
plotly.offline.plot(fig)


# MAKE FLOWCHART OF METHODS
# https://github.com/scottrogowski/code2flow
