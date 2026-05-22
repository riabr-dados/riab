"""
Transform: deflator IPCA (IBGE) e preco medio de ingresso (ANCINE)
Fontes:
  - ibge-deflator-ipca   -> deflator_ipca.parquet
  - ancine-preco-medio-ingresso -> preco_ingresso.parquet
"""
import pandas as pd
from pathlib import Path
from common import latest_snapshot, normalize_header

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

SNAP_IPCA = latest_snapshot(RAW / "ibge-deflator-ipca")
SNAP_PRECO = latest_snapshot(RAW / "ancine-preco-medio-ingresso")

# ── 1. Deflator IPCA ─────────────────────────────────────────────────────────
print("Processando deflator_ipca_base2024.csv …")
df = pd.read_csv(
    SNAP_IPCA / "deflator_ipca_base2024.csv",
    encoding="utf-8-sig",
    sep=None,
    engine="python",
)
# normalise column names (BOM + quotes)
df.columns = [normalize_header(c) for c in df.columns]
# commas as decimal separators
for col in ["ipca_pct", "fator_real_2024"]:
    if col in df.columns:
        df[col] = (
            df[col].astype(str)
            .str.replace(",", ".", regex=False)
            .pipe(pd.to_numeric, errors="coerce")
        )
if "ano" in df.columns:
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")

out1 = OUT / "deflator_ipca.parquet"
df.to_parquet(out1, index=False)
print(f"  -> {out1} ({len(df)} linhas)")

# ── 2. Preco medio de ingresso ────────────────────────────────────────────────
print("Processando preco_medio_ingresso_ancine.csv …")
df2 = pd.read_csv(
    SNAP_PRECO / "preco_medio_ingresso_ancine.csv",
    encoding="latin1",
    sep=None,
    engine="python",
)
df2.columns = [normalize_header(c) for c in df2.columns]
for col in ["pmi_nominal", "fator_real_2024", "pmi_real_2024"]:
    if col in df2.columns:
        df2[col] = (
            df2[col].astype(str)
            .str.replace(",", ".", regex=False)
            .pipe(pd.to_numeric, errors="coerce")
        )
if "ano" in df2.columns:
    df2["ano"] = pd.to_numeric(df2["ano"], errors="coerce").astype("Int64")
for col in ["fonte", "observacao"]:
    if col in df2.columns:
        df2[col] = df2[col].astype(str).str.strip().replace("nan", None)

out2 = OUT / "preco_ingresso.parquet"
df2.to_parquet(out2, index=False)
print(f"  -> {out2} ({len(df2)} linhas)")
print("Deflator + Preco ingresso OK.")
