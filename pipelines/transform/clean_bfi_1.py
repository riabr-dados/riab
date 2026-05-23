"""Transform: BFI Statistical Yearbook 2023, lote 1
Saida: 4 Parquets em pipelines/output/cleaned/
"""
from pathlib import Path

import pandas as pd

from common import latest_snapshot, read_bfi_sheet, write_parquet

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

FILES = [
    ("uk-film-market.ods", "bfi_uk_film_market", ["T1", "T2", "T3"]),
    ("top-films-2023.ods", "bfi_top_films_2023", ["T1"]),
    ("uk-film-economy.ods", "bfi_uk_film_economy", ["T1"]),
    ("box-office-2023.ods", "bfi_box_office_2023", ["T1", "T2"]),
]


def process_file(snapshot: Path, filename: str, table: str, sheets: list[str]) -> None:
    path = snapshot / filename
    xls = pd.ExcelFile(path, engine="odf")
    frames = []

    for sheet in sheets:
        df = read_bfi_sheet(xls, sheet)
        df.insert(0, "arquivo", filename)
        frames.append(df)

    result = pd.concat(frames, ignore_index=True, sort=False)
    write_parquet(result, table, OUT)


def main() -> None:
    snapshot = latest_snapshot(RAW / "bfi-statistical-yearbook-2023")
    for filename, table, sheets in FILES:
        process_file(snapshot, filename, table, sheets)
    print("BFI lote 1 OK.")


if __name__ == "__main__":
    main()
