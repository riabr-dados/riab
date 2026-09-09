"""Atualiza apenas as listas de recursos BFI no catálogo principal."""
from collections import defaultdict
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog/datasets.yaml"
MANIFEST = ROOT / "catalog/bfi_resources.yaml"


def main():
    resources = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["resources"]
    grouped = defaultdict(list)
    for resource in resources:
        grouped[resource["dataset"]].append(resource["table"])
    source = CATALOG.read_text(encoding="utf-8")
    for slug, tables in grouped.items():
        pattern = re.compile(
            rf"(^  - slug: {re.escape(slug)}\n(?:(?!^  - slug: ).)*?^    cleaned:\n^      tables:)\s*\[[^\n]*\]",
            re.MULTILINE | re.DOTALL,
        )
        replacement = r"\1\n" + "\n".join(f"        - {table}" for table in tables)
        source, count = pattern.subn(replacement, source)
        if count != 1:
            raise ValueError(f"{slug}: bloco cleaned.tables não encontrado de forma única")
    CATALOG.write_text(source, encoding="utf-8")
    print(f"Catálogo atualizado para {len(resources)} recursos em {len(grouped)} coleções BFI")


if __name__ == "__main__":
    main()
