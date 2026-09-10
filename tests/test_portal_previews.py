import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREVIEWS = ROOT / "portal" / "public" / "previews"
CLEANED = ROOT / "pipelines" / "output" / "cleaned"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_editorial_previews_reference_current_parquets():
    manifest = json.loads((PREVIEWS / "index.json").read_text(encoding="utf-8"))
    assert set(manifest["previews"]) == {"preco_ingresso", "obras", "pib_audiovisual_total_ano"}
    for table, item in manifest["previews"].items():
        preview = json.loads((PREVIEWS / item["path"]).read_text(encoding="utf-8"))
        assert preview["table"] == table
        assert preview["source"]["parquetSha256"] == digest(CLEANED / f"{table}.parquet")
        assert preview["data"]["rows"]


def test_brasil_no_mundo_stories_keep_distinct_meanings_and_sources():
    document = json.loads((PREVIEWS / "brasil-no-mundo.json").read_text(encoding="utf-8"))
    stories = {story["id"]: story for story in document["stories"]}
    assert set(stories) == {"cinema-admissoes-europa", "cnc-registros-brasil", "bfi-admissoes-brasil"}
    assert {story["section"] for story in stories.values()} == {"cinema", "coproducoes", "mercado"}
    for story in stories.values():
        assert story["sourceSha256"] == digest(CLEANED / f"{story['table']}.parquet")
        assert story["rows"] and story["note"] and story["unit"]
    assert [row["label"] for row in stories["cnc-registros-brasil"]["rows"]] == ["Vistos de exibição", "Filmes com agrément"]
    assert [row["label"] for row in stories["bfi-admissoes-brasil"]["rows"]] == [2019, 2020, 2021, 2022, 2023]
