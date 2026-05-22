"""Transform: dataset ACAU (Agencia del Cine y el Audiovisual del Uruguay)
Fonte: acau-uruguay-apoios-audiovisual
Saida: pipelines/output/cleaned/acau_apoios.parquet
"""
import unicodedata
import pandas as pd
from pathlib import Path
from common import latest_snapshot

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

SNAP = latest_snapshot(RAW / "acau-uruguay-apoios-audiovisual")

def normalize_col(name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_name = nfkd.encode("ascii", "ignore").decode("ascii")
    return ascii_name.strip().lower().replace(" ", "_")

def comma_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", "."), errors="coerce")

df = pd.read_csv(
    SNAP / "acau-apoios-reembolsos-projetos-audiovisuais-2013-2024.csv",
    encoding="utf-8",
    dtype=str,
)

df.columns = [normalize_col(c) for c in df.columns]

for col in ["monto_adjudicado_corriente", "monto_adjudicado_constante", "monto_ejecutado_corriente"]:
    df[col] = comma_float(df[col])

df["rut"] = pd.to_numeric(df["rut"], errors="coerce").astype("Int64")
df["ano_instrumento"] = pd.to_numeric(df["ano_instrumento"], errors="coerce").astype("Int16")
df["fecha_de_resolucion"] = pd.to_datetime(df["fecha_de_resolucion"], dayfirst=True, errors="coerce")

out_path = OUT / "acau_apoios.parquet"
df.to_parquet(out_path, index=False)
print(f"acau_apoios.parquet  {len(df)} linhas  -> {out_path}")
