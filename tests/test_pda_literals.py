"""Casos reais em que o leitor apagava textos da fonte como se fossem nulos."""
from pathlib import Path
import subprocess
import sys

import pandas as pd
import pytest

from pipelines.transform.clean_obras import load_csv


def test_obras_reader_preserves_literals_and_rejects_broken_csv(tmp_path):
    path = tmp_path / 'source.csv'
    path.write_text('CPB;TITULO_ORIGINAL\n001;NA\n002;N/A\n003;\n', encoding='utf-8')
    data = load_csv(str(path), 2020)
    assert data.titulo_original.iloc[:2].tolist() == ['NA', 'N/A']
    assert pd.isna(data.titulo_original.iloc[2])
    path.write_text('CPB;TITULO_ORIGINAL\n001;NA\n002;N/A;extra\n', encoding='utf-8')
    with pytest.raises(pd.errors.ParserError):
        load_csv(str(path), 2020)


@pytest.mark.parametrize('script, args, table, column, literal, expected', [
    ('clean_diretores.py', [], 'diretores_obras', 'titulo_original', 'NA', 2),
    ('clean_produtores.py', [], 'produtores_obras', 'titulo_original', 'NA', 2),
    ('clean_ancine_pda.py', ['pais_origem_obras_br'], 'pais_origem_obras_br', 'titulo_original', 'NA', 1),
    ('clean_ancine_pda.py', ['diretores_obras_estrangeiras'], 'diretores_obras_estrangeiras', 'diretor', 'N/A', 2),
    ('clean_ancine_pda.py', ['produtores_obras_estrangeiras'], 'produtores_obras_estrangeiras', 'produtor', 'N/A', 1),
    ('clean_ancine_pda.py', ['crt_obras_publicitarias'], 'crt_obras_publicitarias', 'produto_servico_anunciado', 'N/A', 1),
])
def test_original_literals_survive_reprocessing(script, args, table, column, literal, expected):
    if not Path('datasets/ancine-diretores-obras/snapshots/2026-05-19').exists():
        pytest.skip('Snapshots originais não disponíveis')
    subprocess.run([sys.executable, 'pipelines/transform/' + script, *args], check=True, capture_output=True)
    data = pd.read_parquet('pipelines/output/cleaned/' + table + '.parquet')
    assert int(data[column].eq(literal).sum()) == expected
