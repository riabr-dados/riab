"""
Transform: agentes_economicos
Fonte: ancine-agentes-economicos (CSV, latin1)
Saída: agentes_economicos.parquet
"""
import pandas as pd
from pathlib import Path
from common import latest_snapshot

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

SNAP = latest_snapshot(RAW / "ancine-agentes-economicos")

print("Processando agentes-economicos-regulares.csv …")
df = pd.read_csv(
    SNAP / "agentes-economicos-regulares.csv",
    encoding="latin1",
    sep=None,
    engine="python",
)

df.columns = [c.lower().strip() for c in df.columns]
rename = {
    "registro_ancine": "registro_ancine",
    "data_registro": "data_registro",
    "razao_social": "razao_social",
    "cnpj": "cnpj",
    "data_constituicao": "data_constituicao",
    "uf": "uf",
    "municipio": "municipio",
    "codigo_municipio_ibge": "codigo_municipio_ibge",
    "classificacao_agente_economico": "classificacao_agente_economico",
    "natureza_juridica": "natureza_juridica",
    "brasileiro_independente": "brasileiro_independente",
}
df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

for col in ["data_registro", "data_constituicao"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], format="%d/%m/%Y", errors="coerce")

for col in ["razao_social", "uf", "municipio", "classificacao_agente_economico",
            "natureza_juridica", "brasileiro_independente"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

out = OUT / "agentes_economicos.parquet"
df.to_parquet(out, index=False)
print(f"  -> {out} ({len(df)} linhas)")
print("Agentes economicos OK.")
