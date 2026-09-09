"""Três tabelas OCA de captação, com uma linha por linha factual da origem."""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import re

import pandas as pd

try:
    from .common import latest_snapshot, norm_col
    from .financial_values import money_column
except ImportError:
    from common import latest_snapshot, norm_col
    from financial_values import money_column

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'datasets/ancine-captacao-por-projeto-investidor'
OUT = ROOT / 'pipelines/output/cleaned'
FILES = {
    'aportes_por_investidor': 'valores-aportados-por-incentivador-investidor-lei-8-313-91-lei-8-685-93-mp-2-228-01-em-reais-r-2007-a-2019.xlsx',
    'captacao_por_projeto': 'valores-captados-por-projeto-incentivado-em-reais-r-2002-a-julho-de-2020.xlsx',
    'captacao_por_projeto_investidor': 'valores-captados-por-projeto-incentivado-e-por-investidor-em-reais-r-2007-a-2019.xlsx',
}
RENAME = {
    'nome_do_projeto': 'titulo_projeto', 'cnpj_do_proponente': 'cnpj_proponente',
    'uf': 'uf_proponente', 'incentivador_investidor': 'nome_investidor',
    'cnpj_incentivador_investidor': 'cnpj_investidor_ou_contribuinte',
    'uf_incentivador_investidor': 'uf_investidor', 'data_da_captacao': 'data_captacao',
    'valor_r': 'valor_aportado', 'lei_8_313_91_lei_rouanet': 'captado_lei_rouanet',
    'art_1o_lei_8_685_93': 'captado_art1', 'art_1o_a_lei_8_685_93': 'captado_art1a',
    'art_3o_lei_8_685_93': 'captado_art3', 'art_3o_a_lei_8_685_93': 'captado_art3a',
    'art_39_mp_2228_1_01': 'captado_art39', 'funcines': 'captado_funcines',
}


def source_text(value):
    return None if value is None or pd.isna(value) or str(value).strip() == '' else str(value).strip()


def source_year(value):
    if isinstance(value, datetime):
        return value.year
    text = str(value).strip()
    if re.fullmatch(r'(19|20)\d{2}', text):
        return int(text)
    return None


def transform(path: Path, table: str, url: str = ''):
    book = pd.ExcelFile(path)
    if len(book.sheet_names) != 1:
        raise ValueError(f'{path.name}: revisar novas abas {book.sheet_names}')
    raw = book.parse(book.sheet_names[0], header=None, keep_default_na=False)
    headers = [norm_col(c) for c in raw.iloc[2]]
    if headers[0] != 'ano_de_captacao' or len(set(headers)) != len(headers):
        raise ValueError(f'{path.name}: cabeçalho mudou')
    body = raw.iloc[3:].copy()
    body.columns = [RENAME.get(c, c) for c in headers]
    years = body.ano_de_captacao.map(source_year)
    data = body.loc[years.notna()].copy()
    notes = body.loc[years.isna()]
    # Notas conhecidas ocupam só a primeira coluna. Dados com ano inválido devem falhar.
    for index, row in notes.iterrows():
        if any(source_text(v) is not None for v in row.iloc[1:]):
            raise ValueError(f'{path.name}: linha não classificada {index + 1}')
    data.insert(0, 'linha_origem', data.index + 1)
    data.insert(1, 'ano', years.loc[data.index].astype('int64'))
    data = data.rename(columns={'ano_de_captacao': 'ano_captacao_original'})
    for col in data:
        if col not in {'ano', 'linha_origem'}:
            data[col] = data[col].map(source_text).astype('string')
    money = [c for c in data if c.startswith('captado_') or c in {'valor_aportado', 'total_captado_no_ano'}]
    expected = {'aportes_por_investidor': 1, 'captacao_por_projeto': 8, 'captacao_por_projeto_investidor': 7}[table]
    if len(money) != expected:
        raise ValueError(f'{path.name}: revisar colunas financeiras {money}')
    for col in money:
        data[col] = money_column(data[col])
    if 'data_captacao' in data:
        data['data_captacao'] = pd.to_datetime(data.data_captacao, errors='raise')
        if (data.data_captacao.dt.year != data.ano).any():
            raise ValueError('Ano diverge da data de captação')
    # Manter também o texto original: inclui a indicação Empresa Estrangeira.
    for col in ('cnpj_proponente', 'cnpj_investidor_ou_contribuinte'):
        if col in data:
            data[col + '_original'] = data[col].copy()
            digits = data[col].str.replace(r'[.\-/\s]', '', regex=True)
            data[col] = digits.where(digits.str.fullmatch(r'\d{1,14}', na=False)).str.zfill(14)
    data['moeda'] = 'BRL'
    data['fonte_arquivo'] = path.name
    data['fonte_aba'] = book.sheet_names[0]
    data['fonte_url'] = url
    data['hash_arquivo'] = hashlib.sha256(path.read_bytes()).hexdigest()
    data['data_coleta'] = path.parent.name
    return data.reset_index(drop=True), {
        'table': table, 'rows': len(data), 'money_columns': money,
        'original_headers': dict(zip(data.columns[2:2 + len(headers)], headers)),
        'notes': [str(v) for v in notes.iloc[:, 0] if source_text(v)],
        'source': path.name, 'sha256': data.hash_arquivo.iloc[0],
    }


def main():
    snap = latest_snapshot(SOURCE)
    inventory_path = latest_snapshot(ROOT / 'datasets/oca-publicacoes-complementares') / 'oca_links.csv'
    inventory = pd.read_csv(inventory_path, keep_default_na=False)
    reports = []
    # Validar todas antes de substituir qualquer saída.
    tables = {}
    for table, filename in FILES.items():
        match = inventory[inventory.local_path.str.endswith('/' + filename)]
        url = match.iloc[0].url_arquivo if len(match) else ''
        data, report = transform(snap / filename, table, url)
        tables[table] = data
        reports.append(report)
    OUT.mkdir(parents=True, exist_ok=True)
    for table, data in tables.items():
        temp = OUT / (table + '.parquet.tmp')
        data.to_parquet(temp, index=False)
        temp.replace(OUT / (table + '.parquet'))
        print(f'{table}: {len(data)} linhas originais preservadas')
    (OUT.parent / 'captacao_validation.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
