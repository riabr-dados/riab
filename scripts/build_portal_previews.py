"""Gera resumos pequenos para as prévias editoriais do portal.

Não altera Parquets nem downloads. Execute da raiz do repositório.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pyarrow.compute as pc
import pyarrow.parquet as pq
import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "catalog" / "portal-presentation.yaml"
STORIES_PATH = ROOT / "catalog" / "portal-stories.yaml"
CLEANED = ROOT / "pipelines" / "output" / "cleaned"
OUT = ROOT / "portal" / "public" / "previews"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repair_text(value):
    if not isinstance(value, str):
        return value
    try:
        repaired = value.encode("latin-1").decode("utf-8")
        return repaired if repaired != value else value
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value


def apply_filters(table, filters):
    for rule in filters or []:
        column = table[rule["column"]]
        if rule["operator"] == "neq":
            mask = pc.not_equal(column, rule["value"])
        elif rule["operator"] == "eq":
            mask = pc.equal(column, rule["value"])
        else:
            raise ValueError(f"Operador não suportado: {rule['operator']}")
        table = table.filter(pc.fill_null(mask, False))
    return table


def line_payload(table, preview):
    columns = [preview["x"], *[item["column"] for item in preview["measures"]]]
    missing = set(columns) - set(table.column_names)
    if missing:
        raise ValueError(f"Colunas ausentes: {sorted(missing)}")
    rows = table.select(columns).to_pylist()
    rows.sort(key=lambda row: (row[preview["x"]] is None, row[preview["x"]]))
    return {"rows": rows, "x": preview["x"], "measures": preview["measures"]}


def bar_payload(table, preview):
    category = preview["category"]
    if category not in table.column_names:
        raise ValueError(f"Coluna ausente: {category}")
    counts = {}
    for value in table[category].to_pylist():
        label = repair_text(value) if value not in (None, "") else "Não informado"
        counts[label] = counts.get(label, 0) + 1
    rows = [{"category": key, "value": value} for key, value in counts.items()]
    rows.sort(key=lambda row: (-row["value"], row["category"]))
    return {"rows": rows[: preview.get("limit", 8)], "unit": preview.get("unit", "registros")}


def main():
    document = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"version": document["version"], "previews": {}}
    config_hash = sha256(CONFIG_PATH)

    for table_id, presentation in document["tables"].items():
        preview = presentation.get("preview")
        if not preview:
            continue
        parquet = CLEANED / f"{table_id}.parquet"
        if not parquet.is_file():
            raise FileNotFoundError(parquet)
        table = apply_filters(pq.read_table(parquet), preview.get("filters"))
        if preview["chart"] == "line":
            data = line_payload(table, preview)
        elif preview["chart"] == "bar":
            data = bar_payload(table, preview)
        else:
            raise ValueError(f"Gráfico não suportado: {preview['chart']}")
        payload = {
            "version": document["version"],
            "id": preview["id"],
            "table": table_id,
            "title": preview["title"],
            "question": presentation.get("question"),
            "rowUnit": presentation.get("row_unit"),
            "chart": preview["chart"],
            "note": preview.get("note"),
            "source": {"parquetSha256": sha256(parquet), "presentationSha256": config_hash},
            "data": data,
        }
        filename = f"{preview['id']}.json"
        (OUT / filename).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["previews"][table_id] = {"id": preview["id"], "path": filename}

    (OUT / "index.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    build_stories()
    print(f"{len(manifest['previews'])} prévias e a curadoria Brasil no Mundo geradas em {OUT}")


def build_stories():
    stories_config = yaml.safe_load(STORIES_PATH.read_text(encoding="utf-8"))
    payload = {"version": stories_config["version"], "stories": []}
    for story_id, config in stories_config["stories"].items():
        parquet = CLEANED / f"{config['table']}.parquet"
        table = pq.read_table(parquet)
        if story_id == "cinema-admissoes-europa":
            rows = sorted(
                ({"label": repair_text(row["titulo"]), "value": row["admissoes_1996_2026"]} for row in table.to_pylist()),
                key=lambda row: -row["value"],
            )[:5]
            view = "bar"
        elif story_id == "cnc-registros-brasil":
            counts = {}
            for value in table["dataset_origem"].to_pylist():
                counts[value] = counts.get(value, 0) + 1
            labels = {"cnc_visas_exploitation": "Vistos de exibição", "cnc_films_agrees": "Filmes com agrément"}
            rows = [
                {"label": labels.get(key, repair_text(key)), "value": value}
                for key, value in sorted(counts.items(), key=lambda item: -item[1])
            ]
            view = "bar"
        elif story_id == "bfi-admissoes-brasil":
            rows = [
                {"label": row["ano"], "value": row["valor"]}
                for row in table.to_pylist()
                if row["indicador"] == "admissoes_cinema"
            ]
            rows.sort(key=lambda row: row["label"])
            view = "line"
        else:
            raise ValueError(f"Curadoria desconhecida: {story_id}")
        payload["stories"].append({
            "id": story_id,
            **config,
            "view": view,
            "rows": rows,
            "sourceSha256": sha256(parquet),
        })
    (OUT / "brasil-no-mundo.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
