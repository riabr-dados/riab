"""
Transforma complementos OCA em parquets iniciais consolidados.

Este pipeline publica apenas tabelas com dados extraidos de fontes oficiais:
- CONDECINE arrecadacao anual/mensal a partir de CSVs OCA.
- Fluxos financeiros de fomento a partir de CSV/XLSX OCA.
- Historico Embrafilme de exibicao a partir de PDFs tabulares OCA.
"""
from __future__ import annotations

import re
import sys
from io import BytesIO
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipelines.extract.oca_inventory import (  # noqa: E402
    SNAPSHOT_DATE,
    build_inventory,
    download_inventory_files,
    write_inventory,
)


CLEANED = ROOT / "pipelines" / "output" / "cleaned"
CLEANED.mkdir(parents=True, exist_ok=True)

MONTHS = {
    "janeiro": 1,
    "fevereiro": 2,
    "marco": 3,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}

MONTH_LABELS = {
    "JANEIRO": 1,
    "FEVEREIRO": 2,
    "MARÇO": 3,
    "MARCO": 3,
    "ABRIL": 4,
    "MAIO": 5,
    "JUNHO": 6,
    "JULHO": 7,
    "AGOSTO": 8,
    "SETEMBRO": 9,
    "OUTUBRO": 10,
    "NOVEMBRO": 11,
    "DEZEMBRO": 12,
}


def strip_accents_light(value: str) -> str:
    repl = str.maketrans("áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ", "aaaaeeiooouucAAAAEEIOOOUUC")
    return value.translate(repl)


def clean_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).replace("\xa0", " ").strip()
    text = re.sub(r"\s+", " ", text)
    # Some OCA CSVs wrap values in explicit double-quotes (e.g. "2017", "Valor")
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        text = text[1:-1].strip()
    return text


def parse_brl(value: object) -> float | None:
    text = clean_cell(value)
    if not text or text in {"-", "–", "--", "nan"}:
        return None
    text = text.replace("R$", "").replace("%", "").strip()
    neg = text.startswith("(") and text.endswith(")")
    text = text.strip("()")
    text = re.sub(r"[^0-9,.\-]", "", text)
    if not text or text in {"-", ","}:
        return None
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    else:
        parts = text.split(".")
        if len(parts) > 1 and all(len(part) == 3 for part in parts[1:]):
            text = "".join(parts)
    try:
        value_float = float(text)
    except ValueError:
        return None
    return -value_float if neg else value_float


def read_raw_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        for enc in ("utf-8-sig", "latin-1"):
            try:
                return pd.read_csv(path, sep=";", header=None, dtype=str, encoding=enc)
            except UnicodeDecodeError:
                continue
        return pd.read_csv(path, sep=";", header=None, dtype=str, encoding_errors="replace")
    return pd.read_excel(path, header=None, dtype=str)


def find_year_header(df: pd.DataFrame) -> int | None:
    for idx, row in df.iterrows():
        years = [clean_cell(v) for v in row if re.fullmatch(r"\d{4}", clean_cell(v))]
        if len(years) >= 2:
            return int(idx)
    return None


def find_month_header(df: pd.DataFrame) -> int | None:
    for idx, row in df.iterrows():
        months = [strip_accents_light(clean_cell(v).lower()) for v in row]
        if sum(1 for v in months if v in MONTHS) >= 3:
            return int(idx)
    return None


def find_detail_header(df: pd.DataFrame) -> int | None:
    candidates = (
        "salic", "cnpj", "proponente", "projeto", "investidor", "ano de",
        "edital", "empresa", "distribuidora", "programadora", "produtora",
        "obra", "festival",
    )
    for idx, row in df.iterrows():
        values = [strip_accents_light(clean_cell(v).lower()) for v in row]
        non_empty = sum(1 for v in values if v)
        if non_empty < 2:
            continue
        score = sum(any(c in v for c in candidates) for v in values)
        if score >= 2:
            return int(idx)
    return None


