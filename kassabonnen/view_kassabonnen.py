# version : 20260526-120000 - Initial version: Streamlit kassabonnen viewer
# version : 20260526-121500 - Highlight ??? uncertain values in red
# version : 20260526-122500 - CRUD: edit/delete receipts and items, add receipt/item manually
current_version = "20260526-122500"

import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Kassabonnen",
    page_icon=":material/receipt_long:",
    layout="wide",
)

# ── DB path ───────────────────────────────────────────────────────────────────

DEFAULT_DB = r"C:\Users\rcxsm\Documents\python_scripts\python_scripts_rcsmit\kassabonnen\receipts.db"
with st.sidebar:
    st.title(":material/receipt_long: Kassabonnen")
    st.caption(f"v{current_version}")

    db_input = st.text_input("Database pad", value=DEFAULT_DB)
    db_path = Path(db_input.strip())

    if not db_path.exists():
        st.error(f"Bestand niet gevonden:\n`{db_path}`")
        st.stop()

    st.success(f"Geladen: `{db_path.name}`")

# ── DB helpers ────────────────────────────────────────────────────────────────

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def recalc_receipt_totals(conn: sqlite3.Connection, receipt_id: int) -> None:
    """Recompute item_count and total_amount from receipt_items."""
    conn.execute("""
        UPDATE receipts
        SET item_count   = (SELECT COUNT(*)      FROM receipt_items WHERE receipt_id = ?),
            total_amount = (SELECT COALESCE(SUM(total_price), 0) FROM receipt_items WHERE receipt_id = ?)
        WHERE id = ?
    """, (receipt_id, receipt_id, receipt_id))


def clear_cache() -> None:
    st.cache_data.clear()

# ── Load data ─────────────────────────────────────────────────────────────────

@st.cache_data(ttl="60s")
def load_receipts(path: str) -> pd.DataFrame:
    with sqlite3.connect(path) as conn:
        return pd.read_sql_query(
            "SELECT * FROM receipts ORDER BY receipt_date DESC, id DESC", conn)

@st.cache_data(ttl="60s")
def load_items_for(path: str, receipt_id: int) -> pd.DataFrame:
    with sqlite3.connect(path) as conn:
        return pd.read_sql_query(
            "SELECT id, description, quantity, unit_price, total_price, tax_category "
            "FROM receipt_items WHERE receipt_id = ? ORDER BY id",
            conn, params=(receipt_id,))

@st.cache_data(ttl="60s")
def load_all_items(path: str) -> pd.DataFrame:
    with sqlite3.connect(path) as conn:
        return pd.read_sql_query("""
            SELECT ri.id, ri.description, ri.quantity, ri.unit_price, ri.total_price,
                   ri.tax_category, r.store, r.receipt_date, r.filename
            FROM receipt_items ri
            JOIN receipts r ON r.id = ri.receipt_id
            ORDER BY r.receipt_date DESC, ri.id""", conn)

with st.spinner("Database laden…"):
    receipts  = load_receipts(str(db_path))
    all_items = load_all_items(str(db_path))

# ── Sidebar filters ───────────────────────────────────────────────────────────

with st.sidebar:
    st.divider()

    stores = sorted(receipts["store"].dropna().unique().tolist())
    store_filter = st.multiselect("Winkel", stores, placeholder="Alle winkels")

    dates = pd.to_datetime(receipts["receipt_date"].dropna(), errors="coerce").dropna()
    if len(dates):
        min_date, max_date = dates.min().date(), dates.max().date()
        date_from = st.date_input("Van", value=min_date, min_value=min_date, max_value=max_date)
        date_to   = st.date_input("Tot", value=max_date, min_value=min_date, max_value=max_date)
    else:
        date_from = date_to = None

    search = st.text_input(":material/search: Zoek artikel", placeholder="bijv. kaas")

    st.divider()
    show_errors = st.toggle("Toon mislukte bonnen", value=False)

# ── Apply filters ─────────────────────────────────────────────────────────────

df = receipts.copy()
if not show_errors:
    df = df[df["status"] == "ok"]
if store_filter:
    df = df[df["store"].isin(store_filter)]
if date_from and date_to:
    df["receipt_date"] = pd.to_datetime(df["receipt_date"], errors="coerce")
    df = df[df["receipt_date"].between(str(date_from), str(date_to))]
if search:
    matched_ids = all_items[
        all_items["description"].str.contains(search, case=False, na=False)
    ]["filename"].unique()
    df = df[
        df["store"].str.contains(search, case=False, na=False) |
        df["filename"].isin(matched_ids)
    ]

ok_df = df[df["status"] == "ok"] if "status" in df.columns else df

# ── KPI metrics ───────────────────────────────────────────────────────────────

