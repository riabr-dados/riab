"""Conversão monetária explícita: ausências são distintas de erros e de zero."""
from decimal import Decimal
import re

import pandas as pd
import pyarrow as pa


def parse_money(value, *, brazilian_text=False):
    if value is None or pd.isna(value):
        return None
    text = str(value).replace('\xa0', ' ').strip()
    if text in {'', '-', '–', '--'}:
        return None
    local = brazilian_text or 'R$' in text or ',' in text
    negative = text.startswith('(') and text.endswith(')')
    if negative:
        text = text[1:-1].strip()
    text = text.removeprefix('R$').strip()
    pattern = r'-?(?:\d+|\d{1,3}(?:\.\d{3})+)(?:,\d{1,2})?' if local else r'-?\d+(?:\.\d+)?'
    if not re.fullmatch(pattern, text):
        raise ValueError(f'Valor monetário não reconhecido: {value!r}')
    if local:
        text = text.replace('.', '').replace(',', '.')
    amount = Decimal(text)
    if negative:
        amount = -amount
    return amount


def money_column(series, *, brazilian_text=False):
    values = []
    for index, value in series.items():
        try:
            values.append(parse_money(value, brazilian_text=brazilian_text))
        except ValueError as exc:
            raise ValueError(f'{series.name}, linha {index}: {exc}') from exc
    # Algumas planilhas oficiais contêm frações de centavo; não arredondar a origem.
    scale = max(2, max((-v.as_tuple().exponent for v in values if v is not None), default=2))
    return pd.Series(values, index=series.index, dtype=pd.ArrowDtype(pa.decimal128(38, scale)))