def numeric_columns(columns: list[str]) -> list[str]:
    patterns = (
        "valor",
        "total",
        "lei ",
        "lei_",
        "art.",
        "art ",
        "art_",
        "mp ",
        "fsa",
        "rouanet",
        "reais",
        "premio",
        "prêmio",
        "investiment",
        "apoio",
        "renda",
    )
    out = []
    for col in columns:
        norm = strip_accents_light(col.lower())
        if any(p in norm for p in patterns):
            out.append(col)
    return out


def normalize_header(values: list[object]) -> list[str]:
    columns = []
    used: dict[str, int] = {}
    for i, value in enumerate(values):
        text = clean_cell(value) or f"coluna_{i + 1}"
        text = strip_accents_light(text.lower())
        text = re.sub(r"[^a-z0-9]+", "_", text).strip("_") or f"coluna_{i + 1}"
        count = used.get(text, 0)
        used[text] = count + 1
        columns.append(f"{text}_{count + 1}" if count else text)
    return columns


def infer_tipo_fluxo(title: str) -> str:
    text = strip_accents_light(title.lower())
    if "condecine" in text:
        return "arrecadacao_condecine"
    if "captado" in text:
        return "captado"
    if "aportado" in text:
        return "aportado"
    if "recolhido" in text or "originado" in text:
        return "recolhido"
    if "execucao fundo" in text or "execucao fsa" in text:
        return "execucao_fsa"
    if "liberado" in text:
        return "liberado"
    if "ibermedia" in text:
        return "ibermedia"
    if "coproducao" in text:
        return "coproducao_internacional"
    if "festival" in text:
        return "apoio_festivais"
    if "edital" in text or "programa" in text or "premio" in text:
        return "edital_programa_premio"
    return "fluxo_financeiro"


def infer_currency(title: str, column: str | None = None) -> str:
    text = strip_accents_light(f"{title} {column or ''}".lower())
    if "valor_us" in text or "us$" in text or "dolar" in text or "dolares" in text:
        return "USD"
    return "BRL"


def first_matching(row: pd.Series, names: list[str]) -> str | None:
    lookup = {strip_accents_light(str(c).lower()): c for c in row.index}
    for name in names:
        key = strip_accents_light(name.lower())
        for norm, original in lookup.items():
            if key in norm:
                value = clean_cell(row[original])
                if value:
                    return value
    return None


def parse_condecine_file(row: pd.Series) -> list[dict[str, object]]:
    path = ROOT / str(row["local_path"])
    df = read_raw_table(path)
    records: list[dict[str, object]] = []

    year_header = find_year_header(df)
    month_header = find_month_header(df)
    title = str(row["titulo"])

    if year_header is not None and (month_header is None or year_header < month_header):
        header = [clean_cell(v) for v in df.iloc[year_header].tolist()]
        year_cols = [(i, int(v)) for i, v in enumerate(header) if re.fullmatch(r"\d{4}", v)]
        for _, values in df.iloc[year_header + 1 :].iterrows():
            recorte_nome = clean_cell(values.iloc[0])
            if not recorte_nome or recorte_nome.lower().startswith("fonte"):
                continue
            for col_idx, ano in year_cols:
                valor = parse_brl(values.iloc[col_idx])
                if valor is None:
                    continue
                records.append(
                    {
                        "periodicidade": "ano",
                        "ano": ano,
                        "mes": None,
                        "data_inicio_periodo": f"{ano}-01-01",
                        "recorte_tipo": "tipo_condecine",
                        "recorte_nome": recorte_nome,
                        "moeda": "BRL",
                        "valor_nominal": valor,
                        "valor_brl_nominal": valor,
                        "valor_brl_real_base_2024": None,
                        "fonte_arquivo": path.name,
                        "fonte_url": row["url_arquivo"],
                        "hash_arquivo": row.get("hash_arquivo"),
                        "titulo_publicacao": title,
                        "data_coleta": SNAPSHOT_DATE,
                    }
                )
    elif month_header is not None:
        header = [clean_cell(v) for v in df.iloc[month_header].tolist()]
        month_cols = []
        for i, value in enumerate(header):
            key = strip_accents_light(value.lower())
            if key in MONTHS:
                month_cols.append((i, MONTHS[key], value))
        year_match = re.search(r"(20\d{2}|19\d{2})", title)
        ano = int(year_match.group(1)) if year_match else None
        if ano is None:
            ano_ref = clean_cell(row.get("ano_referencia"))
            ano = int(ano_ref) if re.fullmatch(r"\d{4}", ano_ref) else None
        for _, values in df.iloc[month_header + 1 :].iterrows():
            recorte_nome = clean_cell(values.iloc[0])
            if not recorte_nome or recorte_nome.lower().startswith("fonte"):
                continue
            for col_idx, mes, _ in month_cols:
                valor = parse_brl(values.iloc[col_idx])
                if valor is None or ano is None:
                    continue
                records.append(
                    {
                        "periodicidade": "mes",
                        "ano": ano,
                        "mes": mes,
                        "data_inicio_periodo": f"{ano}-{mes:02d}-01",
                        "recorte_tipo": "tipo_condecine",
                        "recorte_nome": recorte_nome,
                        "moeda": "BRL",
                        "valor_nominal": valor,
                        "valor_brl_nominal": valor,
                        "valor_brl_real_base_2024": None,
                        "fonte_arquivo": path.name,
                        "fonte_url": row["url_arquivo"],
                        "hash_arquivo": row.get("hash_arquivo"),
                        "titulo_publicacao": title,
                        "data_coleta": SNAPSHOT_DATE,
                    }
                )
    return records


