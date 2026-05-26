"""
IBGE Século XX — Cinema. Extrai séries históricas de cinemas/sessões/entradas
vendidas/filmes exibidos por UF para os anos 1971, 1974, 1980, 1984, 1985.

Layouts variam por ano de publicação do anuário:
  - 1984/1985 (cultura1986m_aeb268, cultura1987_88_aeb33): col 1=sessoes,
    2=entradas_vendidas, 3-5=filmes_curta (total/nac/estr), 6-8=filmes_longa.
  - 1980 (cultura1983_aeb303): col 1=cinemas_informantes, 2=lotacao,
    3=sessoes, 4-5=longa_nac/estr, 6-7=entradas_inteiras/meias.
  - 1971/1974 (cultura1974_aeb35, cultura1976m_aeb236): col 1-6=cinemas
    35mm/70mm (informantes, lotacao, sessoes, longa, _, espectadores).

Output: long format (ano, uf, indicador, valor, unidade, fonte_documento).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "datasets" / "ibge-seculoxx-cinema" / "snapshots" / "2026-05-26"
CLEANED = ROOT / "pipelines" / "output" / "cleaned"
CLEANED.mkdir(parents=True, exist_ok=True)

UF_NAME_TO_CODE = {
    "RONDONIA": "RO", "ACRE": "AC", "AMAZONAS": "AM", "RORAIMA": "RR",
    "PARA": "PA", "AMAPA": "AP", "TOCANTINS": "TO",
    "MARANHAO": "MA", "PIAUI": "PI", "CEARA": "CE", "RIO GRANDE DO NORTE": "RN",
    "PARAIBA": "PB", "PERNAMBUCO": "PE", "ALAGOAS": "AL", "SERGIPE": "SE", "BAHIA": "BA",
    "MINAS GERAIS": "MG", "ESPIRITO SANTO": "ES", "RIO DE JANEIRO": "RJ", "SAO PAULO": "SP",
    "PARANA": "PR", "SANTA CATARINA": "SC", "RIO GRANDE DO SUL": "RS",
    "MATO GROSSO DO SUL": "MS", "MATO GROSSO": "MT", "GOIAS": "GO", "DISTRITO FEDERAL": "DF",
    # Pré-1988: estados antigos
    "GUANABARA": "GB",  # virou Rio de Janeiro em 1975
    "FERNANDO DE NORONHA": "FN",
}


def strip_accents(s: str) -> str:
    repl = str.maketrans("áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ", "aaaaeeiooouucAAAAEEIOOOUUC")
    return s.translate(repl)


def clean_uf_label(s: object) -> str | None:
    if pd.isna(s):
        return None
    text = str(s).strip()
    # tira pontos de preenchimento e múltiplos espaços
    text = re.sub(r"\.{2,}", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    return text


def uf_code(label: str) -> str | None:
    key = strip_accents(label).upper().strip().rstrip(".")
    return UF_NAME_TO_CODE.get(key)


def to_int(v: object) -> float | None:
    if pd.isna(v):
        return None
    s = str(v).strip()
    if s in {"", "-", "—", "...", "(1)", "(2)", "(3)"}:
        return None
    s = re.sub(r"[^\d.,\-]", "", s)
    if not s:
        return None
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def parse_simple_uf_table(path: Path, ano: int, col_specs: list[tuple[int, str, str]],
                          uf_start_row: int) -> list[dict]:
    """col_specs: lista de (col_index, indicador, unidade_original)."""
    df = pd.read_excel(path, header=None)
    records = []
    for i in range(uf_start_row, len(df)):
        label = clean_uf_label(df.iloc[i, 0])
        if not label:
            continue
        upper = strip_accents(label).upper().rstrip(".")
        is_brasil = upper.startswith("BRASIL")
        uf = uf_code(upper) if not is_brasil else None
        if not is_brasil and uf is None:
            # linha não reconhecida (rodapé, nota etc.) — para
            if any(k in upper for k in ("FONTE", "NOTA", "OBS")):
                break
            continue
        terr_tipo = "brasil" if is_brasil else "uf"
        terr_nome = "Brasil" if is_brasil else label.title()
        for col_idx, indicador, unidade in col_specs:
            if col_idx >= df.shape[1]:
                continue
            val = to_int(df.iloc[i, col_idx])
            if val is None:
                continue
            records.append({
                "ano": ano,
                "territorio_tipo": terr_tipo,
                "territorio_nome": terr_nome,
                "uf": uf,
                "indicador": indicador,
                "valor": val,
                "unidade_original": unidade,
                "fonte_documento": path.name,
            })
    return records


def build() -> pd.DataFrame:
    all_records: list[dict] = []

    # 1984 — cultura1986m_aeb268.xls: col 1=sessoes, 2=entradas, 3=curta_total,
    # 4=curta_nac, 5=curta_estr, 6=longa_total, 7=longa_nac, 8=longa_estr
    f = RAW / "cultura1986m_aeb268.xls"
    if f.exists():
        all_records.extend(parse_simple_uf_table(f, 1984, [
            (1, "sessoes_cinematograficas", "sessoes"),
            (2, "publico", "espectadores"),
            (3, "filmes_curta_metragem", "filmes"),
            (4, "filmes_curta_nacionais", "filmes"),
            (5, "filmes_curta_estrangeiros", "filmes"),
            (6, "filmes_longa_metragem", "filmes"),
            (7, "filmes_longa_nacionais", "filmes"),
            (8, "filmes_longa_estrangeiros", "filmes"),
        ], uf_start_row=7))

    # 1985 — cultura1987_88_aeb33.xls: mesmo layout que 1984
    f = RAW / "cultura1987_88_aeb33.xls"
    if f.exists():
        all_records.extend(parse_simple_uf_table(f, 1985, [
            (1, "sessoes_cinematograficas", "sessoes"),
            (2, "publico", "espectadores"),
            (3, "filmes_curta_metragem", "filmes"),
            (4, "filmes_curta_nacionais", "filmes"),
            (5, "filmes_curta_estrangeiros", "filmes"),
            (6, "filmes_longa_metragem", "filmes"),
            (7, "filmes_longa_nacionais", "filmes"),
            (8, "filmes_longa_estrangeiros", "filmes"),
        ], uf_start_row=7))

    # 1980 — cultura1983_aeb303.xls: col 1=cinemas_informantes, 2=lotacao,
    # 3=sessoes, 4=longa_nac, 5=longa_estr, 6=entradas_inteiras, 7=entradas_meias
    f = RAW / "cultura1983_aeb303.xls"
    if f.exists():
        rows = parse_simple_uf_table(f, 1980, [
            (1, "cinemas_informantes", "cinemas"),
            (2, "lugares_oferecidos", "lugares"),
            (3, "sessoes_cinematograficas", "sessoes"),
            (4, "filmes_longa_nacionais", "filmes"),
            (5, "filmes_longa_estrangeiros", "filmes"),
            (6, "publico_inteiras", "espectadores"),
            (7, "publico_meias", "espectadores"),
        ], uf_start_row=7)
        # Calcula público total = inteiras + meias por linha
        by_terr: dict[tuple, dict[str, float]] = {}
        for r in rows:
            key = (r["territorio_tipo"], r["territorio_nome"], r["uf"])
            by_terr.setdefault(key, {})[r["indicador"]] = r["valor"]
        for (tt, tn, uf), inds in by_terr.items():
            if "publico_inteiras" in inds and "publico_meias" in inds:
                rows.append({
                    "ano": 1980,
                    "territorio_tipo": tt,
                    "territorio_nome": tn,
                    "uf": uf,
                    "indicador": "publico",
                    "valor": inds["publico_inteiras"] + inds["publico_meias"],
                    "unidade_original": "espectadores",
                    "fonte_documento": f.name,
                })
        all_records.extend(rows)

    # 1971 — cultura1974_aeb35.xls: cinemas 35mm+70mm
    # col 1=informantes, 2=lotacao, 3=sessoes/ano, 4=longa_total, 6=espectadores
    # (cine-teatros nas cols 8-13; pulamos por enquanto)
    f = RAW / "cultura1974_aeb35.xls"
    if f.exists():
        all_records.extend(parse_simple_uf_table(f, 1971, [
            (1, "cinemas_informantes", "cinemas"),
            (2, "lugares_oferecidos", "lugares"),
            (3, "sessoes_cinematograficas", "sessoes"),
            (4, "filmes_longa_metragem", "filmes"),
            (6, "publico", "espectadores"),
        ], uf_start_row=10))

    # 1974 — cultura1976m_aeb236.xls: mesmo layout que 1971
    f = RAW / "cultura1976m_aeb236.xls"
    if f.exists():
        all_records.extend(parse_simple_uf_table(f, 1974, [
            (1, "cinemas_informantes", "cinemas"),
            (2, "lugares_oferecidos", "lugares"),
            (3, "sessoes_cinematograficas", "sessoes"),
            (4, "filmes_longa_metragem", "filmes"),
            (6, "publico", "espectadores"),
        ], uf_start_row=10))

    df = pd.DataFrame(all_records)
    if df.empty:
        return df
    df["origem_filme"] = "nacionais_e_estrangeiros"
    # Filmes nacionais/estrangeiros já vêm separados em indicadores próprios
    return df


def main() -> int:
    df = build()
    if df.empty:
        print("[ERRO] Nenhum dado extraído", file=sys.stderr)
        return 1
    out_pq = CLEANED / "ibge_seculoxx_cinema.parquet"
    out_csv = CLEANED / "ibge_seculoxx_cinema.csv"
    df.to_parquet(out_pq, index=False)
    df.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"[OK] ibge_seculoxx_cinema: {len(df):,} linhas")
    print("Indicadores:")
    print(df.groupby(["ano", "indicador"]).size().unstack(fill_value=0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
