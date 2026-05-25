"""
Inventario das publicacoes OCA relevantes para complementos RIDAB.

O script le as tabelas publicas do gov.br/ANCINE, preserva os links
originais e baixa snapshots dos arquivos usados pelos datasets derivados.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DATE = "2026-05-23"
USER_AGENT = "Mozilla/5.0 (RIDAB OCA inventory; +https://github.com/riabr)"


SECTIONS = [
    {
        "secao": "dados_financeiros",
        "url": "https://www.gov.br/ancine/pt-br/oca/publicacoes-2/dados-financeiros",
    },
    {
        "secao": "outras_publicacoes",
        "url": "https://www.gov.br/ancine/pt-br/oca/publicacoes-2/outras-publicacoes",
    },
    {
        "secao": "mercado_cinema",
        "url": "https://www.gov.br/ancine/pt-br/oca/publicacoes-2/mercado-audiovisual-brasileiro/cinema",
    },
]

COMEX_BENS_SOURCE = {
    "secao": "mdic_comexstat",
    "titulo": "Base de dados bruta Comex Stat por NCM",
    "formato": "Microdados CSV",
    "data_publicacao": None,
    "ano_referencia": "1997-2026",
    "extensao": "html",
    "url_arquivo": "https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta",
    "pagina_origem": "https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta",
}


DATASET_PATTERNS = [
    # CONDECINE totais (mensal/anual) — pattern simples "condecine" no titulo
    ("ancine_condecine_arrecadacao", r"condecine"),
    # CONDECINE recolhimento por artigo de lei e por empresa contribuinte
    ("ancine_condecine_recolhimento", r"recolhidos?"),
    # Ibermedia (projetos em USD)
    ("ancine_ibermedia_projetos", r"ibermedia"),
    # Coproducao internacional bilateral
    ("ancine_coproducao_internacional_projetos", r"coprodu[cç][aã]o internacional"),
    # Apoio a festivais internacionais
    ("ancine_apoio_festivais_internacionais", r"apoio a participa[cç][aã]o"),
    # Premio Adicional de Renda
    ("ancine_premio_adicional_renda", r"pr[eê]mio adicional de renda"),
    # Filmes lancados com valores captados (serie historica por filme)
    ("ancine_filmes_lancados_captacao", r"filmes? brasileiros? lan[cç]ados?"),
    # Captacao por projeto e por investidor (microdados)
    ("ancine_captacao_por_projeto_investidor", r"captados? por projeto|aportados? por"),
    # Fomento fluxos financeiros (apenas agregados: execucao FSA, liberados, totais por mecanismo/edital)
    (
        "ancine_fomento_fluxos_financeiros",
        r"execu[cç][aã]o.*fundo|liberados?.*mecanismo|totais?.*captados?.*mecanismo|totais?.*editais",
    ),
    ("br_pib_audiovisual", r"valor adicionado pelo setor audiovisual"),
    ("br_rais_emprego_audiovisual", r"emprego no setor audiovisual"),
    ("br_comercio_exterior_servicos_audiovisuais", r"com[eé]rcio exterior de servi[cç]os audiovisuais"),
    ("ancine_diversidade_audiovisual", r"g[eê]nero e ra[cç]a|participa[cç][aã]o feminina"),
    ("br_embrafilme_historico_exibicao", r"embrafilme"),
]


@dataclass
class Link:
    href: str
    text: str


class GovTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[dict[str, object]]] = []
        self._in_cell = False
        self._cell_text: list[str] = []
        self._cell_links: list[Link] = []
        self._row: list[dict[str, object]] = []
        self._link_href: str | None = None
        self._link_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag in {"td", "th"}:
            self._in_cell = True
            self._cell_text = []
            self._cell_links = []
        elif self._in_cell and tag == "a":
            self._link_href = attrs_dict.get("href")
            self._link_text = []

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_text.append(data)
        if self._link_href is not None:
            self._link_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._in_cell and tag == "a":
            if self._link_href:
                self._cell_links.append(Link(self._link_href, clean_text(" ".join(self._link_text))))
            self._link_href = None
            self._link_text = []
        elif tag in {"td", "th"} and self._in_cell:
            self._row.append(
                {
                    "text": clean_text(" ".join(self._cell_text)),
                    "links": [link.__dict__ for link in self._cell_links],
                }
            )
            self._in_cell = False
        elif tag == "tr":
            if self._row:
                self.rows.append(self._row)
            self._row = []


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def slugify_filename(value: str) -> str:
    value = value.lower()
    replacements = {
        "ç": "c",
        "ã": "a",
        "á": "a",
        "à": "a",
        "â": "a",
        "é": "e",
        "ê": "e",
        "í": "i",
        "ó": "o",
        "ô": "o",
        "õ": "o",
        "ú": "u",
        "ü": "u",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:120] or "arquivo"


def classify_dataset(title: str, section: str) -> str | None:
    normalized = title.lower()
    if section == "mercado_cinema" and "embrafilme" in normalized:
        return "br_embrafilme_historico_exibicao"
    for slug, pattern in DATASET_PATTERNS:
        if re.search(pattern, normalized):
            return slug
    return None


def parse_publication_rows(section: dict[str, str]) -> list[dict[str, object]]:
    response = requests.get(
        section["url"],
        headers={"User-Agent": USER_AGENT},
        timeout=60,
    )
    response.raise_for_status()
    parser = GovTableParser()
    parser.feed(response.text)

    records: list[dict[str, object]] = []
    current_meta: dict[str, str] | None = None
    for row in parser.rows:
        cells = [cell["text"] for cell in row]
        if not cells or cells[0].lower() == "titulo":
            continue
        if len(cells) >= 5:
            current_meta = {
                "titulo": str(cells[0]),
                "formato": str(cells[1]),
                "data_publicacao": str(cells[2]) or None,
                "ano_referencia": str(cells[3]) or None,
            }
            link_cell = row[4]
        elif len(cells) == 1 and current_meta:
            link_cell = row[0]
        else:
            continue

        title = current_meta["titulo"]
        dataset_slug = classify_dataset(title, section["secao"])
        if not dataset_slug:
            continue
        links = link_cell.get("links", [])
        if not links:
            continue
        for link in links:
            href = str(link["href"])
            parsed_path = urlparse(href).path.lower()
            ext = Path(parsed_path).suffix.replace(".", "")
            if not ext:
                ext = clean_text(str(link.get("text", ""))).replace(".", "").lower()
            records.append(
                {
                    "dataset_slug": dataset_slug,
                    "secao": section["secao"],
                    "titulo": title,
                    "formato": current_meta["formato"],
                    "data_publicacao": current_meta["data_publicacao"],
                    "ano_referencia": current_meta["ano_referencia"],
                    "extensao": ext,
                    "url_arquivo": href,
                    "pagina_origem": section["url"],
                }
            )
    return records


def build_inventory() -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for section in SECTIONS:
        records.extend(parse_publication_rows(section))
    records.append({"dataset_slug": "br_comex_bens_audiovisuais", **COMEX_BENS_SOURCE})

    df = pd.DataFrame(records)
    if df.empty:
        return df

    df["data_coleta"] = SNAPSHOT_DATE
    df["prioridade_extracao"] = df["extensao"].map({"csv": 1, "xlsx": 2, "pdf": 3}).fillna(9).astype(int)
    df = df.sort_values(["dataset_slug", "titulo", "prioridade_extracao", "url_arquivo"]).reset_index(drop=True)
    return df


def safe_download_name(row: pd.Series) -> str:
    parsed = urlparse(str(row["url_arquivo"]))
    name = Path(parsed.path).name
    if not name or "." not in name:
        name = f"{slugify_filename(str(row['titulo']))}.{row['extensao']}"
    return name


def download_inventory_files(df: pd.DataFrame, slugs: Iterable[str] | None = None) -> pd.DataFrame:
    if df.empty:
        return df

    wanted = set(slugs or df["dataset_slug"].unique())
    out_rows: list[dict[str, object]] = []
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1.2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "HEAD"),
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))

    for _, row in df.iterrows():
        record = row.to_dict()
        if record["dataset_slug"] not in wanted:
            out_rows.append(record)
            continue
        raw_dir = ROOT / "datasets" / str(record["dataset_slug"]).replace("_", "-") / "snapshots" / SNAPSHOT_DATE
        raw_dir.mkdir(parents=True, exist_ok=True)
        if record.get("extensao") == "html":
            source_path = raw_dir / "source.txt"
            if not source_path.exists():
                source_path.write_text(
                    f"{record.get('titulo')}\n{record.get('url_arquivo')}\n",
                    encoding="utf-8",
                )
            record["local_path"] = str(source_path.relative_to(ROOT)).replace("\\", "/")
            record["download_status"] = "referencia_url"
            out_rows.append(record)
            continue

        local_path = raw_dir / safe_download_name(row)
        try:
            if not local_path.exists():
                response = session.get(str(record["url_arquivo"]), timeout=120)
                response.raise_for_status()
                local_path.write_bytes(response.content)
            content = local_path.read_bytes()
            record["local_path"] = str(local_path.relative_to(ROOT)).replace("\\", "/")
            record["hash_arquivo"] = hashlib.sha256(content).hexdigest()
            record["tamanho_bytes"] = len(content)
            record["download_status"] = "ok"
        except requests.RequestException as exc:
            record["download_status"] = "erro"
            record["download_erro"] = str(exc)
        out_rows.append(record)

    return pd.DataFrame(out_rows)


def write_inventory(df: pd.DataFrame) -> None:
    cleaned_dir = ROOT / "pipelines" / "output" / "cleaned"
    cleaned_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cleaned_dir / "oca_publicacoes_complementares.parquet", index=False)
    df.to_csv(cleaned_dir / "oca_publicacoes_complementares.csv", index=False, encoding="utf-8")

    grouped = {
        slug: group.to_dict(orient="records")
        for slug, group in df.groupby("dataset_slug", dropna=False)
    }
    manifest = {
        "snapshot": SNAPSHOT_DATE,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": grouped,
    }
    out = ROOT / "datasets" / "oca-publicacoes-complementares" / "snapshots" / SNAPSHOT_DATE
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    df.to_csv(out / "oca_links.csv", index=False, encoding="utf-8")


def main() -> int:
    download = "--download" in sys.argv
    df = build_inventory()
    if download:
        df = download_inventory_files(df)
    write_inventory(df)
    print(f"Inventario OCA: {len(df)} arquivos/publicacoes")
    print(df.groupby("dataset_slug").size().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
