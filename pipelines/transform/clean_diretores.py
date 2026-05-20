"""
Transform: diretores de obras nao publicitarias brasileiras
Fonte: ancine-diretores-obras (CSV, latin1)
Saída: diretores_obras.parquet
"""
import pandas as pd
from pathlib import Path

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

SNAP = "snapshots/2026-05-19"

print("Processando diretores-de-obras-nao-publicitarias-brasileiras.csv …")
df = pd.read_csv(
    RAW / f"ancine-diretores-obras/{SNAP}/diretores-de-obras-nao-publicitarias-brasileiras.csv",
    encoding="latin1",
    sep=None,
    engine="python",
)

df.columns = [c.lower().strip() for c in df.columns]
# Expected cols: diretor, pais_diretor, titulo_original, cpb
for col in df.columns:
    df[col] = df[col].astype(str).str.strip().replace("nan", None)

out = OUT / "diretores_obras.parquet"
df.to_parquet(out, index=False)
print(f"  -> {out} ({len(df)} linhas)")
print("Diretores OK.")
