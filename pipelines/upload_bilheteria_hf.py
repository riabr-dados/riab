"""
Upload dos datasets de bilheteria diária direto de Downloads para o HF.
Esses arquivos são grandes demais para git (13 GB total) — ficam apenas no HF.

Uso:
    python pipelines/upload_bilheteria_hf.py
"""
import os, sys, glob
from pathlib import Path
from huggingface_hub import HfApi, CommitOperationAdd

HF_ORG  = "riabr-dados"
HF_REPO = "riab"
HF_TYPE = "dataset"
DOWNLOADS = Path.home() / "Downloads"

BILHETERIA = {
    "ancine-bilheteria-diaria-exibidoras":    DOWNLOADS / "bilheteria-diaria-obras-por-exibidoras-csv",
    "ancine-bilheteria-diaria-distribuidoras": DOWNLOADS / "bilheteria-diaria-obras-por-distribuidoras-csv",
}

def get_hf_token():
    token = os.environ.get("HF_TOKEN")
    if token:
        return token
    if os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                token, _ = winreg.QueryValueEx(key, "HF_TOKEN")
                return token or None
        except OSError:
            pass
    return None

token = get_hf_token()
if not token:
    print("HF_TOKEN nao definido.", file=sys.stderr)
    sys.exit(1)

api = HfApi(token=token)

for slug, src_dir in BILHETERIA.items():
    if not src_dir.is_dir():
        print(f"[SKIP] {slug} — pasta nao encontrada: {src_dir}")
        continue

    files = sorted(src_dir.rglob("*.csv"))
    total_mb = sum(f.stat().st_size for f in files) / 1048576
    print(f"\n[{slug}] {len(files)} arquivos, {total_mb:.0f} MB")
    print("  Preparando operacoes...")

    # Upload em lotes de 50 arquivos para evitar timeouts
    BATCH = 50
    for i in range(0, len(files), BATCH):
        batch = files[i:i+BATCH]
        ops = [
            CommitOperationAdd(
                path_in_repo=f"raw/{slug}/{f.name}",
                path_or_fileobj=str(f),
            )
            for f in batch
        ]
        batch_mb = sum(f.stat().st_size for f in batch) / 1048576
        print(f"  Lote {i//BATCH + 1}: {len(batch)} arquivos ({batch_mb:.0f} MB)...")
        api.create_commit(
            repo_id=f"{HF_ORG}/{HF_REPO}",
            repo_type=HF_TYPE,
            operations=ops,
            commit_message=f"raw: {slug} lote {i//BATCH + 1} ({len(batch)} arquivos)",
        )
        print(f"  Lote {i//BATCH + 1} enviado.")

    print(f"[OK] {slug} completo.")

print("\nUpload de bilheteria concluido.")
