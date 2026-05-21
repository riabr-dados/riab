"""
Upload apenas os parquets cleaned/ para o Hugging Face.
Mais rápido que upload_hf.py (não sobe raw/).

Uso:
    set HF_TOKEN=hf_...
    python pipelines/upload_cleaned_only.py
"""
import os, sys, glob
from huggingface_hub import HfApi, CommitOperationAdd

HF_ORG   = "riabr-dados"
HF_REPO  = "riab"
HF_TYPE  = "dataset"
CLEANED  = os.path.join("pipelines", "output", "cleaned")

token = os.environ.get("HF_TOKEN")
if not token:
    print("Defina HF_TOKEN antes de rodar.", file=sys.stderr)
    sys.exit(1)

api = HfApi(token=token)
ops = []
for parquet in sorted(glob.glob(os.path.join(CLEANED, "*.parquet"))):
    fname  = os.path.basename(parquet)
    hf_path = f"cleaned/{fname}"
    size_mb = os.path.getsize(parquet) / 1048576
    ops.append(CommitOperationAdd(path_in_repo=hf_path, path_or_fileobj=parquet))
    print(f"  + {hf_path} ({size_mb:.1f} MB)")

print(f"\nEnviando {len(ops)} parquets...")
api.create_commit(
    repo_id=f"{HF_ORG}/{HF_REPO}",
    repo_type=HF_TYPE,
    operations=ops,
    commit_message="fix: encoding UTF-8 corrigido em fsa, renuncia, diretores, produtores, bilheteria",
)
print("Upload concluído.")
