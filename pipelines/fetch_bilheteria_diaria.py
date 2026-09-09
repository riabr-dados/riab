"""Baixa atomicamente os dois pacotes oficiais de bilheteria diária da ANCINE."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/auditoria-pda-20260908/official/packages"
URLS = [
    "https://dados.ancine.gov.br/dados-abertos/bilheteria-diaria-obras-por-distribuidoras-csv.zip",
    "https://dados.ancine.gov.br/dados-abertos/bilheteria-diaria-obras-por-exibidoras-csv.zip",
]


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def download(url: str, destination: Path) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    sha256 = hashlib.sha256()
    size = 0
    with requests.get(url, stream=True, timeout=(30, 300)) as response:
        response.raise_for_status()
        with temporary.open("wb") as stream:
            for chunk in response.iter_content(8 * 1024 * 1024):
                if chunk:
                    stream.write(chunk)
                    sha256.update(chunk)
                    size += len(chunk)
    temporary.replace(destination)
    return {"url": url, "path": str(destination), "bytes": size, "sha256": sha256.hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    records = []
    for url in URLS:
        path = args.output_dir / url.rsplit("/", 1)[-1]
        record = download(url, path)
        if digest(path) != record["sha256"]:
            raise ValueError(f"Hash divergente após download: {path}")
        records.append(record)
        print(path.name, record["bytes"], record["sha256"])
    (args.output_dir / "download_manifest.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
