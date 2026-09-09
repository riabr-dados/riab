"""Promove originais já baixados pela auditoria para snapshots rastreáveis."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path
import shutil

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "outputs/auditoria-pda-20260908/official"
TASKS = ROOT / "docs/correcoes-auditoria/tarefas.csv"
SNAPSHOT_DATE = "2026-09-08"


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return sha256(stream.read()).hexdigest()


def media_type(path: Path) -> str:
    return {
        ".csv": "text/csv",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".ods": "application/vnd.oasis.opendocument.spreadsheet",
        ".pdf": "application/pdf",
    }.get(path.suffix.lower(), "application/octet-stream")


def update_package(dataset: Path, source_files: list[Path]) -> None:
    package_path = dataset / "datapackage.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    package["version"] = SNAPSHOT_DATE.replace("-", ".")
    package["created"] = f"{SNAPSHOT_DATE}T00:00:00Z"
    package["resources"] = [{
        "name": path.stem,
        "path": f"snapshots/{SNAPSHOT_DATE}/{path.name}",
        "format": path.suffix.lower().lstrip("."),
        "mediatype": media_type(path),
        "encoding": "utf-8" if path.suffix.lower() == ".csv" else "binary",
        "bytes": path.stat().st_size,
        "hash": f"sha256:{digest(path)}",
    } for path in source_files]
    source_url = package.get("sources", [{}])[0].get("path")
    package["snapshots"] = [
        item for item in package.get("snapshots", []) if item.get("date") != SNAPSHOT_DATE
    ]
    package["snapshots"].append({
        "date": SNAPSHOT_DATE,
        "path": f"snapshots/{SNAPSHOT_DATE}/",
        "source_url": source_url,
        "notes": "Original baixado e conferido na auditoria integral de 2026-09-08.",
    })
    text = json.dumps(package, ensure_ascii=False, indent=2) + "\n"
    package_path.write_text(text, encoding="utf-8")
    (dataset / "snapshots" / SNAPSHOT_DATE / "datapackage.json").write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slugs", nargs="*")
    args = parser.parse_args()
    tasks = pd.read_csv(TASKS, encoding="utf-8")
    slugs = args.slugs or tasks.loc[tasks["resultado_auditoria"].eq("Atualizar"), "dataset"].tolist()
    promoted = []
    for slug in slugs:
        source = AUDIT / slug
        files = sorted(path for path in source.iterdir() if path.is_file())
        if not files:
            raise FileNotFoundError(f"{slug}: nenhum original da auditoria")
        dataset = ROOT / "datasets" / slug
        snapshot = dataset / "snapshots" / SNAPSHOT_DATE
        snapshot.mkdir(parents=True, exist_ok=True)
        copied = []
        for path in files:
            target = snapshot / path.name
            shutil.copy2(path, target)
            if digest(target) != digest(path):
                raise ValueError(f"Cópia divergente: {target}")
            copied.append(target)
        update_package(dataset, copied)
        package = json.loads((dataset / "datapackage.json").read_text(encoding="utf-8"))
        source_url = package.get("sources", [{}])[0].get("path", "")
        provenance = {
            "dataset": slug,
            "snapshot": SNAPSHOT_DATE,
            "source_url": source_url,
            "audit_evidence": str(source.relative_to(ROOT)).replace("\\", "/"),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "files": [{"name": path.name, "bytes": path.stat().st_size, "sha256": digest(path)}
                      for path in copied],
        }
        (snapshot / "provenance.json").write_text(
            json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (snapshot / "source.txt").write_text(source_url + "\n", encoding="utf-8")
        promoted.append(slug)
        print(f"{slug}: {len(copied)} arquivo(s) promovido(s)")
    print(f"Snapshots promovidos: {len(promoted)}")


if __name__ == "__main__":
    main()
