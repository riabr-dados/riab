from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CLEANED = ROOT / "pipelines" / "output" / "cleaned"
DATASET_DIR = ROOT / "datasets" / "br-rais-emprego-audiovisual"
SNAPSHOT_DATE = "2026-05-23"
SNAPSHOT = DATASET_DIR / "snapshots" / SNAPSHOT_DATE
SOURCE_TABLE = CLEANED / "rais_emprego_audiovisual_fontes.csv"
SOURCE_FILE = "emprego-no-setor-audiovisual-2019.pdf"
SOURCE_URL_FALLBACK = "https://www.gov.br/ancine/pt-br/oca/resolveuid/992a10f5cca0463eb9b61541e9ceaba5"
SOURCE_PAGE_FALLBACK = "https://www.gov.br/ancine/pt-br/oca/publicacoes-2/outras-publicacoes"

YEARS = list(range(2010, 2020))

SERIES = [
    {
        "cnae_classe": "59.11-1",
        "cnae_subclasse": "59.11-1/01",
        "classe": "Atividades de producao cinematografica, de videos e de programas de televisao",
        "subclasse": "Estudios cinematograficos",
        "valores": [1047, 1148, 927, 1072, 1227, 1079, 835, 750, 764, 706],
    },
    {
        "cnae_classe": "59.11-1",
        "cnae_subclasse": "59.11-1/02",
        "classe": "Atividades de producao cinematografica, de videos e de programas de televisao",
        "subclasse": "Producao de filmes para publicidade",
        "valores": [1648, 2094, 2338, 2625, 2581, 2376, 2355, 2170, 2240, 2229],
    },
    {
        "cnae_classe": "59.11-1",
        "cnae_subclasse": "59.11-1/99",
        "classe": "Atividades de producao cinematografica, de videos e de programas de televisao",
        "subclasse": "Atividades de producao cinematografica, de videos e de programas de televisao nao especificadas anteriormente",
        "valores": [4175, 5121, 5631, 6190, 6084, 6152, 6371, 6014, 6202, 7013],
    },
    {
        "cnae_classe": "59.12-0",
        "cnae_subclasse": "59.12-0/01",
        "classe": "Atividades de pos-producao cinematografica, de videos e de programas de televisao",
        "subclasse": "Servicos de dublagem",
        "valores": [39, 63, 65, 88, 67, 105, 115, 99, 108, 142],
    },
    {
        "cnae_classe": "59.12-0",
        "cnae_subclasse": "59.12-0/02",
        "classe": "Atividades de pos-producao cinematografica, de videos e de programas de televisao",
        "subclasse": "Servicos de mixagem sonora em producao audiovisual",
        "valores": [261, 267, 247, 252, 264, 277, 229, 201, 214, 179],
    },
    {
        "cnae_classe": "59.12-0",
        "cnae_subclasse": "59.12-0/99",
        "classe": "Atividades de pos-producao cinematografica, de videos e de programas de televisao",
        "subclasse": "Atividades de pos-producao cinematografica, de videos e de programas de televisao nao especificadas anteriormente",
        "valores": [1268, 1308, 1792, 1461, 1322, 1263, 1387, 1355, 1096, 845],
    },
    {
        "cnae_classe": "59.13-8",
        "cnae_subclasse": "59.13-8/00",
        "classe": "Distribuicao cinematografica, de video e de programas de televisao",
        "subclasse": "Distribuicao cinematografica, de video e de programas de televisao",
        "valores": [1229, 1070, 1076, 935, 907, 867, 806, 830, 716, 1362],
    },
    {
        "cnae_classe": "59.14-6",
        "cnae_subclasse": "59.14-6/00",
        "classe": "Atividades de exibicao cinematografica",
        "subclasse": "Atividades de exibicao cinematografica",
        "valores": [11247, 11687, 12949, 14027, 14466, 14297, 14754, 14883, 14626, 15587],
    },
    {
        "cnae_classe": "60.21-7",
        "cnae_subclasse": "60.21-7/00",
        "classe": "Atividades de televisao aberta",
        "subclasse": "Atividades de televisao aberta",
        "valores": [48256, 51117, 51994, 51581, 53551, 51721, 49688, 50537, 47985, 50132],
    },
    {
        "cnae_classe": "60.22-5",
        "cnae_subclasse": "60.22-5/01",
        "classe": "Programadoras e atividades relacionadas a televisao por assinatura",
        "subclasse": "Programadoras",
        "valores": [3672, 4036, 3441, 2804, 2905, 3190, 3031, 2876, 2730, 1098],
    },
    {
        "cnae_classe": "60.22-5",
        "cnae_subclasse": "60.22-5/02",
        "classe": "Programadoras e atividades relacionadas a televisao por assinatura",
        "subclasse": "Atividades relacionadas a televisao por assinatura, exceto programadoras",
        "valores": [1573, 935, 802, 1033, 581, 437, 459, 842, 542, 554],
    },
    {
        "cnae_classe": "61.41-8",
        "cnae_subclasse": "61.41-8/00",
        "classe": "Operadoras de televisao por assinatura por cabo",
        "subclasse": "Operadoras de televisao por assinatura por cabo",
        "valores": [15709, 17744, 16470, 16137, 3210, 2986, 3009, 3342, 3302, 3503],
    },
    {
        "cnae_classe": "61.42-6",
        "cnae_subclasse": "61.42-6/00",
        "classe": "Operadoras de televisao por assinatura por micro-ondas",
        "subclasse": "Operadoras de televisao por assinatura por micro-ondas",
        "valores": [862, 944, 676, 345, 186, 106, 37, 14, 12, 20],
    },
    {
        "cnae_classe": "61.43-4",
        "cnae_subclasse": "61.43-4/00",
        "classe": "Operadoras de televisao por assinatura por satelite",
        "subclasse": "Operadoras de televisao por assinatura por satelite",
        "valores": [1508, 2419, 2793, 2595, 2367, 2140, 2036, 1340, 418, 372],
    },
    {
        "cnae_classe": "77.22-5",
        "cnae_subclasse": "77.22-5/00",
        "classe": "Aluguel de fitas de video, DVDs e similares",
        "subclasse": "Aluguel de fitas de video, DVDs e similares",
        "valores": [8228, 7292, 6524, 5543, 4866, 4192, 3407, 3017, 967, 2347],
    },
    {
        "cnae_classe": "47.62-8",
        "cnae_subclasse": "47.62-8/00",
        "classe": "Comercio varejista de discos, CDs, DVDs e fitas",
        "subclasse": "Comercio varejista de discos, CDs, DVDs e fitas",
        "valores": [5300, 5046, 4674, 4373, 4172, 3784, 3315, 2862, 2687, 1964],
    },
]

