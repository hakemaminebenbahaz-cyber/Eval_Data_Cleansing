import pandas as pd
import os
import re
import matplotlib.pyplot as plt
from utils_cleaning import clean_email, clean_country, clean_phone, clean_date, clean_price, USD_TO_EUR

# -------------------------
# Créer dossiers out et reports
# -------------------------
os.makedirs("out", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# =========================
# 1️⃣ NETTOYAGE CLIENTS
# =========================
df_clients = pd.read_csv("data/clients.csv", dtype=str)
df_clients.columns = [c.strip().lower() for c in df_clients.columns]

# Standardisation
df_clients['email'] = df_clients['email'].apply(clean_email)
df_clients['pays'] = df_clients['pays'].apply(clean_country)
df_clients['telephone'] = df_clients['telephone'].apply(clean_phone)
df_clients['naissance'] = df_clients['naissance'].apply(clean_date)

# Lignes manquantes
critical_clients = ['id','nom','prenom','email','telephone','pays','naissance']
df_clients_missing = df_clients[df_clients[critical_clients].isna().any(axis=1)].copy()
df_clients_clean = df_clients[~df_clients.index.isin(df_clients_missing.index)].copy()

# Supprimer doublons email
df_clients_clean.drop_duplicates(subset=['email'], inplace=True)

# KPI clients
kpi_clients = pd.DataFrame([{
    "rows_before": len(df_clients),
    "rows_after": len(df_clients_clean),
    "duplicates_removed": len(df_clients) - len(df_clients_clean),
    "missing_rows": len(df_clients_missing),
    "invalid_emails": df_clients_clean['email'].isna().sum(),
    "pct_invalid_emails": round(100 * df_clients_clean['email'].isna().sum() / len(df_clients_clean),2)
}])

# Sauvegarde
df_clients_clean.to_csv("out/clients_clean.csv", index=False)
df_clients_missing.to_csv("reports/clients_missing.csv", index=False)
kpi_clients.to_csv("reports/kpi_clients.csv", index=False)

# =========================
# 2️⃣ NETTOYAGE CATALOGUE PRODUITS
# =========================
df_fr = pd.read_csv("data/catalog_fr.csv", dtype=str)
df_us = pd.read_csv("data/catalog_us.csv", dtype=str)
df_map = pd.read_csv("data/mapping_categories.csv", dtype=str)

df_fr.columns = [c.strip().lower() for c in df_fr.columns]
df_us.columns = [c.strip().lower() for c in df_us.columns]
df_map.columns = [c.strip().lower() for c in df_map.columns]

# Poids en kg
def clean_weight_force(raw_weight):
    if pd.isna(raw_weight):
        return None
    w = str(raw_weight).lower().replace(" ","")
    try:
        if "kg" in w:
            return float(w.replace("kg",""))
        if "g" in w:
            return float(w.replace("g",""))/1000
        if "lb" in w or "lbs" in w:
            return float(re.sub(r"[^0-9.]","",w))*0.453592
        return float(w)
    except:
        return None

df_fr['weight'] = df_fr['weight'].apply(clean_weight_force)
df_us['weight'] = df_us['weight'].apply(clean_weight_force)

# Prix en EUR
df_fr['price'] = df_fr['price'].apply(clean_price)
df_us['price'] = df_us['price'].apply(clean_price)

# Mapper catégories
df_fr = df_fr.merge(df_map, left_on='category', right_on='source_category', how='left')
df_us = df_us.merge(df_map, left_on='category', right_on='source_category', how='left')
df_fr['category'] = df_fr['target_category']
df_us['category'] = df_us['target_category']
df_fr.drop(columns=['source_category','target_category'], inplace=True)
df_us.drop(columns=['source_category','target_category'], inplace=True)

# Fusion catalogue
df_catalog = pd.concat([df_fr, df_us], ignore_index=True)
df_catalog['sku'] = df_catalog['sku'].astype(str).str.strip().str.upper()
df_catalog['currency'] = "€"

# Lignes manquantes et doublons
critical_catalog = ['sku','name','category','weight','price']
df_catalog_missing = df_catalog[df_catalog[critical_catalog].isna().any(axis=1)].copy()
df_catalog_canonique = df_catalog[~df_catalog.index.isin(df_catalog_missing.index)].copy()
df_catalog_canonique.drop_duplicates(subset=['sku'], inplace=True)

# KPI catalogue
kpi_catalog = pd.DataFrame([{
    "rows_before": len(df_catalog),
    "rows_after": len(df_catalog_canonique),
    "duplicates_removed": len(df_catalog) - len(df_catalog_canonique),
    "missing_rows": len(df_catalog_missing)
}])

# Sauvegarde
df_catalog_canonique.to_csv("out/catalog_canonique.csv", index=False)
df_catalog_missing.to_csv("reports/catalog_missing.csv", index=False)
kpi_catalog.to_csv("reports/kpi_catalog.csv", index=False)

# =========================
# 3️⃣ NETTOYAGE VENTES
# =========================
df_sales = pd.read_csv("data/sales.csv", dtype=str)
df_sales.columns = [c.strip().lower() for c in df_sales.columns]

critical_sales = ['order_id','customer_email','order_date','amount','currency']
df_sales_missing = df_sales[df_sales[critical_sales].isna().any(axis=1)].copy()
df_sales_clean = df_sales[~df_sales.index.isin(df_sales_missing.index)].copy()

# Dates en datetime
df_sales_clean['order_date'] = pd.to_datetime(df_sales_clean['order_date'], errors='coerce')

# Montants en EUR (USD → EUR), garder négatifs
def convert_amount_keep_negative(row):
    try:
        amt = float(re.sub(r"[^0-9.-]", "", str(row['amount'])))
        cur = row['currency'].strip().upper() if isinstance(row['currency'], str) else "€"
        if cur in ["USD","$"]:
            amt = round(amt*USD_TO_EUR,2)
        return amt
    except:
        return None

df_sales_clean['amount'] = df_sales_clean.apply(convert_amount_keep_negative, axis=1)
df_sales_clean['currency'] = "€"

# Séparer remboursements
df_sales_refunds = df_sales_clean[df_sales_clean['amount'] < 0].copy()
df_sales_clean = df_sales_clean[df_sales_clean['amount'] >= 0].copy()

# Standardisation emails et order_id
df_sales_clean['customer_email'] = df_sales_clean['customer_email'].str.strip().str.lower()
df_sales_clean['order_id'] = df_sales_clean['order_id'].astype(str).str.strip()

# Supprimer doublons
df_sales_clean.drop_duplicates(subset=['order_id','customer_email'], inplace=True)

# Revenu journalier
df_sales_valid = df_sales_clean.dropna(subset=['order_date'])
daily_revenue = df_sales_valid.groupby('order_date')['amount'].sum().reset_index()
daily_revenue.rename(columns={'amount':'daily_revenue'}, inplace=True)
daily_revenue = daily_revenue.sort_values('order_date')

# KPI ventes
kpi_sales = pd.DataFrame([{
    "rows_before": len(df_sales),
    "rows_after": len(df_sales_clean),
    "duplicates_removed": len(df_sales)-len(df_sales_clean)-len(df_sales_missing)-len(df_sales_refunds),
    "missing_rows": len(df_sales_missing),
    "invalid_dates": df_sales_clean['order_date'].isna().sum(),
    "invalid_amounts": df_sales_clean['amount'].isna().sum(),
    "refund_rows": len(df_sales_refunds)
}])

# Sauvegarde
df_sales_clean.to_csv("out/sales_clean.csv", index=False)
df_sales_missing.to_csv("reports/sales_missing.csv", index=False)
df_sales_refunds.to_csv("reports/sales_refunds.csv", index=False)
daily_revenue.to_csv("reports/daily_revenue.csv", index=False)
kpi_sales.to_csv("reports/kpi_sales.csv", index=False)

# =========================
# 4️⃣ Dashboard KPI visuel
# =========================
def plot_kpi(title, kpi_df, before_col, after_col, missing_col=None, extra_cols=None):
    plt.figure(figsize=(8,5))
    bars = [kpi_df[before_col].iloc[0], kpi_df[after_col].iloc[0]]
    labels = ['Avant nettoyage', 'Après nettoyage']
    
    if missing_col:
        bars.append(kpi_df[missing_col].iloc[0])
        labels.append('Lignes manquantes')
    
    if extra_cols:
        for col in extra_cols:
            bars.append(kpi_df[col].iloc[0])
            labels.append(col.replace('_',' '))
    
    plt.bar(labels, bars, color=['skyblue','green','orange','red'])
    plt.title(title)
    plt.ylabel('Nombre de lignes')
    for i, v in enumerate(bars):
        plt.text(i, v + 10, str(v), ha='center', fontweight='bold')
    plt.tight_layout()
    plt.show()

# Clients
plot_kpi(
    "KPI Clients",
    kpi_clients,
    before_col="rows_before",
    after_col="rows_after",
    missing_col="missing_rows",
    extra_cols=["duplicates_removed", "invalid_emails"]
)

# Catalogue
plot_kpi(
    "KPI Catalogue",
    kpi_catalog,
    before_col="rows_before",
    after_col="rows_after",
    missing_col="missing_rows",
    extra_cols=["duplicates_removed"]
)

# Ventes
plot_kpi(
    "KPI Ventes",
    kpi_sales,
    before_col="rows_before",
    after_col="rows_after",
    missing_col="missing_rows",
    extra_cols=["duplicates_removed","refund_rows","invalid_dates","invalid_amounts"]
)
