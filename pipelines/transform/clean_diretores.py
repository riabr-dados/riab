"""
Transform: diretores de obras nao publicitarias brasileiras
Fonte: ancine-diretores-obras (CSV, latin1)
Saída: diretores_obras.parquet
"""
import pandas as pd
from pathlib import Path
from common import latest_snapshot


def fix_encoding(s: str) -> str:
    """Corrige mojibake UTF-8 lido como latin-1."""
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except Exception:
        return s

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

SNAP = latest_snapshot(RAW / "ancine-diretores-obras")

print("Processando diretores-de-obras-nao-publicitarias-brasileiras.csv …")
df = pd.read_csv(
    SNAP / "diretores-de-obras-nao-publicitarias-brasileiras.csv",
    encoding="latin1",
    sep=None,
    engine="python",
)

df.columns = [c.lower().strip() for c in df.columns]
# Expected cols: diretor, pais_diretor, titulo_original, cpb
# Corrige mojibake (fonte UTF-8 lida como latin-1)
for col in df.columns:
    df[col] = df[col].apply(lambda x: fix_encoding(x).strip() if isinstance(x, str) else None)
    df[col] = df[col].replace({"": None, "nan": None})

out = OUT / "diretores_obras.parquet"
df.to_parquet(out, index=False)
print(f"  -> {out} ({len(df)} linhas)")
print("Diretores OK.")
