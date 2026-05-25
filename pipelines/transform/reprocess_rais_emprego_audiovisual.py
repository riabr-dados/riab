from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARCHIVE_DIR = ROOT / "analysis" / "rais_repro_test"
DEFAULT_OUTPUT_DIR = ROOT / "datasets" / "br-rais-emprego-audiovisual" / "snapshots" / "2026-05-23"
CLEANED = ROOT / "pipelines" / "output" / "cleaned"
DEFAULT_YEAR = 2019
SEVEN_ZIP_CANDIDATES = [
    Path(r"C:\Program Files\7-Zip\7z.exe"),
    Path(r"C:\Program Files\NVIDIA Corporation\NVIDIA App\7z.exe"),
    Path(r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\Extensions\Xamarin.VisualStudio\7-Zip\7z.exe"),
]

ARCHIVES = [
    "RAIS_VINC_PUB_NORTE.7z",
    "RAIS_VINC_PUB_CENTRO_OESTE.7z",
    "RAIS_VINC_PUB_NORDESTE.7z",
    "RAIS_VINC_PUB_SUL.7z",
    "RAIS_VINC_PUB_MG_ES_RJ.7z",
    "RAIS_VINC_PUB_SP.7z",
]

SUBCLASSES = {
    "5911101": ("59.11-1", "59.11-1/01", "Atividades de producao cinematografica, de videos e de programas de televisao", "Estudios cinematograficos"),
    "5911102": ("59.11-1", "59.11-1/02", "Atividades de producao cinematografica, de videos e de programas de televisao", "Producao de filmes para publicidade"),
    "5911199": ("59.11-1", "59.11-1/99", "Atividades de producao cinematografica, de videos e de programas de televisao", "Atividades de producao cinematografica, de videos e de programas de televisao nao especificadas anteriormente"),
    "5912001": ("59.12-0", "59.12-0/01", "Atividades de pos-producao cinematografica, de videos e de programas de televisao", "Servicos de dublagem"),
    "5912002": ("59.12-0", "59.12-0/02", "Atividades de pos-producao cinematografica, de videos e de programas de televisao", "Servicos de mixagem sonora em producao audiovisual"),
    "5912099": ("59.12-0", "59.12-0/99", "Atividades de pos-producao cinematografica, de videos e de programas de televisao", "Atividades de pos-producao cinematografica, de videos e de programas de televisao nao especificadas anteriormente"),
    "5913800": ("59.13-8", "59.13-8/00", "Distribuicao cinematografica, de video e de programas de televisao", "Distribuicao cinematografica, de video e de programas de televisao"),
    "5914600": ("59.14-6", "59.14-6/00", "Atividades de exibicao cinematografica", "Atividades de exibicao cinematografica"),
    "6021700": ("60.21-7", "60.21-7/00", "Atividades de televisao aberta", "Atividades de televisao aberta"),
    "6022501": ("60.22-5", "60.22-5/01", "Programadoras e atividades relacionadas a televisao por assinatura", "Programadoras"),
    "6022502": ("60.22-5", "60.22-5/02", "Programadoras e atividades relacionadas a televisao por assinatura", "Atividades relacionadas a televisao por assinatura, exceto programadoras"),
    "6141800": ("61.41-8", "61.41-8/00", "Operadoras de televisao por assinatura por cabo", "Operadoras de televisao por assinatura por cabo"),
    "6142600": ("61.42-6", "61.42-6/00", "Operadoras de televisao por assinatura por micro-ondas", "Operadoras de televisao por assinatura por micro-ondas"),
    "6143400": ("61.43-4", "61.43-4/00", "Operadoras de televisao por assinatura por satelite", "Operadoras de televisao por assinatura por satelite"),
    "7722500": ("77.22-5", "77.22-5/00", "Aluguel de fitas de video, DVDs e similares", "Aluguel de fitas de video, DVDs e similares"),
    "4762800": ("47.62-8", "47.62-8/00", "Comercio varejista de discos, CDs, DVDs e fitas", "Comercio varejista de discos, CDs, DVDs e fitas"),
}

PDET_FTP_BASE = "ftp://ftp.mtps.gov.br/pdet/microdados/RAIS"


def digits(value: object) -> str:
    return re.sub(r"\D", "", str(value))


def seven_zip() -> Path:
    exe = next((path for path in SEVEN_ZIP_CANDIDATES if path.exists()), None)
    if exe is None:
        raise RuntimeError(
            "7-Zip nao encontrado. Instale o 7-Zip (https://www.7-zip.org) "
            "ou adicione o caminho do executavel em SEVEN_ZIP_CANDIDATES."
        )
    return exe


def archive_member(archive: Path) -> str:
    exe = seven_zip()
    result = subprocess.run(
        [str(exe), "l", "-slt", str(archive)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    names = [
        line.split("=", 1)[1].strip()
        for line in result.stdout.splitlines()
        if line.startswith("Path =")
    ]
    # 7z l inclui o proprio arquivo .7z como primeiro Path; descartar.
    names = [name for name in names if name and not name.lower().endswith(".7z")]
    if len(names) != 1:
        raise RuntimeError(f"Arquivo inesperado em {archive.name}: {names}")
    return names[0]


def open_archive_stream(archive: Path, member: str) -> subprocess.Popen:
    exe = seven_zip()
    command = [str(exe), "e", "-so", str(archive), member]
    return subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)


ACTIVE_COL_CANDIDATES = ("Vínculo Ativo 31/12", "Vinculo Ativo 31/12", "VINCULOATIVO3112")
CNAE_COL_CANDIDATES = ("CNAE 2.0 Subclasse", "CNAE 2.0 Subclass", "CNAE2.0Subclasse", "CNAE20Subclasse")


def _normalize_header(value: str) -> str:
    cleaned = value.strip().strip('"').strip()
    return re.sub(r"\s+", " ", cleaned)


def resolve_columns(header_line: bytes) -> tuple[int, int, list[str]]:
    raw = header_line.decode("latin1").rstrip("\r\n")
    columns = [_normalize_header(part) for part in raw.split(";")]
    normalized = {col.casefold(): idx for idx, col in enumerate(columns)}
    active_idx = next(
        (normalized[candidate.casefold()] for candidate in ACTIVE_COL_CANDIDATES if candidate.casefold() in normalized),
        None,
    )
    cnae_idx = next(
        (normalized[candidate.casefold()] for candidate in CNAE_COL_CANDIDATES if candidate.casefold() in normalized),
        None,
    )
    if active_idx is None or cnae_idx is None:
        raise RuntimeError(
            "Nao foi possivel localizar as colunas de Vinculo Ativo 31/12 e CNAE 2.0 Subclasse no header da RAIS. "
            f"Header lido: {columns[:50]}"
        )
    return active_idx, cnae_idx, columns


def aggregate_archive(archive: Path) -> tuple[int, int, dict[str, int]]:
    counts = {raw: 0 for raw in SUBCLASSES}
    total_rows = 0
    active_rows = 0
    member = archive_member(archive)
    proc = open_archive_stream(archive, member)
    assert proc.stdout is not None
    try:
        header_line = proc.stdout.readline()
        if not header_line:
            raise RuntimeError(f"Arquivo {archive.name} vazio ou ilegivel")
        active_idx, cnae_idx, _ = resolve_columns(header_line)
        chunks = pd.read_csv(
            proc.stdout,
            sep=";",
            header=None,
            usecols=[active_idx, cnae_idx],
            names=["__active__", "__cnae__"],
            dtype=str,
            chunksize=1_000_000,
            encoding="latin1",
        )
        for chunk in chunks:
            total_rows += len(chunk)
            active = chunk[chunk["__active__"].str.strip().eq("1")]
            active_rows += len(active)
            value_counts = active["__cnae__"].str.strip().value_counts()
            for raw in SUBCLASSES:
                counts[raw] += int(value_counts.get(raw, 0))
    finally:
        proc.stdout.close()
    return_code = proc.wait()
    if return_code not in {0, -1}:
        raise RuntimeError(f"Falha ao descompactar {archive.name}: codigo {return_code}")
    return total_rows, active_rows, counts


def load_published(year: int) -> pd.DataFrame:
    current = pd.read_csv(
        DEFAULT_OUTPUT_DIR / "rais_emprego_audiovisual_subclasse_ano.csv",
    )
    current = current[current["ano"].eq(year)].copy()
    current["cnae_raw"] = current["cnae_subclasse"].map(digits)
    return current[
        [
            "cnae_raw",
            "cnae_classe",
            "cnae_subclasse",
            "classe",
            "subclasse",
            "empregos_formais_ativos_31_12",
        ]
    ].rename(columns={"empregos_formais_ativos_31_12": "valor_publicado_ancine"})


def build_reprocessed(year: int, national: dict[str, int]) -> pd.DataFrame:
    rows = []
    for raw, count in national.items():
        cnae_classe, cnae_subclasse, classe, subclasse = SUBCLASSES[raw]
        rows.append(
            {
                "ano": year,
                "cnae_raw": raw,
                "cnae_classe": cnae_classe,
                "cnae_subclasse": cnae_subclasse,
                "classe": classe,
                "subclasse": subclasse,
                "empregos_formais_ativos_31_12": count,
                "camada_metodologica": "reprocessado_fonte_primaria",
                "fonte_primaria": "MTE/PDET microdados RAIS vinculos publicos",
                "fonte_url": f"{PDET_FTP_BASE}/{year}/",
                "metodo_reprocessamento": "vinculo_ativo_31_12_por_subclasse_cnae_ancine",
            }
        )
    return pd.DataFrame(rows)


def write_outputs(df: pd.DataFrame, comparison: pd.DataFrame, regional: pd.DataFrame, year: int, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    CLEANED.mkdir(parents=True, exist_ok=True)
    tables = {
        f"rais_emprego_audiovisual_subclasse_ano_reprocessado_pdet_{year}": df,
        f"rais_emprego_audiovisual_comparacao_ancine_pdet_{year}": comparison,
        f"rais_emprego_audiovisual_reprocessamento_regioes_pdet_{year}": regional,
    }
    for name, table in tables.items():
        table.to_csv(output_dir / f"{name}.csv", index=False, encoding="utf-8")
        table.to_csv(CLEANED / f"{name}.csv", index=False, encoding="utf-8")
        table.to_parquet(CLEANED / f"{name}.parquet", index=False)
        print(f"[OK] {name}: {len(table):,} linhas")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reprocessa emprego audiovisual a partir de microdados RAIS/PDET.",
    )
    parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    parser.add_argument("--archive-dir", type=Path, default=DEFAULT_ARCHIVE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    national = {raw: 0 for raw in SUBCLASSES}
    regional_rows = []
    for archive_name in ARCHIVES:
        archive = args.archive_dir / archive_name
        if not archive.exists():
            raise FileNotFoundError(f"Arquivo RAIS nao encontrado: {archive}")
        rows, active_rows, counts = aggregate_archive(archive)
        region = archive_name.removeprefix("RAIS_VINC_PUB_").removesuffix(".7z")
        regional_rows.append(
            {
                "ano": args.year,
                "arquivo_regional": archive_name,
                "recorte_regional": region,
                "linhas_brutas": rows,
                "vinculos_ativos_31_12": active_rows,
                "empregos_audiovisual_ativos_31_12": sum(counts.values()),
                "fonte_url": f"{PDET_FTP_BASE}/{args.year}/{archive_name}",
            }
        )
        for raw, count in counts.items():
            national[raw] += count
        print(f"[OK] {region}: audiovisual={sum(counts.values()):,} linhas={rows:,}")

    reprocessed = build_reprocessed(args.year, national)
    published = load_published(args.year)
    comparison = published.merge(
        reprocessed[["cnae_raw", "cnae_subclasse", "empregos_formais_ativos_31_12"]],
        on=["cnae_raw", "cnae_subclasse"],
        how="left",
    ).rename(columns={"empregos_formais_ativos_31_12": "valor_reprocessado_pdet"})
    comparison["diferenca_reprocessado_menos_publicado"] = (
        comparison["valor_reprocessado_pdet"] - comparison["valor_publicado_ancine"]
    )
    comparison["diferenca_percentual_sobre_publicado"] = (
        comparison["diferenca_reprocessado_menos_publicado"]
        / comparison["valor_publicado_ancine"]
        * 100
    ).round(4)
    comparison["camada_publicada"] = "publicado_ancine"
    comparison["camada_reprocessada"] = "reprocessado_fonte_primaria"
    regional = pd.DataFrame(regional_rows)
    write_outputs(reprocessed, comparison, regional, args.year, args.output_dir)
    print(
        "[RESUMO] "
        f"publicado={comparison['valor_publicado_ancine'].sum():,} "
        f"reprocessado={comparison['valor_reprocessado_pdet'].sum():,} "
        f"dif={comparison['diferenca_reprocessado_menos_publicado'].sum():,}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
