from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

import pandas as pd
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
CLEANED = ROOT / "pipelines" / "output" / "cleaned"
DATASET_DIR = ROOT / "datasets" / "br-comercio-exterior-servicos-audiovisuais"
SNAPSHOT_DATE = "2026-05-23"
SNAPSHOT = DATASET_DIR / "snapshots" / SNAPSHOT_DATE
SOURCE_TABLE = CLEANED / "comercio_exterior_servicos_audiovisuais_fontes.csv"
SOURCE_FILE = "comercio-exterior-de-servicos-audiovisuais-ano-base-2019.pdf"
SOURCE_URL_FALLBACK = "https://www.gov.br/ancine/pt-br/oca/resolveuid/5c8cf11479a5472abe8adc08c2bbd1b2"
SOURCE_PAGE_FALLBACK = "https://www.gov.br/ancine/pt-br/oca/publicacoes-2/outras-publicacoes"

YEAR_HEADER_RE = re.compile(
    r"Brasil:\s*Vendas e Aquisi\S+es por Servi\S+o Audiovisual\s*-\s*(\d{4})",
    re.IGNORECASE,
)
CODE_RE = re.compile(r"(1\.\d{4}\.\d{2}\.\d{2})\s*-\s*")
VALUE_RE = re.compile(r"\d{1,3}(?:\.\d{3})*,\d{2}")


def strip_accents_light(value: str) -> str:
    repl = str.maketrans(
        "áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ",
        "aaaaeeiooouucAAAAEEIOOOUUC",
    )
    return value.translate(repl)


def clean_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).replace("\xa0", " ").strip()
    try:
        repaired = text.encode("latin-1").decode("utf-8")
        if repaired:
            text = repaired
    except UnicodeError:
        pass
    return re.sub(r"\s+", " ", text)


def parse_number(text: str) -> float:
    return float(text.replace(".", "").replace(",", "."))


def source_metadata() -> dict[str, object]:
    metadata: dict[str, object] = {
        "fonte_arquivo": SOURCE_FILE,
        "fonte_url": SOURCE_URL_FALLBACK,
        "fonte_pagina": SOURCE_PAGE_FALLBACK,
        "hash_fonte": None,
    }
    if not SOURCE_TABLE.exists():
        return metadata

    fontes = pd.read_csv(SOURCE_TABLE)
    mask = fontes.get("titulo", pd.Series(dtype=str)).astype(str).str.contains(
        "Ano-Base 2019",
        case=False,
        na=False,
    )
    if not mask.any():
        return metadata
    row = fontes.loc[mask].iloc[0]
    metadata["fonte_url"] = row.get("url_arquivo") or SOURCE_URL_FALLBACK
    metadata["fonte_pagina"] = row.get("pagina_origem") or SOURCE_PAGE_FALLBACK
    metadata["hash_fonte"] = row.get("hash_arquivo") if pd.notna(row.get("hash_arquivo")) else None
    local_path = row.get("local_path")
    if pd.notna(local_path):
        metadata["fonte_arquivo"] = Path(str(local_path)).name
    return metadata


def choose_source_pdf() -> Path:
    if SOURCE_TABLE.exists():
        fontes = pd.read_csv(SOURCE_TABLE)
        mask = fontes.get("titulo", pd.Series(dtype=str)).astype(str).str.contains(
            "Ano-Base 2019",
            case=False,
            na=False,
        )
        if mask.any():
            local_path = fontes.loc[mask, "local_path"].iloc[0]
            if pd.notna(local_path):
                return ROOT / str(local_path)
    return SNAPSHOT / SOURCE_FILE


