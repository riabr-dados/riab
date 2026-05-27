"""
Transform: 22 datasets ANCINE PDA coletados em 2026-05-27.
Le todos os CSVs do snapshot mais recente, normaliza headers e empilha em um unico parquet por dataset.
Saida: pipelines/output/cleaned/<table>.parquet
"""
import sys
from pathlib import Path

import pandas as pd

from common import latest_snapshot, normalize_columns

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

# slug -> table_name (cleaned/<table>.parquet)
DATASETS = {
    "ancine-atividades-economicas-agentes":       "atividades_economicas_agentes_regulares",
    "ancine-produtoras-independentes":            "produtoras_independentes",
    "ancine-canais-programadoras":                "canais_programadoras_ativos",
    "ancine-canais-distribuicao-obrigatoria":     "canais_distribuicao_obrigatoria",
    "ancine-salas-exibicao-complexos":            "salas_exibicao_complexos",
    "ancine-obras-fomento-indireto":              "obras_fomento_indireto",
    "ancine-obras-investimento-fsa":              "obras_investimento_fsa_pda",
    "ancine-pais-origem-obras-br":                "pais_origem_obras_br",
    "ancine-obras-estrangeiras-roe":              "obras_estrangeiras_roe",
    "ancine-diretores-obras-estrangeiras":        "diretores_obras_estrangeiras",
    "ancine-produtores-obras-estrangeiras":       "produtores_obras_estrangeiras",
    "ancine-pais-origem-obras-estrangeiras":      "pais_origem_obras_estrangeiras",
    "ancine-grupos-economicos":                   "grupos_economicos",
    "ancine-crt-obras-nao-publicitarias":         "crt_obras_nao_publicitarias",
    "ancine-crt-obras-publicitarias":             "crt_obras_publicitarias",
    "ancine-fsa-investimento-contratados":        "fsa_investimento_contratados",
    "ancine-prestacao-contas-processos":          "prestacao_contas_processos",
    "ancine-filmagem-estrangeira":                "filmagem_estrangeira",
    "ancine-salas-exibicao-evolucao":             "salas_exibicao_evolucao",
    "ancine-lancamentos-distribuidoras":          "lancamentos_distribuidoras",
    "ancine-agentes-economicos-estrangeiros":     "agentes_economicos_estrangeiros",
    "ancine-complexos-cinematograficos-evolucao": "complexos_cinematograficos_evolucao",
}


def read_csv_safe(path: Path) -> pd.DataFrame:
    last_err = None
    for enc in ("utf-8-sig", "latin1", "cp1252"):
        try:
            return pd.read_csv(path, encoding=enc, sep=None, engine="python", dtype=str)
        except Exception as exc:
            last_err = exc
    raise RuntimeError(f"Falha ao ler {path}: {last_err}")


def process_dataset(slug: str, table: str) -> None:
    snap = latest_snapshot(RAW / slug)
    csvs = sorted(p for p in snap.glob("*.csv") if p.stat().st_size > 0)
    if not csvs:
        print(f"[SKIP] {slug} — sem CSV em {snap}")
        return

    print(f"[{slug}] {len(csvs)} arquivo(s) — gerando {table}.parquet")
    frames = []
    for csv in csvs:
        df = read_csv_safe(csv)
        if len(csvs) > 1:
            df["arquivo_origem"] = csv.name
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True, sort=False)
    combined = normalize_columns(combined)

    out = OUT / f"{table}.parquet"
    combined.to_parquet(out, index=False)
    size_mb = out.stat().st_size / 1048576
    print(f"  -> {out}  ({len(combined):>9} linhas, {size_mb:.1f} MB)")


def main() -> None:
    only = set(sys.argv[1:])
    for slug, table in DATASETS.items():
        if only and slug not in only and table not in only:
            continue
        try:
            process_dataset(slug, table)
        except Exception as exc:
            print(f"[ERRO] {slug}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
