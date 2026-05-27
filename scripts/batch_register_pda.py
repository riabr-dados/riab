"""
Registra em lote os datasets PDA coletados manualmente.
Mapeia cada arquivo/pasta de Downloads para o slug correto,
copia para datasets/{slug}/snapshots/2026-05-27/, gera
datapackage.json, source.txt, README e atualiza catalog/datasets.yaml.

Uso:
    python scripts/batch_register_pda.py [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = ROOT / "datasets"
CATALOG_PATH = ROOT / "catalog" / "datasets.yaml"
DOWNLOADS = Path.home() / "Downloads"
SNAP_DATE = "2026-05-27"

MEDIATYPES = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "zip": "application/zip",
}

# Mapeamento: slug -> caminho em Downloads (arquivo ou pasta extraída do ZIP)
MAPPING = {
    "ancine-atividades-economicas-agentes": DOWNLOADS / "atividades-economicas-agentes-regulares.csv",
    "ancine-produtoras-independentes":       DOWNLOADS / "produtoras-independentes.csv",
    "ancine-canais-programadoras":           DOWNLOADS / "canais-de-programacao-de-programadoras-ativos-credenciados.csv",
    "ancine-canais-distribuicao-obrigatoria":DOWNLOADS / "canais-de-programacao-de-distribuicao-obrigatoria-ativos-credenciados.csv",
    "ancine-salas-exibicao-complexos":       DOWNLOADS / "salas-de-exibicao-e-complexos.csv",
    "ancine-obras-fomento-indireto":         DOWNLOADS / "obras-nao-pub-brasileiras-fomento-indireto.csv",
    "ancine-pais-origem-obras-br":           DOWNLOADS / "paises-de-origem-das-obras-nao-publicitarias-brasileiras.csv",
    "ancine-obras-estrangeiras-roe":         DOWNLOADS / "obras-nao-pub-estrangeiras-csv",      # pasta extraída do ZIP
    "ancine-diretores-obras-estrangeiras":   DOWNLOADS / "diretores-de-obras-nao-publicitarias-estrangeiras.csv",
    "ancine-produtores-obras-estrangeiras":  DOWNLOADS / "produtores-de-obras-nao-publicitarias-estrangeiras.csv",
    "ancine-pais-origem-obras-estrangeiras": DOWNLOADS / "paises-de-origem-das-obras-nao-publicitarias-estrangeiras.csv",
    "ancine-grupos-economicos":              DOWNLOADS / "relacao-grupos-economicos.csv",
    "ancine-crt-obras-nao-publicitarias":   DOWNLOADS / "crt-obras-nao-publicitarias-csv",     # pasta extraída do ZIP
    "ancine-crt-obras-publicitarias":       DOWNLOADS / "crt-obras-publicitarias-csv",          # pasta extraída do ZIP
    "ancine-fsa-investimento-contratados":   DOWNLOADS / "projetos-fsa (1).csv",
    "ancine-prestacao-contas-processos":     DOWNLOADS / "processos-em-prestacao-de-contas.csv",
    "ancine-filmagem-estrangeira":           DOWNLOADS / "filmagem-estrangeira.csv",
    "ancine-salas-exibicao-evolucao":        DOWNLOADS / "salas-de-exibicao-evolucao-anual.csv",
    "ancine-lancamentos-distribuidoras":     DOWNLOADS / "lancamentos-comerciais-por-distribuidoras.csv",
    "ancine-agentes-economicos-estrangeiros":DOWNLOADS / "agentes-economicos-estrangeiros-regulares.csv",
    "ancine-complexos-cinematograficos-evolucao": DOWNLOADS / "complexos-cinematograficos-evolucao-anual.csv",
}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def source_files(src: Path) -> list[Path]:
    if src.is_dir():
        return sorted(p for p in src.rglob("*") if p.is_file())
    return [src]


def register_one(slug: str, src: Path, catalog_entry: dict, dry_run: bool) -> dict | None:
    files = source_files(src)
    if not files:
        print(f"  [SKIP] {slug} — nenhum arquivo encontrado em {src}")
        return None

    snap_dir = DATASETS_DIR / slug / "snapshots" / SNAP_DATE
    if not dry_run:
        snap_dir.mkdir(parents=True, exist_ok=True)

    resources = []
    total_bytes = 0
    for f in files:
        dest = snap_dir / f.name
        if not dry_run:
            shutil.copy2(f, dest)
        suffix = f.suffix.lower().lstrip(".")
        mediatype = MEDIATYPES.get(suffix, "application/octet-stream")
        size = f.stat().st_size
        total_bytes += size
        resources.append({
            "name": f.stem,
            "path": f"snapshots/{SNAP_DATE}/{f.name}",
            "format": suffix,
            "mediatype": mediatype,
            "encoding": "utf-8" if suffix == "csv" else "binary",
            "bytes": size,
            "hash": sha256_of(f),
        })

    title = str(catalog_entry.get("title", slug))
    description = str(catalog_entry.get("description", ""))
    source_url = catalog_entry.get("raw", {}).get("url_origem", "https://dados.gov.br")

    pkg = {
        "$schema": "https://specs.frictionlessdata.io/schemas/data-package.json",
        "name": slug,
        "title": title,
        "description": description,
        "version": SNAP_DATE.replace("-", "."),
        "created": f"{SNAP_DATE}T00:00:00Z",
        "homepage": f"https://github.com/riabr-dados/riab/tree/main/datasets/{slug}",
        "licenses": [{"name": "CC-BY-4.0", "title": "Creative Commons Attribution 4.0 International", "path": "https://creativecommons.org/licenses/by/4.0/"}],
        "sources": [{"title": "ANCINE — dados.gov.br", "path": source_url}],
        "contributors": [{"title": "dados-audiovisual-br", "role": "publisher", "path": "https://github.com/riabr-dados/riab"}],
        "status": {"value": "ativo", "options": ["ativo", "intermitente", "alterado", "offline", "descontinuado"], "last_checked": SNAP_DATE, "notes": ""},
        "collection": {"method": "manual", "script": None, "frequency": "ad-hoc"},
        "resources": resources,
        "snapshots": [{"date": SNAP_DATE, "path": f"snapshots/{SNAP_DATE}/", "source_url": source_url, "notes": f"Snapshot inicial coletado em {SNAP_DATE} via dados.gov.br."}],
    }
    pkg_json = json.dumps(pkg, indent=2, ensure_ascii=False)

    source_txt = (
        f"Dataset: {title}\nFonte oficial: ANCINE -- dados.gov.br\nURL: {source_url}\n"
        f"Data do snapshot: {SNAP_DATE}\nStatus na data: ativo\nColeta: manual, download via dados.gov.br\nArquivos:\n"
        + "\n".join(f"  - {r['name']} ({r['bytes']} bytes, {r['hash']})" for r in resources) + "\n"
    )

    file_list = "\n".join(f"- `{r['name']}.{r['format']}` ({r['bytes']:,} bytes)" for r in resources)
    readme = f"""# {title}