def parse_wide_year_flux(row: pd.Series, df: pd.DataFrame, header_idx: int) -> list[dict[str, object]]:
    path = ROOT / str(row["local_path"])
    header = [clean_cell(v) for v in df.iloc[header_idx].tolist()]
    year_cols = [(i, int(v)) for i, v in enumerate(header) if re.fullmatch(r"\d{4}", v)]
    label_col = 0
    title = str(row["titulo"])
    records = []
    for _, values in df.iloc[header_idx + 1 :].iterrows():
        label = clean_cell(values.iloc[label_col])
        if not label or label.lower().startswith("fonte"):
            continue
        for col_idx, ano in year_cols:
            valor = parse_brl(values.iloc[col_idx])
            if valor is None:
                continue
            records.append(
                {
                    "ano": ano,
                    "periodo": str(ano),
                    "tipo_fluxo": infer_tipo_fluxo(title),
                    "mecanismo": label if "mecanismo" in strip_accents_light(title.lower()) else None,
                    "programa": label if "mecanismo" not in strip_accents_light(title.lower()) else None,
                    "edital": None,
                    "salic": None,
                    "titulo_projeto": None,
                    "cnpj_proponente": None,
                    "cnpj_investidor_ou_contribuinte": None,
                    "moeda_original": infer_currency(title),
                    "valor_original": valor,
                    "valor_brl_nominal": valor if infer_currency(title) == "BRL" else None,
                    "valor_brl_real_base_2024": None,
                    "nivel_agregacao": "agregado_ano",
                    "fonte_arquivo": path.name,
                    "hash_arquivo": row.get("hash_arquivo"),
                    "fonte_url": row["url_arquivo"],
                    "titulo_publicacao": title,
                    "data_coleta": SNAPSHOT_DATE,
                }
            )
    return records


