import pandas as pd
import re

# https://opendata.cbs.nl/#/CBS/nl/dataset/03759ned/table?ts=1755082034581
import pandas as pd
import csv
import io
import re

def cbs_wide_to_long(input_path: str, output_path: str):
    # 1) Robuust inlezen, BOM strippen, quotes laten staan, daarna zelf strippen
    with open(input_path, 'rb') as f:
        raw = f.read()
    try:
        text = raw.decode('utf-8-sig')  # verwijdert BOM als die er is
    except UnicodeDecodeError:
        text = raw.decode('latin-1')

    # Gebruik QUOTE_NONE om de pandas-python parser bug te omzeilen
    buf = io.StringIO(text)
    df = pd.read_csv(
        buf,
        sep=';',
        header=None,
        engine='python',
        dtype=str,
        quoting=csv.QUOTE_NONE,
        on_bad_lines='skip'
    )

    # 2) Alle celwaarden ontdoen van aanhalingstekens en whitespace
    df = df.applymap(lambda x: x.strip().strip('"') if isinstance(x, str) else x)

    # 3) Rijen met labels en start van data vinden
    idx_geslacht = df.index[df.iloc[:, 1].fillna('').eq('Geslacht')][0]
    idx_leeftijd = df.index[df.iloc[:, 1].fillna('').eq('Leeftijd')][0]
    idx_header   = df.index[df.iloc[:, 0].fillna('').eq("Regio's")][0]

    # 4) Labels per kolom vanaf kolom 2
    geslacht_labels = df.iloc[idx_geslacht, 2:].replace('', pd.NA).ffill().tolist()
    leeftijd_labels = df.iloc[idx_leeftijd, 2:].replace('', pd.NA).ffill().tolist()

    # 5) Data-gebied selecteren en eventuele bronregel verwijderen
    data = df.iloc[idx_header + 1:].copy()
    data = data[~data.iloc[:, 0].fillna('').str.contains('Bron:', na=False)]

    # 6) Jaar uit kolom "Perioden"
    jaren = data.iloc[:, 1].astype(str).str.extract(r'(\d{4})')[0].astype(int)

    # 7) Waardenmatrix en MultiIndex kolommen bouwen
    values = data.iloc[:, 2:].apply(pd.to_numeric, errors='coerce')
    cols = pd.MultiIndex.from_tuples(list(zip(geslacht_labels, leeftijd_labels)),
                                     names=['geslacht_label', 'leeftijd_label'])
    values.columns = cols

    # 8) Alleen Mannen en Vrouwen en exacte leeftijden "NN jaar"
    mask_sex = values.columns.get_level_values('geslacht_label').isin(['Mannen', 'Vrouwen'])
    mask_age = values.columns.get_level_values('leeftijd_label').str.match(r'^\d+\s+jaar$')
    values = values.loc[:, mask_sex & mask_age]

    # 9) Jaar als index, stapelen naar lang formaat
    values.index = jaren.values
    long = values.stack(level=['geslacht_label', 'leeftijd_label']).reset_index()
    long.columns = ['jaar', 'geslacht_label', 'leeftijd_label', 'aantal']

    # 10) Velden schonen
    sex_map = {'Mannen': 'M', 'Vrouwen': 'F'}
    long['geslacht'] = long['geslacht_label'].map(sex_map)
    long['leeftijd'] = long['leeftijd_label'].str.extract(r'(\d+)').astype(int)
    long['aantal'] = long['aantal'].fillna(0).round(0).astype(int)

    out = long[['leeftijd', 'geslacht', 'jaar', 'aantal']].sort_values(['jaar', 'geslacht', 'leeftijd'])

    # 11) Wegschrijven
    out.to_csv(output_path, sep=';', index=False)

# Voorbeeld
# cbs_wide_to_long('cbs_input.csv', 'leeftijd_geslacht_jaar_aantal.csv')

url=r"C:\Users\rcxsm\Downloads\Bevolking_op_1_januari_en_gemiddeld__geslacht__leeftijd_en_regio_13082025_124329.csv"
# voorbeeld:
cbs_wide_to_long(url, 'bevolking_leeftijd_NL.csv.csv')
