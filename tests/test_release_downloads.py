import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from pipelines.build_downloads import generate
from pipelines.upload_hf import download_operations


def test_release_rejects_missing_or_stale_downloads(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path('catalog').mkdir()
    cleaned = Path('pipelines/output/cleaned'); cleaned.mkdir(parents=True)
    path = cleaned / 'example.parquet'
    pq.write_table(pa.table({'id': ['001']}), path)
    manifest = {'resources': {'example': generate(path, Path('pipelines/output/downloads'))}}
    Path('catalog/downloads.json').write_text(json.dumps(manifest), encoding='utf-8')
    dataset = {'slug': 'example', 'cleaned': {'tables': ['example']}}
    assert len(download_operations([dataset])) == 2
    with pytest.raises(ValueError, match='ainda não gerados'):
        download_operations([{'slug': 'missing', 'cleaned': {'tables': ['missing']}}])
    pq.write_table(pa.table({'id': ['002']}), path)
    with pytest.raises(ValueError, match='Regerar downloads'):
        download_operations([dataset])