def parse_detail_flux(row: pd.Series, df: pd.DataFrame, header_idx: int) -> list[dict[str, object]]:
    path = ROOT / str(row["local_path"])
    columns = normalize_header(df.iloc[header_idx].tolist())
    body = df.iloc[header_idx + 1 :].copy()
    body = body.iloc[:, : len(columns)]
    body.columns = columns
    body = body.dropna(how="all")

    value_cols = numeric_columns(columns)
    if not value_cols:
        value_cols = [c for c in columns if c.startswith("valor") or c.startswith("total")]

    title = str(row["titulo"])
    records = []
    for _, data in body.iterrows():
        ano_text = first_matching(data, ["ano de captacao", "ano", "ano edital", "ano referencia"])
        ano = int(ano_text) if ano_text and re.fullmatch(r"\d{4}", ano_text) else None
        salic = first_matching(data, ["salic"])
        titulo_projeto = first_matching(data, ["nome do projeto", "titulo", "projeto"])
        cnpj_prop = first_matching(data, ["cnpj do proponente", "cnpj proponente"])
        cnpj_inv = first_matching(data, ["cnpj do investidor", "cnpj investidor", "cnpj incentivador", "cnpj contribuinte"])
        edital = first_matching(data, ["edital", "chamada"])
        programa = first_matching(data, ["programa"])
        mecanismo_base = first_matching(data, ["mecanismo"])

        for col in value_cols:
            valor = parse_brl(data[col])
            if valor is None:
                continue
            moeda = infer_currency(title, col)
            records.append(
                {
                    "ano": ano,
                    "periodo": str(ano) if ano else clean_cell(row.get("ano_referencia")),
                    "tipo_fluxo": infer_tipo_fluxo(title),
                    "mecanismo": mecanismo_base or col,
                    "programa": programa,
                    "edital": edital,
                    "salic": salic,
                    "titulo_projeto": titulo_projeto,
                    "cnpj_proponente": re.sub(r"\D", "", cnpj_prop or "") or None,
                    "cnpj_investidor_ou_contribuinte": re.sub(r"\D", "", cnpj_inv or "") or None,
                    "moeda_original": moeda,
                    "valor_original": valor,
                    "valor_brl_nominal": valor if moeda == "BRL" else None,
                    "valor_brl_real_base_2024": None,
                    "nivel_agregacao": "linha_original",
                    "fonte_arquivo": path.name,
                    "hash_arquivo": row.get("hash_arquivo"),
                    "fonte_url": row["url_arquivo"],
                    "titulo_publicacao": title,
                    "data_coleta": SNAPSHOT_DATE,
                }
            )
    return records


def parse_flux_file(row: pd.Series) -> list[dict[str, object]]:
    path = ROOT / str(row["local_path"])
    df = read_raw_table(path)
    detail_header = find_detail_header(df)
    year_header = find_year_header(df)
    if detail_header is not None and (year_header is None or detail_header <= year_header):
        return parse_detail_flux(row, df, detail_header)
    if year_header is not None:
        return parse_wide_year_flux(row, df, year_header)
    return []


def build_condecine(df_inventory: pd.DataFrame) -> pd.DataFrame:
    rows = df_inventory[
        (df_inventory["dataset_slug"] == "ancine_condecine_arrecadacao")
        & (df_inventory["extensao"].eq("csv"))
        & (df_inventory["local_path"].notna())
    ]
    records: list[dict[str, object]] = []
    for _, row in rows.iterrows():
        records.extend(parse_condecine_file(row))
    return pd.DataFrame(records)


SLUGS_FLUX = [
    "ancine_fomento_fluxos_financeiros",
    "ancine_condecine_recolhimento",
    "ancine_ibermedia_projetos",
    "ancine_coproducao_internacional_projetos",
    "ancine_apoio_festivais_internacionais",
    "ancine_premio_adicional_renda",
    "ancine_filmes_lancados_captacao",
    "ancine_captacao_por_projeto_investidor",
]

TABLE_NAMES_FLUX = {
    "ancine_fomento_fluxos_financeiros":        "fomento_fluxos_financeiros",
    "ancine_condecine_recolhimento":            "condecine_recolhimento",
    "ancine_ibermedia_projetos":                "ibermedia_projetos",
    "ancine_coproducao_internacional_projetos": "coproducao_internacional_projetos",
    "ancine_apoio_festivais_internacionais":    "apoio_festivais_internacionais",
    "ancine_premio_adicional_renda":            "premio_adicional_renda",
    "ancine_filmes_lancados_captacao":          "filmes_lancados_captacao",
    "ancine_captacao_por_projeto_investidor":   "captacao_por_projeto_investidor",
}


def choose_sources_for_slug(df_inventory: pd.DataFrame, slug: str) -> pd.DataFrame:
    rows = df_inventory[
        (df_inventory["dataset_slug"] == slug)
        & (df_inventory["local_path"].notna())
        & (df_inventory["extensao"].isin(["csv", "xlsx"]))
    ].copy()
    rows["rank_ext"] = rows["extensao"].map({"csv": 1, "xlsx": 2}).fillna(9)
    rows = rows.sort_values(["titulo", "rank_ext"]).drop_duplicates("titulo", keep="first")
    return rows


