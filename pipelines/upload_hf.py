"""
Publica os dados no Hugging Face.

Estrutura no HF (org: riabr-dados, repo: riab, tipo: dataset):
  raw/{slug-dataset}/    <- dados brutos dos snapshots atuais
  cleaned/*.parquet      <- parquets tratados
  cleaned/*.csv          <- versoes CSV tratadas

Requer: HF_TOKEN no ambiente (com permissao de escrita no repo).
Execute a partir da raiz: python pipelines/upload_hf.py
"""
import os
import sys
import glob
import json
import hashlib
import yaml
from pathlib import Path
from huggingface_hub import HfApi, CommitOperationAdd, CommitOperationDelete

HF_ORG  = "riabr-dados"
HF_REPO = "riab"
HF_TYPE = "dataset"

CATALOG_PATH = "catalog/datasets.yaml"
RAW_LOCAL    = "datasets"
CLEANED_LOCAL = os.path.join("pipelines", "output", "cleaned")
MAX_COMMIT_FILES = 100
MAX_COMMIT_BYTES = 256 * 1024 * 1024


def download_operations(datasets: list) -> list:
    """Recusar publicação incompleta ou manifesto desatualizado."""
    manifest = json.loads(Path('catalog/downloads.json').read_text(encoding='utf-8'))['resources']
    tables = {t if isinstance(t, str) else t['name']
              for ds in datasets if not ds.get('hidden')
              for t in ds.get('cleaned', {}).get('tables', [])}
    missing = tables - set(manifest)
    if missing:
        raise ValueError(f'Downloads completos ainda não gerados: {sorted(missing)}')
    ops = []
    for table in sorted(tables):
        item = manifest[table]
        parquet = Path(CLEANED_LOCAL) / f'{table}.parquet'
        with parquet.open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != item['parquet_sha256']:
                raise ValueError(f'Regerar downloads após alteração de {table}')
        for file in item['files']:
            if Path(file['path']).name != file['path']:
                raise ValueError('Caminho de download inválido')
            path = Path('pipelines/output/downloads') / file['path']
            with path.open('rb') as stream:
                if hashlib.file_digest(stream, 'sha256').hexdigest() != file['sha256']:
                    raise ValueError(f'Download alterado: {path}')
            ops.append(CommitOperationAdd(path_in_repo=f'downloads/{path.name}', path_or_fileobj=str(path)))
    return ops


def get_hf_token() -> str | None:
    """Read HF_TOKEN from process env or persisted Windows user env."""
    token = os.environ.get("HF_TOKEN")
    if token:
        return token

    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                token, _ = winreg.QueryValueEx(key, "HF_TOKEN")
                if token:
                    return token
        except OSError:
            pass

        try:
            import subprocess

            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "[Environment]::GetEnvironmentVariable('HF_TOKEN','User')",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            token = result.stdout.strip()
            return token or None
        except Exception:
            return None

    return None


def load_catalog():
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["datasets"]


def raw_dataset_dir(ds: dict) -> str:
    raw = ds.get("raw", {})
    raw_path = raw.get("path") or f"{ds['slug']}/"
    raw_path = raw_path.strip("/\\").replace("/", os.sep)
    return os.path.join(RAW_LOCAL, raw_path)


def latest_snapshot(ds: dict) -> str | None:
    """Retorna o caminho do snapshot mais recente de um dataset."""
    base = os.path.join(raw_dataset_dir(ds), "snapshots")
    if not os.path.isdir(base):
        return None
    snaps = sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)))
    return os.path.join(base, snaps[-1]) if snaps else None


