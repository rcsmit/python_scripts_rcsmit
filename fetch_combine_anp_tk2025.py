import json, datetime, time
from pathlib import Path
import requests
import pandas as pd

# https://widgets.verkiezingsdienst.anp.nl/tk25/web/2qxn3l/index.html
# https://widgets.verkiezingsdienst.anp.nl/tk25/data/rh3xjs/index.json

BASE = "https://widgets.verkiezingsdienst.anp.nl/tk25/data/rh3xjs"
OUT_CSV = "alle_resultaten_per_gemeente_2025b.csv"
TIMEOUT = 15

s = requests.Session()

def get(url):
    for _ in range(3):
        r = s.get(url, timeout=TIMEOUT)
        if r.ok:
            return r
        time.sleep(1.0)
    r.raise_for_status()

def parse_num(v):
    if v is None or v == "null":
        return None
    if isinstance(v, (int, float)):
        return v
    s = str(v).strip().replace("\u00a0","").replace(" ","").replace(".","").replace(",",".")
    try:
        return int(s) if s.isdigit() else float(s)
    except:
        return None

# 1) index.json ophalen
index = get(f"{BASE}/index.json").json()

rows, missing = [], []

# 2) alle gemeenten uit views
for i,v in enumerate(index.get("views", [])):
    print (i+1, "/", len(index.get("views", [])), end="\r")
    if v.get("type") == 0 and v.get("key"):
        key = v["key"]
        cbs = v.get("cbsCode")
        label = v.get("label")
        url = f"{BASE}/{key}.json"

        try:
            j = get(url).json()
        except Exception:
            missing.append(key)
            continue

        # metadata
        upd = j.get("updated")
        updated_utc = None
        if isinstance(upd, (int, float)):
            try:
                updated_utc = datetime.datetime.utcfromtimestamp(upd).strftime("%Y-%m-%d %H:%M:%S")
            except:
                updated_utc = upd

        turnout_cur = parse_num(j.get("turnout", {}).get("current"))
        turnout_prev = parse_num(j.get("turnout", {}).get("previous"))
        voters_cur  = parse_num(j.get("voters", {}).get("current"))
        voters_prev = parse_num(j.get("voters", {}).get("previous"))
        invalid_cur = parse_num(j.get("invalid", {}).get("current"))
        invalid_prev= parse_num(j.get("invalid", {}).get("previous"))
        blank_cur   = parse_num(j.get("blank", {}).get("current"))
        blank_prev  = parse_num(j.get("blank", {}).get("previous"))

        # per partij
        for p in j.get("parties", []):
            res = p.get("results", {})
            prev = res.get("previous", {})
            cur  = res.get("current", {})
            diff = res.get("diff", {})

            rows.append({
                "municipality_cbs": cbs,
                "municipality": label,
                "municipality_key": key,
                "party_key": p.get("key"),
                "prev_votes": parse_num(prev.get("votes")),
                "prev_percentage": parse_num(prev.get("percentage")),
                "cur_votes": parse_num(cur.get("votes")),
                "cur_percentage": parse_num(cur.get("percentage")),
                "diff_votes": parse_num(diff.get("votes")),
                "diff_percentage": parse_num(diff.get("percentage")),
                "turnout_current": turnout_cur,
                "turnout_previous": turnout_prev,
                "voters_current": voters_cur,
                "voters_previous": voters_prev,
                "invalid_current": invalid_cur,
                "invalid_previous": invalid_prev,
                "blank_current": blank_cur,
                "blank_previous": blank_prev,
                "updated_utc": updated_utc,
                "source_key_in_file": j.get("key"),
                "status": j.get("status"),
            })

# 3) naar CSV
df = pd.DataFrame(rows)
df.to_csv(OUT_CSV, index=False, encoding="utf-8")

# 4) optioneel: missende keys loggen
if missing:
    Path("missing_keys.txt").write_text("\n".join(missing), encoding="utf-8")
print(f"Geschreven: {OUT_CSV}  | rijen: {len(df)}")
if missing:
    print(f"Ontbrekend: {len(missing)}  -> missing_keys.txt")