def build_flux_for_slug(df_inventory: pd.DataFrame, slug: str) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for _, row in choose_sources_for_slug(df_inventory, slug).iterrows():
        try:
            records.extend(parse_flux_file(row))
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] Falha ao parsear {row['titulo']}: {exc}", file=sys.stderr)
    return pd.DataFrame(records)


def build_fomento_fluxos(df_inventory: pd.DataFrame) -> pd.DataFrame:
    return build_flux_for_slug(df_inventory, "ancine_fomento_fluxos_financeiros")


def pdf_text(path: Path) -> str:
    reader = PdfReader(BytesIO(path.read_bytes()))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def embrafilme_metric(title: str) -> tuple[str, str, int]:
    normalized = strip_accents_light(title.lower())
    if "arrecadacao" in normalized:
        return "renda_brl_nominal", "CRUZADO", 1
    if "lugares" in normalized:
        return "lugares_oferecidos", "mil_lugares", 1000
    return "publico", "mil_espectadores", 1000


FAIXA_HABITANTES_LABELS = {
    "ACIMA DE 2 MILHOES": "Acima de 2 milhões",
    "DE 600 MIL A 2 MILHOES": "De 600 mil a 2 milhões",
    "DE 200 MIL A 600 MIL": "De 200 mil a 600 mil",
    "DE 100 MIL A 200 MIL": "De 100 mil a 200 mil",
    "DE 50 MIL A 200 MIL": "De 50 mil a 200 mil",
    "DE 50 MIL A 100 MIL": "De 50 mil a 100 mil",
    "MENOS DE 50 MIL": "Menos de 50 mil",
    "MENOS DE 50 MI": "Menos de 50 mil",
    "TOTAL": "Brasil (total municípios)",
}


def parse_faixa_habitantes_pdf(row: pd.Series) -> list[dict[str, object]]:
    """Parse o PDF Embrafilme 'arrecadacao por faixa de habitantes' (1 ano/pág, 6 col)."""
    path = ROOT / str(row["local_path"])
    reader = PdfReader(BytesIO(path.read_bytes()))
    records: list[dict[str, object]] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        # Captura "ANO DE 1983" ou "PERIODO: JANEIRO - ABRIL / 87"
        ano: int | None = None
        m_ano = re.search(r"ANO\s+DE\s+(19\d{2}|20\d{2})", text, re.IGNORECASE)
        if m_ano:
            ano = int(m_ano.group(1))
        else:
            m_per = re.search(r"PER\W*ODO[:\s]*.*?/\s*(\d{2,4})", text, re.IGNORECASE)
            if m_per:
                yr = int(m_per.group(1))
                ano = 1900 + yr if yr < 100 else yr
        if ano is None:
            continue

        for raw_line in text.splitlines():
            line = strip_accents_light(clean_cell(raw_line)).upper()
            if not line:
                continue
            matched_label = None
            for key in FAIXA_HABITANTES_LABELS:
                if line.startswith(key):
                    matched_label = key
                    break
            if matched_label is None:
                continue
            tail = line[len(matched_label):].strip()
            tokens = tail.split()
            # esperamos pelo menos: cinemas_cadastrados cinemas_arrec arrec %arrec espectadores %esp
            nums = [parse_brl(tok) for tok in tokens]
            nums = [n for n in nums if n is not None]
            if len(nums) < 5:
                continue
            cinemas_cadastrados = int(nums[0]) if nums[0] is not None else None
            cinemas_com_arrec = int(nums[1]) if len(nums) > 1 else None
            arrecadacao = nums[2] if len(nums) > 2 else None
            espectadores = nums[4] if len(nums) > 4 else None

            base = {
                "ano": ano,
                "territorio_tipo": "faixa_habitantes",
                "territorio_nome": FAIXA_HABITANTES_LABELS[matched_label],
                "uf": None,
                "regiao": None,
                "origem_filme": "nacionais_e_estrangeiros",
                "fonte_documento": path.name,
                "confiabilidade": "oficial_compilado",
                "mes": None,
                "mes_nome": None,
            }
            if arrecadacao is not None:
                records.append({**base, "indicador": "renda_brl_nominal", "valor": arrecadacao, "unidade_original": "CRUZADO"})
            if espectadores is not None:
                records.append({**base, "indicador": "publico", "valor": float(espectadores), "unidade_original": "espectadores"})
            if cinemas_cadastrados is not None:
                records.append({**base, "indicador": "cinemas_cadastrados", "valor": float(cinemas_cadastrados), "unidade_original": "cinemas"})
            if cinemas_com_arrec is not None:
                records.append({**base, "indicador": "cinemas_com_arrecadacao", "valor": float(cinemas_com_arrec), "unidade_original": "cinemas"})
    return records


