"""
Le os ~13 GB de CSV diario de bilheteria em ~/Downloads/bilheteria-diaria-obras-por-{exibidoras,distribuidoras}-csv/
e gera agregados leves em pipelines/output/cleaned/ usando DuckDB nativo.

Saidas (parquet):
 - bilheteria_diaria_exibidora_filme_ano.parquet  (cpb_roe, ano, cnpj_exibidor, exibidora, publico_total, sessoes, n_complexos)
 - bilheteria_diaria_distribuidora_filme_ano.parquet (cpb_roe, ano, cnpj_distribuidor, distribuidora, publico_total)
 - bilheteria_diaria_municipio_filme_ano.parquet (cpb_roe, ano, uf, municipio, publico_total)
 - bilheteria_diaria_exibidora_ano.parquet  (exibidora, cnpj_exibidor, ano, publico_total, n_complexos, n_filmes)

Uso:
   .venv/Scripts/python.exe pipelines/transform/aggregate_bilheteria_diaria.py
"""
import os
import re
import sys
import tempfile
from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.csv as pcsv
import pyarrow.parquet as pq

HOME = Path.home()
EXIB_DIR = HOME / "Downloads" / "bilheteria-diaria-obras-por-exibidoras-csv"
DIST_DIR = HOME / "Downloads" / "bilheteria-diaria-obras-por-distribuidoras-csv"
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

STAGE = Path(tempfile.gettempdir()) / "ridab_bilheteria_stage"
STAGE.mkdir(parents=True, exist_ok=True)


def csvs_to_staging_parquet(src_dir: Path, stage_file: Path, kind: str) -> int:
    """Read every CSV via pyarrow (latin1 → UTF-8 in arrow), write a single staged parquet."""
    if stage_file.exists():
        n = pq.ParquetFile(stage_file).metadata.num_rows
        print(f"      [cache] {stage_file.name} ja existe ({n:,} linhas) — pulando releitura")
        return n

    files = sorted(src_dir.glob("*.csv"))
    print(f"      Lendo {len(files)} arquivos {kind}...")
    read_opts = pcsv.ReadOptions(encoding="latin1", use_threads=True)
    parse_opts = pcsv.ParseOptions(delimiter=";", quote_char='"')
    conv_opts = pcsv.ConvertOptions(strings_can_be_null=True)

    writer = None
    total = 0
    for i, f in enumerate(files):
        try:
            tbl = pcsv.read_csv(str(f), read_options=read_opts, parse_options=parse_opts, convert_options=conv_opts)
        except Exception as exc:
            print(f"      [SKIP] {f.name}: {exc}")
            continue
        # Cast all columns to string for uniform schema
        tbl = tbl.cast(pa.schema([(name, pa.string()) for name in tbl.column_names]))
        if writer is None:
            writer = pq.ParquetWriter(stage_file, tbl.schema, compression="zstd")
        else:
            # ensure same column order
            tbl = tbl.select(writer.schema.names) if set(tbl.column_names) >= set(writer.schema.names) else tbl
        writer.write_table(tbl)
        total += tbl.num_rows
        if (i + 1) % 50 == 0:
            print(f"        ...{i+1}/{len(files)} arquivos, {total:,} linhas")
    if writer:
        writer.close()
    print(f"      [OK] staged {total:,} linhas em {stage_file.name}")
    return total


