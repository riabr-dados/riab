from decimal import Decimal
import csv
import gzip

import openpyxl
import pyarrow as pa
import pyarrow.parquet as pq

from pipelines.build_downloads import catalog_tables, descriptor_is_current, generate


def test_downloads_preserve_full_data_ids_and_precise_values(tmp_path):
    source = tmp_path / 'example.parquet'
    pq.write_table(pa.table({'id': ['00123', 'NA', '=1+1'],
                            'valor': [Decimal('123.45'), Decimal('123456789012345.6789'), Decimal('0')]}), source)
    dest = tmp_path / 'downloads'
    result = generate(source, dest, csv_rows=2)
    parts = [f for f in result['files'] if f['format'] == 'csv']
    assert [f['rows'] for f in parts] == [2, 1]
    rows = []
    for part in parts:
        with (dest / part['path']).open(encoding='utf-8-sig', newline='') as f:
            rows.extend(csv.DictReader(f))
    assert [r['id'] for r in rows] == ['00123', 'NA', '=1+1']
    assert Decimal(rows[1]['valor']) == Decimal('123456789012345.6789')
    book = openpyxl.load_workbook(dest / 'example.xlsx', data_only=False)
    assert book['Dados']['A2'].value == '00123'
    assert book['Dados']['A4'].data_type == 's'
    assert book['Dados']['B3'].value == '123456789012345.6789'
    assert book['Dados'].max_row == 4
    assert book['Dados'].freeze_panes == 'A2'
    assert book['Dados'].auto_filter.ref == 'A1:B4'


def test_large_resource_has_all_csv_parts_without_truncation(tmp_path):
    source = tmp_path / 'large.parquet'
    pq.write_table(pa.table({'id': range(7)}), source)
    result = generate(source, tmp_path / 'out', csv_rows=3, xlsx_rows=5)
    assert [f['rows'] for f in result['files']] == [3, 3, 1]
    assert all(f['format'] == 'csv' for f in result['files'])
    assert 'xlsx_note' in result


def test_very_large_resource_uses_workable_compressed_csv(tmp_path):
    source = tmp_path / 'large.parquet'
    pq.write_table(pa.table({'id': range(7)}), source)
    destination = tmp_path / 'out'
    result = generate(source, destination, csv_rows=3, xlsx_rows=5, gzip_rows=5)
    assert all(f['compression'] == 'gzip' and f['path'].endswith('.csv.gz') for f in result['files'])
    with gzip.open(destination / result['files'][0]['path'], 'rt', encoding='utf-8-sig') as stream:
        assert list(csv.reader(stream)) == [['id'], ['0'], ['1'], ['2']]


def test_catalog_tables_ignores_hidden_and_accepts_detailed_resources(tmp_path):
    catalog = tmp_path / 'datasets.yaml'
    catalog.write_text('''datasets:\n  - slug: visible\n    cleaned:\n      tables:\n        - simple\n        - name: detailed\n          parquet: detailed.parquet\n  - slug: hidden\n    hidden: true\n    cleaned:\n      tables: [private]\n''', encoding='utf-8')
    assert catalog_tables(catalog) == ['simple', 'detailed']


def test_descriptor_current_requires_matching_parquet_and_downloads(tmp_path):
    source = tmp_path / 'example.parquet'
    destination = tmp_path / 'downloads'
    pq.write_table(pa.table({'id': [1]}), source)
    descriptor = generate(source, destination)
    assert descriptor_is_current(source, destination, descriptor)
    (destination / 'example.csv').write_text('alterado', encoding='utf-8')
    assert not descriptor_is_current(source, destination, descriptor)
