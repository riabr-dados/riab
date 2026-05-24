from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CLEANED = ROOT / "pipelines" / "output" / "cleaned"
DATASET_DIR = ROOT / "datasets" / "ancine-diversidade-audiovisual"
SNAPSHOT_DATE = "2026-05-23"
SNAPSHOT = DATASET_DIR / "snapshots" / SNAPSHOT_DATE
SOURCE_TABLE = CLEANED / "diversidade_audiovisual_fontes.csv"
SOURCE_FILE = "estudo-genero-e-raca-no-setor-audiovisual-2011-2021.pdf"
SOURCE_URL_FALLBACK = "https://www.gov.br/ancine/pt-br/oca/resolveuid/7e062995b4ed488fb68616ad39e3e81e"
SOURCE_PAGE_FALLBACK = "https://www.gov.br/ancine/pt-br/oca/publicacoes-2/outras-publicacoes"

SEXO_ROWS = [
    (2011, "feminino", 45262, 113298),
    (2011, "masculino", 68036, 113298),
    (2012, "feminino", 45555, 113357),
    (2012, "masculino", 67802, 113357),
    (2013, "feminino", 44622, 111881),
    (2013, "masculino", 67259, 111881),
    (2014, "feminino", 40411, 99642),
    (2014, "masculino", 59231, 99642),
    (2015, "feminino", 38739, 95784),
    (2015, "masculino", 57045, 95784),
    (2016, "feminino", 37371, 92550),
    (2016, "masculino", 55179, 92550),
    (2017, "feminino", 37173, 91821),
    (2017, "masculino", 54648, 91821),
    (2018, "feminino", 34341, 85200),
    (2018, "masculino", 50859, 85200),
    (2019, "feminino", 35237, 86719),
    (2019, "masculino", 51482, 86719),
    (2020, "feminino", 31687, 79311),
    (2020, "masculino", 47624, 79311),
    (2021, "feminino", 31958, 77632),
    (2021, "masculino", 45674, 77632),
]

RACA_ROWS = [
    (2011, "amarela", 925, 113298),
    (2011, "branca", 72892, 113298),
    (2011, "indigena", 332, 113298),
    (2011, "parda", 28031, 113298),
    (2011, "preta", 5936, 113298),
    (2012, "amarela", 1003, 113357),
    (2012, "branca", 71678, 113357),
    (2012, "indigena", 222, 113357),
    (2012, "parda", 29075, 113357),
    (2012, "preta", 5832, 113357),
    (2013, "amarela", 1107, 111881),
    (2013, "branca", 69523, 111881),
    (2013, "indigena", 189, 111881),
    (2013, "parda", 29660, 111881),
    (2013, "preta", 5599, 111881),
    (2014, "amarela", 992, 99642),
    (2014, "branca", 60189, 99642),
    (2014, "indigena", 189, 99642),
    (2014, "parda", 27422, 99642),
    (2014, "preta", 4886, 99642),
    (2015, "amarela", 971, 95784),
    (2015, "branca", 56338, 95784),
    (2015, "indigena", 179, 95784),
    (2015, "parda", 26895, 95784),
    (2015, "preta", 4897, 95784),
    (2016, "amarela", 974, 92550),
    (2016, "branca", 53531, 92550),
    (2016, "indigena", 194, 92550),
    (2016, "parda", 26461, 92550),
    (2016, "preta", 4903, 92550),
    (2017, "amarela", 921, 91821),
    (2017, "branca", 52348, 91821),
    (2017, "indigena", 160, 91821),
    (2017, "parda", 25961, 91821),
    (2017, "preta", 4981, 91821),
    (2018, "amarela", 793, 85200),
    (2018, "branca", 48173, 85200),
    (2018, "indigena", 121, 85200),
    (2018, "parda", 24284, 85200),
    (2018, "preta", 4838, 85200),
    (2019, "amarela", 747, 86719),
    (2019, "branca", 45369, 86719),
    (2019, "indigena", 124, 86719),
    (2019, "parda", 26191, 86719),
    (2019, "preta", 5187, 86719),
    (2020, "amarela", 718, 79311),
    (2020, "branca", 41841, 79311),
    (2020, "indigena", 108, 79311),
    (2020, "parda", 23538, 79311),
    (2020, "preta", 4688, 79311),
    (2021, "amarela", 715, 77632),
    (2021, "branca", 40948, 77632),
    (2021, "indigena", 118, 77632),
    (2021, "parda", 22358, 77632),
    (2021, "preta", 4712, 77632),
]


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
        "Estudo G",
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


def build_sexo_table(source: dict[str, object]) -> pd.DataFrame:
    rows = []
    for ano, sexo, empregos, total in SEXO_ROWS:
        rows.append(
            {
                "ano": ano,
                "sexo": sexo,
                "empregos_formais_ativos_31_12": empregos,
                "total_ano": total,
                "fonte_tabela": "Tabela 1",
                "status_serie": "oficial_ancine_reconstruida_pdf_2011_2021",
                "nota_metodologica": (
                    "Serie documental transcrita da Tabela 1 do estudo ANCINE "
                    "Genero e Raca no Setor Audiovisual 2011-2021, secao RAIS."
                ),
                **source,
            }
        )
    return pd.DataFrame(rows)


def build_raca_table(source: dict[str, object]) -> pd.DataFrame:
    rows = []
    for ano, raca_cor, empregos, total in RACA_ROWS:
        rows.append(
            {
                "ano": ano,
                "raca_cor": raca_cor,
                "empregos_formais_ativos_31_12": empregos,
                "total_ano": total,
                "fonte_tabela": "Tabela 2",
                "status_serie": "oficial_ancine_reconstruida_pdf_2011_2021",
                "nota_metodologica": (
                    "Serie documental transcrita da Tabela 2 do estudo ANCINE "
                    "Genero e Raca no Setor Audiovisual 2011-2021, secao RAIS. "
                    "O proprio estudo informa que registros sem identificacao de "
                    "raca ou cor nao entram nas analises subsequentes."
                ),
                **source,
            }
        )
    return pd.DataFrame(rows)


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
    df["status_extracao"] = "extracao_factual_publicada_parcial"
    df["observacao_metodologica"] = (
        "Inventario oficial das fontes. As tabelas factuais "
        "diversidade_audiovisual_emprego_sexo_ano e "
        "diversidade_audiovisual_emprego_raca_ano sao geradas por "
        "pipelines/transform/clean_diversidade_audiovisual.py a partir das "
        "Tabelas 1 e 2 do estudo ANCINE 2011-2021. O estudo completo menciona "
        "planilha anexa para detalhamentos adicionais, nao inventariada neste "
        "snapshot."
    )
    df.to_csv(SOURCE_TABLE, index=False, encoding="utf-8")
    df.to_parquet(SOURCE_TABLE.with_suffix(".parquet"), index=False)


def main() -> int:
    source = source_metadata()
    sexo = build_sexo_table(source)
    raca = build_raca_table(source)
    write_table(sexo, "diversidade_audiovisual_emprego_sexo_ano")
    write_table(raca, "diversidade_audiovisual_emprego_raca_ano")
    update_source_table()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
