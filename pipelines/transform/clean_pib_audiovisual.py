from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CLEANED = ROOT / "pipelines" / "output" / "cleaned"
DATASET_DIR = ROOT / "datasets" / "br-pib-audiovisual"
SNAPSHOT_DATE = "2026-05-23"
SNAPSHOT = DATASET_DIR / "snapshots" / SNAPSHOT_DATE
SOURCE_FILE = "valor-adicionado-pelo-setor-audiovisual-2019.pdf"
SOURCE_TABLE = CLEANED / "pib_audiovisual_fontes.csv"
SOURCE_URL_FALLBACK = "https://www.gov.br/ancine/pt-br/oca/resolveuid/bd4f7d2608e541608e151c168da6d823"
SOURCE_PAGE_FALLBACK = "https://www.gov.br/ancine/pt-br/oca/publicacoes-2/outras-publicacoes"
UNIT = "R$ 1.000.000 correntes"

YEARS = list(range(2007, 2020))

TOTALS = {
    2007: 8866.1,
    2008: 10224.7,
    2009: 11985.2,
    2010: 13180.0,
    2011: 16930.5,
    2012: 20390.5,
    2013: 23079.5,
    2014: 25550.2,
    2015: 25742.4,
    2016: 24222.4,
    2017: 26015.1,
    2018: 26689.2,
    2019: 27475.8,
}

SHARES = {
    2007: (2.78, 0.55, 0.37),
    2008: (2.68, 0.56, 0.38),
    2009: (2.75, 0.59, 0.41),
    2010: (2.63, 0.59, 0.40),
    2011: (2.80, 0.65, 0.44),
    2012: (3.06, 0.72, 0.50),
    2013: (3.12, 0.73, 0.51),
    2014: (3.06, 0.72, 0.51),
    2015: (3.03, 0.69, 0.50),
    2016: (2.78, 0.61, 0.45),
    2017: (2.87, 0.62, 0.46),
    2018: (2.77, 0.61, 0.44),
    2019: (2.59, 0.59, 0.43),
}

