"""
Executa todos os pipelines de transformacao em sequencia.
Chame a partir da raiz do repositorio: python pipelines/transform/run_all.py
"""
import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "pipelines/transform/clean_obras.py",
    "pipelines/transform/clean_fsa.py",
    "pipelines/transform/clean_bilheteria.py",
    "pipelines/transform/clean_agentes.py",
    "pipelines/transform/clean_diretores.py",
    "pipelines/transform/clean_produtores.py",
    "pipelines/transform/clean_renuncia.py",
    "pipelines/transform/clean_deflator.py",
    "pipelines/transform/clean_lumiere.py",
    "pipelines/transform/clean_incaa.py",
    "pipelines/transform/clean_acau.py",
]


def main():
    ok = 0
    fail = 0
    for script in SCRIPTS:
        path = Path(script)
        if not path.exists():
            print(f"[SKIP] {script} — nao encontrado")
            continue
        print(f"\n[RUN] {script}")
        result = subprocess.run(
            [sys.executable, script],
            capture_output=False,
        )
        if result.returncode == 0:
            ok += 1
        else:
            fail += 1
            print(f"[ERRO] {script} retornou codigo {result.returncode}", file=sys.stderr)

    print(f"\nResultado: {ok} OK / {fail} com erro")
    if fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
