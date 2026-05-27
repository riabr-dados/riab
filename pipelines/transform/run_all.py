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
    "pipelines/transform/clean_atas_fsa.py",
    "pipelines/transform/clean_oca_complementos.py",
    "pipelines/transform/clean_ibge_seculoxx_cinema.py",
    "pipelines/transform/clean_bilheteria_historica_complementar.py",
    "pipelines/transform/clean_pib_audiovisual.py",
    "pipelines/transform/clean_rais_emprego_audiovisual.py",
    "pipelines/transform/clean_comercio_exterior_servicos_audiovisuais.py",
    "pipelines/transform/clean_diversidade_audiovisual.py",
    "pipelines/transform/clean_lumiere.py",
    "pipelines/transform/clean_incaa.py",
    "pipelines/transform/clean_acau.py",
    "pipelines/transform/clean_cnc_simples.py",
    "pipelines/transform/clean_cnc_visas.py",
    "pipelines/transform/clean_cnc_complexos.py",
    "pipelines/transform/clean_cnc_geographie.py",
    "pipelines/transform/clean_cnc_xls.py",
    "pipelines/transform/clean_bfi_1.py",
    "pipelines/transform/clean_bfi_2.py",
    "pipelines/transform/clean_bfi_3.py",
    "pipelines/transform/clean_bfi_4.py",
    "pipelines/transform/clean_ancine_pda.py",
    "pipelines/transform/build_brasil_no_mundo.py",
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