ACTIVITIES = [
    {
        "cnae_classe": "59.11-1",
        "atividade": "Atividades de producao cinematografica, de videos e de programas de televisao",
        "segmento_ancine": "Producao cinematografica, video e TV",
        "valores": [238.2, 256.2, 294.4, 387.3, 382.5, 529.7, 457.3, 634.9, 555.7, 530.4, 517.3, 527.1, 536.1],
    },
    {
        "cnae_classe": "59.12-0",
        "atividade": "Atividades de pos-producao cinematografica, de videos e de programas de televisao",
        "segmento_ancine": "Pos-producao cinematografica, video e TV",
        "valores": [28.6, 35.9, 35.3, 41.2, 36.0, 55.7, 65.5, 64.3, 34.7, 44.5, 45.0, 46.2, 47.7],
    },
    {
        "cnae_classe": "59.13-8",
        "atividade": "Distribuicao cinematografica, de videos e de programas de televisao",
        "segmento_ancine": "Distribuicao cinematografica, video e TV",
        "valores": [71.3, 96.6, 81.5, 72.4, 83.4, 86.3, 96.1, 131.8, 164.9, 243.5, 235.3, 208.0, 314.8],
    },
    {
        "cnae_classe": "59.14-6",
        "atividade": "Atividades de exibicao cinematografica",
        "segmento_ancine": "Exibicao cinematografica",
        "valores": [135.9, 260.3, 354.9, 280.7, 474.1, 606.6, 667.9, 749.1, 938.4, 1061.0, 1106.4, 926.1, 1136.7],
    },
    {
        "cnae_classe": "60.21-7",
        "atividade": "Atividades de televisao aberta",
        "segmento_ancine": "Televisao aberta",
        "valores": [5514.2, 5818.5, 6307.8, 7146.3, 8436.2, 9611.7, 9829.0, 10173.6, 9988.3, 7892.8, 8092.5, 7811.9, 8359.2],
    },
    {
        "cnae_classe": "60.22-5",
        "atividade": "Programadoras e atividades relacionadas a televisao por assinatura",
        "segmento_ancine": "Programacao de TV por assinatura",
        "valores": [523.0, 738.6, 838.4, 1172.8, 1549.5, 2076.5, 2715.9, 3298.4, 3520.2, 3698.9, 3468.8, 2869.9, 2608.1],
    },
    {
        "cnae_classe": "61.41-8",
        "atividade": "Operadoras de televisao por assinatura por cabo",
        "segmento_ancine": "Operacao de TV por assinatura por cabo",
        "valores": [1526.8, 1775.0, 2525.8, 2630.2, 3361.4, 3675.0, 4437.6, 5508.7, 5599.5, 5121.2, 4592.2, 4573.4, 5162.6],
    },
    {
        "cnae_classe": "61.42-6",
        "atividade": "Operadoras de televisao por assinatura por microondas",
        "segmento_ancine": "Operacao de TV por assinatura por microondas",
        "valores": [26.0, 23.9, 39.8, 56.1, 31.4, 34.4, 1.2, 1.0, 1.3, 5.7, 0.0, 0.0, 0.0],
    },
    {
        "cnae_classe": "61.43-4",
        "atividade": "Operadoras de televisao por assinatura por satelite",
        "segmento_ancine": "Operacao de TV por assinatura por satelite",
        "valores": [551.8, 831.7, 986.4, 1279.3, 1871.3, 2809.2, 3888.9, 3842.6, 3670.1, 4031.6, 4304.1, 4098.1, 2834.4],
    },
    {
        "cnae_classe": "77.22-5",
        "atividade": "Aluguel de fitas de video, DVDs e similares",
        "segmento_ancine": "Aluguel de midias fisicas",
        "valores": [9.9, 28.7, 26.8, 17.5, 23.2, 25.1, 11.5, 15.8, 7.5, 8.9, 6.3, 7.7, 2.6],
    },
    {
        "cnae_classe": "47.62-8",
        "atividade": "Comercio varejista de discos, CDs, DVDs e fitas",
        "segmento_ancine": "Comercio varejista de midias fisicas",
        "valores": [32.6, 32.6, 52.0, 31.1, 34.3, 47.0, 51.8, 77.4, 65.1, 72.2, 70.6, 52.0, 40.5],
    },
    {
        "cnae_classe": "63.19-4",
        "atividade": "Portais, provedores de conteudo e outros servicos de informacao na internet",
        "segmento_ancine": "Portais e provedores de conteudo na internet",
        "valores": [207.9, 326.6, 442.2, 65.2, 647.3, 833.4, 856.8, 1052.5, 1196.9, 1511.7, 3576.6, 5568.1, 6433.1],
    },
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
        "Valor Adicionado pelo Setor Audiovisual 2019",
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


def marker_for(cnae: str, year: int) -> str | None:
    if cnae == "61.41-8" and year >= 2015:
        return "**"
    if cnae == "63.19-4" and year <= 2011:
        return "***"
    if cnae == "59.14-6" and year == 2017:
        return "*"
    if cnae == "47.62-8" and year == 2017:
        return "*"
    if cnae == "63.19-4" and year == 2018:
        return "*"
    return None


def marker_text(marker: str | None) -> str | None:
    if marker == "*":
        return "Valor atualizado pelo IBGE e incorporado pela ANCINE no estudo ano-base 2019."
    if marker == "**":
        return (
            "Valor estimado pela ANCINE por regressao linear via minimos quadrados ordinarios, "
            "usando assinantes de TV paga da ANATEL e VA das operadoras de TV por assinatura."
        )
    if marker == "***":
        return "Informacao marcada pela ANCINE como nao considerada para fins deste estudo."
    return None


def method_for(cnae: str, year: int) -> str:
    if cnae == "61.41-8" and year >= 2015:
        return "estimativa_ancine_regressao_ols"
    return "tabulacao_especial_ibge_pas_pac"


def build_activity_table(source: dict[str, object]) -> pd.DataFrame:
    rows = []
    for activity in ACTIVITIES:
        cnae = activity["cnae_classe"]
        for year, value in zip(YEARS, activity["valores"], strict=True):
            marker = marker_for(cnae, year)
            rows.append(
                {
                    "ano": year,
                    "cnae_classe": cnae,
                    "atividade": activity["atividade"],
                    "segmento_ancine": activity["segmento_ancine"],
                    "valor_adicionado_brl_milhoes_correntes": value,
                    "valor_adicionado_brl_correntes": int(round(value * 1_000_000)),
                    "unidade_original": UNIT,
                    "incluido_no_total_publicado": True,
                    "metodo_valor": method_for(cnae, year),
                    "marcador_nota_ancine": marker,
                    "nota_ancine": marker_text(marker),
                    "fonte_tabela": "Anexo 1",
                    "status_serie": "oficial_ancine_reconstruida_pdf_2007_2019",
                    "nota_metodologica": (
                        "Valor adicionado bruto a precos basicos das empresas com 20 ou mais "
                        "pessoas ocupadas, segundo atividades CNAE. Serie transcrita do Anexo 1 "
                        "do estudo ANCINE ano-base 2019."
                    ),
                    **source,
                }
            )

    df = pd.DataFrame(rows)
    validate_activity_totals(df)
    return df


def build_total_table(source: dict[str, object], activity: pd.DataFrame) -> pd.DataFrame:
    activity_totals = activity.groupby("ano", as_index=True)[
        "valor_adicionado_brl_milhoes_correntes"
    ].sum()
    rows = []
    for year in YEARS:
        share_business, share_services, share_economy = SHARES[year]
        marker = "*" if year in {2017, 2018} else None
        activity_sum = round(float(activity_totals.loc[year]), 1)
        difference = round(TOTALS[year] - activity_sum, 1)
        rows.append(
            {
                "ano": year,
                "valor_adicionado_brl_milhoes_correntes": TOTALS[year],
                "valor_adicionado_brl_correntes": int(round(TOTALS[year] * 1_000_000)),
                "soma_atividades_brl_milhoes_correntes": activity_sum,
                "diferenca_total_menos_soma_atividades_brl_milhoes": difference,
                "participacao_va_servicos_empresariais_nao_financeiros_pct": share_business,
                "participacao_va_total_servicos_pct": share_services,
                "participacao_va_total_economia_pct": share_economy,
                "unidade_original": UNIT,
                "metodo_valor": "total_ancine_soma_atividades_cnae",
                "marcador_nota_ancine": marker,
                "nota_ancine": marker_text(marker),
                "fonte_tabela": "Anexo 1; Grafico 3",
                "status_serie": "oficial_ancine_reconstruida_pdf_2007_2019",
                "nota_metodologica": (
                    "A ANCINE denomina a serie como Valor Adicionado pelo setor audiovisual. "
                    "Trata-se de VA bruto a precos basicos, nao PIB a precos de mercado."
                ),
                **source,
            }
        )
    return pd.DataFrame(rows)


def validate_activity_totals(df: pd.DataFrame) -> None:
    totals = df.groupby("ano", as_index=True)["valor_adicionado_brl_milhoes_correntes"].sum()
    errors = []
    for year, expected in TOTALS.items():
        observed = round(float(totals.loc[year]), 1)
        # The source table publishes one-decimal activity values; the total can
        # differ slightly because it was calculated before rounding.
        if abs(observed - expected) > 0.8:
            errors.append((year, observed, expected))
    if errors:
        raise ValueError(f"Soma das atividades diverge do total ANCINE: {errors}")


def write_table(df: pd.DataFrame, table_name: str) -> None:
    CLEANED.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEANED / f"{table_name}.csv", index=False, encoding="utf-8")
    df.to_parquet(CLEANED / f"{table_name}.parquet", index=False)
    df.to_csv(SNAPSHOT / f"{table_name}.csv", index=False, encoding="utf-8")
    print(f"[OK] {table_name}: {len(df):,} linhas")


def main() -> int:
    source = source_metadata()
    activity = build_activity_table(source)
    total = build_total_table(source, activity)
    write_table(activity, "pib_audiovisual_atividade_ano")
    write_table(total, "pib_audiovisual_total_ano")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
