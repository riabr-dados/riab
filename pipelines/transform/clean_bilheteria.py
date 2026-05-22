"""
Transform: bilheteria domestica
Fontes:
  - ancine-bilheteria-consolidada  (Excel, histórico de obras BR)
  - ancine-bilheteria-agregada-filme-ano (CSV, público por filme/ano, todos os países)
Saída:
  - bilheteria_consolidada_br.parquet  — top filmes brasileiros histórico
  - bilheteria_por_filme_ano.parquet   — série temporal completa (todos os países)
"""
import pandas as pd
from pathlib import Path
from common import latest_snapshot

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

SNAP_CONSOL = latest_snapshot(RAW / "ancine-bilheteria-consolidada")
SNAP_ANO = latest_snapshot(RAW / "ancine-bilheteria-agregada-filme-ano")

# ── 1. Bilheteria consolidada BR (Excel) ─────────────────────────────────────
print("Processando bilheteria_brasileira_consolidada.xlsx …")
df_consol = pd.read_excel(
    SNAP_CONSOL / "bilheteria_brasileira_consolidada.xlsx",
    sheet_name="Bilheteria BR Completa",
)
df_consol.columns = ["rank", "titulo", "ano_lancamento", "publico_total", "fonte"]
df_consol = df_consol.dropna(subset=["titulo"])
df_consol["rank"] = pd.to_numeric(df_consol["rank"], errors="coerce").astype("Int64")
df_consol["ano_lancamento"] = pd.to_numeric(df_consol["ano_lancamento"], errors="coerce").astype("Int64")
df_consol["publico_total"] = pd.to_numeric(df_consol["publico_total"], errors="coerce").astype("Int64")
df_consol["titulo"] = df_consol["titulo"].astype(str).str.strip()
df_consol["fonte"] = df_consol["fonte"].astype(str).str.strip()

out1 = OUT / "bilheteria_consolidada_br.parquet"
df_consol.to_parquet(out1, index=False)
print(f"  -> {out1} ({len(df_consol)} linhas)")

# ── 2. Bilheteria por filme/ano (CSV) ────────────────────────────────────────
print("Processando por_filme_ano.csv …")
df_ano = pd.read_csv(
    SNAP_ANO / "por_filme_ano.csv",
    encoding="utf-8-sig",
    sep=None,
    engine="python",
)
df_ano.columns = [c.lower() for c in df_ano.columns]
# rename to snake_case
rename = {
    "cpb_roe": "cpb_roe",
    "titulo_brasil": "titulo_brasil",
    "titulo_original": "titulo_original",
    "pais_obra": "pais_obra",
    "ano": "ano",
    "publico": "publico",
}
df_ano = df_ano.rename(columns=rename)
df_ano["ano"] = pd.to_numeric(df_ano["ano"], errors="coerce").astype("Int64")
df_ano["publico"] = pd.to_numeric(df_ano["publico"], errors="coerce").astype("Int64")
def _clean_str(series):
    """Strip sem converter NaN em string 'nan'."""
    return series.where(series.notna(), other=None).str.strip().replace({"": None})

df_ano["titulo_brasil"]   = _clean_str(df_ano["titulo_brasil"])
df_ano["titulo_original"] = _clean_str(df_ano["titulo_original"])
df_ano["pais_obra"]       = _clean_str(df_ano["pais_obra"])

out2 = OUT / "bilheteria_por_filme_ano.parquet"
df_ano.to_parquet(out2, index=False)
print(f"  -> {out2} ({len(df_ano)} linhas)")

print("Bilheteria OK.")
