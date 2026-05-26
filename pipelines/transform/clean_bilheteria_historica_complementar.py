"""
Bilheteria histórica complementar — agrega séries não cobertas pelas duas
fontes oficiais já publicadas (SADIS/consolidada e OCA por_filme_ano).

Fontes incluídas nesta versão:
1. Embrafilme (1982-1987) — anuais Brasil + por UF + por região + faixa habitantes,
   por origem (nacionais / estrangeiros / total)
2. OCA "Listagem de Filmes Brasileiros Lançados 1995-2024" — agregado anual BR
   (público acumulado e renda acumulada somados por ano de lançamento)
3. IBGE Século XX — cinema (1971, 1974, 1980, 1984, 1985) — censo IBGE de
   cinemas, sessões, entradas vendidas, filmes exibidos por UF

Schema long: (ano, origem_filme, territorio_tipo, territorio_nome, uf, indicador,
              valor, unidade_original, fonte, fonte_documento, confiabilidade).

Esta tabela é COMPLEMENTAR às oficiais — não substitui nem corrige
`bilheteria_brasileira_consolidada` (SADIS) nem `bilheteria_por_filme_ano` (OCA).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CLEANED = ROOT / "pipelines" / "output" / "cleaned"
CLEANED.mkdir(parents=True, exist_ok=True)


def from_embrafilme() -> pd.DataFrame:
    """
    Pega Embrafilme do parquet long, removendo:
    - linhas mensais (já há linhas anuais agregadas com mes=NaN)
    - duplicatas de Brasil cross-PDF: para territorio_tipo='brasil', mantém
      apenas linhas vindas dos PDFs "no_brasil" (autoritativos pro escopo).
      Os PDFs por-UF/por-regiao/faixa também trazem totais Brasil que
      coincidem mas são redundantes nesta agregação.
    """
    path = CLEANED / "embrafilme_exibicao_territorio_ano.parquet"
    if not path.exists():
        print(f"[WARN] {path.name} não encontrado; rode clean_oca_complementos antes", file=sys.stderr)
        return pd.DataFrame()
    df = pd.read_parquet(path)
    df = df[df["mes"].isna()].copy()

    # Para cada territorio_tipo, escolhe o PDF autoritativo
    is_brasil = df["territorio_tipo"].eq("brasil")
    fonte_lower = df["fonte_documento"].str.lower()
    is_no_brasil_pdf = fonte_lower.str.contains("no-brasil")
    # Brasil: só vindo de PDFs "no-brasil"
    keep_brasil = is_brasil & is_no_brasil_pdf
    keep_other = ~is_brasil
    df = df[keep_brasil | keep_other].copy()

    keep = ["ano", "origem_filme", "territorio_tipo", "territorio_nome", "uf",
            "indicador", "valor", "unidade_original", "fonte_documento"]
    df = df[keep]
    df["fonte"] = "Embrafilme (via OCA/ANCINE)"
    df["confiabilidade"] = "oficial_secundario"
    return df


def from_oca_filmes_br_1995() -> pd.DataFrame:
    path = ROOT / "datasets/ancine-filmes-lancados-captacao/snapshots/2026-05-23/listagem-de-filmes-brasileiros-lancados-1995-a-2024r-1.xlsx"
    if not path.exists():
        print(f"[WARN] {path} não encontrado", file=sys.stderr)
        return pd.DataFrame()

    raw = pd.read_excel(path, skiprows=1, dtype=str)

    # Normaliza nomes de colunas (alguns vêm com encoding latin1 quebrado)
    def find_col(cands):
        for c in raw.columns:
            cl = str(c).lower()
            if any(k in cl for k in cands):
                return c
        return None

    col_ano = find_col(["ano de lan", "ano"])
    col_pub = find_col(["blico acumul", "blico", "publico"])
    col_ren = find_col(["renda"])

    df = raw[[col_ano, col_pub, col_ren]].rename(
        columns={col_ano: "ano", col_pub: "publico", col_ren: "renda"}
    )
    # Filtra linhas válidas (ano numérico 4 dígitos)
    df = df[df["ano"].str.fullmatch(r"\d{4}", na=False)].copy()
    df["ano"] = df["ano"].astype(int)

    def to_num(s):
        if pd.isna(s):
            return None
        s = str(s).strip()
        if s in {"", "-", "–", "ND", "nd", "N/D"}:
            return None
        s = s.replace(".", "").replace(",", ".")
        try:
            return float(s)
        except ValueError:
            return None

    df["publico"] = df["publico"].map(to_num)
    df["renda"] = df["renda"].map(to_num)

    agg = df.groupby("ano", as_index=False).agg(
        publico=("publico", "sum"),
        renda=("renda", "sum"),
        filmes_lancados=("publico", "size"),
    )

    rows = []
    for _, r in agg.iterrows():
        base = {
            "ano": int(r["ano"]),
            "origem_filme": "brasileiros",
            "territorio_tipo": "brasil",
            "territorio_nome": "Brasil",
            "uf": None,
            "fonte_documento": path.name,
            "fonte": "OCA — Listagem de Filmes Brasileiros Lançados 1995-2024",
            "confiabilidade": "oficial_compilado",
        }
        rows.append({**base, "indicador": "publico", "valor": float(r["publico"]),
                     "unidade_original": "espectadores"})
        rows.append({**base, "indicador": "renda_brl_nominal", "valor": float(r["renda"]),
                     "unidade_original": "BRL"})
        rows.append({**base, "indicador": "filmes_lancados", "valor": float(r["filmes_lancados"]),
                     "unidade_original": "filmes"})
    return pd.DataFrame(rows)


def from_ibge_seculo_xx() -> pd.DataFrame:
    path = CLEANED / "ibge_seculoxx_cinema.parquet"
    if not path.exists():
        print(f"[WARN] {path.name} não encontrado; rode clean_ibge_seculoxx_cinema antes", file=sys.stderr)
        return pd.DataFrame()
    df = pd.read_parquet(path).copy()
    # IBGE não desagrega público por origem do filme — mantém o agregado
    df = df.rename(columns={"fonte_documento": "fonte_documento"})
    df["fonte"] = "IBGE Século XX — Cinema"
    df["confiabilidade"] = "oficial_compilado"
    keep = ["ano", "origem_filme", "territorio_tipo", "territorio_nome", "uf",
            "indicador", "valor", "unidade_original", "fonte", "fonte_documento",
            "confiabilidade"]
    return df[keep]


def main() -> int:
    parts = []
    for fn in (from_embrafilme, from_oca_filmes_br_1995, from_ibge_seculo_xx):
        df = fn()
        if not df.empty:
            parts.append(df)

    if not parts:
        print("[ERRO] Nenhuma fonte produziu dados", file=sys.stderr)
        return 1

    final = pd.concat(parts, ignore_index=True)
    cols = ["ano", "origem_filme", "territorio_tipo", "territorio_nome", "uf",
            "indicador", "valor", "unidade_original", "fonte", "fonte_documento",
            "confiabilidade"]
    final = final[cols].sort_values(["ano", "origem_filme", "territorio_tipo",
                                      "territorio_nome", "indicador"]).reset_index(drop=True)

    out_pq = CLEANED / "bilheteria_historica_complementar.parquet"
    out_csv = CLEANED / "bilheteria_historica_complementar.csv"
    final.to_parquet(out_pq, index=False)
    final.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"[OK] bilheteria_historica_complementar: {len(final):,} linhas")
    print(final.groupby(["fonte", "indicador"]).size())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
