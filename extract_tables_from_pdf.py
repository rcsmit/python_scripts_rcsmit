"""
extract_pdf_tables.py
- Leest alle tabellen uit een PDF
- Probeert: Camelot (lattice -> stream) → Tabula → pdfplumber
- Schrijft: tables/table_{idx}.csv en tables/all_tables_merged.csv
"""

import os
import re
import sys
import shutil
from pathlib import Path
from typing import List, Optional

import pandas as pd

# Optionele imports
try:
    import camelot  # type: ignore
except Exception:
    camelot = None

try:
    import tabula  # type: ignore
except Exception:
    tabula = None

try:
    import pdfplumber  # type: ignore
except Exception:
    pdfplumber = None


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Maak kolomnamen schoon en verwijder lege kolommen/rijen."""
    df = df.copy()
    # Strip en merge multi-line kolomnamen
    df.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in df.columns]
    # Drop volledig lege kolommen
    df = df.dropna(axis=1, how="all")
    # Drop volledig lege rijen
    df = df.dropna(axis=0, how="all")
    # Reset index
    df = df.reset_index(drop=True)
    return df


def save_tables(dfs: List[pd.DataFrame], out_dir: Path) -> Path:
    """Sla tabellen op als losse CSV’s en als één merged CSV."""
    out_dir.mkdir(parents=True, exist_ok=True)
    merged = []
    for i, df in enumerate(dfs, start=1):
        df_clean = normalize_df(df)
        if df_clean.shape[0] == 0 or df_clean.shape[1] == 0:
            continue
        path = out_dir / f"table_{i}.csv"
        df_clean.to_csv(path, index=False, encoding="utf-8-sig")
        merged.append(df_clean)

    merged_path = out_dir / "all_tables_merged.csv"
    if merged:
        # Harmoniseer kolommen door union van alle kolomnamen
        all_cols = list({c for df in merged for c in df.columns})
        merged_harmonized = (
            pd.concat([d.reindex(columns=all_cols) for d in merged], ignore_index=True)
        )
        merged_harmonized.to_csv(merged_path, index=False, encoding="utf-8-sig")
    else:
        merged_path.write_text("", encoding="utf-8")
    return merged_path


def extract_with_camelot(pdf_path: str, pages: str = "all") -> List[pd.DataFrame]:
    """Camelot: eerst lattice, dan stream."""
    if camelot is None:
        return []
    dfs: List[pd.DataFrame] = []

    # 1) Lattice
    try:
        tables_lat = camelot.read_pdf(
            pdf_path,
            pages=pages,
            flavor="lattice",
            strip_text="\n",
            line_scale=40,
        )
        for t in tables_lat:
            dfs.append(t.df)
    except Exception:
        pass

    # 2) Stream
    try:
        tables_str = camelot.read_pdf(
            pdf_path,
            pages=pages,
            flavor="stream",
            strip_text="\n",
            edge_tol=250,
            row_tol=10,
            column_tol=10,
        )
        for t in tables_str:
            dfs.append(t.df)
    except Exception:
        pass

    # Verwijder duplicaten op basis van shape en eerste rij
    unique = []
    seen = set()
    for d in dfs:
        key = (d.shape, tuple(d.iloc[0].astype(str)) if d.shape[0] > 0 else ("",))
        if key not in seen:
            seen.add(key)
            unique.append(d)
    return unique


def extract_with_tabula(pdf_path: str, pages: str = "all") -> List[pd.DataFrame]:
    """Tabula: stream extraction."""
    if tabula is None:
        return []
    dfs: List[pd.DataFrame] = []
    try:
        # De optie multiple_tables=True splitst per gevonden tabel
        out = tabula.read_pdf(
            pdf_path,
            pages=pages,
            multiple_tables=True,
            lattice=False,
            stream=True,
            pandas_options={"dtype": str},
        )
        if isinstance(out, list):
            dfs.extend(out)
    except Exception:
        pass
    return dfs


def extract_with_pdfplumber(pdf_path: str, max_cols: int = 30) -> List[pd.DataFrame]:
    """pdfplumber als fallback. Probeert eenvoudige table extraction per pagina."""
    if pdfplumber is None:
        return []
    dfs: List[pd.DataFrame] = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Als er geometrie is, probeer table extraction
                try:
                    tables = page.extract_tables(
                        table_settings={
                            "vertical_strategy": "lines",
                            "horizontal_strategy": "lines",
                            "intersection_x_tolerance": 5,
                            "intersection_y_tolerance": 5,
                        }
                    )
                    if not tables:
                        # fallback op text-based
                        tables = page.extract_tables()
                    for tbl in tables or []:
                        # tbl is list[list[str]]
                        if not tbl or len(tbl[0]) > max_cols:
                            continue
                        df = pd.DataFrame(tbl)
                        # Gebruik eerste rij als header wanneer die header-achtig oogt
                        header = df.iloc[0].tolist()
                        header_has_text = sum(bool(str(x).strip()) for x in header) >= max(2, len(header)//2)
                        if header_has_text:
                            df.columns = [str(c).strip() for c in header]
                            df = df[1:].reset_index(drop=True)
                        dfs.append(df)
                except Exception:
                    continue
    except Exception:
        pass
    return dfs


def extract_all(pdf_path: str, pages: str = "all") -> List[pd.DataFrame]:
    """Combineer alle methoden met prioriteit: Camelot → Tabula → pdfplumber."""
    all_tables: List[pd.DataFrame] = []

    # Camelot
    # camelot_tables = extract_with_camelot(pdf_path, pages)
    # all_tables.extend(camelot_tables)

    # # Tabula
    # tabula_tables = extract_with_tabula(pdf_path, pages)
    # # Voeg alleen toe als ze niet verdacht veel lijken op bestaande
    # for t in tabula_tables:
    #     if not any((t.shape == d.shape and t.head(1).equals(d.head(1))) for d in all_tables):
    #         all_tables.append(t)

    # pdfplumber
    plumber_tables = extract_with_pdfplumber(pdf_path)
    for t in plumber_tables:
        if not any((t.shape == d.shape and t.head(1).equals(d.head(1))) for d in all_tables):
            all_tables.append(t)

    # Laatste schoonmaak
    cleaned = []
    for d in all_tables:
        d = d.astype(str)
        d = d.replace({"None": "", "nan": ""})
        cleaned.append(d)
    return cleaned


def main():
    # if len(sys.argv) < 2:
    #     print("Gebruik: python extract_pdf_tables.py <pad/naar/bestand.pdf> [pages]")
    #     sys.exit(1)

    # pdf_path = sys.argv[1]
    # pages = sys.argv[2] if len(sys.argv) >= 3 else "all"
    pdf_path = r"c:\Users\rcxsm\Downloads\kemptener-tab-6-2025.pdf"
    pages = "all"
    out_dir = r"c:\Users\rcxsm\Downloads"
        # Path("tables")
    # if out_dir.exists():
    #     shutil.rmtree(out_dir)

    print("Lezen van tabellen...")
    dfs = extract_all(pdf_path, pages=pages)

    if not dfs:
        print("Geen tabellen gevonden.")
        sys.exit(0)

    merged_path = save_tables(dfs, out_dir)
    print(f"Gereed. CSV’s in: {out_dir.resolve()}")
    print(f"Samengevoegd CSV: {merged_path.resolve()}")


if __name__ == "__main__":
    main()
