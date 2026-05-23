"""Transform: BFI Statistical Yearbook 2023, lote 2
Saida: 4 Parquets em pipelines/output/cleaned/
"""
from pathlib import Path

import pandas as pd

from common import latest_snapshot, read_bfi_sheet, write_parquet

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

FILES = [
    ("audiences.ods", "bfi_audiences"),
    ("exhibition.ods", "bfi_exhibition"),
    ("film-industry-employment.ods", "bfi_emprego_industria"),
    ("film-industry-companies.ods", "bfi_empresas_industria"),
]


def t_sheets(xls: pd.ExcelFile) -> list[str]:
    return [sheet for sheet in xls.sheet_names if sheet.startswith("T")]


def process_file(snapshot: Path, filename: str, table: str) -> None:
    path = snapshot / filename
    xls = pd.ExcelFile(path, engine="odf")
    frames = []

    for sheet in t_sheets(xls):
        df = read_bfi_sheet(xls, sheet)
        df.insert(0, "arquivo", filename)
        frames.append(df)

    result = pd.concat(frames, ignore_index=True, sort=False)
    write_parquet(result, table, OUT)


def main() -> None:
    snapshot = latest_snapshot(RAW / "bfi-statistical-yearbook-2023")
    for filename, table in FILES:
        process_file(snapshot, filename, table)
    print("BFI lote 2 OK.")


if __name__ == "__main__":
    main()