TOTALS = {
    2010: 106022,
    2011: 112291,
    2012: 112399,
    2013: 111061,
    2014: 98756,
    2015: 94972,
    2016: 91834,
    2017: 91132,
    2018: 84609,
    2019: 88053,
}


def source_metadata() -> dict[str, object]:
    metadata: dict[str, object] = {
        "fonte_arquivo": SOURCE_FILE,
        "fonte_url": SOURCE_URL_FALLBACK,
        "fonte_pagina": SOURCE_PAGE_FALLBACK,
        "hash_fonte": None,
    }
    if not SOURCE_TABLE.exists():
        return metadata

    fontes = pd.read_csv(SOURCE_TABLE)
    mask = fontes.get("titulo", pd.Series(dtype=str)).astype(str).str.contains(
        "Emprego no Setor Audiovisual 2019",
        case=False,
        na=False,
    )
    if not mask.any():
        return metadata
    row = fontes.loc[mask].iloc[0]
    metadata["fonte_url"] = row.get("url_arquivo") or SOURCE_URL_FALLBACK
    metadata["fonte_pagina"] = row.get("pagina_origem") or SOURCE_PAGE_FALLBACK
    metadata["hash_fonte"] = row.get("hash_arquivo") if pd.notna(row.get("hash_arquivo")) else None
    local_path = row.get("local_path")
    if pd.notna(local_path):
        metadata["fonte_arquivo"] = Path(str(local_path)).name
    return metadata


