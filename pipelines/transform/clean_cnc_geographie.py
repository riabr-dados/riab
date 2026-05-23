"""Transform: CNC geographie du cinema
Saida: 4 Parquets em pipelines/output/cleaned/
"""
from pathlib import Path

import pandas as pd

from common import data_sheets, latest_snapshot, read_excel_table, write_parquet

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

FILES = {
    "geographie-par-commune.xlsx": "cnc_geographie_commune",
    "geographie-par-departement.xlsx": "cnc_geographie_departement",
    "geographie-par-region.xlsx": "cnc_geographie_region",
    "geographie-par-unite-urbaine.xlsx": "cnc_geographie_urbain",
}


def process_file(snapshot: Path, filename: str, table: str) -> None:
    path = snapshot / filename
    xls = pd.ExcelFile(path)
    frames = []

    for sheet in data_sheets(xls.sheet_names):
        df = read_excel_table(path, sheet, header=6)
        df.insert(0, "sheet", sheet)
        frames.append(df)

    if not frames:
        raise ValueError(f"Nenhuma sheet de dados encontrada em {path}")

    result = pd.concat(frames, ignore_index=True, sort=False)
    write_parquet(result, table, OUT)


def main() -> None:
    snapshot = latest_snapshot(RAW / "cnc-geographie-cinema")
    for filename, table in FILES.items():
        process_file(snapshot, filename, table)
    print("CNC geographie OK.")


if __name__ == "__main__":
    main()
