"""
Transform: ancine-fsa-projetos -> cleaned/fomento_fsa.parquet

Le o CSV de projetos FSA (latin-1, sep=;), extrai valores monetarios
das strings "R$ X,XX", converte tipos e salva como Parquet.
"""
import os
import re
import sys
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

RAW_DIR = os.path.join("datasets", "ancine-fsa-projetos", "snapshots")
OUT_FILE = os.path.join("pipelines", "output", "cleaned", "fomento_fsa.parquet")

RENAME = {
    "TITULO_PROJETO":             "titulo_projeto",
    "CHAMADA_PUBLICA":            "chamada_publica",
    "ANO_EDITAL":                 "ano_edital",
    "CNPJ_PROPONENTE":            "cnpj_proponente",
    "RAZAO_SOCIAL_PROPONENTE":    "razao_social_proponente",
    "CNPJ_PRODUTORA":             "cnpj_produtora",
    "RAZAO_SOCIAL_PRODUTORA":     "razao_social_produtora",
    "CNPJ_PROGRAMADORA":          "cnpj_programadora",
    "RAZAO_SOCIAL_PROGRAMADORA":  "razao_social_programadora",
    "DATA_EXTRATO_CONTRATO_DOU":  "data_extrato_contrato_dou",
    "VALOR_CONTRATO_DOU":         "valor_contrato_brl",
    "DATA_PRIMEIRO_DESEMBOLSO":   "data_primeiro_desembolso",
    "VALOR_TOTAL_LIBERADO":       "valor_total_liberado_brl",
}


def fix_encoding(s: str) -> str:
    """Corrige mojibake UTF-8 lido como latin-1 (mesmo padrão de clean_obras.py)."""
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except Exception:
        return s


def parse_brl(s):
    """Extrai valor numerico de 'R$ 1.234.567,89' -> 1234567.89"""
    if pd.isna(s) or not isinstance(s, str):
        return None
    # Remove "R$ ", pontos de milhar, troca virgula por ponto
    clean = re.sub(r"[R$\s\.]", "", s).replace(",", ".")
    try:
        return float(clean)
    except ValueError:
        return None


def find_snapshot():
    snapshots = sorted(
        d for d in os.listdir(RAW_DIR)
        if os.path.isdir(os.path.join(RAW_DIR, d))
    )
    if not snapshots:
        raise FileNotFoundError(f"Nenhum snapshot em {RAW_DIR}")
    return os.path.join(RAW_DIR, snapshots[-1])


def main():
    snap_dir = find_snapshot()
    csv_path = os.path.join(snap_dir, "projetos-fsa.csv")
    if not os.path.exists(csv_path):
        print(f"Arquivo nao encontrado: {csv_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Lendo {csv_path}...")
    df = pd.read_csv(csv_path, sep=";", encoding="latin-1", dtype=str, on_bad_lines="skip")
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={k: v for k, v in RENAME.items() if k in df.columns})
    df = df[[c for c in df.columns if c in RENAME.values()]]
    print(f"  {len(df):,} linhas carregadas")

    # Strings: corrige mojibake (fonte UTF-8 lida como latin-1)
    str_cols = ["titulo_projeto", "chamada_publica", "razao_social_proponente",
                "razao_social_produtora", "razao_social_programadora"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: fix_encoding(x).strip() if isinstance(x, str) else None)
            df[col] = df[col].replace({"": None, "nan": None})

    # CNPJs: manter como string, apenas strip
    for col in ["cnpj_proponente", "cnpj_produtora", "cnpj_programadora"]:
        if col in df.columns:
            df[col] = df[col].str.strip().replace({"": None})

    # Datas
    for col in ["data_extrato_contrato_dou", "data_primeiro_desembolso"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="%d/%m/%Y", errors="coerce")

    # Valores monetarios
    for col in ["valor_contrato_brl", "valor_total_liberado_brl"]:
        if col in df.columns:
            df[col] = df[col].apply(parse_brl)

    # Ano edital
    if "ano_edital" in df.columns:
        df["ano_edital"] = pd.to_numeric(df["ano_edital"], errors="coerce").astype("Int32")

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, OUT_FILE, compression="zstd")
    size_kb = os.path.getsize(OUT_FILE) / 1024
    print(f"Salvo: {OUT_FILE} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
