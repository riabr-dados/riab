"""Publica cada tabela factual dos arquivos CNC como recurso independente.

Abas anuais com o mesmo desenho são consolidadas e recebem ``ano``. As demais
abas são exportadas separadamente para impedir que indicadores e unidades
distintos apareçam no mesmo download.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sys

import pandas as pd
import pyarrow.parquet as pq
import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "pipelines/transform") not in sys.path:
    sys.path.insert(0, str(ROOT / "pipelines/transform"))

from common import data_sheets, latest_snapshot, norm_col, normalize_columns, write_parquet  # noqa: E402

RAW = ROOT / "datasets"
OUT = ROOT / "pipelines/output/cleaned"
MANIFEST = ROOT / "catalog/cnc_resources.yaml"
SCHEMAS = ROOT / "catalog/schemas"

# slug, arquivo, prefixo. Arquivos separados da coleção geográfica têm
# prefixos próprios para manter nomes inequívocos.
FILES = [
    ("cnc-audience-television", "audience-television.xlsx", "cnc_audience_television"),
    ("cnc-consumo-vod", "consumo-menages-vod.xlsx", "cnc_consumo_vod"),
    ("cnc-distribution-salles", "distribution-films-salles.xlsx", "cnc_distribution_salles"),
    ("cnc-donnees-internationales", "donnees-internationales-cinema.xlsx", "cnc_donnees_internationales"),
    ("cnc-etablissements", "etablissements-cinematographiques.xlsx", "cnc_etablissements"),
    ("cnc-exportacao-programas-audiovisuais", "exportacao-programas-audiovisuais.xls", "cnc_exportacao_programas"),
    ("cnc-films-agrees", "films-agrees-production.xlsx", "cnc_films_agrees"),
    ("cnc-films-million-entrees", "films-plus-million-entrees.xlsx", "cnc_films_million_entrees"),
    ("cnc-films-television", "films-television.xls", "cnc_films_television"),
    ("cnc-financement-television", "financement-television.xls", "cnc_financement_television"),
    ("cnc-frequentation-salles", "frequentation-salles.xlsx", "cnc_frequentation_salles"),
    ("cnc-geographie-cinema", "geographie-par-commune.xlsx", "cnc_geographie_commune"),
    ("cnc-geographie-cinema", "geographie-par-departement.xlsx", "cnc_geographie_departement"),
    ("cnc-geographie-cinema", "geographie-par-region.xlsx", "cnc_geographie_region"),
    ("cnc-geographie-cinema", "geographie-par-unite-urbaine.xlsx", "cnc_geographie_urbain"),
    ("cnc-parc-cinematographique", "parc-cinematographique.xlsx", "cnc_parc_cinematographique"),
    ("cnc-public-films", "public-films.xlsx", "cnc_public_films"),
    ("cnc-public-vod", "public-vod.xlsx", "cnc_public_vod"),
    ("cnc-referencias-ativas-vod", "referencias-ativas-vod.xlsx", "cnc_referencias_ativas_vod"),
]

ANNUAL_PREFIXES = {"cnc_etablissements", "cnc_films_agrees", "cnc_films_million_entrees"}
ANNUAL_TITLES = {
    "cnc_etablissements": "Estabelecimentos cinematográficos por ano",
    "cnc_films_agrees": "Filmes aprovados para produção por ano",
    "cnc_films_million_entrees": "Filmes com mais de um milhão de entradas por ano",
}
EXTRA_IGNORE = {"fiche", "reglementation"}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return sha256(stream.read()).hexdigest()


def open_workbook(path: Path) -> pd.ExcelFile:
    """Abre inclusive arquivos OOXML publicados com extensão .xls."""
    try:
        return pd.ExcelFile(path, engine="xlrd" if path.suffix.lower() == ".xls" else None)
    except Exception:
        return pd.ExcelFile(path)


def find_header_row(raw: pd.DataFrame) -> int:
    """Localiza o cabeçalho que sucede a área de título, sem fixar uma linha."""
    limit = min(16, len(raw) - 1)
    for index in range(limit):
        current = raw.iloc[index].dropna()
        following = raw.iloc[index + 1].dropna()
        previous_count = len(raw.iloc[index - 1].dropna()) if index else 0
        if len(current) < 2 or len(following) < 2 or previous_count > 1:
            continue
        first = str(current.iloc[0]).strip().casefold()
        if first.startswith(("retour au menu", "source :", "source:", "note :", "note:")):
            continue
        return index
    raise ValueError("Cabeçalho factual não localizado nas primeiras 16 linhas")


def read_sheet(workbook: pd.ExcelFile, sheet: str) -> tuple[pd.DataFrame, str]:
    raw = workbook.parse(sheet, header=None)
    if len(raw) <= 2:
        raise ValueError(f"{workbook.io} — {sheet}: tabela sem linhas suficientes")
    title = next((str(value).strip() for value in raw.iloc[:10, 0].dropna()
                  if not str(value).strip().casefold().startswith("retour au menu")), sheet)
    header_row = find_header_row(raw)
    header = raw.iloc[header_row].tolist()
    names = []
    for index, value in enumerate(header, start=1):
        if pd.isna(value) or not str(value).strip():
            names.append("codigo_ou_categoria" if index == 1 else
                         "nome_ou_categoria" if index == 2 else f"dimensao_{index}")
        else:
            names.append(int(value) if isinstance(value, float) and value.is_integer() else value)
    frame = raw.iloc[header_row + 1:].copy()
    frame.columns = names
    frame = frame.replace(r"^\s*$", pd.NA, regex=True).dropna(how="all").dropna(axis=1, how="all")
    keep = []
    for _, row in frame.iterrows():
        filled = row.dropna()
        first = str(filled.iloc[0]).strip().casefold() if not filled.empty else ""
        keep.append(len(filled) >= 2 and not first.startswith(
            ("source :", "source:", "note :", "note:", "retour au menu")))
    frame = normalize_columns(frame.loc[keep])
    frame.insert(0, "sheet", sheet)
    frame.insert(1, "titulo_tabela", title)
    return frame, title


def unique_table(prefix: str, sheet: str, used: set[str]) -> str:
    base = f"{prefix}_{norm_col(sheet)}"
    table = base
    sequence = 2
    while table in used:
        table = f"{base}_{sequence}"
        sequence += 1
    used.add(table)
    return table


def schema_document(table: str, title: str, slug: str, filename: str, parquet: Path) -> dict:
    columns = []
    for field in pq.read_schema(parquet):
        description = {
            "arquivo": "Arquivo oficial publicado pelo CNC.",
            "sheet": "Aba original do arquivo CNC.",
            "titulo_tabela": "Título original da tabela.",
            "ano": "Ano representado pela aba anual original.",
            "snapshot_data": "Data do snapshot local.",
            "hash_arquivo": "SHA-256 do arquivo oficial.",
        }.get(field.name, f"Campo original normalizado: {field.name}.")
        columns.append({"name": field.name, "type": str(field.type), "nullable": field.nullable,
                        "description": description})
    return {
        "table": table,
        "description": title,
        "source_raw": slug,
        "source_file": filename,
        "columns": columns,
        "notes": ["Uma saída corresponde a uma tabela factual; abas temáticas diferentes não são empilhadas."],
    }


def write_resource(frame: pd.DataFrame, *, dataset: str, table: str, filename: str,
                   sheet: str, title: str, snapshot: str, file_hash: str) -> dict:
    frame = frame.copy()
    frame.insert(0, "arquivo", filename)
    frame["snapshot_data"] = snapshot
    frame["hash_arquivo"] = file_hash
    write_parquet(frame, table, OUT)
    parquet = OUT / f"{table}.parquet"
    schema = schema_document(table, title, dataset, filename, parquet)
    (SCHEMAS / f"{table}.yaml").write_text(
        yaml.safe_dump(schema, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8")
    return {"dataset": dataset, "table": table, "file": filename, "sheet": sheet,
            "title": title, "rows": len(frame), "columns": len(frame.columns),
            "source_sha256": file_hash, "snapshot": snapshot}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SCHEMAS.mkdir(parents=True, exist_ok=True)
    resources = []
    used: set[str] = set()
    for dataset, filename, prefix in FILES:
        snapshot = latest_snapshot(RAW / dataset)
        path = snapshot / filename
        file_hash = digest(path)
        workbook = open_workbook(path)
        sheets = [sheet for sheet in data_sheets(workbook.sheet_names, extra_ignore=EXTRA_IGNORE)
                  if norm_col(sheet) not in EXTRA_IGNORE]
        if prefix in ANNUAL_PREFIXES:
            sheets = [sheet for sheet in sheets if sheet.strip().isdigit()]
            frames = []
            titles = []
            for sheet in sheets:
                frame, title = read_sheet(workbook, sheet)
                frame.insert(2, "ano", int(sheet))
                frames.append(frame)
                titles.append(title)
            if not frames:
                raise ValueError(f"{filename}: nenhuma aba anual encontrada")
            used.add(prefix)
            resources.append(write_resource(
                pd.concat(frames, ignore_index=True, sort=False), dataset=dataset, table=prefix,
                filename=filename, sheet="abas anuais", title=ANNUAL_TITLES[prefix], snapshot=snapshot.name,
                file_hash=file_hash))
            continue
        for sheet in sheets:
            frame, title = read_sheet(workbook, sheet)
            if frame.empty:
                continue
            table = unique_table(prefix, sheet, used)
            resources.append(write_resource(frame, dataset=dataset, table=table, filename=filename,
                                             sheet=sheet, title=title, snapshot=snapshot.name,
                                             file_hash=file_hash))
    MANIFEST.write_text(yaml.safe_dump({"version": 1, "resources": resources},
                                       allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    print(f"CNC: {len(resources)} recursos independentes gerados")


if __name__ == "__main__":
    main()
