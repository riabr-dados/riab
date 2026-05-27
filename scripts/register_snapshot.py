"""
Registra um arquivo baixado manualmente como snapshot de um dataset pendente.

Uso:
    python scripts/register_snapshot.py <slug> <arquivo> [--date YYYY-MM-DD] [--url URL] [--notes TEXTO]

Exemplo:
    python scripts/register_snapshot.py ancine-salas-exibicao-complexos Downloads/salas-exibicao.csv

O script:
  1. Cria datasets/<slug>/snapshots/<date>/<arquivo>
  2. Cria source.txt e datapackage.json no snapshot
  3. Cria/atualiza datasets/<slug>/datapackage.json
  4. Atualiza catalog/datasets.yaml: status, files, size_bytes, format
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import date
from pathlib import Path

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = ROOT / "datasets"
CATALOG_PATH = ROOT / "catalog" / "datasets.yaml"

MEDIATYPES = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xls": "application/vnd.ms-excel",
    "zip": "application/zip",
    "json": "application/json",
    "pdf": "application/pdf",
    "ods": "application/vnd.oasis.opendocument.spreadsheet",
}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def guess_format(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower().lstrip(".")
    return suffix, MEDIATYPES.get(suffix, "application/octet-stream")


def load_catalog_entry(slug: str) -> dict | None:
    yaml = YAML()
    doc = yaml.load(CATALOG_PATH.open(encoding="utf-8"))
    for ds in doc["datasets"]:
        if ds["slug"] == slug:
            return ds, doc
    return None, doc


def update_catalog(slug: str, snap_date: str, file_path: Path, new_status: str = "ativo") -> None:
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096

    doc = yaml.load(CATALOG_PATH.open(encoding="utf-8"))
    updated = False
    for ds in doc["datasets"]:
        if ds["slug"] != slug:
            continue

        fmt, _ = guess_format(file_path)
        size = file_path.stat().st_size

        ds["status"] = new_status
        if "raw" not in ds:
            ds["raw"] = {}
        ds["raw"]["format"] = fmt
        ds["raw"]["files"] = 1
        ds["raw"]["size_bytes"] = size

        updated = True
        break

    if not updated:
        print(f"[ERRO] slug '{slug}' não encontrado no catalog.", file=sys.stderr)
        sys.exit(1)

    yaml.dump(doc, CATALOG_PATH.open("w", encoding="utf-8"))
    print(f"  catalog/datasets.yaml atualizado: {slug} -> {new_status}")


def build_datapackage(
    slug: str,
    title: str,
    description: str,
    source_title: str,
    source_url: str,
    snap_date: str,
    resources: list[dict],
    notes: str,
) -> dict:
    return {
        "$schema": "https://specs.frictionlessdata.io/schemas/data-package.json",
        "name": slug,
        "title": title,
        "description": description,
        "version": snap_date.replace("-", "."),
        "created": f"{snap_date}T00:00:00Z",
        "homepage": f"https://github.com/riabr-dados/riab/tree/main/datasets/{slug}",
        "licenses": [
            {
                "name": "CC-BY-4.0",
                "title": "Creative Commons Attribution 4.0 International",
                "path": "https://creativecommons.org/licenses/by/4.0/",
            }
        ],
        "sources": [{"title": source_title, "path": source_url}],
        "contributors": [
            {
                "title": "dados-audiovisual-br",
                "role": "publisher",
                "path": "https://github.com/riabr-dados/riab",
            }
        ],
        "status": {
            "value": "ativo",
            "options": ["ativo", "intermitente", "alterado", "offline", "descontinuado"],
            "last_checked": snap_date,
            "notes": notes,
        },
        "collection": {"method": "manual", "script": None, "frequency": "ad-hoc"},
        "resources": resources,
        "snapshots": [
            {
                "date": snap_date,
                "path": f"snapshots/{snap_date}/",
                "source_url": source_url,
                "notes": f"Snapshot inicial coletado em {snap_date} via dados.gov.br.",
            }
        ],
    }


def write_readme(dataset_dir: Path, title: str, description: str, source_title: str, source_url: str, snap_date: str, resources: list[dict], notes: str) -> None:
    file_list = "\n".join(f"- `{r['name']}.{r['format']}` ({r['bytes']:,} bytes)" for r in resources)
    md = f"""# {title}

{description}

## Fonte oficial

- **Órgão**: {source_title}
- **URL viva**: <{source_url}>
- **Status na última verificação**: `ativo` ({snap_date})

