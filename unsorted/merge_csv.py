import pandas as pd
from pathlib import Path


def save_df(df, name):
    """  _ _ _ """
    name_ =  name + ".csv"
    compression_opts = dict(method=None, archive_name=name_)
    df.to_csv(name_, index=False, compression=compression_opts)

    print("--- Saving " + name_ + " ---")


source_files = sorted(Path(r'C:\Users\rcxsm\Downloads\mygeodata\Conscious_communities_and_ecovillages_1').glob('*.csv'))

dataframes = []
for file in source_files:
    df = pd.read_csv(file) # additional arguments up to your needs
    df['source'] = file.name
    dataframes.append(df)

df_all = pd.concat(dataframes)
save_df(df_all,"merged_csv")