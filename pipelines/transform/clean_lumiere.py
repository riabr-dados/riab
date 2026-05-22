"""
Transform: dados Lumiere (observatório europeu do audiovisual)
Fontes:
  - lumiere-cinemas-europa (Excel) -> bilheteria_europa.parquet
  - lumiere-vod-europa     (Excel) -> vod_europa.parquet
"""
import pandas as pd
from pathlib import Path
from common import latest_snapshot

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

SNAP_CINEMAS = latest_snapshot(RAW / "lumiere-cinemas-europa")
SNAP_VOD = latest_snapshot(RAW / "lumiere-vod-europa")

# ── 1. Lumiere Cinemas Europa ─────────────────────────────────────────────────
print("Processando lumiere_search.xlsx …")
df = pd.read_excel(
    SNAP_CINEMAS / "lumiere_search.xlsx",
    sheet_name="lumiere search results",
)

df.columns = [
    c.strip().lower()
    .replace(" ", "_")
    .replace("-", "_")
    .replace("+", "")
    .replace("/", "_")
    for c in df.columns
]

rename = {
    "original_title": "titulo_original",
    "producing_country": "paises_producao",
    "production_year": "ano_producao",
    "directors": "diretores",
    "admissions_1996_2026": "admissoes_1996_2026",
    "total_eu27gb_since_1996": "total_eu27_gb_desde_1996",
}
df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

for col in ["admissoes_1996_2026", "total_eu27_gb_desde_1996"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
if "ano_producao" in df.columns:
    df["ano_producao"] = pd.to_numeric(df["ano_producao"], errors="coerce").astype("Int64")

# flag filmes com participacao brasileira
if "paises_producao" in df.columns:
    df["tem_brasil"] = df["paises_producao"].astype(str).str.contains(r"\bBR\b", regex=True)

out1 = OUT / "bilheteria_europa.parquet"
df.to_parquet(out1, index=False)
print(f"  -> {out1} ({len(df)} linhas)")

# ── 2. Lumiere VOD Europa ─────────────────────────────────────────────────────
print("Processando lumiere_vod_search.xlsx …")
df_vod = pd.read_excel(
    SNAP_VOD / "lumiere_vod_search.xlsx",
    sheet_name=0,
)

# keep only the most useful columns to avoid bloat
keep = [
    "Original title", "Producing country", "Production year",
    "Directors", "Work type", "Season", "Catalog", "Catalog group",
    "Business model", "Country", "Presence date",
    "Lumiere ID", "IMDb ID",
]
df_vod = df_vod[[c for c in keep if c in df_vod.columns]].copy()
df_vod.columns = [
    c.strip().lower()
    .replace(" ", "_")
    .replace("-", "_")
    for c in df_vod.columns
]
rename_vod = {
    "original_title": "titulo_original",
    "producing_country": "paises_producao",
    "production_year": "ano_producao",
    "directors": "diretores",
    "work_type": "tipo_obra",
    "business_model": "modelo_negocio",
    "presence_date": "data_presenca",
    "lumiere_id": "lumiere_id",
    "imdb_id": "imdb_id",
}
df_vod = df_vod.rename(columns={k: v for k, v in rename_vod.items() if k in df_vod.columns})

if "ano_producao" in df_vod.columns:
    df_vod["ano_producao"] = pd.to_numeric(df_vod["ano_producao"], errors="coerce").astype("Int64")
if "data_presenca" in df_vod.columns:
    df_vod["data_presenca"] = pd.to_datetime(df_vod["data_presenca"], dayfirst=True, errors="coerce")
if "paises_producao" in df_vod.columns:
    df_vod["tem_brasil"] = df_vod["paises_producao"].astype(str).str.contains(r"\bBR\b", regex=True)

out2 = OUT / "vod_europa.parquet"
df_vod.to_parquet(out2, index=False)
print(f"  -> {out2} ({len(df_vod)} linhas)")
print("Lumiere OK.")