col1, col2, col3, col4 = st.columns(4)
col1.metric("Bonnen",            len(df),                                  border=True)
col2.metric("Artikelen",         int(ok_df["item_count"].sum()),           border=True)
col3.metric("Totaal uitgegeven", f"€ {ok_df['total_amount'].sum():.2f}",  border=True)
col4.metric("Winkels",           ok_df["store"].nunique(),                 border=True)

st.divider()

# ── CRUD dialogs ──────────────────────────────────────────────────────────────

@st.dialog("Bon toevoegen")
def dialog_add_receipt():
    with st.form("add_receipt_form"):
        new_store    = st.text_input("Winkel")
        new_date     = st.date_input("Datum", value=date.today())
        new_currency = st.selectbox("Valuta", ["EUR", "USD", "GBP"], index=0)
        new_filename = st.text_input("Bestandsnaam (optioneel)")
        submitted = st.form_submit_button(":material/save: Opslaan")
    if submitted:
        with get_conn() as conn:
            conn.execute("""
                INSERT INTO receipts (filename, original_path, store, receipt_date,
                                      currency, item_count, total_amount, processed_at, status)
                VALUES (?, ?, ?, ?, ?, 0, 0, datetime('now'), 'ok')
            """, (new_filename or f"handmatig_{new_date}", new_filename or "",
                  new_store, str(new_date), new_currency))
        clear_cache()
        st.success("Bon toegevoegd!")
        st.rerun()


@st.dialog("Bon bewerken")
def dialog_edit_receipt(receipt_id: int):
    row = receipts[receipts["id"] == receipt_id].iloc[0]
    with st.form("edit_receipt_form"):
        new_store    = st.text_input("Winkel",  value=row.get("store") or "")
        cur_date     = pd.to_datetime(row.get("receipt_date"), errors="coerce")
        new_date     = st.date_input("Datum",   value=cur_date.date() if pd.notna(cur_date) else date.today())
        cur_currency = row.get("currency") or "EUR"
        currencies   = ["EUR", "USD", "GBP"]
        new_currency = st.selectbox("Valuta", currencies,
                                    index=currencies.index(cur_currency) if cur_currency in currencies else 0)
        submitted = st.form_submit_button(":material/save: Opslaan")
    if submitted:
        with get_conn() as conn:
            conn.execute("""
                UPDATE receipts SET store=?, receipt_date=?, currency=? WHERE id=?
            """, (new_store, str(new_date), new_currency, receipt_id))
        clear_cache()
        st.success("Bon bijgewerkt!")
        st.rerun()


@st.dialog("Bon verwijderen")
def dialog_delete_receipt(receipt_id: int):
    row = receipts[receipts["id"] == receipt_id].iloc[0]
    st.warning(f"Weet je zeker dat je **{row.get('store') or row.get('filename')}** "
               f"({row.get('receipt_date', '')}) wilt verwijderen?\n\n"
               f"Alle artikelen van deze bon worden ook verwijderd.")
    c1, c2 = st.columns(2)
    if c1.button(":material/delete: Ja, verwijderen", type="primary"):
        with get_conn() as conn:
            conn.execute("DELETE FROM receipt_items WHERE receipt_id=?", (receipt_id,))
            conn.execute("DELETE FROM receipts WHERE id=?", (receipt_id,))
        clear_cache()
        if "selected_receipt_id" in st.session_state:
            del st.session_state["selected_receipt_id"]
        st.success("Bon verwijderd.")
        st.rerun()
    if c2.button("Annuleren"):
        st.rerun()


