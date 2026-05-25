"""
Sincroniza a reestruturacao de mai/2026:
- Remove do HF os arquivos movidos para fora de ancine-fomento-fluxos-financeiros
- Sobe os 7 novos datasets criados
- Atualiza ancine-fomento-fluxos-financeiros com os 10 arquivos restantes
"""
from __future__ import annotations

import os
import glob
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from huggingface_hub import HfApi, CommitOperationAdd, CommitOperationDelete

HF_ORG  = "riabr-dados"
HF_REPO = "riab"
HF_TYPE = "dataset"

DATASETS_LOCAL = ROOT / "datasets"
SNAP = "snapshots/2026-05-23"

NOVOS_DATASETS = [
    "ancine-condecine-recolhimento",
    "ancine-ibermedia-projetos",
    "ancine-coproducao-internacional-projetos",
    "ancine-apoio-festivais-internacionais",
    "ancine-premio-adicional-renda",
    "ancine-filmes-lancados-captacao",
    "ancine-captacao-por-projeto-investidor",
]


def get_hf_token() -> str:
    token = os.environ.get("HF_TOKEN")
    if token:
        return token
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "[Environment]::GetEnvironmentVariable('HF_TOKEN','User')"],
        capture_output=True, text=True, check=False,
    )
    token = result.stdout.strip()
    if not token:
        raise RuntimeError("HF_TOKEN nao encontrado")
    return token


def files_in_hf_dir(api: HfApi, hf_dir: str) -> list[str]:
    """Retorna todos os paths no HF sob hf_dir."""
    try:
        infos = api.list_repo_tree(
            repo_id=f"{HF_ORG}/{HF_REPO}",
            repo_type=HF_TYPE,
            path_in_repo=hf_dir,
            recursive=True,
        )
        return [f.path for f in infos if f.path.endswith(tuple(
            [".csv", ".xlsx", ".pdf", ".parquet", ".json", ".txt"]
        ))]
    except Exception:
        return []


def main():
    token = get_hf_token()
    api = HfApi(token=token)

    ops: list = []

    # ------------------------------------------------------------------ #
    # 1. Deletar do HF os arquivos que saíram de ancine-fomento-fluxos   #
    # ------------------------------------------------------------------ #
    slug_fomento = "ancine-fomento-fluxos-financeiros"
    local_snap = DATASETS_LOCAL / slug_fomento / SNAP
    local_files = {f.name for f in local_snap.iterdir() if f.is_file()}

    hf_files = files_in_hf_dir(api, f"raw/{slug_fomento}")
    for hf_path in hf_files:
        fname = Path(hf_path).name
        if fname not in local_files:
            ops.append(CommitOperationDelete(path_in_repo=hf_path))
            print(f"  - DELETE {hf_path}")

    # Sobe os 10 arquivos que ficaram no fomento (para garantir consistência)
    for f in sorted(local_snap.iterdir()):
        if f.is_file():
            hf_path = f"raw/{slug_fomento}/{f.name}"
            ops.append(CommitOperationAdd(path_in_repo=hf_path, path_or_fileobj=str(f)))
            print(f"  + {hf_path}")

    # ------------------------------------------------------------------ #
    # 2. Subir os 7 novos datasets                                        #
    # ------------------------------------------------------------------ #
    for slug in NOVOS_DATASETS:
        snap_dir = DATASETS_LOCAL / slug / SNAP
        if not snap_dir.exists():
            print(f"  [SKIP] {slug} — diretorio nao encontrado")
            continue
        for f in sorted(snap_dir.iterdir()):
            if f.is_file():
                hf_path = f"raw/{slug}/{f.name}"
                ops.append(CommitOperationAdd(path_in_repo=hf_path, path_or_fileobj=str(f)))
                print(f"  + {hf_path}")

    if not ops:
        print("Nenhuma operacao gerada.")
        return

    n_add = sum(1 for o in ops if isinstance(o, CommitOperationAdd))
    n_del = sum(1 for o in ops if isinstance(o, CommitOperationDelete))
    print(f"\nTotal: {n_add} uploads + {n_del} delecoes")
    print("Enviando para o Hugging Face...")

    api.create_commit(
        repo_id=f"{HF_ORG}/{HF_REPO}",
        repo_type=HF_TYPE,
        operations=ops,
        commit_message=(
            "curadoria: separa ancine-fomento-fluxos-financeiros em 7 datasets (mai/2026)\n\n"
            "- ancine-condecine-recolhimento: CONDECINE por artigo e contribuinte (2002-2017)\n"
            "- ancine-ibermedia-projetos: projetos Ibermedia em USD (2004-2019)\n"
            "- ancine-coproducao-internacional-projetos: editais bilaterais (2005-2016)\n"
            "- ancine-apoio-festivais-internacionais: programa apoio festivais (2010-2019)\n"
            "- ancine-premio-adicional-renda: PAR producao e distribuicao (2005-2013)\n"
            "- ancine-filmes-lancados-captacao: filmes lancados x captacao (1995-2022)\n"
            "- ancine-captacao-por-projeto-investidor: captacao e investidores (2002-2020)\n"
            "- ancine-fomento-fluxos-financeiros: reduzido a 4 agregados puros OCA"
        ),
    )
    print("Sincronizacao concluida.")


if __name__ == "__main__":
    main()
