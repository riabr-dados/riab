from pathlib import Path
import re
import unicodedata

import pandas as pd


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


def strip_accents(value) -> str:
    return (
        unicodedata.normalize("NFKD", str(value))
        .encode("ascii", "ignore")
        .decode("ascii")
    )


def norm_col(value) -> str:
    value = strip_accents(value).strip().lower()
    value = re.sub(r"[^0-9a-z]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "coluna"


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop empty axes, normalize column names, and make object columns parquet-safe."""
    df = df.dropna(how="all").dropna(axis=1, how="all").copy()

    counts: dict[str, int] = {}
    columns = []
    for index, column in enumerate(df.columns, start=1):
        name = norm_col(column)
        if name == "unnamed":
            name = f"coluna_{index}"
        counts[name] = counts.get(name, 0) + 1
        if counts[name] > 1:
            name = f"{name}_{counts[name]}"
        columns.append(name)

    df.columns = columns
    for column, dtype in df.dtypes.items():
        if pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
            df[column] = df[column].astype("string")
    return df


def data_sheets(sheet_names, extra_ignore=()):
    ignore = {"sommaire", "definitions", "sources", "index", "esri_mapinfo_sheet"}
    ignore.update(norm_col(item) for item in extra_ignore)
    return [sheet for sheet in sheet_names if norm_col(sheet) not in ignore]


def write_parquet(df: pd.DataFrame, table: str, out_dir: Path) -> None:
    df = df.copy()
    for column, dtype in df.dtypes.items():
        if pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
            df[column] = df[column].astype("string")
    out = out_dir / f"{table}.parquet"
    df.to_parquet(out, index=False)
    print(f"{table}.parquet  {len(df)} linhas")


def read_excel_table(path: Path, sheet, header=6, engine=None) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet, header=header, engine=engine)
    return normalize_columns(df)


def _is_note_row(first_value: object) -> bool:
    text = str(first_value).strip().lower()
    return text.startswith(
        (
            "return",
            "retour",
            "source:",
            "notes:",
            "note:",
            "see notes",
            "includes ",
            "table ",
            "figure ",
            "this worksheet",
            "some cells",
        )
    )


def _is_year_like(value: object) -> bool:
    text = str(value).strip()
    return bool(re.match(r"^\d{4}(/\d{2})?$", text))


def find_bfi_header_row(raw: pd.DataFrame) -> int:
    for index, row in raw.head(20).iterrows():
        filled = row.dropna()
        if len(filled) < 2:
            continue
        first = filled.iloc[0]
        if _is_note_row(first):
            continue
        next_filled = raw.iloc[index + 1].dropna() if index + 1 < len(raw) else []
        non_first = [value for value in filled.iloc[1:].tolist()]
        if pd.isna(row.iloc[0]) and non_first and all(_is_year_like(value) for value in non_first):
            continue
        if (
            pd.isna(row.iloc[0])
            and index + 1 < len(raw)
            and pd.isna(raw.iloc[index + 1].iloc[0])
            and len(next_filled) > len(filled)
        ):
            continue
        return index
    return 0


def _bfi_columns(raw: pd.DataFrame, header_row: int) -> list[str]:
    current = raw.iloc[header_row]
    previous = raw.iloc[header_row - 1] if header_row > 0 else None
    use_previous = (
        previous is not None
        and len(previous.dropna()) >= 2
        and not _is_note_row(previous.dropna().iloc[0])
    )
    previous_filled = previous.ffill() if use_previous else None

    columns = []
    for index, value in enumerate(current.tolist(), start=1):
        prev = previous_filled.iloc[index - 1] if previous_filled is not None else None
        parts = []
        if pd.notna(prev) and str(prev).strip() != str(value).strip():
            parts.append(prev)
        if pd.notna(value):
            parts.append(value)
        if not parts:
            parts.append("categoria" if index == 1 else f"coluna_{index}")
        columns.append(" ".join(str(part).strip() for part in parts))
    return columns


def read_bfi_sheet(xls: pd.ExcelFile, sheet: str) -> pd.DataFrame:
    raw = xls.parse(sheet, header=None)
    title = None
    for value in raw.iloc[:, 0].dropna().head(3):
        if str(value).strip().lower().startswith("table "):
            title = str(value).strip()
            break

    header_row = find_bfi_header_row(raw)
    columns = _bfi_columns(raw, header_row)
    df = raw.iloc[header_row + 1:].copy()
    df.columns = columns
    df = df.dropna(how="all").dropna(axis=1, how="all")

    keep_rows = []
    for _, row in df.iterrows():
        filled = row.dropna()
        if filled.empty:
            keep_rows.append(False)
            continue
        keep_rows.append(not _is_note_row(filled.iloc[0]))
    df = df.loc[keep_rows].copy()

    df = normalize_columns(df)
    df.insert(0, "sheet", sheet)
    if title:
        df.insert(1, "titulo_tabela", title)
    return df
