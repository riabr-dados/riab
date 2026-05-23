"""Transform: CNC complexos
Saida:
  - pipelines/output/cleaned/cnc_donnees_internationales.parquet
  - pipelines/output/cleaned/cnc_etablissements.parquet
  - pipelines/output/cleaned/cnc_films_agrees.parquet
"""
from pathlib import Path

import pandas as pd

from common import data_sheets, latest_snapshot, read_excel_table, write_parquet

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)


def concat_sheets(path: Path, sheets: list[str], header: int, label_col: str) -> pd.DataFrame:
    frames = []
    for sheet in sheets:
        df = read_excel_table(path, sheet, header=header)
        df.insert(0, label_col, sheet)
        if sheet.strip().isdigit():
            df.insert(0, "ano", int(sheet))
        frames.append(df)
    if not frames:
        raise ValueError(f"Nenhuma sheet de dados encontrada em {path}")
    return pd.concat(frames, ignore_index=True, sort=False)


def process_donnees_internationales() -> None:
    snapshot = latest_snapshot(RAW / "cnc-donnees-internationales")
    path = snapshot / "donnees-internationales-cinema.xlsx"
    xls = pd.ExcelFile(path)
    sheets = data_sheets(xls.sheet_names)
    df = concat_sheets(path, sheets, header=6, label_col="pays")
    write_parquet(df, "cnc_donnees_internationales", OUT)


def process_etablissements() -> None:
    snapshot = latest_snapshot(RAW / "cnc-etablissements")
    path = snapshot / "etablissements-cinematographiques.xlsx"
    xls = pd.ExcelFile(path)
    sheets = [sheet for sheet in data_sheets(xls.sheet_names) if sheet.strip().isdigit()]
    df = concat_sheets(path, sheets, header=4, label_col="sheet")
    write_parquet(df, "cnc_etablissements", OUT)


def process_films_agrees() -> None:
    snapshot = latest_snapshot(RAW / "cnc-films-agrees")
    path = snapshot / "films-agrees-production.xlsx"
    xls = pd.ExcelFile(path)
    sheets = [sheet for sheet in data_sheets(xls.sheet_names) if sheet.strip().isdigit()]
    df = concat_sheets(path, sheets, header=4, label_col="sheet")
    write_parquet(df, "cnc_films_agrees", OUT)


def main() -> None:
    process_donnees_internationales()
    process_etablissements()
    process_films_agrees()
    print("CNC complexos OK.")


if __name__ == "__main__":
    main()