def main():
    if not EXIB_DIR.exists():
        print(f"[ERR] {EXIB_DIR} nao existe", file=sys.stderr)
        return 1
    if not DIST_DIR.exists():
        print(f"[ERR] {DIST_DIR} nao existe", file=sys.stderr)
        return 1

    exib_stage = STAGE / "exib_stage.parquet"
    dist_stage = STAGE / "dist_stage.parquet"

    print("[1/4] Stage exibidoras...")
    rows_exib = csvs_to_staging_parquet(EXIB_DIR, exib_stage, "exibidoras")

    print("[2/4] Stage distribuidoras...")
    rows_dist = csvs_to_staging_parquet(DIST_DIR, dist_stage, "distribuidoras")

    con = duckdb.connect()
    con.execute("PRAGMA threads=4")

    print("[3/4] Carregando staged parquets em DuckDB...")
    con.execute(f"""
        CREATE VIEW exib_raw AS SELECT * FROM read_parquet('{exib_stage.as_posix()}');
        CREATE VIEW dist_raw AS SELECT * FROM read_parquet('{dist_stage.as_posix()}');
    """)
    con.execute("""
        CREATE TABLE exib AS
        SELECT
          TRY_STRPTIME(DATA_EXIBICAO, '%d/%m/%Y') AS data_exibicao,
          CAST(EXTRACT(YEAR FROM TRY_STRPTIME(DATA_EXIBICAO, '%d/%m/%Y')) AS INTEGER) AS ano,
          NULLIF(TRIM(CPB_ROE), '')                AS cpb_roe,
          NULLIF(TRIM(TITULO_BRASIL), '')          AS titulo_brasil,
          NULLIF(TRIM(TITULO_ORIGINAL), '')        AS titulo_original,
          NULLIF(TRIM(PAIS_OBRA), '')              AS pais_obra,
          NULLIF(TRIM(REGISTRO_COMPLEXO), '')      AS registro_complexo,
          NULLIF(TRIM(MUNICIPIO_SALA_COMPLEXO),'') AS municipio,
          NULLIF(TRIM(UF_SALA_COMPLEXO), '')       AS uf,
          NULLIF(TRIM(RAZAO_SOCIAL_EXIBIDORA), '') AS exibidora,
          regexp_replace(COALESCE(CNPJ_EXIBIDORA, ''), '[^0-9]', '', 'g') AS cnpj_exibidor,
          TRY_CAST(PUBLICO AS BIGINT) AS publico
        FROM exib_raw
    """)
    con.execute("""
        CREATE TABLE dist AS
        SELECT
          TRY_STRPTIME(DATA_EXIBICAO, '%d/%m/%Y') AS data_exibicao,
          CAST(EXTRACT(YEAR FROM TRY_STRPTIME(DATA_EXIBICAO, '%d/%m/%Y')) AS INTEGER) AS ano,
          NULLIF(TRIM(CPB_ROE), '')                AS cpb_roe,
          NULLIF(TRIM(TITULO_BRASIL), '')          AS titulo_brasil,
          NULLIF(TRIM(TITULO_ORIGINAL), '')        AS titulo_original,
          NULLIF(TRIM(PAIS_OBRA), '')              AS pais_obra,
          NULLIF(TRIM(REGISTRO_COMPLEXO), '')      AS registro_complexo,
          NULLIF(TRIM(MUNICIPIO_SALA_COMPLEXO),'') AS municipio,
          NULLIF(TRIM(UF_SALA_COMPLEXO), '')       AS uf,
          NULLIF(TRIM(RAZAO_SOCIAL_DISTRIBUIDORA), '') AS distribuidora,
          regexp_replace(COALESCE(CNPJ_DISTRIBUIDORA, ''), '[^0-9]', '', 'g') AS cnpj_distribuidor,
          TRY_CAST(PUBLICO AS BIGINT) AS publico
        FROM dist_raw
    """)
    print(f"      exib: {rows_exib:,} linhas, dist: {rows_dist:,} linhas")

    print("[4/4] Gerando agregados...")

    # a) bilheteria_diaria_exibidora_filme_ano
    con.execute(f"""
        COPY (
          SELECT
            cpb_roe,
            ano,
            ANY_VALUE(titulo_brasil)   AS titulo_brasil,
            ANY_VALUE(titulo_original) AS titulo_original,
            ANY_VALUE(pais_obra)       AS pais_obra,
            cnpj_exibidor,
            ANY_VALUE(exibidora)       AS exibidora,
            SUM(publico)                                             AS publico_total,
            COUNT(*)                                                 AS sessoes,
            COUNT(DISTINCT registro_complexo)                        AS n_complexos,
            COUNT(DISTINCT municipio)                                AS n_municipios
          FROM exib
          WHERE ano IS NOT NULL AND cpb_roe IS NOT NULL AND cnpj_exibidor != ''
          GROUP BY cpb_roe, ano, cnpj_exibidor
        ) TO '{OUT / 'bilheteria_diaria_exibidora_filme_ano.parquet'}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
    sz1 = (OUT / 'bilheteria_diaria_exibidora_filme_ano.parquet').stat().st_size / 1048576
    rows1 = con.execute(f"SELECT COUNT(*) FROM read_parquet('{OUT / 'bilheteria_diaria_exibidora_filme_ano.parquet'}')").fetchone()[0]
    print(f"      [a] bilheteria_diaria_exibidora_filme_ano.parquet : {rows1:,} linhas, {sz1:.1f} MB")

    # b) bilheteria_diaria_distribuidora_filme_ano
    con.execute(f"""
        COPY (
          SELECT
            cpb_roe,
            ano,
            ANY_VALUE(titulo_brasil)   AS titulo_brasil,
            ANY_VALUE(titulo_original) AS titulo_original,
            ANY_VALUE(pais_obra)       AS pais_obra,
            cnpj_distribuidor,
            ANY_VALUE(distribuidora)   AS distribuidora,
            SUM(publico)               AS publico_total,
            COUNT(*)                   AS sessoes
          FROM dist
          WHERE ano IS NOT NULL AND cpb_roe IS NOT NULL AND cnpj_distribuidor != ''
          GROUP BY cpb_roe, ano, cnpj_distribuidor
        ) TO '{OUT / 'bilheteria_diaria_distribuidora_filme_ano.parquet'}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
    sz2 = (OUT / 'bilheteria_diaria_distribuidora_filme_ano.parquet').stat().st_size / 1048576
    rows2 = con.execute(f"SELECT COUNT(*) FROM read_parquet('{OUT / 'bilheteria_diaria_distribuidora_filme_ano.parquet'}')").fetchone()[0]
    print(f"      [b] bilheteria_diaria_distribuidora_filme_ano.parquet : {rows2:,} linhas, {sz2:.1f} MB")

    # c) bilheteria_diaria_municipio_filme_ano (combinado das duas fontes)
    con.execute(f"""
        COPY (
          SELECT
            cpb_roe,
            ano,
            ANY_VALUE(titulo_brasil)   AS titulo_brasil,
            ANY_VALUE(pais_obra)       AS pais_obra,
            uf,
            municipio,
            SUM(publico) AS publico_total,
            COUNT(*)     AS sessoes
          FROM exib
          WHERE ano IS NOT NULL AND cpb_roe IS NOT NULL AND uf IS NOT NULL AND municipio IS NOT NULL
          GROUP BY cpb_roe, ano, uf, municipio
        ) TO '{OUT / 'bilheteria_diaria_municipio_filme_ano.parquet'}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
    sz3 = (OUT / 'bilheteria_diaria_municipio_filme_ano.parquet').stat().st_size / 1048576
    rows3 = con.execute(f"SELECT COUNT(*) FROM read_parquet('{OUT / 'bilheteria_diaria_municipio_filme_ano.parquet'}')").fetchone()[0]
    print(f"      [c] bilheteria_diaria_municipio_filme_ano.parquet : {rows3:,} linhas, {sz3:.1f} MB")

    # d) bilheteria_diaria_exibidora_ano (panorama por exibidora)
    con.execute(f"""
        COPY (
          SELECT
            cnpj_exibidor,
            ANY_VALUE(exibidora)                  AS exibidora,
            ano,
            SUM(publico)                          AS publico_total,
            COUNT(*)                              AS sessoes,
            COUNT(DISTINCT cpb_roe)               AS n_filmes,
            COUNT(DISTINCT registro_complexo)     AS n_complexos,
            COUNT(DISTINCT municipio)             AS n_municipios
          FROM exib
          WHERE ano IS NOT NULL AND cnpj_exibidor != ''
          GROUP BY cnpj_exibidor, ano
        ) TO '{OUT / 'bilheteria_diaria_exibidora_ano.parquet'}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)
    sz4 = (OUT / 'bilheteria_diaria_exibidora_ano.parquet').stat().st_size / 1048576
    rows4 = con.execute(f"SELECT COUNT(*) FROM read_parquet('{OUT / 'bilheteria_diaria_exibidora_ano.parquet'}')").fetchone()[0]
    print(f"      [d] bilheteria_diaria_exibidora_ano.parquet : {rows4:,} linhas, {sz4:.1f} MB")

    print("[done]")
    print(f"\nInput: {rows_exib + rows_dist:,} linhas brutas")
    print(f"Output: 4 parquets totalizando {sz1 + sz2 + sz3 + sz4:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
