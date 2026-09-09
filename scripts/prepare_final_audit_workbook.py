"""Prepara JSON compacto usado para gerar o Excel final da auditoria."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs/.drafts/01a0827c-c716-7520-b995-a3be53ec857e/audit_data.json"


def main() -> None:
    with (ROOT / "docs/correcoes-auditoria/tarefas.csv").open(encoding="utf-8-sig", newline="") as stream:
        tasks = list(csv.DictReader(stream))
    catalog = yaml.safe_load((ROOT / "catalog/datasets.yaml").read_text(encoding="utf-8"))["datasets"]
    downloads = json.loads((ROOT / "catalog/downloads.json").read_text(encoding="utf-8"))["resources"]
    sources = yaml.safe_load((ROOT / "catalog/sources.yaml").read_text(encoding="utf-8"))["sources"]
    task_by_slug = {row["dataset"]: row for row in tasks}
    resources = []
    for dataset in catalog:
        if dataset.get("hidden"):
            continue
        task = task_by_slug.get(dataset["slug"], {})
        for entry in dataset.get("cleaned", {}).get("tables", []):
            table = entry if isinstance(entry, str) else entry["name"]
            descriptor = downloads[table]
            parquet = ROOT / "pipelines/output/cleaned" / f"{table}.parquet"
            formats = sorted({
                "CSV.GZ" if item.get("compression") == "gzip" else item["format"].upper()
                for item in descriptor["files"]
            })
            resources.append({
                "dataset": dataset["slug"],
                "titulo": dataset["title"],
                "fonte": dataset.get("source_id", ""),
                "recurso": table,
                "linhas": descriptor["rows"],
                "colunas": len(pq.read_schema(parquet).names),
                "formatos": ", ".join(formats),
                "cobertura": str(dataset.get("coverage", "")),
                "origem": dataset.get("raw", {}).get("url_origem", ""),
                "execucao": task.get("execucao", "Concluído"),
            })
    source_rows = []
    for source in sources:
        datasets = [d for d in catalog if not d.get("hidden") and d.get("source_id") == source["id"]]
        source_rows.append({
            "id": source["id"], "nome": source["name"], "pais": source.get("country", ""),
            "datasets": len(datasets), "portal": source.get("data_portal", source.get("url", "")),
            "licenca": source.get("license", ""), "observacao": source.get("notes", ""),
        })
    status = Counter(row["execucao"] for row in tasks)
    payload = {
        "generated_at": "2026-09-09",
        "summary": {
            "audited": len(tasks), "catalog_datasets": len(catalog),
            "published_datasets": sum(not d.get("hidden") for d in catalog),
            "resources": len(resources), "download_files": sum(len(x["files"]) for x in downloads.values()),
            "status": dict(status),
        },
        "tasks": tasks, "resources": resources, "sources": source_rows,
        "limitations": [row for row in tasks if row["execucao"] != "Concluído"],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
