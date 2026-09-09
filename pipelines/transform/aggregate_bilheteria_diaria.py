"""Gera quatro agregados a partir das partições anuais de bilheteria diária.

As partições detalhadas são criadas por ``clean_bilheteria_diaria.py``. O campo
``registros_reportados`` conta linhas da fonte e não representa necessariamente
sessões, pois o arquivo de distribuidoras não possui uma coluna de sessão.
"""
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "pipelines/output/cleaned"


def main() -> None:
    exib = (OUT / "bilheteria_diaria_exibidora_detalhe_*.parquet").as_posix()
    dist = (OUT / "bilheteria_diaria_distribuidora_detalhe_*.parquet").as_posix()
    if not list(OUT.glob("bilheteria_diaria_exibidora_detalhe_*.parquet")):
        raise FileNotFoundError("Partições detalhadas de exibidoras ausentes")
    if not list(OUT.glob("bilheteria_diaria_distribuidora_detalhe_*.parquet")):
        raise FileNotFoundError("Partições detalhadas de distribuidoras ausentes")

    con = duckdb.connect()
    con.execute("PRAGMA threads=4")
    con.execute(f"CREATE VIEW exib AS SELECT * FROM read_parquet('{exib}', union_by_name=true)")
    con.execute(f"CREATE VIEW dist AS SELECT * FROM read_parquet('{dist}', union_by_name=true)")

    jobs = {
        "bilheteria_diaria_exibidora_filme_ano": """
            SELECT cpb_roe, year(data_exibicao)::INTEGER AS ano,
                   any_value(nullif(trim(titulo_brasil), '')) AS titulo_brasil,
                   any_value(nullif(trim(titulo_original), '')) AS titulo_original,
                   any_value(nullif(trim(pais_obra), '')) AS pais_obra,
                   regexp_replace(cnpj_exibidora, '[^0-9]', '', 'g') AS cnpj_exibidor,
                   any_value(nullif(trim(razao_social_exibidora), '')) AS exibidora,
                   sum(publico)::HUGEINT AS publico_total, count(*)::BIGINT AS registros_reportados,
                   count(DISTINCT nullif(trim(registro_complexo), ''))::BIGINT AS n_complexos,
                   count(DISTINCT nullif(trim(municipio_sala_complexo), ''))::BIGINT AS n_municipios
            FROM exib WHERE data_exibicao IS NOT NULL AND nullif(trim(cpb_roe), '') IS NOT NULL
              AND nullif(regexp_replace(cnpj_exibidora, '[^0-9]', '', 'g'), '') IS NOT NULL
            GROUP BY cpb_roe, ano, cnpj_exibidor
        """,
        "bilheteria_diaria_distribuidora_filme_ano": """
            SELECT cpb_roe, year(data_exibicao)::INTEGER AS ano,
                   any_value(nullif(trim(titulo_brasil), '')) AS titulo_brasil,
                   any_value(nullif(trim(titulo_original), '')) AS titulo_original,
                   any_value(nullif(trim(pais_obra), '')) AS pais_obra,
                   regexp_replace(cnpj_distribuidora, '[^0-9]', '', 'g') AS cnpj_distribuidor,
                   any_value(nullif(trim(razao_social_distribuidora), '')) AS distribuidora,
                   sum(publico)::HUGEINT AS publico_total, count(*)::BIGINT AS registros_reportados
            FROM dist WHERE data_exibicao IS NOT NULL AND nullif(trim(cpb_roe), '') IS NOT NULL
              AND nullif(regexp_replace(cnpj_distribuidora, '[^0-9]', '', 'g'), '') IS NOT NULL
            GROUP BY cpb_roe, ano, cnpj_distribuidor
        """,
        "bilheteria_diaria_municipio_filme_ano": """
            SELECT cpb_roe, year(data_exibicao)::INTEGER AS ano,
                   any_value(nullif(trim(titulo_brasil), '')) AS titulo_brasil,
                   any_value(nullif(trim(pais_obra), '')) AS pais_obra,
                   nullif(trim(uf_sala_complexo), '') AS uf,
                   nullif(trim(municipio_sala_complexo), '') AS municipio,
                   sum(publico)::HUGEINT AS publico_total, count(*)::BIGINT AS registros_reportados
            FROM exib WHERE data_exibicao IS NOT NULL AND nullif(trim(cpb_roe), '') IS NOT NULL
              AND nullif(trim(uf_sala_complexo), '') IS NOT NULL
              AND nullif(trim(municipio_sala_complexo), '') IS NOT NULL
            GROUP BY cpb_roe, ano, uf, municipio
        """,
        "bilheteria_diaria_exibidora_ano": """
            SELECT regexp_replace(cnpj_exibidora, '[^0-9]', '', 'g') AS cnpj_exibidor,
                   any_value(nullif(trim(razao_social_exibidora), '')) AS exibidora,
                   year(data_exibicao)::INTEGER AS ano,
                   sum(publico)::HUGEINT AS publico_total, count(*)::BIGINT AS registros_reportados,
                   count(DISTINCT nullif(trim(cpb_roe), ''))::BIGINT AS n_filmes,
                   count(DISTINCT nullif(trim(registro_complexo), ''))::BIGINT AS n_complexos,
                   count(DISTINCT nullif(trim(municipio_sala_complexo), ''))::BIGINT AS n_municipios
            FROM exib WHERE data_exibicao IS NOT NULL
              AND nullif(regexp_replace(cnpj_exibidora, '[^0-9]', '', 'g'), '') IS NOT NULL
            GROUP BY cnpj_exibidor, ano
        """,
    }
    for name, query in jobs.items():
        path = (OUT / f"{name}.parquet").as_posix()
        con.execute(f"COPY ({query}) TO '{path}' (FORMAT PARQUET, COMPRESSION ZSTD)")
        rows = con.execute(f"SELECT count(*) FROM read_parquet('{path}')").fetchone()[0]
        print(f"{name}: {rows:,} linhas")
    con.close()


if __name__ == "__main__":
    main()
