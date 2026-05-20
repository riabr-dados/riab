"""
Publica os dados no Hugging Face.

Estrutura no HF (org: riabr-dados, repo: riab, tipo: dataset):
  raw/{slug-dataset}/    <- dados brutos dos snapshots atuais
  cleaned/*.parquet      <- parquets tratados

Requer: HF_TOKEN no ambiente (com permissao de escrita no repo).
Execute a partir da raiz: python pipelines/upload_hf.py
"""
import os
import sys
import glob
import yaml
from pathlib import Path
from huggingface_hub import HfApi, CommitOperationAdd

HF_ORG  = "riabr-dados"
HF_REPO = "riab"
HF_TYPE = "dataset"

CATALOG_PATH = "catalog/datasets.yaml"
RAW_LOCAL    = "datasets"
CLEANED_LOCAL = os.path.join("pipelines", "output", "cleaned")


def load_catalog():
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["datasets"]


def latest_snapshot(slug: str) -> str | None:
    """Retorna o caminho do snapshot mais recente de um dataset."""
    base = os.path.join(RAW_LOCAL, slug, "snapshots")
    if not os.path.isdir(base):
        return None
    snaps = sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)))
    return os.path.join(base, snaps[-1]) if snaps else None


def build_operations(datasets: list) -> list:
    ops = []

    # 1. Dados brutos — um arquivo por dataset (snapshot mais recente)
    for ds in datasets:
        slug = ds["slug"]
        snap_dir = latest_snapshot(slug)
        if not snap_dir:
            print(f"  [SKIP raw] {slug} — sem snapshot local")
            continue
        files = [f for f in glob.glob(os.path.join(snap_dir, "**"), recursive=True)
                 if os.path.isfile(f)]
        for local_path in files:
            rel = os.path.relpath(local_path, snap_dir).replace("\\", "/")
            hf_path = f"raw/{slug}/{rel}"
            ops.append(CommitOperationAdd(path_in_repo=hf_path, path_or_fileobj=local_path))
            print(f"  + raw/{slug}/{rel}")

    # 2. Dados tratados — todos os Parquets em pipelines/output/cleaned/
    if os.path.isdir(CLEANED_LOCAL):
        for parquet in glob.glob(os.path.join(CLEANED_LOCAL, "*.parquet")):
            fname = os.path.basename(parquet)
            hf_path = f"cleaned/{fname}"
            ops.append(CommitOperationAdd(path_in_repo=hf_path, path_or_fileobj=parquet))
            size_mb = os.path.getsize(parquet) / 1048576
            print(f"  + cleaned/{fname} ({size_mb:.1f} MB)")

    return ops


def main():
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("HF_TOKEN nao definido. Configure a variavel de ambiente.", file=sys.stderr)
        sys.exit(1)

    api = HfApi(token=token)

    # Garante que o repo existe
    try:
        api.repo_info(repo_id=f"{HF_ORG}/{HF_REPO}", repo_type=HF_TYPE)
        print(f"Repo encontrado: {HF_ORG}/{HF_REPO}")
    except Exception:
        print(f"Criando repo {HF_ORG}/{HF_REPO}...")
        api.create_repo(
            repo_id=f"{HF_ORG}/{HF_REPO}",
            repo_type=HF_TYPE,
            private=False,
            exist_ok=True,
        )

    datasets = load_catalog()
    print(f"\nPreparando operacoes para {len(datasets)} datasets...")
    ops = build_operations(datasets)

    if not ops:
        print("Nenhuma operacao gerada.")
        return

    print(f"\nEnviando {len(ops)} arquivo(s) para o Hugging Face...")
    api.create_commit(
        repo_id=f"{HF_ORG}/{HF_REPO}",
        repo_type=HF_TYPE,
        operations=ops,
        commit_message="dados: atualiza raw e cleaned",
    )
    print("Upload concluido.")


if __name__ == "__main__":
    main()
