from pathlib import Path
import re

import pandas as pd
import yaml

from pipelines.transform.clean_bfi_split import FILES, main


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "pipelines/output/cleaned"


def test_every_bfi_t_sheet_has_one_independent_resource():
    main()
    resources = yaml.safe_load((ROOT / "catalog/bfi_resources.yaml").read_text(encoding="utf-8"))["resources"]
    assert len(resources) == 98
    assert len({resource["table"] for resource in resources}) == 98
    for filename, (dataset, _) in FILES.items():
        source = ROOT / "datasets/bfi-statistical-yearbook-2023/snapshots/2026-05-19" / filename
        sheets = {sheet for sheet in pd.ExcelFile(source, engine="odf").sheet_names if re.fullmatch(r"T\d+", sheet)}
        represented = {resource["sheet"] for resource in resources if resource["dataset"] == dataset}
        assert represented == sheets


def test_bfi_outputs_do_not_mix_sheets_or_use_unnamed_headers():
    resources = yaml.safe_load((ROOT / "catalog/bfi_resources.yaml").read_text(encoding="utf-8"))["resources"]
    for resource in resources:
        frame = pd.read_parquet(OUTPUT / f"{resource['table']}.parquet")
        assert set(frame["sheet"]) == {resource["sheet"]}
        assert not any(re.match(r"^(coluna|unnamed)", column) for column in frame.columns)
        assert len(frame) == resource["rows"]
        assert (ROOT / "catalog/schemas" / f"{resource['table']}.yaml").exists()


def test_bfi_catalog_uses_split_resources_and_publishes_education():
    catalog = yaml.safe_load((ROOT / "catalog/datasets.yaml").read_text(encoding="utf-8"))["datasets"]
    bfi = [dataset for dataset in catalog if dataset["slug"].startswith("bfi-")]
    tables = [table for dataset in bfi for table in dataset["cleaned"]["tables"]]
    assert len(tables) == 98
    assert all(re.search(r"_t\d{2}$", table) for table in tables)
    education = next(dataset for dataset in bfi if dataset["slug"] == "bfi-educacao-cinematografica")
    assert not education.get("hidden")
