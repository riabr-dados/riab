"""Build derived datasets for the "Brasil no Mundo" section.

Outputs:
  pipelines/output/cleaned/brasil_no_mundo_indice.parquet
  pipelines/output/cleaned/brasil_no_mundo_obras_franca_cnc.parquet
  pipelines/output/cleaned/brasil_no_mundo_bilheteria_europa.parquet
  pipelines/output/cleaned/brasil_no_mundo_vod_europa.parquet
  pipelines/output/cleaned/brasil_no_mundo_mercado_bfi.parquet
  pipelines/output/cleaned/brasil_no_mundo_mencoes_outros_paises.parquet
"""
from __future__ import annotations

from pathlib import Path
import re
import unicodedata

import pandas as pd

from common import write_parquet

OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)


def strip_accents(value: object) -> str:
    return (
        unicodedata.normalize("NFKD", "" if pd.isna(value) else str(value))
        .encode("ascii", "ignore")
        .decode("ascii")
    )


def norm_text(value: object) -> str:
    return strip_accents(value).lower()


def slug_text(value: object) -> str:
    text = norm_text(value)
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def has_brazil(value: object) -> bool:
    text = norm_text(value)
    if re.search(r"brasil|brazil|bresil|brasileir|brasilen|brasileno|brasilena", text):
        return True
    raw = "" if pd.isna(value) else str(value)
    return bool(re.search(r"(^|[^A-Za-z])BR([^A-Za-z]|$)", raw))


def brazil_pct(value: object) -> float | None:
    text = norm_text(value)
    match = re.search(r"(?:brasil|brazil|bresil)\s*-?\s*(\d+(?:[\.,]\d+)?)", text)
    if not match:
        return None
    return float(match.group(1).replace(",", "."))


def to_numeric(value: object) -> float | None:
    if pd.isna(value):
        return None
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return None
    return float(numeric)


def read_table(table: str) -> pd.DataFrame:
    return pd.read_parquet(OUT / f"{table}.parquet")


def unique_join(values: pd.Series, limit: int | None = None) -> str | None:
    clean = []
    seen = set()
    for value in values.dropna().astype(str):
        value = value.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        clean.append(value)
        if limit and len(clean) >= limit:
            break
    return " | ".join(clean) if clean else None


def yes_no(value: object) -> bool:
    if isinstance(value, bool):
        return value
    text = norm_text(value).strip()
    return text in {"true", "1", "sim", "yes"}


