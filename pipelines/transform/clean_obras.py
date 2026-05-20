"""
Transform: ancine-obras-nao-publicitarias -> cleaned/obras.parquet

Le os 25 CSVs anuais (2002-2026) com encoding latin-1,
padroniza colunas, converte tipos e salva como Parquet UTF-8.
"""
import os
import re
import sys
import glob
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

RAW_DIR = os.path.join("datasets", "ancine-obras-nao-publicitarias", "snapshots")
OUT_FILE = os.path.join("pipelines", "output", "cleaned", "obras.parquet")

RENAME = {
    "TITULO_ORIGINAL":            "titulo_original",
    "CPB":                        "cpb",
    "DATA_EMISSAO_CPB":           "data_emissao_cpb",
    "SITUACAO_OBRA":              "situacao_obra",
    "TIPO_OBRA":                  "tipo_obra",
    "SUBTIPO_OBRA":               "subtipo_obra",
    "CLASSIFICACAO_OBRA":         "classificacao_obra",
    "ORGANIZACAO_TEMPORAL":       "organizacao_temporal",
    "DURACAO_TOTAL_MINUTOS":      "duracao_total_minutos",
    "QUANTIDADE_EPISODIOS":       "quantidade_episodios",
    "ANO_PRODUCAO_INICIAL":       "ano_producao_inicial",
    "ANO_PRODUCAO_FINAL":         "ano_producao_final",
    "SEGMENTO_DESTINACAO_INICIAL":"segmento_destinacao_inicial",
    "COPRODUCAO_INTERNACIONAL":   "coproducao_internacional",
    "REQUERENTE":                 "requerente",
    "CNPJ_REQUERENTE":            "cnpj_requerente",
    "UF_REQUERENTE":              "uf_requerente",
    "MUNICIPIO_REQUERENTE":       "municipio_requerente",
}


def fix_encoding(s: str) -> str:
    """Corrige mojibake latin-1/utf-8 que aparece ao ler com encoding errado."""
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except Exception:
        return s


def parse_float_br(s):
    """Converte '4,6' -> 4.6 e trata nulos."""
    if pd.isna(s) or s == "":
        return None
    try:
        return float(str(s).replace(",", "."))
    except ValueError:
        return None


def find_snapshots():
    """Retorna o snapshot mais recente (pasta YYYY-MM-DD mais recente)."""
    snapshots = sorted(
        d for d in os.listdir(RAW_DIR)
        if os.path.isdir(os.path.join(RAW_DIR, d))
    )
    if not snapshots:
        raise FileNotFoundError(f"Nenhum snapshot encontrado em {RAW_DIR}")
    return os.path.join(RAW_DIR, snapshots[-1])


def load_csv(path: str, ano: int) -> pd.DataFrame:
    """Le um CSV anual da ANCINE com encoding latin-1 e separador ;"""
    try:
        df = pd.read_csv(
            path,
            sep=";",
            encoding="latin-1",
            dtype=str,
            on_bad_lines="skip",
        )
    except Exception as e:
        print(f"  ERRO ao ler {os.path.basename(path)}: {e}", file=sys.stderr)
        return pd.DataFrame()

    # Corrige nomes de colunas (mojibake)
    df.columns = [fix_encoding(c).strip() for c in df.columns]

    # Descarta colunas desconhecidas, renomeia as conhecidas
    df = df.rename(columns={k: v for k, v in RENAME.items() if k in df.columns})
    known = list(RENAME.values())
    df = df[[c for c in df.columns if c in known]]

    # Adiciona ano do arquivo como coluna
    df["ano_arquivo"] = ano

    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica transformacoes de tipo e limpeza."""

    # Strings: strip + upper para campos categoricos
    str_cols = [
        "titulo_original", "situacao_obra", "tipo_obra", "subtipo_obra",
        "classificacao_obra", "organizacao_temporal", "segmento_destinacao_inicial",
        "coproducao_internacional", "requerente", "cnpj_requerente",
        "uf_requerente", "municipio_requerente",
    ]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: fix_encoding(x).strip().upper() if isinstance(x, str) else None
            )
            df[col] = df[col].replace({"": None, "NAN": None, "NONE": None})

    # CPB: strip simples (nao altera case)
    if "cpb" in df.columns:
        df["cpb"] = df["cpb"].apply(lambda x: x.strip() if isinstance(x, str) else None)

    # Data
    if "data_emissao_cpb" in df.columns:
        df["data_emissao_cpb"] = pd.to_datetime(
            df["data_emissao_cpb"], format="%d/%m/%Y", errors="coerce"
        )

    # Numericos
    if "duracao_total_minutos" in df.columns:
        df["duracao_total_minutos"] = df["duracao_total_minutos"].apply(parse_float_br)

    for col in ["quantidade_episodios", "ano_producao_inicial", "ano_producao_final"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].apply(
                lambda x: x.replace(",", "").replace(".", "") if isinstance(x, str) else x
            ), errors="coerce").astype("Int32")

    # Boolean
    if "coproducao_internacional" in df.columns:
        df["coproducao_internacional"] = df["coproducao_internacional"].map(
            {"SIM": True, "NAO": False, "NÃO": False}
        )

    return df


def main():
    snap_dir = find_snapshots()
    print(f"Snapshot: {snap_dir}")

    csvs = sorted(glob.glob(os.path.join(snap_dir, "obras-nao-pub-brasileiras-*.csv")))
    if not csvs:
        print("Nenhum CSV encontrado.", file=sys.stderr)
        sys.exit(1)

    frames = []
    for path in csvs:
        # Extrai ano do nome do arquivo
        match = re.search(r"(\d{4})\.csv$", path)
        ano = int(match.group(1)) if match else 0
        print(f"  Lendo {os.path.basename(path)} (ano {ano})...")
        df = load_csv(path, ano)
        if not df.empty:
            frames.append(df)

    if not frames:
        print("Nenhum dado carregado.", file=sys.stderr)
        sys.exit(1)

    combined = pd.concat(frames, ignore_index=True)
    print(f"Total bruto: {len(combined):,} linhas")

    combined = transform(combined)

    # Remove duplicatas pelo CPB (pode haver entradas em mais de um arquivo anual)
    before = len(combined)
    combined = combined.drop_duplicates(subset=["cpb"], keep="last")
    print(f"Apos deduplicacao por CPB: {len(combined):,} linhas ({before - len(combined):,} removidas)")

    # Salva como Parquet
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    table = pa.Table.from_pandas(combined, preserve_index=False)
    pq.write_table(table, OUT_FILE, compression="zstd")
    size_mb = os.path.getsize(OUT_FILE) / 1048576
    print(f"Salvo: {OUT_FILE} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
