"""
Agrega crt_obras_publicitarias (548k linhas) e crt_obras_nao_publicitarias (184k)
em views mais leves usaveis para joins no /transformar.

Saidas (parquet):
 - crt_publicitarias_anunciante_ano.parquet  (anunciante, cnpj, ano, n_crts, segmentos)
 - crt_publicitarias_agencia_ano.parquet     (agencia, cnpj, ano, n_crts, anunciantes)
 - crt_publicitarias_segmento_ano.parquet    (segmento, tipo_publicidade, ano, n_crts)
 - crt_nao_publicitarias_pais_ano.parquet    (pais, tipo_obra, ano, n_crts, duracao_media_min)
 - crt_nao_publicitarias_requerente_ano.parquet (requerente, cnpj, ano, n_crts)
"""
import sys
from pathlib import Path

import duckdb

OUT = Path("pipelines/output/cleaned")
PUB = OUT / "crt_obras_publicitarias.parquet"
NPUB = OUT / "crt_obras_nao_publicitarias.parquet"


def year_of(col_iso_or_br: str) -> str:
    """Extract year from string that may be 'YYYY-MM-DD' or 'DD/MM/YYYY'."""
    return (
        f"COALESCE("
        f"TRY_CAST(SUBSTR({col_iso_or_br}, 1, 4) AS INTEGER),"
        f"TRY_CAST(SUBSTR({col_iso_or_br}, -4) AS INTEGER)"
        f")"
    )


def main():
    if not PUB.exists():
        print(f"[ERR] {PUB} nao existe", file=sys.stderr)
        return 1
    if not NPUB.exists():
        print(f"[ERR] {NPUB} nao existe", file=sys.stderr)
        return 1

    con = duckdb.connect()
    con.execute(f"CREATE VIEW pub  AS SELECT * FROM read_parquet('{PUB.as_posix()}')")
    con.execute(f"CREATE VIEW npub AS SELECT * FROM read_parquet('{NPUB.as_posix()}')")

    pub_year  = year_of("data_emissao_crt")
    npub_year = year_of("data_emissao_crt")

    print("[1/5] crt_publicitarias_anunciante_ano...")
    con.execute(f"""
        COPY (
          SELECT
            regexp_replace(COALESCE(cnpj_anunciante,''), '[^0-9]', '', 'g') AS cnpj_anunciante,
            ANY_VALUE(anunciante) AS anunciante,
            {pub_year} AS ano,
            COUNT(*) AS n_crts,
            COUNT(DISTINCT segmento) AS n_segmentos,
            COUNT(DISTINCT cnpj_agencia) AS n_agencias
          FROM pub
          WHERE cnpj_anunciante IS NOT NULL AND cnpj_anunciante != '' AND {pub_year} IS NOT NULL
          GROUP BY cnpj_anunciante, ano
        ) TO '{OUT / 'crt_publicitarias_anunciante_ano.parquet'}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    print("[2/5] crt_publicitarias_agencia_ano...")
    con.execute(f"""
        COPY (
          SELECT
            regexp_replace(COALESCE(cnpj_agencia,''), '[^0-9]', '', 'g') AS cnpj_agencia,
            ANY_VALUE(agencia) AS agencia,
            {pub_year} AS ano,
            COUNT(*) AS n_crts,
            COUNT(DISTINCT cnpj_anunciante) AS n_anunciantes,
            COUNT(DISTINCT segmento) AS n_segmentos
          FROM pub
          WHERE cnpj_agencia IS NOT NULL AND cnpj_agencia != '' AND {pub_year} IS NOT NULL
          GROUP BY cnpj_agencia, ano
        ) TO '{OUT / 'crt_publicitarias_agencia_ano.parquet'}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    print("[3/5] crt_publicitarias_segmento_ano...")
    con.execute(f"""
        COPY (
          SELECT
            segmento,
            tipo_publicidade,
            {pub_year} AS ano,
            COUNT(*) AS n_crts,
            COUNT(DISTINCT cnpj_anunciante) AS n_anunciantes,
            COUNT(DISTINCT cnpj_agencia) AS n_agencias
          FROM pub
          WHERE segmento IS NOT NULL AND {pub_year} IS NOT NULL
          GROUP BY segmento, tipo_publicidade, ano
        ) TO '{OUT / 'crt_publicitarias_segmento_ano.parquet'}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    print("[4/5] crt_nao_publicitarias_pais_ano...")
    con.execute(f"""
        COPY (
          SELECT
            pais,
            tipo_obra,
            {npub_year} AS ano,
            COUNT(*) AS n_crts,
            AVG(TRY_CAST(REPLACE(duracao_total_minutos, ',', '.') AS DOUBLE)) AS duracao_media_min,
            COUNT(DISTINCT cpb_roe) AS n_obras_unicas
          FROM npub
          WHERE pais IS NOT NULL AND {npub_year} IS NOT NULL
          GROUP BY pais, tipo_obra, ano
        ) TO '{OUT / 'crt_nao_publicitarias_pais_ano.parquet'}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    print("[5/5] crt_nao_publicitarias_requerente_ano...")
    con.execute(f"""
        COPY (
          SELECT
            regexp_replace(COALESCE(cnpj_requerente,''), '[^0-9]', '', 'g') AS cnpj_requerente,
            ANY_VALUE(requerente) AS requerente,
            ANY_VALUE(uf_requerente) AS uf,
            {npub_year} AS ano,
            COUNT(*) AS n_crts,
            COUNT(DISTINCT cpb_roe) AS n_obras_unicas,
            COUNT(DISTINCT tipo_obra) AS n_tipos
          FROM npub
          WHERE cnpj_requerente IS NOT NULL AND cnpj_requerente != '' AND {npub_year} IS NOT NULL
          GROUP BY cnpj_requerente, ano
        ) TO '{OUT / 'crt_nao_publicitarias_requerente_ano.parquet'}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)

    targets = [
        'crt_publicitarias_anunciante_ano',
        'crt_publicitarias_agencia_ano',
        'crt_publicitarias_segmento_ano',
        'crt_nao_publicitarias_pais_ano',
        'crt_nao_publicitarias_requerente_ano',
    ]
    print()
    for t in targets:
        p = OUT / f"{t}.parquet"
        sz = p.stat().st_size / 1048576
        n = duckdb.connect().execute(f"SELECT COUNT(*) FROM read_parquet('{p.as_posix()}')").fetchone()[0]
        print(f"  {t}.parquet : {n:>8,} linhas, {sz:.2f} MB")

    return 0


if __name__ == "__main__":
    sys.exit(main())
