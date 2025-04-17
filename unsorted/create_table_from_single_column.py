import pandas as pd


def create_table(file_name):
    with open(file_name,  encoding='UTF-8') as file:
        lines = file.readlines()
    
    # Create an empty list to store the table
    list = []
    
    # Loop through each line in the file
    for line in lines:
        # Split the line into a list of values
        values = line.strip().split("\n")
        for v in values:
        # Add the values to the table
            list.append(v)
    
    # Return the table
    return list

def make_table(list):
    date = list[0::3]
    event_name = list[1::3]
    organizer = list[2::3]
    df = pd.DataFrame(columns=["date", "event name", "organizer"])
    df['date'] = date
    df['event name'] = event_name
    df['organizer'] = organizer
    df['organizer'] = df['organizer'].str.replace('Created by','')
    return df

# Example usage:
filename = r"C:\Users\rcxsm\Documents\python_scripts\streamlit_scripts\input\kpg_events.txt"
list = create_table(filename)
df =make_table(list)
print(df)

df.to_csv(r"C:\Users\rcxsm\Downloads\events_kpg.csv",  sep=";", index=False)