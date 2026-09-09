from pathlib import Path

import pyarrow.parquet as pq
import yaml

from pipelines.build_downloads import catalog_tables


ROOT = Path(__file__).resolve().parents[1]


def test_every_published_resource_has_matching_parquet_and_schema():
    tables = catalog_tables(ROOT / "catalog/datasets.yaml")
    assert len(tables) == len(set(tables))
    for table in tables:
        parquet = ROOT / "pipelines/output/cleaned" / f"{table}.parquet"
        schema = ROOT / "catalog/schemas" / f"{table}.yaml"
        assert parquet.is_file(), table
        assert schema.is_file(), table
        document = yaml.safe_load(schema.read_text(encoding="utf-8"))
        assert document["table"] == table
        assert [column["name"] for column in document["columns"]] == pq.read_schema(parquet).names