def normalize_group(text: str) -> str:
    norm = strip_accents_light(text.lower())
    norm = re.sub(r"\s+", " ", norm).strip()
    if "licencia" in norm:
        return "Licenciamento de Direitos"
    if "cess" in norm and "direit" in norm:
        return "Cessao de Direitos"
    if "tv paga" in norm:
        return "TV Paga"
    if norm == "vod" or " vod" in f" {norm} ":
        return "VoD"
    if "tv aberta" in norm:
        return "TV Aberta"
    if "produc" in norm and "pos" in norm:
        return "Producao e Pos-Producao"
    if "outros" in norm:
        return "Outros"
    return text.strip() or "Nao informado"


def keep_context_line(line: str) -> bool:
    if not line:
        return False
    if re.fullmatch(r"\d+", line):
        return False
    norm = strip_accents_light(line.lower())
    skip_tokens = [
        "comercio exterior de servicos audiovisuais",
        "ano-base",
        "valor vendido",
        "valor adquirido",
        "saldo",
        "grupo nbs",
        "fonte:",
        "anexo - dados primarios",
        "brasil: vendas e aquisicoes",
    ]
    return not any(token in norm for token in skip_tokens)


def split_year_blocks(text: str) -> dict[int, str]:
    matches = list(YEAR_HEADER_RE.finditer(text))
    blocks: dict[int, str] = {}
    for idx, match in enumerate(matches):
        year = int(match.group(1))
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        blocks[year] = text[start:end]
    return blocks


def coerce_trade_values(values: list[float], entry_text: str) -> tuple[float, float, float]:
    negatives = re.findall(r"-\s*(\d{1,3}(?:\.\d{3})*,\d{2})", entry_text)
    negative_last = bool(negatives) and values and parse_number(negatives[-1]) == values[-1]

    if not values:
        return 0.0, 0.0, 0.0

    if len(values) >= 3:
        sold = values[-3]
        acquired = values[-2]
        saldo = -values[-1] if negative_last else values[-1]
        return sold, acquired, saldo

    if len(values) == 2:
        saldo = -values[-1] if negative_last else values[-1]
        if abs(values[0] + saldo) < 0.01:
            return 0.0, values[0], saldo
        if abs(values[0] - saldo) < 0.01:
            return values[0], 0.0, saldo
        if negative_last:
            return values[0], values[1], values[0] - values[1]
        return values[0], 0.0, saldo

    if len(values) == 1:
        saldo = -values[0] if negative_last else values[0]
        if negative_last:
            return 0.0, values[0], saldo
        return values[0], 0.0, saldo

    raise ValueError(f"Linha com padrao numerico inesperado: {entry_text}")


