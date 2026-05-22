from pathlib import Path


def latest_snapshot(dataset_dir: Path) -> Path:
    """Return the most recent snapshot directory for a raw dataset."""
    snap_root = dataset_dir / "snapshots"
    snapshots = sorted(path for path in snap_root.iterdir() if path.is_dir())
    if not snapshots:
        raise FileNotFoundError(f"Nenhum snapshot encontrado em {snap_root}")
    return snapshots[-1]


def normalize_header(name) -> str:
    """Normalize raw CSV/Excel headers with BOM and stray quotes."""
    return (
        str(name)
        .strip()
        .replace("\ufeff", "")
        .replace("\xef\xbb\xbf", "")
        .strip('"')
        .strip()
        .lower()
    )
