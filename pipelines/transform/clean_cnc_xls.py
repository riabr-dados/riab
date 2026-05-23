"""Transform: CNC XLS antigos
Saida: 3 Parquets em pipelines/output/cleaned/
"""
from pathlib import Path

import pandas as pd

from common import data_sheets, latest_snapshot, read_excel_table, write_parquet

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

DATASETS = [
    {
        "slug": "cnc-financement-television",
        "file": "financement-television.xls",
        "table": "cnc_financement_television",
    },
    {
        "slug": "cnc-films-television",
        "file": "films-television.xls",
        "table": "cnc_films_television",
    },
    {
        "slug": "cnc-exportacao-programas-audiovisuais",
        "file": "exportacao-programas-audiovisuais.xls",
        "table": "cnc_exportacao_programas",
    },
]


def process_dataset(config: dict[str, str]) -> None:
    snapshot = latest_snapshot(RAW / config["slug"])
    path = snapshot / config["file"]
    try:
        xls = pd.ExcelFile(path, engine="xlrd")
        engine = "xlrd"
    except Exception:
        xls = pd.ExcelFile(path)
        engine = None
    frames = []

    for sheet in data_sheets(xls.sheet_names, extra_ignore=["reglementation"]):
        df = read_excel_table(path, sheet, header=6, engine=engine)
        df.insert(0, "sheet", sheet)
        frames.append(df)

    if not frames:
        raise ValueError(f"Nenhuma sheet de dados encontrada em {path}")

    result = pd.concat(frames, ignore_index=True, sort=False)
    write_parquet(result, config["table"], OUT)


def main() -> None:
    for config in DATASETS:
        process_dataset(config)
    print("CNC XLS OK.")


if __name__ == "__main__":
    main()
