"""Transform: datasets CNC simples
Saida: 9 Parquets em pipelines/output/cleaned/
"""
from pathlib import Path
import re
import unicodedata

import pandas as pd

from common import latest_snapshot

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

IGNORE_SHEETS = {"sommaire", "definitions", "sources", "index", "esri_mapinfo_sheet"}

DATASETS = [
    {
        "slug": "cnc-frequentation-salles",
        "file": "frequentation-salles.xlsx",
        "table": "cnc_frequentation_salles",
        "sheet": "freqciné",
    },
    {
        "slug": "cnc-audience-television",
        "file": "audience-television.xlsx",
        "table": "cnc_audience_television",
    },
    {
        "slug": "cnc-public-films",
        "file": "public-films.xlsx",
        "table": "cnc_public_films",
    },
    {
        "slug": "cnc-public-vod",
        "file": "public-vod.xlsx",
        "table": "cnc_public_vod",
    },
    {
        "slug": "cnc-consumo-vod",
        "file": "consumo-menages-vod.xlsx",
        "table": "cnc_consumo_vod",
    },
    {
        "slug": "cnc-referencias-ativas-vod",
        "file": "referencias-ativas-vod.xlsx",
        "table": "cnc_referencias_ativas_vod",
    },
    {
        "slug": "cnc-parc-cinematographique",
        "file": "parc-cinematographique.xlsx",
        "table": "cnc_parc_cinematographique",
    },
    {
        "slug": "cnc-distribution-salles",
        "file": "distribution-films-salles.xlsx",
        "table": "cnc_distribution_salles",
    },
]


def strip_accents(value) -> str:
    return (
        unicodedata.normalize("NFKD", str(value))
        .encode("ascii", "ignore")
        .decode("ascii")
    )


def norm_col(value) -> str:
    value = strip_accents(value).strip().lower()
    value = re.sub(r"[^0-9a-z]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "coluna"


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how="all").dropna(axis=1, how="all").copy()

    counts: dict[str, int] = {}
    columns = []
    for index, column in enumerate(df.columns, start=1):
        name = norm_col(column)
        if name == "unnamed":
            name = f"coluna_{index}"
        counts[name] = counts.get(name, 0) + 1
        if counts[name] > 1:
            name = f"{name}_{counts[name]}"
        columns.append(name)

    df.columns = columns
    for column, dtype in df.dtypes.items():
        if pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
            df[column] = df[column].astype("string")
    return df


def sheet_key(sheet: str) -> str:
    return norm_col(sheet)


def first_data_sheet(xls: pd.ExcelFile) -> str:
    for sheet in xls.sheet_names:
        if sheet_key(sheet) not in IGNORE_SHEETS:
            return sheet
    raise ValueError("Nenhuma sheet de dados encontrada")


def read_header6(path: Path, sheet: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet, header=6)
    return normalize_columns(df)


def write_table(df: pd.DataFrame, table: str) -> None:
    out = OUT / f"{table}.parquet"
    df.to_parquet(out, index=False)
    print(f"{table}.parquet  {len(df)} linhas")


def process_simple_dataset(config: dict[str, str]) -> None:
    snapshot = latest_snapshot(RAW / config["slug"])
    path = snapshot / config["file"]
    xls = pd.ExcelFile(path)
    sheet = config.get("sheet") or first_data_sheet(xls)
    df = read_header6(path, sheet)
    write_table(df, config["table"])


def process_films_million_entrees() -> None:
    snapshot = latest_snapshot(RAW / "cnc-films-million-entrees")
    path = snapshot / "films-plus-million-entrees.xlsx"
    xls = pd.ExcelFile(path)
    frames = []

    for sheet in xls.sheet_names:
        if not sheet.strip().isdigit():
            continue
        df = read_header6(path, sheet)
        df["ano"] = int(sheet)
        frames.append(df)

    if not frames:
        raise ValueError("Nenhuma sheet anual encontrada em films-plus-million-entrees.xlsx")

    result = pd.concat(frames, ignore_index=True)
    write_table(result, "cnc_films_million_entrees")


def main() -> None:
    for config in DATASETS:
        process_simple_dataset(config)
    process_films_million_entrees()
    print("CNC simples OK.")


if __name__ == "__main__":
    main()
