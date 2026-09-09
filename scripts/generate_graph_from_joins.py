"""Reconstrói o grafo do portal usando apenas recursos atualmente catalogados."""
from pathlib import Path
import json
import yaml

ROOT = Path(__file__).resolve().parents[1]
JOINS = ROOT / "catalog/joins.yaml"
CATALOG = ROOT / "catalog/datasets.yaml"
GRAPH = ROOT / "portal/src/data/grafo.json"


def main():
    joins = yaml.safe_load(JOINS.read_text(encoding="utf-8"))
    catalog = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))["datasets"]
    descriptions = {dataset["slug"]: str(dataset.get("description", "")).strip() for dataset in catalog}
    old = json.loads(GRAPH.read_text(encoding="utf-8"))
    countries = old.get("countries", {})
    key_colors = old.get("key_colors", {})
    nodes = []
    for resource in joins["tables"]:
        key_cols = {}
        for exposed in resource["exposes"]:
            key_cols.setdefault(exposed["key"], []).append(exposed["col"])
        country = resource["_country"]
        country_meta = countries.get(country, country)
        nodes.append({"data": {
            "id": resource["table"], "label": resource["_title"], "table": resource["table"],
            "slug": resource["_dataset"], "country": country,
            "country_label": (country_meta.get("label", country) if isinstance(country_meta, dict) else country_meta),
            "source_id": resource["_source"],
            "source_label": "", "keys": sorted(key_cols), "columns_n": resource["_columns_count"],
            "description": descriptions.get(resource["_dataset"], ""), "key_cols": key_cols,
        }})
    edges = []
    for bridge in joins["bridges"]:
        source, target = bridge["tables"]
        edges.append({"data": {
            "id": f"{source}__{target}", "source": source, "target": target,
            "keys": bridge["via_keys"], "top_key": bridge["top_key"], "weight": bridge["weight"],
            "color": key_colors.get(bridge["top_key"], "#64748b"),
        }})
    result = {"nodes": nodes, "edges": edges, "key_colors": key_colors,
              "key_weights": old.get("key_weights", {}), "countries": countries}
    GRAPH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Grafo: {len(nodes)} recursos atuais, {len(edges)} conexões válidas")


if __name__ == "__main__":
    main()
