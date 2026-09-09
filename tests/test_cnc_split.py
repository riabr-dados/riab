from pathlib import Path
import re

import pandas as pd
import yaml

from pipelines.transform.clean_cnc_split import ANNUAL_PREFIXES, EXTRA_IGNORE, FILES, main, open_workbook
from pipelines.transform.common import data_sheets, norm_col


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "pipelines/output/cleaned"


def test_every_cnc_data_sheet_has_an_independent_resource_or_annual_union():
    main()
    resources = yaml.safe_load((ROOT / "catalog/cnc_resources.yaml").read_text(encoding="utf-8"))["resources"]
    assert len({resource["table"] for resource in resources}) == len(resources)
    for dataset, filename, prefix in FILES:
        source = next((ROOT / "datasets" / dataset / "snapshots").glob(f"*/{filename}"))
        sheets = open_workbook(source).sheet_names
        represented = {resource["sheet"] for resource in resources
                       if resource["dataset"] == dataset and resource["file"] == filename}
        if prefix in ANNUAL_PREFIXES:
            assert represented == {"abas anuais"}
            expected_years = {int(sheet) for sheet in sheets if sheet.strip().isdigit()}
            frame = pd.read_parquet(OUTPUT / f"{prefix}.parquet")
            assert set(frame["ano"].dropna().astype(int)) == expected_years
        else:
            expected = {sheet for sheet in data_sheets(sheets, extra_ignore=EXTRA_IGNORE)
                        if norm_col(sheet) not in EXTRA_IGNORE}
            assert represented == expected


def test_cnc_outputs_do_not_mix_thematic_sheets_or_use_placeholder_headers():
    resources = yaml.safe_load((ROOT / "catalog/cnc_resources.yaml").read_text(encoding="utf-8"))["resources"]
    for resource in resources:
        frame = pd.read_parquet(OUTPUT / f"{resource['table']}.parquet")
        if resource["sheet"] != "abas anuais":
            assert set(frame["sheet"]) == {resource["sheet"]}
        assert not any(re.match(r"^(nan|unnamed|coluna_)", column) for column in frame.columns)
        assert len(frame) == resource["rows"]
        assert (ROOT / "catalog/schemas" / f"{resource['table']}.yaml").exists()
