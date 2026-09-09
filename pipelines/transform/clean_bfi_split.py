"""Publica cada tabela T do BFI Statistical Yearbook como recurso independente."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import re
import sys

import pandas as pd
import pyarrow.parquet as pq
import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "pipelines/transform") not in sys.path:
    sys.path.insert(0, str(ROOT / "pipelines/transform"))

from common import latest_snapshot, read_bfi_sheet, write_parquet  # noqa: E402

RAW = ROOT / "datasets/bfi-statistical-yearbook-2023"
OUT = ROOT / "pipelines/output/cleaned"
MANIFEST = ROOT / "catalog/bfi_resources.yaml"
SCHEMAS = ROOT / "catalog/schemas"

FILES = {
    "audiences.ods": ("bfi-publicos-cinema", "bfi_audiences"),
    "box-office-2023.ods": ("bfi-bilheteria-2023", "bfi_box_office_2023"),
    "exhibition.ods": ("bfi-exibicao-cinematografica", "bfi_exhibition"),
    "film-education.ods": ("bfi-educacao-cinematografica", "bfi_educacao_cinematografica"),
    "film-industry-companies.ods": ("bfi-empresas-industria", "bfi_empresas_industria"),
    "film-industry-employment.ods": ("bfi-emprego-industria", "bfi_emprego_industria"),
    "film-on-digital-video.ods": ("bfi-video-digital", "bfi_video_digital"),
    "film-on-physical-video.ods": ("bfi-video-fisico", "bfi_video_fisico"),
    "film-on-television.ods": ("bfi-filmes-televisao", "bfi_filmes_televisao"),
    "public-investment-in-film.ods": ("bfi-investimento-publico", "bfi_investimento_publico"),
    "screen-sector-certification.ods": ("bfi-certificacao-obras", "bfi_certificacao_obras"),
    "top-films-2023.ods": ("bfi-top-filmes-2023", "bfi_top_films_2023"),
    "uk-film-economy.ods": ("bfi-economia-do-cinema", "bfi_uk_film_economy"),
    "uk-film-market.ods": ("bfi-mercado-cinematografico", "bfi_uk_film_market"),
    "uk-films-talent-worldwide.ods": ("bfi-talentos-britanicos-mundo", "bfi_talentos_mundo"),
}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return sha256(stream.read()).hexdigest()


def schema_document(table: str, title: str, source_file: str, parquet: Path) -> dict:
    schema = pq.read_schema(parquet)
    columns = []
    for field in schema:
        description = {
            "arquivo": "Arquivo ODS oficial do BFI.",
            "sheet": "Aba original no arquivo ODS.",
            "titulo_tabela": "Título original da tabela no BFI Statistical Yearbook.",
            "snapshot_data": "Data do snapshot local.",
            "hash_arquivo": "SHA-256 do arquivo ODS oficial.",
        }.get(field.name, f"Campo original normalizado: {field.name}.")
        columns.append({"name": field.name, "type": str(field.type),
                        "nullable": field.nullable, "description": description})
    return {
        "table": table,
        "description": title,
        "source_raw": "bfi-statistical-yearbook-2023",
        "source_file": source_file,
        "columns": columns,
        "notes": ["Uma saída corresponde a uma única aba factual do ODS; nenhuma aba T é empilhada com outra."],
    }


def main() -> None:
    snapshot = latest_snapshot(RAW)
    resources = []
    OUT.mkdir(parents=True, exist_ok=True)
    SCHEMAS.mkdir(parents=True, exist_ok=True)
    for filename, (dataset, prefix) in FILES.items():
        path = snapshot / filename
        file_hash = digest(path)
        workbook = pd.ExcelFile(path, engine="odf")
        sheets = [sheet for sheet in workbook.sheet_names if re.fullmatch(r"T\d+", sheet)]
        if not sheets:
            raise ValueError(f"{filename}: nenhuma aba T encontrada")
        for sheet in sheets:
            number = int(sheet[1:])
            table = f"{prefix}_t{number:02d}"
            frame = read_bfi_sheet(workbook, sheet)
            frame.insert(0, "arquivo", filename)
            frame["snapshot_data"] = snapshot.name
            frame["hash_arquivo"] = file_hash
            write_parquet(frame, table, OUT)
            title = (frame["titulo_tabela"].dropna().iloc[0]
                     if "titulo_tabela" in frame and frame["titulo_tabela"].notna().any()
                     else f"{filename} — {sheet}")
            schema = schema_document(table, str(title), filename, OUT / f"{table}.parquet")
            (SCHEMAS / f"{table}.yaml").write_text(
                yaml.safe_dump(schema, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8")
            resources.append({
                "dataset": dataset, "table": table, "file": filename, "sheet": sheet,
                "title": str(title), "rows": len(frame), "columns": len(frame.columns),
                "source_sha256": file_hash, "snapshot": snapshot.name,
            })
    MANIFEST.write_text(yaml.safe_dump({"version": 1, "resources": resources},
                                       allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    print(f"BFI: {len(resources)} recursos independentes gerados")


if __name__ == "__main__":
    main()
