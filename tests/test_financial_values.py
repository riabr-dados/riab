from decimal import Decimal
from pathlib import Path
import csv

import pandas as pd
import pytest

from pipelines.transform.financial_values import parse_money
from pipelines.transform.clean_renuncia import transform, MONEY_COLUMNS


@pytest.mark.parametrize('source, expected', [
    ('R$ 1.475.535,00', '1475535.00'), ('R$\xa00,00', '0.00'),
    ('(R$ 1,00)', '-1.00'), (1234.5, '1234.50'), ('0', '0.00'), ('', None), ('-', None),
    ('3216629.5245', '3216629.5245'),
])
def test_money(source, expected):
    assert parse_money(source) == (Decimal(expected) if expected is not None else None)


@pytest.mark.parametrize('source', ['abc123', 'R$ desconhecido', '1,2,3', 'nan'])
def test_invalid_value_does_not_become_null(source):
    with pytest.raises(ValueError):
        parse_money(source)


def test_renuncia_preserves_identifiers_and_literal_na(tmp_path):
    row = {c.upper(): 'R$ 0,00' for c in MONEY_COLUMNS}
    row.update(NUMERO_SALIC='00123', CNPJ_PROPONENTE='00123456000190', TITULO_PROJETO='NA',
               DATA_PUB_APROVACAO_PROJETO='31/12/2020', DATA_PRIMEIRA_LIBERACAO='',
               TOTAL_CAPTADO='R$ 44.000,00')
    path = tmp_path / 'source.csv'
    pd.DataFrame([row]).to_csv(path, sep=';', index=False)
    result = transform(path)
    assert result.loc[0, 'total_captado'] == Decimal('44000.00')
    assert result.loc[0, 'captado_art1'] == Decimal('0.00')
    assert result.loc[0, 'cnpj_proponente'] == '00123456000190'
    assert result.loc[0, 'numero_salic'] == '00123'
    assert result.loc[0, 'titulo_projeto'] == 'NA'
    assert pd.isna(result.loc[0, 'data_primeira_liberacao'])
    row['TOTAL_CAPTADO'] = 'R$ erro'
    pd.DataFrame([row]).to_csv(path, sep=';', index=False)
    with pytest.raises(ValueError, match='total_captado'):
        transform(path)


@pytest.mark.parametrize('snapshot, count', [('2026-05-19', 4215), ('2026-09-08', 4315)])
def test_renuncia_full_audited_snapshot_matches_independent_integer_cents(snapshot, count):
    source = Path(f'datasets/ancine-renuncia-fiscal/snapshots/{snapshot}/projetos-com-renuncia-fiscal.csv')
    if not source.exists():
        pytest.skip('Snapshot auditado não disponível neste checkout')
    with source.open(encoding='utf-8-sig', newline='') as stream:
        original = list(csv.DictReader(stream, delimiter=';'))
    result = transform(source)
    assert len(result) == len(original) == count
    # A referência é calculada em centavos inteiros sem chamar o conversor monetário.
    for col in MONEY_COLUMNS:
        reference = [int(row[col.upper()].removeprefix('R$ ').replace('.', '').replace(',', '')) for row in original]
        assert [int(value * 100) for value in result[col]] == reference