def build_subclasse_table(source: dict[str, object]) -> pd.DataFrame:
    rows = []
    for item in SERIES:
        for year, value in zip(YEARS, item["valores"], strict=True):
            rows.append(
                {
                    "ano": year,
                    "cnae_classe": item["cnae_classe"],
                    "cnae_subclasse": item["cnae_subclasse"],
                    "classe": item["classe"],
                    "subclasse": item["subclasse"],
                    "empregos_formais_ativos_31_12": value,
                    "fonte_tabela": "Apendice 2",
                    "status_serie": "oficial_ancine_reconstruida_pdf_2010_2019",
                    "nota_metodologica": (
                        "Serie transcrita do Apendice 2 do estudo ANCINE ano-base 2019. "
                        "Registra empregos formais ativos em 31/12 por subclasse CNAE, "
                        "a partir da metodologia ANCINE aplicada sobre a RAIS."
                    ),
                    **source,
                }
            )
    df = pd.DataFrame(rows)
    validate_totals(df)
    return df


def build_total_table(source: dict[str, object]) -> pd.DataFrame:
    rows = []
    for year in YEARS:
        rows.append(
            {
                "ano": year,
                "empregos_formais_ativos_31_12": TOTALS[year],
                "fonte_tabela": "Apendice 2",
                "status_serie": "oficial_ancine_reconstruida_pdf_2010_2019",
                "nota_metodologica": (
                    "Total do setor audiovisual publicado pela ANCINE no Apendice 2 do estudo "
                    "Emprego no Setor Audiovisual, ano-base 2019."
                ),
                **source,
            }
        )
    return pd.DataFrame(rows)


def validate_totals(df: pd.DataFrame) -> None:
    grouped = df.groupby("ano", as_index=True)["empregos_formais_ativos_31_12"].sum()
    errors = []
    for year, expected in TOTALS.items():
        observed = int(grouped.loc[year])
        if observed != expected:
            errors.append((year, observed, expected))
    if errors:
        raise ValueError(f"Soma das subclasses diverge do total ANCINE: {errors}")


def write_table(df: pd.DataFrame, table_name: str) -> None:
    CLEANED.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEANED / f"{table_name}.csv", index=False, encoding="utf-8")
    df.to_parquet(CLEANED / f"{table_name}.parquet", index=False)
    df.to_csv(SNAPSHOT / f"{table_name}.csv", index=False, encoding="utf-8")
    print(f"[OK] {table_name}: {len(df):,} linhas")


def update_source_table() -> None:
    if not SOURCE_TABLE.exists():
        return
    df = pd.read_csv(SOURCE_TABLE)
    df["status_extracao"] = "extracao_factual_publicada"
    df["observacao_metodologica"] = (
        "Inventario oficial das fontes. As tabelas factuais "
        "rais_emprego_audiovisual_total_ano e "
        "rais_emprego_audiovisual_subclasse_ano sao geradas por "
        "pipelines/transform/clean_rais_emprego_audiovisual.py a partir do "
        "Apendice 2 do estudo ANCINE ano-base 2019."
    )
    df.to_csv(SOURCE_TABLE, index=False, encoding="utf-8")
    df.to_parquet(SOURCE_TABLE.with_suffix(".parquet"), index=False)


def main() -> int:
    source = source_metadata()
    subclasse = build_subclasse_table(source)
    total = build_total_table(source)
    write_table(subclasse, "rais_emprego_audiovisual_subclasse_ano")
    write_table(total, "rais_emprego_audiovisual_total_ano")
    update_source_table()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