def infer_territory(title: str, label: str) -> tuple[str, str, str | None, str | None, int | None, str | None]:
    title_norm = strip_accents_light(title.lower())
    label_norm = strip_accents_light(label.upper())
    if label_norm in MONTH_LABELS:
        return "brasil", "Brasil", None, None, MONTH_LABELS[label_norm], label.upper()
    if label_norm == "TOTAL":
        return "brasil", "Brasil", None, None, None, None
    if "regiao" in title_norm or label_norm in {"NORTE", "NORDESTE", "SUDESTE", "SUL", "CENTRO-OESTE", "BRASIL"}:
        return "regiao" if label_norm != "BRASIL" else "brasil", label.title(), None, label.title(), None, None
    if " uf" in title_norm or title_norm.endswith("por uf (embrafilme)"):
        uf = label_norm[:2] if re.fullmatch(r"[A-Z]{2}.*", label_norm) else None
        return "uf", label.upper(), uf, None, None, None
    if "capitais" in title_norm and "interior" in title_norm:
        if "CAPITAL" in label_norm or "CAPITAIS" in label_norm:
            return "capitais", label.title(), None, None, None, None
        if "INTERIOR" in label_norm:
            return "interior", label.title(), None, None, None, None
    if "municip" in title_norm:
        return "municipio_ou_faixa", label.title(), None, None, None, None
    return "brasil", "Brasil", None, None, None, None


def parse_page_header(page_text: str, fallback_title: str) -> tuple[str, str, str, int, str | None]:
    """
    Extrai do texto de UMA página:
      - indicador (renda_brl_nominal | publico | lugares_oferecidos)
      - unidade_original (CRUZADO | OTN | espectadores | mil_espectadores | mil_lugares | lugares)
      - origem_filme (nacionais_e_estrangeiros | nacionais | estrangeiros)
      - multiplier
      - escopo territorial inferido do título da página (brasil | capitais | interior | None)

    O título da página tem prioridade para definir o INDICADOR (LUGARES OFERECIDOS,
    ESPECTADORES, ARRECADACAO) porque alguns PDFs têm legenda de unidade incorreta
    (ex.: lugares-uf diz "EM 1.000 ESPECTADORES" mas o conteúdo é lugares).
    A linha de unidade é usada apenas para refinar CRUZADO vs OTN vs base 1000.
    """
    # Junta linhas vizinhas truncadas pelo PDF (ex.: "ESTRANGEIRO\nS")
    raw_lines = [clean_cell(l) for l in page_text.splitlines()]
    raw_lines = [l for l in raw_lines if l]
    glued: list[str] = []
    skip = False
    for i, l in enumerate(raw_lines):
        if skip:
            skip = False
            continue
        if i + 1 < len(raw_lines) and raw_lines[i + 1].strip() in {"S", "R", "O"} and len(l) > 10:
            glued.append(l + raw_lines[i + 1])
            skip = True
        else:
            glued.append(l)
    lines = [strip_accents_light(l).upper() for l in glued]

    # 1) Indicador pelo título da página (prioridade)
    indicator, unit, mult = embrafilme_metric(fallback_title)
    title_line = next((l for l in lines if "FILMES" in l and (
        "ARRECADAC" in l or "ESPECTADOR" in l or "LUGARES OFERECIDOS" in l)), None)
    if title_line:
        if "LUGARES OFERECIDOS" in title_line:
            indicator = "lugares_oferecidos"
        elif "ARRECADAC" in title_line:
            indicator = "renda_brl_nominal"
        elif "ESPECTADOR" in title_line:
            indicator = "publico"

    # 2) Unidade pela linha de hint "EM ..."
    for line in lines:
        if "EM CRUZADOS" in line or line.endswith("EM CRUZADOS"):
            unit, mult = "CRUZADO", 1
            break
        if "EM OTN" in line or "OTN'S" in line or "EM OTNS" in line:
            unit, mult = "OTN", 1
            break
        if "1.000 ESPECTADORES" in line or "1000 ESPECTADORES" in line:
            # Hint de unidade base 1000; só aceita se indicador combinar
            if indicator == "publico":
                unit, mult = "mil_espectadores", 1000
            elif indicator == "lugares_oferecidos":
                unit, mult = "mil_lugares", 1000  # PDF tem hint errado, mas conteúdo é lugares
            break
        if "1.000 LUGARES" in line or "1000 LUGARES" in line:
            unit, mult = "mil_lugares", 1000
            break

    # 3) Origem + escopo do título
    origem = "nacionais_e_estrangeiros"
    escopo_territorial: str | None = None
    if title_line:
        if "NACIONAIS E ESTRANGEIRO" in title_line:
            origem = "nacionais_e_estrangeiros"
        elif "NACIONAIS" in title_line and "ESTRANGEIR" not in title_line:
            origem = "nacionais"
        elif "ESTRANGEIR" in title_line and "NACIONAIS" not in title_line:
            origem = "estrangeiros"
        if "NAS CAPITAIS" in title_line or "PRINCIPAIS CAPITAIS" in title_line:
            escopo_territorial = "capitais"
        elif "NO INTERIOR" in title_line:
            escopo_territorial = "interior"
        elif "NO BRASIL" in title_line:
            escopo_territorial = "brasil"

    return indicator, unit, origem, mult, escopo_territorial