{notes}

## Snapshots disponíveis

- [`{snap_date}`](snapshots/{snap_date}/) — snapshot inicial

## Arquivos no snapshot mais recente

{file_list}

Metadados completos (hash SHA256, tamanho) em [`datapackage.json`](datapackage.json).

## Licença

Dados sob [CC-BY-4.0](../../LICENSE-data). Atribuição obrigatória à fonte original.
"""
    (dataset_dir / "README.md").write_text(md, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Registra snapshot de dataset PDA coletado manualmente.")
    parser.add_argument("slug", help="Slug do dataset (ex: ancine-salas-exibicao-complexos)")
    parser.add_argument("arquivo", help="Caminho para o arquivo baixado")
    parser.add_argument("--date", default=str(date.today()), help="Data do snapshot (YYYY-MM-DD)")
    parser.add_argument("--url", help="URL de origem (sobrescreve url_origem do catalog)")
    parser.add_argument("--notes", default="Coletado via dados.gov.br — download manual.", help="Notas do snapshot")
    args = parser.parse_args()

    snap_date = args.date
    src_file = Path(args.arquivo).expanduser().resolve()

    if not src_file.exists():
        print(f"[ERRO] Arquivo não encontrado: {src_file}", file=sys.stderr)
        return 1

    # Carregar entrada do catalog
    yaml = YAML()
    doc = yaml.load(CATALOG_PATH.open(encoding="utf-8"))
    entry = next((ds for ds in doc["datasets"] if ds["slug"] == args.slug), None)
    if entry is None:
        print(f"[ERRO] Slug '{args.slug}' não encontrado no catalog.", file=sys.stderr)
        return 1

    title = str(entry.get("title", args.slug))
    description = str(entry.get("description", ""))
    source_url = args.url or entry.get("raw", {}).get("url_origem") or "https://dados.gov.br"
    source_title = "ANCINE — dados.gov.br"

    # Criar diretório do snapshot
    dataset_dir = DATASETS_DIR / args.slug
    snap_dir = dataset_dir / "snapshots" / snap_date
    snap_dir.mkdir(parents=True, exist_ok=True)

    # Copiar arquivo
    dest_file = snap_dir / src_file.name
    shutil.copy2(src_file, dest_file)
    print(f"  Copiado: {src_file.name} -> datasets/{args.slug}/snapshots/{snap_date}/")

    # Computar hash e formato
    fmt, mediatype = guess_format(dest_file)
    file_hash = sha256_of(dest_file)
    file_bytes = dest_file.stat().st_size

    resources = [
        {
            "name": dest_file.stem,
            "path": f"snapshots/{snap_date}/{dest_file.name}",
            "format": fmt,
            "mediatype": mediatype,
            "encoding": "utf-8" if fmt in {"csv", "json"} else "binary",
            "bytes": file_bytes,
            "hash": file_hash,
        }
    ]

    # source.txt
    source_txt = (
        f"Dataset: {title}\n"
        f"Fonte oficial: {source_title}\n"
        f"URL: {source_url}\n"
        f"Data do snapshot: {snap_date}\n"
        f"Status na data: ativo\n"
        f"Coleta: manual, download via dados.gov.br\n"
        f"Arquivos:\n"
        + "\n".join(f"  - {r['name']} ({r['bytes']} bytes, {r['hash']})" for r in resources)
        + "\n"
    )
    (snap_dir / "source.txt").write_text(source_txt, encoding="utf-8")

    # datapackage.json do snapshot e do dataset
    pkg = build_datapackage(
        slug=args.slug,
        title=title,
        description=description,
        source_title=source_title,
        source_url=source_url,
        snap_date=snap_date,
        resources=resources,
        notes=args.notes,
    )
    pkg_json = json.dumps(pkg, indent=2, ensure_ascii=False)
    (snap_dir / "datapackage.json").write_text(pkg_json, encoding="utf-8")
    (dataset_dir / "datapackage.json").write_text(pkg_json, encoding="utf-8")

    # README
    write_readme(dataset_dir, title, description, source_title, source_url, snap_date, resources, args.notes)

    # Atualizar catalog/datasets.yaml
    update_catalog(args.slug, snap_date, dest_file, new_status="ativo")

    print(f"\n[OK] {args.slug} registrado com sucesso.")
    print(f"     datasets/{args.slug}/snapshots/{snap_date}/{dest_file.name}")
    print(f"     {file_bytes:,} bytes | {file_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
