"""Registra no repositório o snapshot oficial auditado da bilheteria diária."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-08"
CONFIG = {
    "distribuidoras": {
        "slug": "ancine-bilheteria-diaria-distribuidoras",
        "zip": "bilheteria-diaria-obras-por-distribuidoras-csv.zip",
        "url": "https://dados.ancine.gov.br/dados-abertos/bilheteria-diaria-obras-por-distribuidoras-csv.zip",
        "rows": 21_274_038,
    },
    "exibidoras": {
        "slug": "ancine-bilheteria-diaria-exibidoras",
        "zip": "bilheteria-diaria-obras-por-exibidoras-csv.zip",
        "url": "https://dados.ancine.gov.br/dados-abertos/bilheteria-diaria-obras-por-exibidoras-csv.zip",
        "rows": 37_672_799,
    },
}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> None:
    for config in CONFIG.values():
        package = ROOT / "outputs/auditoria-pda-20260908/official/packages" / config["zip"]
        with zipfile.ZipFile(package) as archive:
            files = [i for i in archive.infolist() if i.filename.lower().endswith(".csv")]
            expanded = sum(i.file_size for i in files)
        sha256 = digest(package)
        dataset = ROOT / "datasets" / config["slug"]
        root_package = dataset / "datapackage.json"
        document = json.loads(root_package.read_text(encoding="utf-8"))
        document["version"] = "2026.09.08"
        document["status"]["last_checked"] = DATE
        document["status"]["notes"] = (
            f"Snapshot oficial verificado: {len(files)} CSVs, {expanded} bytes expandidos e "
            f"{config['rows']} linhas tratadas em partições anuais."
        )
        document["collection"] = {
            "method": "automated",
            "script": "pipelines/fetch_bilheteria_diaria.py",
            "frequency": "mensal",
        }
        document["resources"] = [{
            "name": config["zip"].removesuffix(".zip"),
            "path": config["url"],
            "format": "zip",
            "mediatype": "application/zip",
            "bytes": package.stat().st_size,
            "expanded_bytes": expanded,
            "files": len(files),
            "sha256": sha256,
            "note": "Pacote oficial; o ZIP não é versionado no Git devido ao tamanho.",
        }]
        snapshot_record = {
            "date": DATE,
            "path": f"snapshots/{DATE}/",
            "source_url": config["url"],
            "sha256": sha256,
            "notes": f"{len(files)} CSVs oficiais, {config['rows']} linhas publicadas em partições anuais.",
        }
        document["snapshots"] = [s for s in document.get("snapshots", []) if s.get("date") != DATE]
        document["snapshots"].append(snapshot_record)
        root_package.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        snapshot = dataset / "snapshots" / DATE
        snapshot.mkdir(parents=True, exist_ok=True)
        (snapshot / "datapackage.json").write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        provenance = {
            "collected_at": DATE,
            "source_url": config["url"],
            "archive": config["zip"],
            "sha256": sha256,
            "archive_bytes": package.stat().st_size,
            "expanded_bytes": expanded,
            "csv_files": len(files),
            "rows": config["rows"],
        }
        (snapshot / "provenance.json").write_text(
            json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (snapshot / "source.txt").write_text(config["url"] + "\n", encoding="utf-8")
        print(config["slug"], len(files), config["rows"], sha256)


if __name__ == "__main__":
    main()
