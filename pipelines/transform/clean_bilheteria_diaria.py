"""Converte os ZIPs oficiais de bilheteria diária em Parquets anuais homogêneos.

Os CSVs oficiais são UTF-8. A leitura é feita diretamente do ZIP em lotes, sem
extrair os ~13 GB para o disco. Cada saída contém apenas uma granularidade:
uma linha reportada pela distribuidora ou exibidora, conforme a fonte.
"""
from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pacsv
import pyarrow.parquet as pq
import yaml

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "outputs/auditoria-pda-20260908/official/packages"
OUT = ROOT / "pipelines/output/cleaned"
SCHEMAS = ROOT / "catalog/schemas"

SOURCES = {
    "distribuidora": PACKAGE_DIR / "bilheteria-diaria-obras-por-distribuidoras-csv.zip",
    "exibidora": PACKAGE_DIR / "bilheteria-diaria-obras-por-exibidoras-csv.zip",
}


def snake(name: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", name.lower())).strip("_")


def normalize_batch(batch: pa.RecordBatch, source_file: str) -> pa.Table:
    table = pa.Table.from_batches([batch]).rename_columns([snake(c) for c in batch.schema.names])
    columns = []
    for name in table.column_names:
        values = table[name]
        if name == "data_exibicao":
            values = pc.strptime(values, format="%d/%m/%Y", unit="s", error_is_null=True).cast(pa.date32())
        elif name == "sessao":
            values = pc.strptime(values, format="%d/%m/%Y %H:%M:%S", unit="s", error_is_null=True)
        elif name == "publico":
            values = pc.cast(pc.if_else(pc.equal(values, ""), None, values), pa.int64(), safe=False)
        columns.append(values)
    table = pa.Table.from_arrays(columns, names=table.column_names)
    return table.append_column("arquivo_origem", pa.array([source_file] * table.num_rows, pa.string()))


def write_schema(kind: str, year: int, parquet: Path, schema_dir: Path = SCHEMAS) -> None:
    descriptions = {
        "data_exibicao": "Data da exibição informada à ANCINE.",
        "sessao": "Data e horário da sessão informada pela exibidora.",
        "publico": "Público informado na linha da fonte.",
        "cpb_roe": "Identificador CPB ou ROE da obra.",
        "arquivo_origem": "Arquivo CSV oficial do qual a linha foi lida.",
    }
    columns = [
        {
            "name": field.name,
            "type": str(field.type),
            "nullable": field.nullable,
            "description": descriptions.get(field.name, f"Campo oficial normalizado: {field.name}."),
        }
        for field in pq.read_schema(parquet)
    ]
    table = parquet.stem
    document = {
        "table": table,
        "description": f"Bilheteria diária informada por {kind}s em {year}; uma linha por registro da fonte.",
        "source_raw": f"ancine-bilheteria-diaria-{kind}s",
        "columns": columns,
        "notes": [
            "Partição anual detalhada; não contém agregados.",
            "Os textos foram decodificados como UTF-8 e os campos originais foram preservados.",
        ],
    }
    schema_dir.mkdir(parents=True, exist_ok=True)
    (schema_dir / f"{table}.yaml").write_text(
        yaml.safe_dump(document, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8"
    )


def convert_zip(
    kind: str, source: Path, output_dir: Path = OUT, schema_dir: Path | None = None
) -> dict[int, int]:
    if not source.is_file():
        raise FileNotFoundError(source)
    output_dir.mkdir(parents=True, exist_ok=True)
    writers: dict[int, pq.ParquetWriter] = {}
    rows: dict[int, int] = {}
    try:
        with zipfile.ZipFile(source) as archive:
            members = sorted(
                (i for i in archive.infolist() if i.filename.lower().endswith(".csv")),
                key=lambda item: item.filename,
            )
            for index, info in enumerate(members, 1):
                match = re.search(r"-(20\d{2})-", Path(info.filename).name)
                if not match:
                    raise ValueError(f"Ano ausente no nome: {info.filename}")
                year = int(match.group(1))
                with archive.open(info) as raw:
                    names = raw.readline().decode("utf-8-sig").rstrip("\r\n").split(";")
                    reader = pacsv.open_csv(
                        pa.PythonFile(raw),
                        read_options=pacsv.ReadOptions(
                            encoding="utf8", block_size=8 * 1024 * 1024, column_names=names
                        ),
                        parse_options=pacsv.ParseOptions(delimiter=";", quote_char='"'),
                        convert_options=pacsv.ConvertOptions(
                            column_types={name: pa.string() for name in names}, strings_can_be_null=False
                        ),
                    )
                    for batch in reader:
                        table = normalize_batch(batch, Path(info.filename).name)
                        if year not in writers:
                            path = output_dir / f"bilheteria_diaria_{kind}_detalhe_{year}.parquet"
                            writers[year] = pq.ParquetWriter(path, table.schema, compression="zstd")
                            rows[year] = 0
                        if table.schema != writers[year].schema:
                            raise ValueError(f"Schema divergente em {info.filename}")
                        writers[year].write_table(table)
                        rows[year] += table.num_rows
                if index % 25 == 0 or index == len(members):
                    print(f"{kind}: {index}/{len(members)} arquivos; {sum(rows.values()):,} linhas")
    finally:
        for writer in writers.values():
            writer.close()
    schema_dir = schema_dir or (SCHEMAS if output_dir.resolve() == OUT.resolve() else output_dir / "schemas")
    for year in rows:
        write_schema(
            kind, year, output_dir / f"bilheteria_diaria_{kind}_detalhe_{year}.parquet", schema_dir
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=sorted(SOURCES), action="append")
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    for kind in args.kind or SOURCES:
        rows = convert_zip(kind, SOURCES[kind], args.output_dir)
        print(f"{kind}: {sum(rows.values()):,} linhas em {len(rows)} anos")


if __name__ == "__main__":
    main()
