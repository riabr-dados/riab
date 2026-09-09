import hashlib
import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = '2026-09-08'
TABLES = {
    'ancine-agentes-economicos': 'agentes_economicos',
    'ancine-atividades-economicas-agentes': 'atividades_economicas_agentes_regulares',
    'ancine-produtoras-independentes': 'produtoras_independentes',
    'ancine-canais-programadoras': 'canais_programadoras_ativos',
    'ancine-salas-exibicao-complexos': 'salas_exibicao_complexos',
    'ancine-obras-fomento-indireto': 'obras_fomento_indireto',
    'ancine-obras-investimento-fsa': 'obras_investimento_fsa_pda',
    'ancine-pais-origem-obras-estrangeiras': 'pais_origem_obras_estrangeiras',
    'ancine-grupos-economicos': 'grupos_economicos',
    'ancine-prestacao-contas-processos': 'prestacao_contas_processos',
    'ancine-salas-exibicao-evolucao': 'salas_exibicao_evolucao',
    'ancine-lancamentos-distribuidoras': 'lancamentos_distribuidoras',
    'ancine-agentes-economicos-estrangeiros': 'agentes_economicos_estrangeiros',
    'ancine-complexos-cinematograficos-evolucao': 'complexos_cinematograficos_evolucao',
}


def file_digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def test_updated_pda_snapshots_are_traceable_and_row_complete():
    for slug, table in TABLES.items():
        snapshot = ROOT / 'datasets' / slug / 'snapshots' / SNAPSHOT
        provenance = json.loads((snapshot / 'provenance.json').read_text(encoding='utf-8'))
        csvs = list(snapshot.glob('*.csv'))
        assert len(csvs) == 1
        source = csvs[0]
        assert provenance['files'][0]['sha256'] == file_digest(source)
        raw_rows = len(pd.read_csv(source, sep=None, engine='python', dtype=str,
                                   keep_default_na=False, encoding='utf-8-sig'))
        cleaned_rows = pq.ParquetFile(ROOT / 'pipelines/output/cleaned' / f'{table}.parquet').metadata.num_rows
        assert cleaned_rows == raw_rows, slug
