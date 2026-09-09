"""Separa as planilhas financeiras OCA em recursos analíticos homogêneos.

Cada saída representa uma única medida e granularidade. Totais publicados nas
planilhas são usados para validação, mas não são repetidos nas tabelas tratadas.
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import re
import sys

import pandas as pd
import pyarrow as pa

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipelines.transform.financial_values import parse_money  # noqa: E402

SNAPSHOT = "2026-05-23"
INVENTORY = ROOT / "datasets/oca-publicacoes-complementares/snapshots" / SNAPSHOT / "oca_links.csv"
OUTPUT = ROOT / "pipelines/output/cleaned"

MONTHS = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}


def text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    value = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        value = value[1:-1].strip()
    return value


def key(value: object) -> str:
    value = text(value).lower().translate(str.maketrans(
        "áàâãéêíóôõúüçº°", "aaaaeeiooouucoo"
    ))
    return re.sub(r"[^a-z0-9]+", "_", value).strip("_")


def read_csv(path: Path) -> pd.DataFrame:
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return pd.read_csv(path, sep=";", header=None, dtype=str,
                               keep_default_na=False, encoding=encoding)
        except UnicodeDecodeError:
            pass
    raise UnicodeError(f"Codificação não reconhecida: {path}")


def inventory() -> dict[str, dict[str, object]]:
    frame = pd.read_csv(INVENTORY, dtype=str, keep_default_na=False)
    return {Path(row.local_path).name: row._asdict() for row in frame.itertuples(index=False)}


def provenance(filename: str, line: int, meta: dict[str, dict[str, object]]) -> dict[str, object]:
    source = meta[filename]
    return {
        "linha_origem": line + 1,
        "fonte_arquivo": filename,
        "fonte_url": source["url_arquivo"],
        "hash_arquivo": source["hash_arquivo"],
        "data_coleta": SNAPSHOT,
    }


def amount(value: object, *, brazilian: bool) -> Decimal | None:
    if isinstance(value, (int, float)):
        # Remove ruído binário do XLSX, preservando frações de centavo publicadas.
        return Decimal(str(round(float(value), 6)))
    return parse_money(text(value), brazilian_text=brazilian)


def write(records: list[dict[str, object]], name: str) -> None:
    if not records:
        raise ValueError(f"{name}: nenhuma linha gerada")
    frame = pd.DataFrame(records)
    money_cols = [column for column in frame if column.startswith("valor_")]
    for column in money_cols:
        values = frame[column].tolist()
        scale = max(2, max((-value.as_tuple().exponent for value in values if value is not None), default=2))
        frame[column] = pd.Series(values, dtype=pd.ArrowDtype(pa.decimal128(38, scale)))
    for column in ("ano", "ano_inicio", "ano_fim", "mes", "linha_origem"):
        if column in frame:
            frame[column] = pd.to_numeric(frame[column], errors="raise").astype("Int64")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    target = OUTPUT / f"{name}.parquet"
    temporary = target.with_suffix(".parquet.tmp")
    frame.to_parquet(temporary, index=False)
    pd.read_parquet(temporary)
    temporary.replace(target)
    print(f"{name}: {len(frame):,} linhas")


def validate_reconciliation() -> None:
    """Confere que microdados de empresas fecham com as séries mensais oficiais."""
    monthly = pd.read_parquet(OUTPUT / "condecine_recolhimento_mensal.parquet")
    pairs = {
        "condecine_recolhimento_distribuidoras_art3": "artigo_3",
        "condecine_recolhimento_empresas_art3a": "artigo_3a",
        "condecine_recolhimento_programadoras_art39": "artigo_39",
    }
    for table, mechanism in pairs.items():
        detail = pd.read_parquet(OUTPUT / f"{table}.parquet")
        detail_totals = detail.groupby("ano", dropna=False)["valor_nominal_brl"].sum()
        monthly_totals = monthly.loc[monthly["mecanismo"] == mechanism].groupby("ano")["valor_nominal_brl"].sum()
        if not detail_totals.equals(monthly_totals):
            delta = detail_totals.subtract(monthly_totals, fill_value=Decimal("0"))
            raise ValueError(f"{table}: não reconcilia com série mensal: {delta[delta != 0].to_dict()}")
    print("reconciliação CONDECINE: microdados = séries mensais em todos os anos")


def parse_fsa_workbook(meta: dict[str, dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    filename = "valores-execucao-fundo-setorial-do-audiovisual-em-reais-r-2007-a-2019.xlsx"
    path = ROOT / meta[filename]["local_path"]
    outputs = {
        "fsa_arrecadacao_anual": [],
        "fsa_editais_lancados": [],
        "fsa_desembolsos": [],
    }
    for sheet, output in zip(pd.ExcelFile(path).sheet_names, outputs, strict=True):
        frame = pd.read_excel(path, sheet_name=sheet, header=None, keep_default_na=False)
        for row_number, row in frame.iterrows():
            period = text(row.iloc[0])
            match = re.fullmatch(r"(\d{4})(?:/(\d{4}))?", period)
            if not match or row.shape[0] < 2 or text(row.iloc[1]) == "":
                continue
            outputs[output].append({
                "periodo": period,
                "ano_inicio": int(match.group(1)),
                "ano_fim": int(match.group(2) or match.group(1)),
                "valor_nominal_brl": amount(row.iloc[1], brazilian=False),
                **provenance(filename, row_number, meta),
            })
    return outputs


def parse_wide(filename: str, *, label_name: str, meta: dict[str, dict[str, object]],
               sections: tuple[tuple[int, int, int, str | None], ...] | None = None,
               mechanism: str | None = None, currency_aware: bool = False) -> list[dict[str, object]]:
    """Lê matriz categoria x ano; sections contém (header, first, last, section)."""
    frame = read_csv(ROOT / meta[filename]["local_path"])
    if sections is None:
        header = next(i for i, row in frame.iterrows()
                      if sum(bool(re.fullmatch(r"\d{4}", text(v))) for v in row) >= 2)
        sections = ((header, header + 1, len(frame), None),)
    records: list[dict[str, object]] = []
    for header, first, last, section in sections:
        years = [(column, int(text(value))) for column, value in enumerate(frame.iloc[header])
                 if re.fullmatch(r"\d{4}", text(value))]
        for row_number in range(first, min(last, len(frame))):
            label = text(frame.iat[row_number, 0])
            if not label or key(label) == "total" or key(label).startswith(("fonte", "nota", "subtotal")):
                continue
            for column, year in years:
                raw = frame.iat[row_number, column]
                if text(raw) in {"", "-", "–", "--"}:
                    continue
                record = {"ano": year, label_name: label,
                          **provenance(filename, row_number, meta)}
                if currency_aware:
                    raw_text = text(raw)
                    currency = ("USD" if raw_text.startswith("$") and not raw_text.startswith("R$")
                                else "EUR" if raw_text.startswith("€") else "BRL")
                    record["moeda_original"] = currency
                    cleaned = raw_text.removeprefix("$").removeprefix("€").strip()
                    record["valor_original"] = amount(cleaned, brazilian=True)
                else:
                    record["valor_nominal_brl"] = amount(raw, brazilian=True)
                if section is not None:
                    record["secao_origem"] = section
                if mechanism is not None:
                    record["mecanismo"] = mechanism
                records.append(record)
    return records


def parse_condecine_monthly(filename: str, section: int,
                            meta: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    frame = read_csv(ROOT / meta[filename]["local_path"])
    headers = [i for i, row in frame.iterrows()
               if sum(key(v) in MONTHS for v in row) >= 10]
    if len(headers) < 2:
        raise ValueError(f"{filename}: duas seções mensais não encontradas")
    header = headers[section]
    year = int(re.search(r"(20\d{2})", filename).group(1))
    records = []
    for row_number in range(header + 1, min(header + 5, len(frame))):
        category = text(frame.iat[row_number, 0])
        if not category:
            continue
        for column, value in enumerate(frame.iloc[header]):
            month = MONTHS.get(key(value))
            if month is None:
                continue
            raw = frame.iat[row_number, column]
            if text(raw) in {"", "-", "–", "--"}:
                continue
            records.append({
                "ano": year, "mes": month, "tipo_condecine": category,
                "valor_nominal_brl": amount(raw, brazilian=True),
                **provenance(filename, row_number, meta),
            })
    return records


def parse_detail(filename: str, columns: tuple[str, ...],
                 meta: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    frame = read_csv(ROOT / meta[filename]["local_path"])
    header = next(i for i, row in frame.iterrows() if key(row.iloc[0]) == "ano_de_recolhimento")
    records = []
    for row_number in range(header + 1, len(frame)):
        year = text(frame.iat[row_number, 0])
        if not re.fullmatch(r"\d{4}", year):
            continue
        record = {"ano": int(year)}
        for offset, column in enumerate(columns, start=1):
            record[column] = text(frame.iat[row_number, offset]) or None
        record["valor_nominal_brl"] = amount(frame.iat[row_number, len(columns) + 1], brazilian=True)
        record.update(provenance(filename, row_number, meta))
        records.append(record)
    return records


def main() -> None:
    meta = inventory()
    for name, records in parse_fsa_workbook(meta).items():
        write(records, name)

    wide_sources = [
        ("valores-liberados-por-mecanismo-de-incentivo-em-reais-r-2015-a-2019.xlsx", "fomento_valores_liberados_mecanismo"),
        ("valores-totais-captados-por-mecanismo-de-incentivo-2006-a-2024r.csv", "fomento_valores_captados_mecanismo"),
        ("valores-totais-de-editais-programas-e-premios-2003-a-2020.csv", "fomento_editais_programas_premios"),
    ]
    for filename, output in wide_sources:
        # Apenas as duas fontes antigas sem CSV usam XLSX.
        path = ROOT / meta[filename]["local_path"]
        if path.suffix == ".xlsx":
            frame = pd.read_excel(path, header=None, keep_default_na=False)
            header = next(i for i, row in frame.iterrows()
                          if sum(bool(re.fullmatch(r"\d{4}", text(v))) for v in row) >= 2)
            records = []
            years = [(c, int(text(v))) for c, v in enumerate(frame.iloc[header]) if re.fullmatch(r"\d{4}", text(v))]
            for row_number in range(header + 1, len(frame)):
                label = text(frame.iat[row_number, 0])
                if not label or key(label) == "total" or key(label).startswith(("fonte", "nota")):
                    continue
                for column, year in years:
                    raw = frame.iat[row_number, column]
                    if text(raw) in {"", "-", "–", "--"}:
                        continue
                    records.append({"ano": year, "mecanismo_ou_programa": label,
                                    "valor_nominal_brl": amount(raw, brazilian=False),
                                    **provenance(filename, row_number, meta)})
        else:
            records = parse_wide(filename, label_name="mecanismo_ou_programa", meta=meta,
                                 currency_aware=output == "fomento_editais_programas_premios")
        write(records, output)

    annual = "planilha-valores-arrecadados-condecine-2007-a-2025.csv"
    write(parse_wide(annual, label_name="tipo_condecine", meta=meta,
                     sections=((3, 4, 8, None),)), "condecine_arrecadacao_bruta_anual")
    write(parse_wide(annual, label_name="tipo_condecine", meta=meta,
                     sections=((11, 12, 16, None),)), "condecine_arrecadacao_pos_dru_anual")

    monthly = sorted(name for name in meta if re.fullmatch(r"valores-condecine-por-mes-20\d{2}\.csv", name))
    for section, output in ((0, "condecine_arrecadacao_bruta_mensal"),
                            (1, "condecine_arrecadacao_pos_dru_mensal")):
        records = []
        for filename in monthly:
            records.extend(parse_condecine_monthly(filename, section, meta))
        write(records, output)

    mechanisms = {
        "valores-recolhidos-art-3deg-da-lei-8-685-93-2002-a-2017.csv": "artigo_3",
        "valores-recolhidos-art-3dega-da-lei-8-685-93-2009-a-2017.csv": "artigo_3a",
        "valores-recolhidos-art-39-da-mp-2-228-1-01-2003-a-2017.csv": "artigo_39",
    }
    records = []
    for filename, mechanism in mechanisms.items():
        source = parse_wide(filename, label_name="mes_nome", meta=meta, mechanism=mechanism)
        source = [row for row in source if key(row["mes_nome"]) in MONTHS]
        for row in source:
            row["mes"] = MONTHS[key(row.pop("mes_nome"))]
        records.extend(source)
    write(records, "condecine_recolhimento_mensal")

    combined = "valores-recolhidos-por-mecanismo-de-incentivo-e-respectivos-creditos-remessas-para-o-exterior-2002-a-2017.csv"
    write(parse_wide(combined, label_name="mecanismo", meta=meta,
                     sections=((2, 3, 6, None),)), "condecine_recolhimento_mecanismo")
    write(parse_wide(combined, label_name="mecanismo", meta=meta,
                     sections=((10, 11, 14, None),)), "condecine_creditos_remessas_exterior")

    detail_sources = [
        ("valores-recolhidos-por-distribuidora-art-3deg-da-lei-8-685-93-2002-a-2017.csv",
         ("empresa_estrangeira_representada", "empresa_brasileira"), "condecine_recolhimento_distribuidoras_art3"),
        ("valores-recolhidos-por-empresa-art-3dega-da-lei-8-685-93-2009-a-2017.csv",
         ("empresa_remetente", "empresa_estrangeira_contribuinte"), "condecine_recolhimento_empresas_art3a"),
        ("valores-recolhidos-por-programadora-art-39-da-mp-2-228-1-01-2003-a-2017.csv",
         ("programadora_estrangeira",), "condecine_recolhimento_programadoras_art39"),
    ]
    for filename, columns, output in detail_sources:
        write(parse_detail(filename, columns, meta), output)
    validate_reconciliation()


if __name__ == "__main__":
    main()
