"""
Upload apenas os arquivos cleaned/ para o Hugging Face.
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


token = get_hf_token()
if not token:
    print("Defina HF_TOKEN antes de rodar.", file=sys.stderr)
    sys.exit(1)

api = HfApi(token=token)
ops = []
cleaned_files = []
for pattern in ("*.parquet", "*.csv"):
    cleaned_files.extend(glob.glob(os.path.join(CLEANED, pattern)))

for local_path in sorted(cleaned_files):
    fname  = os.path.basename(local_path)
    hf_path = f"cleaned/{fname}"
    size_mb = os.path.getsize(local_path) / 1048576
    ops.append(CommitOperationAdd(path_in_repo=hf_path, path_or_fileobj=local_path))
    print(f"  + {hf_path} ({size_mb:.1f} MB)")

print(f"\nEnviando {len(ops)} arquivos cleaned...")
api.create_commit(
    repo_id=f"{HF_ORG}/{HF_REPO}",
    repo_type=HF_TYPE,
    operations=ops,
    commit_message="dados: atualiza arquivos cleaned",
)
print("Upload concluído.")