def parse_embrafilme_pdf(row: pd.Series) -> list[dict[str, object]]:
    title = str(row["titulo"])
    path = ROOT / str(row["local_path"])
    reader = PdfReader(BytesIO(path.read_bytes()))
    records: list[dict[str, object]] = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        indicator, unit, origem, multiplier, scope_override = parse_page_header(page_text, title)

        current_years: list[int] = []
        for raw_line in page_text.splitlines():
            line = clean_cell(raw_line)
            if not line:
                continue
            years = [int(v) for v in re.findall(r"\b(19[7-9]\d|20\d{2})\b", line)]
            if len(years) >= 2 and not re.search(r"\d+[,.]\d+", line):
                current_years = years
                continue
            if not current_years:
                continue
            if line.lower().startswith(("fonte", "espectadores", "arrecad", "lugares", "em ")):
                continue

            parts = line.split()
            value_positions = [i for i, part in enumerate(parts) if parse_brl(part) is not None]
            if not value_positions:
                continue
            first_value = value_positions[0]
            label = " ".join(parts[:first_value]).strip()
            if not label:
                continue
            values = [parse_brl(part) for part in parts[first_value:]]
            values = [v for v in values if v is not None]
            if not values:
                continue

            territorio_tipo, territorio_nome, uf, regiao, mes, mes_nome = infer_territory(title, label)
            # Sobrepõe escopo se a página declarou capitais/interior/brasil específico
            # e o territorio resolvido caiu no default "brasil" (catch-all do infer_territory).
            if scope_override and territorio_tipo == "brasil" and mes is None:
                territorio_tipo = scope_override
                territorio_nome = {
                    "brasil": "Brasil",
                    "capitais": "Capitais",
                    "interior": "Interior",
                }[scope_override]

            for ano, value in zip(current_years, values):
                metric_value = value * multiplier
                records.append(
                    {
                        "ano": ano,
                        "territorio_tipo": territorio_tipo,
                        "territorio_nome": territorio_nome,
                        "uf": uf,
                        "regiao": regiao,
                        "origem_filme": origem,
                        "fonte_documento": path.name,
                        "confiabilidade": "oficial_compilado",
                        "indicador": indicator,
                        "valor": metric_value,
                        "unidade_original": unit,
                        "mes": mes,
                        "mes_nome": mes_nome,
                    }
                )
    return records


