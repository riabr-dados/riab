"""
Transform: projetos com renuncia fiscal (Lei Rouanet / ANCINE)
Fonte: ancine-renuncia-fiscal (CSV, latin1)
Saída: renuncia_fiscal.parquet
"""
import pandas as pd
from pathlib import Path


def fix_encoding(s: str) -> str:
    """Corrige mojibake UTF-8 lido como latin-1 (mesmo padrão de clean_obras.py)."""
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except Exception:
        return s

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

SNAP = "snapshots/2026-05-19"

print("Processando projetos-com-renuncia-fiscal.csv …")
df = pd.read_csv(
    RAW / f"ancine-renuncia-fiscal/{SNAP}/projetos-com-renuncia-fiscal.csv",
    encoding="latin1",
    sep=None,
    engine="python",
)

df.columns = [c.lower().strip() for c in df.columns]

# Dates
for col in ["data_pub_aprovacao_projeto", "data_primeira_liberacao"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")

# Monetary columns (may use comma as decimal)
money_cols = [c for c in df.columns if c.startswith("captado_") or c == "total_captado"]
for col in money_cols:
    if col in df.columns:
        df[col] = (
            df[col].astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .pipe(pd.to_numeric, errors="coerce")
        )

# String cleanup: corrige mojibake (fonte UTF-8 lida como latin-1)
str_cols = ["numero_salic", "titulo_projeto", "situacao_atual", "mecanismo",
            "proponente", "cnpj_proponente", "municipio_proponente", "uf_proponente"]
for col in str_cols:
    if col in df.columns:
        df[col] = df[col].apply(lambda x: fix_encoding(x).strip() if isinstance(x, str) else None)
        df[col] = df[col].replace({"": None, "nan": None})

out = OUT / "renuncia_fiscal.parquet"
df.to_parquet(out, index=False)
print(f"  -> {out} ({len(df)} linhas)")
print("Renuncia fiscal OK.")