{description}

## Fonte oficial

- **Orgao**: ANCINE -- dados.gov.br
- **URL viva**: <{source_url}>
- **Status na ultima verificacao**: `ativo` ({SNAP_DATE})

## Snapshots disponiveis

- [`{SNAP_DATE}`](snapshots/{SNAP_DATE}/) -- snapshot inicial

## Arquivos no snapshot mais recente

{file_list}

Metadados completos (hash SHA256, tamanho) em [`datapackage.json`](datapackage.json).

## Licenca

Dados sob [CC-BY-4.0](../../LICENSE-data). Atribuicao obrigatoria a fonte original.
"""

    if not dry_run:
        (snap_dir / "datapackage.json").write_text(pkg_json, encoding="utf-8")
        (DATASETS_DIR / slug / "datapackage.json").write_text(pkg_json, encoding="utf-8")
        (snap_dir / "source.txt").write_text(source_txt, encoding="utf-8")
        (DATASETS_DIR / slug / "README.md").write_text(readme, encoding="utf-8")

    n = len(files)
    print(f"  [OK] {slug} — {n} arquivo(s), {total_bytes/1024:.0f} KB")
    return {"slug": slug, "total_bytes": total_bytes, "files": n, "format": resources[0]["format"]}


def update_catalog(results: list[dict], dry_run: bool) -> None:
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096
    doc = yaml.load(CATALOG_PATH.open(encoding="utf-8"))

    result_map = {r["slug"]: r for r in results}
    updated = 0
    for ds in doc["datasets"]:
        slug = ds["slug"]
        if slug not in result_map:
            continue
        r = result_map[slug]
        ds["status"] = "ativo"
        if "raw" not in ds:
            ds["raw"] = {}
        ds["raw"]["format"] = r["format"]
        ds["raw"]["files"] = r["files"]
        ds["raw"]["size_bytes"] = r["total_bytes"]
        updated += 1

    if not dry_run:
        yaml.dump(doc, CATALOG_PATH.open("w", encoding="utf-8"))
    print(f"\ncatalog/datasets.yaml: {updated} datasets atualizados -> ativo")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Nao copia arquivos nem escreve nada")
    args = parser.parse_args()

    yaml = YAML()
    doc = yaml.load(CATALOG_PATH.open(encoding="utf-8"))
    catalog_map = {ds["slug"]: ds for ds in doc["datasets"]}

    if args.dry_run:
        print("[DRY RUN] Nenhum arquivo sera copiado.\n")

    results = []
    missing = []
    for slug, src in MAPPING.items():
        if not src.exists():
            missing.append(f"  {slug} <- {src.name}")
            continue
        entry = catalog_map.get(slug, {})
        r = register_one(slug, src, entry, args.dry_run)
        if r:
            results.append(r)

    if missing:
        print("\n[PENDENTE] Arquivos ainda nao encontrados:")
        for m in missing:
            print(m)

    if results and not args.dry_run:
        update_catalog(results, args.dry_run)

    print(f"\nTotal registrado: {len(results)}/{len(MAPPING)} datasets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