@st.dialog("Artikel toevoegen")
def dialog_add_item(receipt_id: int):
    with st.form("add_item_form"):
        desc     = st.text_input("Omschrijving")
        qty      = st.number_input("Aantal", min_value=0.0, value=1.0, step=0.5)
        u_price  = st.number_input("Stukprijs (€)", min_value=0.0, value=0.0, step=0.01, format="%.2f")
        t_price  = st.number_input("Totaalprijs (€)", min_value=0.0,
                                   value=round(qty * u_price, 2), step=0.01, format="%.2f")
        tax_cat  = st.text_input("BTW-categorie", value="")
        submitted = st.form_submit_button(":material/save: Opslaan")
    if submitted:
        if not desc.strip():
            st.error("Omschrijving is verplicht.")
            return
        with get_conn() as conn:
            conn.execute("""
                INSERT INTO receipt_items (receipt_id, description, quantity, unit_price, total_price, tax_category)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (receipt_id, desc.strip(), qty, u_price, t_price, tax_cat.strip()))
            recalc_receipt_totals(conn, receipt_id)
        clear_cache()
        st.success("Artikel toegevoegd!")
        st.rerun()


@st.dialog("Artikel bewerken")
def dialog_edit_item(item_id: int, receipt_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM receipt_items WHERE id=?", (item_id,)).fetchone()
    if not row:
        st.error("Artikel niet gevonden.")
        return
    with st.form("edit_item_form"):
        desc    = st.text_input("Omschrijving", value=row["description"] or "")
        qty     = st.number_input("Aantal",        value=float(row["quantity"] or 1),    step=0.5)
        u_price = st.number_input("Stukprijs (€)", value=float(row["unit_price"] or 0),  step=0.01, format="%.2f")
        t_price = st.number_input("Totaalprijs (€)", value=float(row["total_price"] or 0), step=0.01, format="%.2f")
        tax_cat = st.text_input("BTW-categorie",  value=row["tax_category"] or "")
        submitted = st.form_submit_button(":material/save: Opslaan")
    if submitted:
        with get_conn() as conn:
            conn.execute("""
                UPDATE receipt_items
                SET description=?, quantity=?, unit_price=?, total_price=?, tax_category=?
                WHERE id=?
            """, (desc.strip(), qty, u_price, t_price, tax_cat.strip(), item_id))
            recalc_receipt_totals(conn, receipt_id)
        clear_cache()
        st.success("Artikel bijgewerkt!")
        st.rerun()


@st.dialog("Artikel verwijderen")
def dialog_delete_item(item_id: int, receipt_id: int, description: str):
    st.warning(f"Weet je zeker dat je **{description}** wilt verwijderen?")
    c1, c2 = st.columns(2)
    if c1.button(":material/delete: Ja, verwijderen", type="primary"):
        with get_conn() as conn:
            conn.execute("DELETE FROM receipt_items WHERE id=?", (item_id,))
            recalc_receipt_totals(conn, receipt_id)
        clear_cache()
        st.success("Artikel verwijderd.")
        st.rerun()
    if c2.button("Annuleren"):
        st.rerun()

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab_bonnen, tab_artikelen, tab_grafiek = st.tabs([
    ":material/receipt: Bonnen",
    ":material/list: Alle artikelen",
    ":material/bar_chart: Grafiek",
])

# ── Tab 1: Bonnen ─────────────────────────────────────────────────────────────

with tab_bonnen:
    # Add receipt button
    add_col, _ = st.columns([1, 4])
    with add_col:
        if st.button(":material/add: Nieuwe bon", type="secondary"):
            dialog_add_receipt()

    if df.empty:
        st.info("Geen bonnen gevonden met deze filters.")
    else:
        list_col, detail_col = st.columns([2, 3], gap="large")

        with list_col:
            st.subheader(f"{len(df)} bon{'nen' if len(df) != 1 else ''}")

            list_df = ok_df[["id", "store", "receipt_date", "total_amount", "item_count"]].copy()
            list_df["receipt_date"] = pd.to_datetime(list_df["receipt_date"], errors="coerce").dt.strftime("%d %b %Y")
            list_df["total_amount"] = list_df["total_amount"].apply(lambda x: f"€ {x:.2f}" if pd.notna(x) else "—")
            list_df.rename(columns={
                "store":        "Winkel",
                "receipt_date": "Datum",
                "total_amount": "Totaal",
                "item_count":   "Artikelen",
            }, inplace=True)

            selected = st.dataframe(
                list_df[["Winkel", "Datum", "Totaal", "Artikelen"]],
                hide_index=True,
                width="stretch",
                on_select="rerun",
                selection_mode="single-row",
            )

        with detail_col:
            sel_rows = selected.get("selection", {}).get("rows", [])
            if sel_rows:
                receipt_id  = int(list_df.iloc[sel_rows[0]]["id"])
                receipt_row = receipts[receipts["id"] == receipt_id].iloc[0]

                store    = receipt_row.get("store") or receipt_row.get("filename", "—")
                date_str = receipt_row.get("receipt_date", "")
                total    = receipt_row.get("total_amount", 0) or 0
                currency = receipt_row.get("currency", "EUR") or "EUR"
                filename = receipt_row.get("filename", "")
                sym      = "€" if currency == "EUR" else currency + " "

                # Header row with edit/delete buttons
                h1, h2, h3 = st.columns([3, 1, 1])
                h1.subheader(f"**{store}**")
                with h2:
                    if st.button(":material/edit: Bewerken", key="edit_receipt"):
                        dialog_edit_receipt(receipt_id)
                with h3:
                    if st.button(":material/delete: Verwijderen", key="del_receipt", type="primary"):
                        dialog_delete_receipt(receipt_id)

                m1, m2 = st.columns(2)
                m1.metric("Totaal", f"{sym}{total:.2f}")
                m2.metric("Datum", date_str or "—")
                st.caption(f":material/folder: {filename}")

                if receipt_row.get("status") == "error":
                    st.error(f"OCR mislukt: {receipt_row.get('error_message', '')}")
                else:
                    items_df = load_items_for(str(db_path), receipt_id)

                    # Add item button
                    if st.button(":material/add: Artikel toevoegen", key="add_item"):
                        dialog_add_item(receipt_id)

                    if items_df.empty:
                        st.info("Geen artikelen gevonden voor deze bon.")
                    else:
                        # Check for ??? uncertain values
                        uncertain_mask = items_df[["description", "quantity", "unit_price", "total_price"]].isin(["???"])
                        if uncertain_mask.any().any():
                            st.warning(
                                f":material/help: {uncertain_mask.any(axis=1).sum()} regel(s) met onzekere waarden (???) — controleer de originele bon.",
                            )

                        # Render each item row with edit/delete
                        for _, item_row in items_df.iterrows():
                            item_id   = int(item_row["id"])
                            desc      = item_row["description"] or "—"
                            qty       = item_row["quantity"]
                            u_pr      = item_row["unit_price"]
                            t_pr      = item_row["total_price"]
                            tax       = item_row["tax_category"] or ""

                            qty_str   = f"{qty:g} ×" if qty != 1 else ""
                            upr_str   = f"{sym}{u_pr:.2f}" if pd.notna(u_pr) and qty != 1 else ""
                            tpr_str   = f"{sym}{t_pr:.2f}" if pd.notna(t_pr) else "—"
                            tax_str   = f" [{tax}]" if tax else ""

                            ic1, ic2, ic3, ic4 = st.columns([4, 1, 1, 1])
                            ic1.markdown(
                                f"{'🔴 ' if desc == '???' else ''}"
                                f"**{desc}**{tax_str}  "
                                f":small[{qty_str} {upr_str}]"
                            )
                            ic2.markdown(f"**{tpr_str}**")
                            with ic3:
                                if st.button(":material/edit:",
                                             key=f"edit_item_{item_id}",
                                             help="Bewerken"):
                                    dialog_edit_item(item_id, receipt_id)
                            with ic4:
                                if st.button(":material/delete:",
                                             key=f"del_item_{item_id}",
                                             help="Verwijderen"):
                                    dialog_delete_item(item_id, receipt_id, desc)
            else:
                st.info(":material/arrow_back: Selecteer een bon in de lijst.")

# ── Tab 2: Alle artikelen ─────────────────────────────────────────────────────

with tab_artikelen:
    items_filtered = all_items.copy()
    if store_filter:
        items_filtered = items_filtered[items_filtered["store"].isin(store_filter)]
    if search:
        items_filtered = items_filtered[
            items_filtered["description"].str.contains(search, case=False, na=False)]
    if date_from and date_to:
        items_filtered["receipt_date"] = pd.to_datetime(items_filtered["receipt_date"], errors="coerce")
        items_filtered = items_filtered[
            items_filtered["receipt_date"].between(str(date_from), str(date_to))]

    st.caption(f"{len(items_filtered)} artikelregels")

    display_items = items_filtered[["description", "quantity", "unit_price",
                                    "total_price", "store", "receipt_date"]].copy()
    display_items.rename(columns={
        "description":  "Artikel",
        "quantity":     "Aantal",
        "unit_price":   "Stukprijs (€)",
        "total_price":  "Totaal (€)",
        "store":        "Winkel",
        "receipt_date": "Datum",
    }, inplace=True)

    st.dataframe(
        display_items,
        hide_index=True,
        width="stretch",
        column_config={
            "Stukprijs (€)": st.column_config.NumberColumn(format="€ %.2f"),
            "Totaal (€)":    st.column_config.NumberColumn(format="€ %.2f"),
        },
    )

# ── Tab 3: Grafiek ────────────────────────────────────────────────────────────

with tab_grafiek:
    chart_df = ok_df[["receipt_date", "total_amount", "store"]].copy()
    chart_df["receipt_date"] = pd.to_datetime(chart_df["receipt_date"], errors="coerce")
    chart_df = chart_df.dropna(subset=["receipt_date", "total_amount"])

    if chart_df.empty:
        st.info("Niet genoeg data voor een grafiek.")
    else:
        gcol1, gcol2 = st.columns(2)
        with gcol1:
            st.subheader("Uitgaven per bon")
            st.bar_chart(chart_df.sort_values("receipt_date"),
                         x="receipt_date", y="total_amount")
        with gcol2:
            st.subheader("Uitgaven per winkel")
            by_store = (chart_df.groupby("store")["total_amount"]
                        .sum().reset_index()
                        .sort_values("total_amount", ascending=False))
            st.bar_chart(by_store, x="store", y="total_amount", horizontal=True)
