from datetime import datetime
from decimal import Decimal
from pathlib import Path

import openpyxl
import pandas as pd
import pytest

from pipelines.transform.clean_captacao import transform, FILES, RENAME


def test_capta_preserves_foreign_identifier_and_rejects_unknown_row(tmp_path):
    path = tmp_path / 'source.xlsx'
    headers = ['Ano de captação', 'Salic', 'Nome do Projeto', 'Proponente', 'CNPJ Proponente',
               'UF Proponente', 'Incentivador/Investidor', 'CNPJ Incentivador/Investidor',
               'UF Incentivador/Investidor', 'Data da Captação', 'Lei 8.313/91 (Lei Rouanet)',
               'Art. 1º Lei 8.685/93', 'Art. 1º A Lei 8.685/93', 'Art. 3º Lei 8.685/93',
               'Art. 3º A Lei 8.685/93', 'Art. 39 MP 2228-1/01', 'Funcines']
    row = [datetime(2007, 1, 2), '00123', 'NA', 'Proponente', '00.123.456/0001-90', 'SP',
           'Investidor externo', 'Empresa Estrangeira', '', datetime(2007, 1, 2), 0, 36000, 0, 0, 0, 0, 10]
    book = openpyxl.Workbook(); s = book.active
    s.append(['Título']); s.append([]); s.append(headers); s.append(row); s.append(['Fonte: ANCINE'])
    book.save(path)
    data, _ = transform(path, 'captacao_por_projeto_investidor')
    assert len(data) == 1 and data.ano.iloc[0] == 2007
    assert data.salic.iloc[0] == '00123' and data.titulo_projeto.iloc[0] == 'NA'
    assert data.cnpj_proponente.iloc[0] == '00123456000190'
    assert data.cnpj_investidor_ou_contribuinte_original.iloc[0] == 'Empresa Estrangeira'
    assert pd.isna(data.cnpj_investidor_ou_contribuinte.iloc[0])
    assert data.captado_funcines.iloc[0] == Decimal('10')
    row[0] = 'data desconhecida'; s.append(row); book.save(path)
    with pytest.raises(ValueError, match='não classificada'):
        transform(path, 'captacao_por_projeto_investidor')


@pytest.mark.parametrize('table, count', [('aportes_por_investidor', 5326), ('captacao_por_projeto', 5281), ('captacao_por_projeto_investidor', 18104)])
def test_all_original_financial_cells_and_names(table, count):
    path = Path('datasets/ancine-captacao-por-projeto-investidor/snapshots/2026-05-23') / FILES[table]
    if not path.exists():
        pytest.skip('Snapshot original não disponível')
    data, report = transform(path, table)
    assert len(data) == count
    original = openpyxl.load_workbook(path, data_only=True, read_only=True)
    rows = list(original.active.values)
    original.close()
    # Posições conferidas diretamente nas três planilhas originais.
    money_positions = {'aportes_por_investidor': [3], 'captacao_por_projeto': list(range(8, 16)),
                       'captacao_por_projeto_investidor': list(range(10, 17))}[table]
    name_positions = {'aportes_por_investidor': {'nome_investidor': 1},
                      'captacao_por_projeto': {'titulo_projeto': 2, 'proponente': 4},
                      'captacao_por_projeto_investidor': {'titulo_projeto': 2, 'proponente': 3, 'nome_investidor': 6}}[table]
    for record in data.itertuples(index=False):
        row = rows[record.linha_origem - 1]
        for column, index in zip(report['money_columns'], money_positions):
            assert getattr(record, column) == Decimal(str(row[index]))
        for column, index in name_positions.items():
            if row[index] is None or str(row[index]).strip() == '':
                assert pd.isna(getattr(record, column))
            else:
                assert getattr(record, column) == str(row[index]).strip()
        id_positions = {'captacao_por_projeto': {'cnpj_proponente_original': 3},
                        'captacao_por_projeto_investidor': {'cnpj_proponente_original': 4, 'cnpj_investidor_ou_contribuinte_original': 7}}.get(table, {})
        for column, index in id_positions.items():
            if row[index] is None or str(row[index]).strip() == '':
                assert pd.isna(getattr(record, column))
            else:
                assert getattr(record, column) == str(row[index]).strip()
