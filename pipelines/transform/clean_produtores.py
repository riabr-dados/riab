"""
Transform: produtores de obras nao publicitarias brasileiras
Fonte: ancine-produtores-obras (CSV, latin1)
Saída: produtores_obras.parquet
"""
import pandas as pd
from pathlib import Path

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

SNAP = "snapshots/2026-05-19"

print("Processando produtores-de-obras-nao-publicitarias-brasileiras.csv …")
df = pd.read_csv(
    RAW / f"ancine-produtores-obras/{SNAP}/produtores-de-obras-nao-publicitarias-brasileiras.csv",
    encoding="latin1",
    sep=None,
    engine="python",
)

df.columns = [c.lower().strip() for c in df.columns]
# Expected cols: produtor, cnpj_produtor, pais_produtor, titulo_original, cpb
for col in df.columns:
    df[col] = df[col].astype(str).str.strip().replace("nan", None)

out = OUT / "produtores_obras.parquet"
df.to_parquet(out, index=False)
print(f"  -> {out} ({len(df)} linhas)")
print("Produtores OK.")