def build_obras_franca_cnc() -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    visas = read_table("cnc_visas_exploitation")
    visas = visas[visas["nationalite"].map(has_brazil)].copy()
    for _, row in visas.iterrows():
        rows.append(
            {
                "pais_fonte": "Franca",
                "instituicao": "CNC",
                "dataset_origem": "cnc_visas_exploitation",
                "tipo_aparicao": "obra_brasileira_explicita",
                "nivel_evidencia": "forte",
                "titulo": row.get("titre"),
                "chave_titulo": slug_text(row.get("titre")),
                "ano": row.get("date"),
                "diretor": row.get("realisation"),
                "produtora": row.get("production"),
                "formato": row.get("format"),
                "genero": None,
                "nacionalidade": row.get("nationalite"),
                "participacao_brasil_pct": brazil_pct(row.get("nationalite")),
                "decisao_classificacao": row.get("decision"),
                "id_origem": row.get("n_de_visa"),
                "valor_orcamento_eur": None,
                "observacao": "Nacionalidade no cadastro frances de visas inclui Brasil.",
            }
        )

    agrees = read_table("cnc_films_agrees")
    agrees = agrees[agrees["nationalite"].map(has_brazil)].copy()
    for _, row in agrees.iterrows():
        rows.append(
            {
                "pais_fonte": "Franca",
                "instituicao": "CNC",
                "dataset_origem": "cnc_films_agrees",
                "tipo_aparicao": "coproducao_brasileira",
                "nivel_evidencia": "forte",
                "titulo": row.get("titre"),
                "chave_titulo": slug_text(row.get("titre")),
                "ano": row.get("ano"),
                "diretor": row.get("realisateur"),
                "produtora": row.get("producteurs"),
                "formato": None,
                "genero": row.get("genre"),
                "nacionalidade": row.get("nationalite"),
                "participacao_brasil_pct": brazil_pct(row.get("nationalite")),
                "decisao_classificacao": None,
                "id_origem": row.get("visa"),
                "valor_orcamento_eur": row.get("devis"),
                "observacao": "Tabela de filmes agreees pelo CNC inclui percentual brasileiro.",
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
    df["id_origem"] = pd.to_numeric(df["id_origem"], errors="coerce").astype("Int64")
    df["participacao_brasil_pct"] = pd.to_numeric(
        df["participacao_brasil_pct"], errors="coerce"
    )
    df["valor_orcamento_eur"] = pd.to_numeric(df["valor_orcamento_eur"], errors="coerce")
    return df.sort_values(["ano", "titulo", "dataset_origem"], na_position="last")


def build_bilheteria_europa() -> pd.DataFrame:
    df = read_table("bilheteria_europa")
    if "tem_brasil" in df.columns:
        df = df[df["tem_brasil"].map(yes_no)].copy()
    else:
        df = df[df["paises_producao"].map(has_brazil)].copy()

    result = pd.DataFrame(
        {
            "pais_fonte": "Europa",
            "instituicao": "Lumiere",
            "dataset_origem": "bilheteria_europa",
            "tipo_aparicao": "obra_brasileira_explicita",
            "nivel_evidencia": "forte",
            "titulo": df["titulo_original"],
            "chave_titulo": df["titulo_original"].map(slug_text),
            "ano_producao": df["ano_producao"],
            "paises_producao": df["paises_producao"],
            "diretores": df["diretores"],
            "admissoes_1996_2026": df["admissoes_1996_2026"],
            "total_eu27_gb_desde_1996": df["total_eu27_gb_desde_1996"],
        }
    )
    return result.sort_values("admissoes_1996_2026", ascending=False, na_position="last")


def build_vod_europa() -> pd.DataFrame:
    df = read_table("vod_europa")
    if "tem_brasil" in df.columns:
        df = df[df["tem_brasil"].map(yes_no)].copy()
    else:
        df = df[df["paises_producao"].map(has_brazil)].copy()

    grouped = (
        df.groupby(["titulo_original", "paises_producao", "ano_producao", "tipo_obra"], dropna=False)
        .agg(
            diretores=("diretores", lambda s: unique_join(s, 3)),
            presencas_catalogo=("titulo_original", "size"),
            paises_catalogo_qtd=("country", lambda s: s.dropna().astype(str).nunique()),
            paises_catalogo=("country", lambda s: unique_join(s.sort_values())),
            catalogos_qtd=("catalog_group", lambda s: s.dropna().astype(str).nunique()),
            catalogos=("catalog_group", lambda s: unique_join(s.sort_values(), 20)),
            modelos_negocio=("modelo_negocio", lambda s: unique_join(s.sort_values())),
            primeira_presenca=("data_presenca", "min"),
            ultima_presenca=("data_presenca", "max"),
            lumiere_ids=("lumiere_id", lambda s: unique_join(s.astype("string").sort_values(), 5)),
            imdb_ids=("imdb_id", lambda s: unique_join(s.sort_values(), 5)),
        )
        .reset_index()
    )
    grouped.insert(0, "nivel_evidencia", "forte")
    grouped.insert(0, "tipo_aparicao", "obra_brasileira_explicita")
    grouped.insert(0, "dataset_origem", "vod_europa")
    grouped.insert(0, "instituicao", "Lumiere")
    grouped.insert(0, "pais_fonte", "Europa")
    grouped = grouped.rename(columns={"titulo_original": "titulo"})
    grouped.insert(6, "chave_titulo", grouped["titulo"].map(slug_text))
    return grouped.sort_values(["presencas_catalogo", "titulo"], ascending=[False, True])


def add_metric(
    rows: list[dict[str, object]],
    *,
    dataset_origem: str,
    tabela_origem: str,
    indicador: str,
    ano: int | None,
    territorio: str,
    valor: object,
    unidade: str,
    observacao: str | None = None,
) -> None:
    numeric = to_numeric(valor)
    if numeric is None:
        return
    rows.append(
        {
            "pais_fonte": "Reino Unido",
            "instituicao": "BFI",
            "dataset_origem": dataset_origem,
            "tabela_origem": tabela_origem,
            "tipo_aparicao": "mercado_brasil",
            "nivel_evidencia": "mercado",
            "indicador": indicador,
            "ano": ano,
            "territorio": territorio,
            "valor": numeric,
            "unidade": unidade,
            "observacao": observacao,
        }
    )


def build_mercado_bfi() -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    box = read_table("bfi_box_office_2023")
    brazil = box[box["territory"].astype("string").str.lower().eq("brazil")]
    for _, row in brazil.iterrows():
        for year in range(2019, 2024):
            add_metric(
                rows,
                dataset_origem="bfi_box_office_2023",
                tabela_origem=row.get("titulo_tabela"),
                indicador="admissoes_cinema",
                ano=year,
                territorio="Brasil",
                valor=row.get(f"{year}_0"),
                unidade="milhoes_de_ingressos",
                observacao="Brasil aparece como mercado de exibicao no anuarios BFI.",
            )

    market = read_table("bfi_uk_film_market")
    market = market[market["country"].astype("string").str.lower().eq("brazil")]
    for _, row in market.iterrows():
        add_metric(
            rows,
            dataset_origem="bfi_uk_film_market",
            tabela_origem=row.get("titulo_tabela"),
            indicador="receita_entretenimento_filmado",
            ano=2023,
            territorio="Brasil",
            valor=row.get("us_million"),
            unidade="milhoes_usd",
            observacao="Receita do mercado brasileiro de filmed entertainment em 2023.",
        )
        add_metric(
            rows,
            dataset_origem="bfi_uk_film_market",
            tabela_origem=row.get("titulo_tabela"),
            indicador="participacao_mercado_global",
            ano=2023,
            territorio="Brasil",
            valor=row.get("market_share"),
            unidade="pct",
            observacao="Participacao do Brasil no mercado global de filmed entertainment em 2023.",
        )
        add_metric(
            rows,
            dataset_origem="bfi_uk_film_market",
            tabela_origem=row.get("titulo_tabela"),
            indicador="receita_entretenimento_filmado_prevista",
            ano=2028,
            territorio="Brasil",
            valor=row.get("us_million_2028"),
            unidade="milhoes_usd",
            observacao="Previsao BFI para o mercado brasileiro em 2028.",
        )
        add_metric(
            rows,
            dataset_origem="bfi_uk_film_market",
            tabela_origem=row.get("titulo_tabela"),
            indicador="participacao_mercado_global_prevista",
            ano=2028,
            territorio="Brasil",
            valor=row.get("market_share_2028"),
            unidade="pct",
            observacao="Participacao prevista do Brasil no mercado global em 2028.",
        )
        add_metric(
            rows,
            dataset_origem="bfi_uk_film_market",
            tabela_origem=row.get("titulo_tabela"),
            indicador="crescimento_previsto_2023_2028",
            ano=2028,
            territorio="Brasil",
            valor=row.get("predicted_growth_2023_2028"),
            unidade="pct",
            observacao="Crescimento previsto entre 2023 e 2028.",
        )

    talent = read_table("bfi_talentos_mundo")
    talent = talent[talent["territory"].astype("string").str.lower().eq("brazil")]
    for _, row in talent.iterrows():
        add_metric(
            rows,
            dataset_origem="bfi_talentos_mundo",
            tabela_origem=row.get("titulo_tabela"),
            indicador="bilheteria_filmes_britanicos_qualificados",
            ano=2023,
            territorio="Brasil",
            valor=row.get("box_office_for_uk_qualifying_films_us_million"),
            unidade="milhoes_usd",
            observacao="Bilheteria de filmes britanicos qualificados no Brasil.",
        )
        add_metric(
            rows,
            dataset_origem="bfi_talentos_mundo",
            tabela_origem=row.get("titulo_tabela"),
            indicador="participacao_filmes_britanicos_qualificados",
            ano=2023,
            territorio="Brasil",
            valor=row.get("uk_qualifying_films_share"),
            unidade="pct",
            observacao="Market share de filmes britanicos qualificados no Brasil.",
        )
        add_metric(
            rows,
            dataset_origem="bfi_talentos_mundo",
            tabela_origem=row.get("titulo_tabela"),
            indicador="participacao_filmes_britanicos_independentes",
            ano=2023,
            territorio="Brasil",
            valor=row.get("uk_independent_films_share"),
            unidade="pct",
            observacao=f"Top filme britanico independente: {row.get('top_uk_independent_film')}.",
        )
        add_metric(
            rows,
            dataset_origem="bfi_talentos_mundo",
            tabela_origem=row.get("titulo_tabela"),
            indicador="participacao_outros_filmes_britanicos_qualificados",
            ano=2023,
            territorio="Brasil",
            valor=row.get("other_uk_qualifying_films_share"),
            unidade="pct",
            observacao="Parcela de outros filmes britanicos qualificados no Brasil.",
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    return df.sort_values(["dataset_origem", "indicador", "ano"], na_position="last")


def build_mencoes_outros_paises() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    acau = read_table("acau_apoios")
    matches = acau[acau["titulo"].map(has_brazil)].copy()
    for _, row in matches.iterrows():
        rows.append(
            {
                "pais_fonte": "Uruguai",
                "instituicao": "ACAU",
                "dataset_origem": "acau_apoios",
                "tipo_aparicao": "mencao_textual",
                "nivel_evidencia": "fraco",
                "titulo_ou_texto": row.get("titulo"),
                "ano": row.get("ano_instrumento"),
                "campo_encontrado": "titulo",
                "formato": row.get("formato"),
                "tipo_narrativo": row.get("tipo_narrativo"),
                "genero": row.get("genero"),
                "tipo_de_produccion": row.get("tipo_de_produccion"),
                "valor_local": row.get("monto_adjudicado_corriente"),
                "postulante": row.get("postulante"),
                "observacao": "Mencao textual a Brasil no titulo; nao comprova origem brasileira.",
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
    df["valor_local"] = pd.to_numeric(df["valor_local"], errors="coerce")
    return df.sort_values(["pais_fonte", "titulo_ou_texto"])


def build_indice(
    obras_franca: pd.DataFrame,
    bilheteria_europa: pd.DataFrame,
    vod_europa: pd.DataFrame,
    mercado_bfi: pd.DataFrame,
    mencoes: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    def add(
        *,
        pais_fonte: str,
        instituicao: str,
        dataset_derivado: str,
        dataset_origem: str,
        tipo_aparicao: str,
        nivel_evidencia: str,
        titulo_ou_indicador: object,
        ano: object,
        descricao_curta: str,
        linhas_relacionadas: int,
    ) -> None:
        rows.append(
            {
                "pais_fonte": pais_fonte,
                "instituicao": instituicao,
                "dataset_derivado": dataset_derivado,
                "dataset_origem": dataset_origem,
                "tipo_aparicao": tipo_aparicao,
                "nivel_evidencia": nivel_evidencia,
                "titulo_ou_indicador": titulo_ou_indicador,
                "chave_titulo_ou_indicador": slug_text(titulo_ou_indicador),
                "ano": ano,
                "descricao_curta": descricao_curta,
                "linhas_relacionadas": linhas_relacionadas,
                "arquivo_derivado": f"{dataset_derivado}.parquet",
            }
        )

    if not obras_franca.empty:
        grouped = (
            obras_franca.groupby(
                [
                    "pais_fonte",
                    "instituicao",
                    "dataset_origem",
                    "tipo_aparicao",
                    "nivel_evidencia",
                    "titulo",
                ],
                dropna=False,
            )
            .agg(ano=("ano", "min"), linhas=("titulo", "size"))
            .reset_index()
        )
        for _, row in grouped.iterrows():
            add(
                pais_fonte=row["pais_fonte"],
                instituicao=row["instituicao"],
                dataset_derivado="brasil_no_mundo_obras_franca_cnc",
                dataset_origem=row["dataset_origem"],
                tipo_aparicao=row["tipo_aparicao"],
                nivel_evidencia=row["nivel_evidencia"],
                titulo_ou_indicador=row["titulo"],
                ano=row["ano"],
                descricao_curta="Obra aparece nos dados franceses com nacionalidade ou coproducao brasileira.",
                linhas_relacionadas=int(row["linhas"]),
            )

    for _, row in bilheteria_europa.iterrows():
        add(
            pais_fonte=row["pais_fonte"],
            instituicao=row["instituicao"],
            dataset_derivado="brasil_no_mundo_bilheteria_europa",
            dataset_origem=row["dataset_origem"],
            tipo_aparicao=row["tipo_aparicao"],
            nivel_evidencia=row["nivel_evidencia"],
            titulo_ou_indicador=row["titulo"],
            ano=row["ano_producao"],
            descricao_curta=f"{row.get('admissoes_1996_2026')} admissoes acumuladas na Europa.",
            linhas_relacionadas=1,
        )

    for _, row in vod_europa.iterrows():
        add(
            pais_fonte=row["pais_fonte"],
            instituicao=row["instituicao"],
            dataset_derivado="brasil_no_mundo_vod_europa",
            dataset_origem=row["dataset_origem"],
            tipo_aparicao=row["tipo_aparicao"],
            nivel_evidencia=row["nivel_evidencia"],
            titulo_ou_indicador=row["titulo"],
            ano=row["ano_producao"],
            descricao_curta=f"{row.get('presencas_catalogo')} presencas em catalogos VOD europeus.",
            linhas_relacionadas=int(row["presencas_catalogo"]),
        )

    for _, row in mercado_bfi.iterrows():
        add(
            pais_fonte=row["pais_fonte"],
            instituicao=row["instituicao"],
            dataset_derivado="brasil_no_mundo_mercado_bfi",
            dataset_origem=row["dataset_origem"],
            tipo_aparicao=row["tipo_aparicao"],
            nivel_evidencia=row["nivel_evidencia"],
            titulo_ou_indicador=row["indicador"],
            ano=row["ano"],
            descricao_curta=f"{row.get('valor')} {row.get('unidade')} no territorio Brasil.",
            linhas_relacionadas=1,
        )

    for _, row in mencoes.iterrows():
        add(
            pais_fonte=row["pais_fonte"],
            instituicao=row["instituicao"],
            dataset_derivado="brasil_no_mundo_mencoes_outros_paises",
            dataset_origem=row["dataset_origem"],
            tipo_aparicao=row["tipo_aparicao"],
            nivel_evidencia=row["nivel_evidencia"],
            titulo_ou_indicador=row["titulo_ou_texto"],
            ano=row["ano"],
            descricao_curta=row["observacao"],
            linhas_relacionadas=1,
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df.insert(0, "id_brasil_no_mundo", [f"bnm_{i:05d}" for i in range(1, len(df) + 1)])
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
    return df.sort_values(["pais_fonte", "tipo_aparicao", "titulo_ou_indicador"])


def main() -> None:
    obras_franca = build_obras_franca_cnc()
    bilheteria_europa = build_bilheteria_europa()
    vod_europa = build_vod_europa()
    mercado_bfi = build_mercado_bfi()
    mencoes = build_mencoes_outros_paises()
    indice = build_indice(obras_franca, bilheteria_europa, vod_europa, mercado_bfi, mencoes)

    write_parquet(indice, "brasil_no_mundo_indice", OUT)
    write_parquet(obras_franca, "brasil_no_mundo_obras_franca_cnc", OUT)
    write_parquet(bilheteria_europa, "brasil_no_mundo_bilheteria_europa", OUT)
    write_parquet(vod_europa, "brasil_no_mundo_vod_europa", OUT)
    write_parquet(mercado_bfi, "brasil_no_mundo_mercado_bfi", OUT)
    write_parquet(mencoes, "brasil_no_mundo_mencoes_outros_paises", OUT)


if __name__ == "__main__":
    main()