def build_embrafilme(df_inventory: pd.DataFrame) -> pd.DataFrame:
    rows = df_inventory[
        (df_inventory["dataset_slug"] == "br_embrafilme_historico_exibicao")
        & (df_inventory["extensao"].eq("pdf"))
        & (df_inventory["local_path"].notna())
    ]
    records: list[dict[str, object]] = []
    for _, row in rows.iterrows():
        title_norm = strip_accents_light(str(row["titulo"]).lower())
        is_faixa = "faixa de habitantes" in title_norm
        try:
            if is_faixa:
                records.extend(parse_faixa_habitantes_pdf(row))
            else:
                records.extend(parse_embrafilme_pdf(row))
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] Falha ao parsear Embrafilme {row['titulo']}: {exc}", file=sys.stderr)
    return pd.DataFrame(records)


def write_clean(df: pd.DataFrame, name: str) -> None:
    if df.empty:
        print(f"[WARN] {name}: 0 linhas; parquet nao escrito")
        return
    df.to_parquet(CLEANED / f"{name}.parquet", index=False)
    df.to_csv(CLEANED / f"{name}.csv", index=False, encoding="utf-8")
    print(f"[OK] {name}: {len(df):,} linhas")


SOURCE_TABLES = {
    "br_pib_audiovisual": "pib_audiovisual_fontes",
    "br_rais_emprego_audiovisual": "rais_emprego_audiovisual_fontes",
    "br_comercio_exterior_servicos_audiovisuais": "comercio_exterior_servicos_audiovisuais_fontes",
    "br_comex_bens_audiovisuais": "comex_bens_audiovisuais_fontes",
    "ancine_diversidade_audiovisual": "diversidade_audiovisual_fontes",
}


def build_source_table(inventory: pd.DataFrame, dataset_slug: str) -> pd.DataFrame:
    cols = [
        "dataset_slug",
        "secao",
        "titulo",
        "formato",
        "data_publicacao",
        "ano_referencia",
        "extensao",
        "url_arquivo",
        "pagina_origem",
        "local_path",
        "hash_arquivo",
        "tamanho_bytes",
        "download_status",
        "download_erro",
        "data_coleta",
    ]
    out = inventory[inventory["dataset_slug"].eq(dataset_slug)].copy()
    for col in cols:
        if col not in out.columns:
            out[col] = None
    out = out[cols].drop_duplicates()
    if dataset_slug == "br_pib_audiovisual":
        out["status_extracao"] = "extracao_factual_publicada"
        out["observacao_metodologica"] = (
            "Inventario oficial das fontes. As tabelas factuais "
            "pib_audiovisual_total_ano e pib_audiovisual_atividade_ano sao "
            "geradas por pipelines/transform/clean_pib_audiovisual.py."
        )
    else:
        out["status_extracao"] = "inventariado_pendente_transformacao_factual"
        out["observacao_metodologica"] = (
            "Inventario oficial de fontes complementares. "
            "A tabela factual sera publicada somente apos extracao tabular verificavel."
        )
    return out.reset_index(drop=True)


def main() -> int:
    inventory = build_inventory()
    slugs_to_download = [
        "ancine_condecine_arrecadacao",
        *SLUGS_FLUX,
        "br_pib_audiovisual",
        "br_rais_emprego_audiovisual",
        "br_comercio_exterior_servicos_audiovisuais",
        "br_comex_bens_audiovisuais",
        "br_embrafilme_historico_exibicao",
        "ancine_diversidade_audiovisual",
    ]
    inventory = download_inventory_files(inventory, slugs=slugs_to_download)
    write_inventory(inventory)

    write_clean(build_condecine(inventory), "condecine_arrecadacao")
    for slug, table_name in TABLE_NAMES_FLUX.items():
        write_clean(build_flux_for_slug(inventory, slug), table_name)
    write_clean(build_embrafilme(inventory), "embrafilme_exibicao_territorio_ano")
    for dataset_slug, table_name in SOURCE_TABLES.items():
        write_clean(build_source_table(inventory, dataset_slug), table_name)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