def build_operations(datasets: list) -> list:
    ops = download_operations(datasets)

    # 1. Dados brutos — um arquivo por dataset (snapshot mais recente)
    for ds in datasets:
        slug = ds["slug"]
        snap_dir = latest_snapshot(ds)
        if not snap_dir:
            print(f"  [SKIP raw] {slug} — sem snapshot local")
            continue
        raw_file = ds.get("raw", {}).get("file")
        if raw_file:
            candidates = [os.path.join(snap_dir, raw_file)]
            candidates.extend(os.path.join(snap_dir, name) for name in ["datapackage.json", "source.txt", "source.json"])
            files = [path for path in candidates if os.path.isfile(path)]
        else:
            files = [f for f in glob.glob(os.path.join(snap_dir, "**"), recursive=True)
                     if os.path.isfile(f)]
        for local_path in files:
            rel = os.path.relpath(local_path, snap_dir).replace("\\", "/")
            hf_path = f"raw/{slug}/{rel}"
            ops.append(CommitOperationAdd(path_in_repo=hf_path, path_or_fileobj=local_path))
            print(f"  + raw/{slug}/{rel}")

    # 2. Dados tratados: Parquet e CSV em pipelines/output/cleaned/
    if os.path.isdir(CLEANED_LOCAL):
        cleaned_files = []
        tables = {t if isinstance(t, str) else t['name'] for ds in datasets
                  for t in ds.get('cleaned', {}).get('tables', [])}
        cleaned_files = [os.path.join(CLEANED_LOCAL, f'{table}.parquet') for table in sorted(tables)
                         if os.path.isfile(os.path.join(CLEANED_LOCAL, f'{table}.parquet'))]

        for local_path in sorted(cleaned_files):
            fname = os.path.basename(local_path)
            hf_path = f"cleaned/{fname}"
            ops.append(CommitOperationAdd(path_in_repo=hf_path, path_or_fileobj=local_path))
            size_mb = os.path.getsize(local_path) / 1048576
            print(f"  + cleaned/{fname} ({size_mb:.1f} MB)")

    return ops


def operation_size(operation) -> int:
    """Tamanho local usado para manter cada commit dentro de um lote administrável."""
    if isinstance(operation, CommitOperationAdd):
        path = operation.path_or_fileobj
        if isinstance(path, (str, os.PathLike)) and os.path.isfile(path):
            return os.path.getsize(path)
    return 0


def operation_batches(operations: list) -> list[list]:
    """Divide a publicação para permitir retomada e limitar memória do cliente."""
    batches = []
    current = []
    current_bytes = 0
    for operation in operations:
        size = operation_size(operation)
        if current and (len(current) >= MAX_COMMIT_FILES or current_bytes + size > MAX_COMMIT_BYTES):
            batches.append(current)
            current = []
            current_bytes = 0
        current.append(operation)
        current_bytes += size
    if current:
        batches.append(current)
    return batches


def main():
    datasets = load_catalog()
    # Preparar e validar localmente antes de qualquer chamada com efeito externo.
    ops = build_operations(datasets)
    token = get_hf_token()
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

    print(f"\nPreparando operacoes para {len(datasets)} datasets...")

    if not ops:
        print("Nenhuma operacao gerada.")
        return

    desired = {operation.path_in_repo for operation in ops if isinstance(operation, CommitOperationAdd)}
    remote = set(api.list_repo_files(repo_id=f"{HF_ORG}/{HF_REPO}", repo_type=HF_TYPE))
    stale = sorted(
        path for path in remote
        if path.startswith(("cleaned/", "downloads/")) and path not in desired
    )
    ops.extend(CommitOperationDelete(path_in_repo=path) for path in stale)
    batches = operation_batches(ops)
    print(
        f"\nEnviando {len(desired)} arquivo(s) e removendo {len(stale)} obsoleto(s) "
        f"em {len(batches)} lote(s)..."
    )
    for index, batch in enumerate(batches, start=1):
        print(f"[LOTE {index}/{len(batches)}] {len(batch)} operacoes")
        api.create_commit(
            repo_id=f"{HF_ORG}/{HF_REPO}",
            repo_type=HF_TYPE,
            operations=batch,
            commit_message=f"dados: atualiza raw e cleaned ({index}/{len(batches)})",
        )
    print("Upload concluido.")


if __name__ == "__main__":
    main()
