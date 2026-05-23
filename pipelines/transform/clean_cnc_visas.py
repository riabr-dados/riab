"""Transform: CNC visas d'exploitation
Saida: pipelines/output/cleaned/cnc_visas_exploitation.parquet
"""
from pathlib import Path

import pandas as pd

from common import latest_snapshot, normalize_columns, write_parquet

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    snapshot = latest_snapshot(RAW / "cnc-visas-exploitation")
    path = snapshot / "visas-exploitation-1945-2025.csv"

    df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
    df = normalize_columns(df)

    if "date" in df.columns:
        numeric_date = pd.to_numeric(df["date"], errors="coerce")
        if numeric_date.notna().sum() >= len(df) * 0.9:
            df["date"] = numeric_date.astype("Int64")
        else:
            df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    for column in ["n_de_visa", "numero_visa", "entrees"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")

    write_parquet(df, "cnc_visas_exploitation", OUT)


if __name__ == "__main__":
    main()
