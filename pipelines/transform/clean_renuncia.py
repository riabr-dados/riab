"""Renúncia fiscal: preserva identificadores e valores exatos em reais."""
from pathlib import Path
import argparse
import pandas as pd

try:
    from .common import latest_snapshot
    from .financial_values import money_column
except ImportError:
    from common import latest_snapshot
    from financial_values import money_column

ROOT = Path(__file__).resolve().parents[2]
MONEY_COLUMNS = [
    'captado_art1', 'captado_art1a', 'captado_art3', 'captado_art3a',
    'captado_art18', 'captado_art25', 'captado_art39', 'captado_funcines',
    'captado_edital_ancine', 'captado_par', 'captado_paq', 'captado_outros_editais',
    'captado_lei_estadual', 'captado_lei_municipal', 'captado_outras_fontes',
    'captado_contrapartida', 'captado_conversao', 'total_captado',
]


def transform(path: Path) -> pd.DataFrame:
    for encoding in ('utf-8-sig', 'latin1'):
        try:
            df = pd.read_csv(path, encoding=encoding, sep=';', dtype='string', keep_default_na=False)
            break
        except UnicodeDecodeError:
            continue
    df.columns = [c.lower().strip() for c in df.columns]
    missing = set(MONEY_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f'Colunas monetárias ausentes: {sorted(missing)}')
    for col in df:
        df[col] = df[col].str.strip().replace('', pd.NA)
    for col in MONEY_COLUMNS:
        df[col] = money_column(df[col], brazilian_text=True)
    for col in ['data_pub_aprovacao_projeto', 'data_primeira_liberacao']:
        df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='raise')
    return df


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'pipelines/output/cleaned/renuncia_fiscal.parquet')
    args = parser.parse_args()
    source = args.input or latest_snapshot(ROOT / 'datasets/ancine-renuncia-fiscal') / 'projetos-com-renuncia-fiscal.csv'
    df = transform(source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_suffix('.parquet.tmp')
    df.to_parquet(temp, index=False)
    temp.replace(args.output)
    print(f'{args.output.name}: {len(df)} linhas; 18 campos monetários validados.')


if __name__ == '__main__':
    main()