def parse_year_block(year: int, block: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    lines = [clean_cell(line) for line in block.splitlines()]
    records: list[dict[str, object]] = []
    current_group_parts: list[str] = []
    current_group = "Nao informado"
    total_record: dict[str, object] | None = None
    i = 0

    while i < len(lines):
        line = lines[i]
        if not line or line.startswith("Fonte:"):
            i += 1
            continue

        if line.startswith("Total"):
            nums = [parse_number(token) for token in VALUE_RE.findall(line)]
            sold, acquired, saldo = coerce_trade_values(nums, line)
            total_record = {
                "ano": year,
                "valor_vendido_usd_nominal": sold,
                "valor_adquirido_usd_nominal": acquired,
                "saldo_usd_nominal": saldo,
                "unidade_original": "USD nominal",
            }
            i += 1
            continue

        code_match = CODE_RE.search(line)
        if not code_match:
            if keep_context_line(line):
                current_group_parts.append(line)
            i += 1
            continue

        group_prefix = clean_cell(line[: code_match.start()])
        if group_prefix:
            current_group_parts.append(group_prefix)
        if current_group_parts:
            current_group = normalize_group(" ".join(current_group_parts))
        entry_text = clean_cell(line[code_match.start() :])
        j = i + 1
        while j < len(lines):
            next_line = lines[j]
            if not next_line or next_line.startswith("Fonte:") or next_line.startswith("Total"):
                break
            if CODE_RE.search(next_line):
                break
            entry_text = clean_cell(f"{entry_text} {next_line}")
            j += 1

        code = code_match.group(1)
        values = [parse_number(token) for token in VALUE_RE.findall(entry_text)]
        sold, acquired, saldo = coerce_trade_values(values, entry_text)
        description = clean_cell(entry_text[code_match.end() :])
        for token in VALUE_RE.findall(entry_text):
            description = description.replace(token, "")
        description = re.sub(r"\s*-\s*$", "", description).strip(" -")

        records.append(
            {
                "ano": year,
                "grupo_servico": current_group,
                "codigo_nbs": code,
                "descricao_servico": description,
                "valor_vendido_usd_nominal": sold,
                "valor_adquirido_usd_nominal": acquired,
                "saldo_usd_nominal": saldo,
                "unidade_original": "USD nominal",
            }
        )
        current_group_parts = []
        i = j

    if total_record is None:
        raise ValueError(f"Nenhum total anual encontrado para {year}")
    return records, total_record


def build_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    path = choose_source_pdf()
    text = "\n".join(
        (page.extract_text() or "")
        for page in PdfReader(BytesIO(path.read_bytes())).pages
    )
    blocks = split_year_blocks(text)
    service_rows: list[dict[str, object]] = []
    total_rows: list[dict[str, object]] = []
    for year in sorted(blocks):
        if year < 2014 or year > 2019:
            continue
        records, total = parse_year_block(year, blocks[year])
        service_rows.extend(records)
        total_rows.append(total)

    service = pd.DataFrame(service_rows).sort_values(["ano", "grupo_servico", "codigo_nbs"]).reset_index(drop=True)
    total = pd.DataFrame(total_rows).sort_values("ano").reset_index(drop=True)

    grouped = (
        service.groupby("ano", as_index=False)[
            ["valor_vendido_usd_nominal", "valor_adquirido_usd_nominal", "saldo_usd_nominal"]
        ]
        .sum()
        .round(2)
    )
    merged = total.merge(
        grouped,
        on="ano",
        suffixes=("_publicado", "_soma_servicos"),
    )
    for metric in ("valor_vendido_usd_nominal", "valor_adquirido_usd_nominal", "saldo_usd_nominal"):
        diff = (
            merged[f"{metric}_publicado"].round(2)
            - merged[f"{metric}_soma_servicos"].round(2)
        ).abs()
        if diff.max() > 0.5:
            raise ValueError(f"Soma dos servicos diverge do total publicado para {metric}: {diff.tolist()}")

    return service, total


def write_table(df: pd.DataFrame, table_name: str) -> None:
    CLEANED.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEANED / f"{table_name}.csv", index=False, encoding="utf-8")
    df.to_parquet(CLEANED / f"{table_name}.parquet", index=False)
    df.to_csv(SNAPSHOT / f"{table_name}.csv", index=False, encoding="utf-8")
    print(f"[OK] {table_name}: {len(df):,} linhas")


def update_source_table() -> None:
    if not SOURCE_TABLE.exists():
        return
    df = pd.read_csv(SOURCE_TABLE)
    df["status_extracao"] = "extracao_factual_publicada"
    df["observacao_metodologica"] = (
        "Inventario oficial das fontes. As tabelas factuais "
        "comercio_exterior_servicos_audiovisuais_total_ano e "
        "comercio_exterior_servicos_audiovisuais_servico_ano sao geradas por "
        "pipelines/transform/clean_comercio_exterior_servicos_audiovisuais.py "
        "a partir do Anexo do estudo ANCINE ano-base 2019."
    )
    df.to_csv(SOURCE_TABLE, index=False, encoding="utf-8")
    df.to_parquet(SOURCE_TABLE.with_suffix(".parquet"), index=False)


def main() -> int:
    service, total = build_tables()
    write_table(service, "comercio_exterior_servicos_audiovisuais_servico_ano")
    write_table(total, "comercio_exterior_servicos_audiovisuais_total_ano")
    update_source_table()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
