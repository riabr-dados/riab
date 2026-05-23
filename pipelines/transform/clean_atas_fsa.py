"""Extract tabular facts from FSA result PDFs.

Outputs:
  pipelines/output/cleaned/fsa_atas_resultados.parquet
  pipelines/output/cleaned/fsa_atas_resultados.csv
  pipelines/output/cleaned/fsa_atas_festivais.parquet
  pipelines/output/cleaned/fsa_atas_festivais.csv

The source PDFs are official result minutes. Text extraction is necessarily
best-effort: line wrapping varies across files and older PDFs are not born as
clean tables. The output keeps source metadata and method notes so rows remain
auditable.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import re
import sys
import unicodedata

import pandas as pd

from common import write_parquet

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "datasets" / "ancine-atas-fsa"
SNAPSHOT = DATASET / "snapshots" / "2026-05-19"
OUT = ROOT / "pipelines" / "output" / "cleaned"
OUT.mkdir(parents=True, exist_ok=True)

PYPDF_FALLBACK = (
    Path.home()
    / ".cache"
    / "codex-runtimes"
    / "codex-primary-runtime"
    / "dependencies"
    / "python"
    / "Lib"
    / "site-packages"
)

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - local runtime fallback
    if PYPDF_FALLBACK.exists():
        sys.path.append(str(PYPDF_FALLBACK))
    from pypdf import PdfReader


UF_CODES = {
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
}

COUNTRY_ALIASES = {
    "africa do sul",
    "alemanha",
    "argentina",
    "australia",
    "belgica",
    "bosnia herzegovina",
    "brasil",
    "brazil",
    "canada",
    "chile",
    "china",
    "colombia",
    "coreia",
    "cuba",
    "dinamarca",
    "espanha",
    "eua",
    "estados unidos",
    "franca",
    "grecia",
    "holanda",
    "india",
    "inglaterra",
    "italia",
    "japao",
    "mexico",
    "nova zelandia",
    "peru",
    "portugal",
    "russia",
    "suecia",
    "suica",
    "turquia",
    "uruguai",
}

EVENT_KEYWORDS = (
    "academia brasileira",
    "afi fest",
    "annecy",
    "bafici",
    "berlim",
    "berlinale",
    "bfI".lower(),
    "biarritz",
    "busan",
    "cannes",
    "cartagena",
    "cine ",
    "cinema",
    "cinelatino",
    "doclisboa",
    "festival",
    "film",
    "filmfest",
    "fica",
    "fipresci",
    "forumdoc",
    "giffoni",
    "gramado",
    "havana",
    "huelva",
    "indielisboa",
    "janela internacional",
    "jeonju",
    "locarno",
    "mar del plata",
    "melbourne",
    "miami",
    "mostra",
    "palm springs",
    "rotterdam",
    "san sebastian",
    "san sebastián",
    "sarajevo",
    "sitges",
    "sundance",
    "sxsw",
    "sydney",
    "thessaloniki",
    "toronto",
    "toulouse",
    "tribeca",
    "veneza",
    "viena",
)


@dataclass
class ProjectContext:
    posicao: int | None
    beneficiario: str | None
    cnpj: str | None
    uf: str | None
    cpb: str | None
    titulo_obra: str | None
    pontuacao_final: float | None
    empresa_vocacionada: bool | None
    resultado: str | None
    source_file: str
    chamada: str
    ano_chamada: int | None


def strip_accents(value: object) -> str:
    return (
        unicodedata.normalize("NFKD", "" if value is None else str(value))
        .encode("ascii", "ignore")
        .decode("ascii")
    )


def norm_text(value: object) -> str:
    return strip_accents(value).lower()


def clean_line(line: str) -> str:
    line = line.replace("\xa0", " ")
    line = re.sub(r"\s+", " ", line).strip()
    return line


def skip_line(line: str) -> bool:
    if not line:
        return True
    if re.fullmatch(r"\d{1,3}", line):
        return True
    lowered = norm_text(line)
    return lowered in {
        "informacao publica",
        "informacao publica 1",
        "agencia nacional do cinema - ancine",
    }


COMPANY_START_HINTS = (
    "audiovis",
    "cinema",
    "cinemato",
    "comunic",
    "conteudo",
    "criac",
    "criacao",
    "entretenimento",
    "experienc",
    "filme",
    "films",
    "ltda",
    "multimidia",
    "produc",
    "servic",
    "video",
    "vídeo",
)


def looks_like_project_start_after_rank(line: str) -> bool:
    """Detect a producer/project row after a detached rank number.

    Some PDFs split the ranking number onto its own line. Page numbers are also
    standalone numbers, so we only stitch the number to the next line when that
    next line looks like the start of a proponent/company entry, not an event.
    """
    lowered = norm_text(line)
    if not line or is_rank_line(line) or looks_like_event(line):
        return False
    if re.match(r"^(Especial|AA|A|B|C)\b", line, flags=re.I):
        return False
    if lowered.startswith(
        (
            "#",
            "a classificacao",
            "agencia nacional",
            "anexo",
            "ata ",
            "banco regional",
            "brde/fsa",
            "cada uma",
            "divisao",
            "encerrado",
            "informacao",
            "rio de janeiro",
        )
    ):
        return False
    return any(hint in lowered for hint in COMPANY_START_HINTS)


def parse_decimal(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def parse_brl(value: object) -> float | None:
    text = "" if value is None else str(value)
    match = re.search(r"R\$\s*([\d\.\s]+,\d{2})", text)
    if not match:
        return None
    return parse_decimal(match.group(1).replace(" ", ""))


def title_key(value: object) -> str:
    text = norm_text(value)
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_meta(path: Path) -> tuple[str, int | None]:
    name = path.name.lower()
    if "2o-edicao" in name:
        return "BRDE/FSA - Producao Cinema: Desempenho Artistico 2a edicao 2024", 2024
    if "desempenho-artistico-2024" in name or "2024_26" in name:
        return "BRDE/FSA - Producao Cinema: Desempenho Artistico 2024", 2024
    if "2018" in name:
        return "BRDE/FSA - Suporte Automatico: Desempenho Artistico 2018", 2018
    if "2017" in name:
        return "BRDE/FSA - PRODAV 07/2017: Desempenho Artistico", 2017
    if "2015" in name:
        return "BRDE/FSA - PRODAV 07/2015: Desempenho Artistico", 2015
    if "2014" in name:
        return "BRDE/FSA - PRODAV 07/2014: PAQ", 2014
    return path.stem, None


def pdf_lines(path: Path) -> list[str]:
    reader = PdfReader(str(path))
    raw_lines: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        for raw in text.splitlines():
            line = clean_line(raw)
            if line:
                raw_lines.append(line)

    lines: list[str] = []
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        if re.fullmatch(r"\d{1,3}", line):
            next_line = ""
            j = i + 1
            while j < len(raw_lines):
                if raw_lines[j]:
                    next_line = raw_lines[j]
                    break
                j += 1
            if next_line and looks_like_project_start_after_rank(next_line):
                lines.append(f"{line} {next_line}")
                i = j + 1
                continue
            i += 1
            continue
        if not skip_line(line):
            lines.append(line)
        i += 1
    return lines


def is_rank_line(line: str) -> bool:
    if not re.match(r"^\d{1,3}\s+\S", line):
        return False
    if re.match(r"^(19|20)\d{2}\b", line):
        return False
    return True


def line_ends_score(line: str) -> bool:
    return bool(re.search(r"\s\d+(?:,\d+)?$", line.strip()))


def starts_event_fragment(line: str) -> bool:
    lowered = norm_text(line)
    if is_rank_line(line):
        return False
    if re.match(r"^(Especial|AA|A|B|C)(?:\s|$)", line, flags=re.I):
        return True
    return any(keyword in lowered for keyword in EVENT_KEYWORDS)


def looks_like_event(line: str) -> bool:
    lowered = norm_text(line)
    if not line_ends_score(line):
        return False
    if is_rank_line(line):
        return False
    parens = re.findall(r"\(([^()]+)\)", line)
    if parens and norm_text(parens[-1].strip()) in COUNTRY_ALIASES:
        return True
    return any(keyword in lowered for keyword in EVENT_KEYWORDS)


def split_score(line: str) -> tuple[str, float | None]:
    match = re.search(r"^(.*?)\s+(\d+(?:,\d+)?)$", line.strip())
    if not match:
        return line.strip(), None
    return match.group(1).strip(), parse_decimal(match.group(2))


def parse_event_text(text: str) -> dict[str, object] | None:
    text = clean_line(text)
    label, points = split_score(text)
    if points is None:
        return None

    categoria = None
    match = re.match(r"^(Especial|AA|A|B|C)\s+(.+)$", label, flags=re.I)
    if match:
        categoria = match.group(1)
        label = match.group(2).strip()

    tipo_pontuacao = None
    tipo_re = re.compile(
        r"\s+(Competitiva|N[aã]o Competitiva|Melhor Filme/Diretor|Outros Pr[eê]mios?)$",
        flags=re.I,
    )
    match = tipo_re.search(label)
    if match:
        tipo_pontuacao = match.group(1)
        label = label[: match.start()].strip()

    pais_evento = None
    parens = re.findall(r"\(([^()]+)\)", label)
    if parens:
        candidate = parens[-1].strip()
        if norm_text(candidate) in COUNTRY_ALIASES or len(candidate) > 3:
            pais_evento = candidate

    lowered = norm_text(label)
    internacional = None
    if pais_evento:
        internacional = norm_text(pais_evento) not in {"brasil", "brazil"}
    elif any(token in lowered for token in ("international", "internacional", "cannes", "berlim", "toronto", "sundance", "locarno", "rotterdam")):
        internacional = True

    return {
        "categoria_festival": categoria,
        "evento": label,
        "pais_evento_extraido": pais_evento,
        "tipo_pontuacao": tipo_pontuacao,
        "pontos_evento": points,
        "evento_internacional_estimado": internacional,
    }


def parse_project_header(lines: list[str], source_file: str, chamada: str, ano: int | None) -> ProjectContext | None:
    text = clean_line(" ".join(lines))
    text = text.replace("# ", "")
    if not text:
        return None

    match = re.match(
        r"^(?P<pos>\d{1,3})\s+(?P<benef>.+?)\s+(?P<cnpj>\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})\s+"
        r"(?P<cpb>B\d{13})\s+(?P<title>.+?)\s+(?P<score>\d+(?:,\d+)?)\s+"
        r"(?P<voc>Sim)?\s*(?P<result>Classificada|Desclassificada)\s*$",
        text,
        flags=re.I,
    )
    if match:
        return ProjectContext(
            posicao=int(match.group("pos")),
            beneficiario=match.group("benef").strip(),
            cnpj=match.group("cnpj"),
            uf=None,
            cpb=match.group("cpb"),
            titulo_obra=match.group("title").strip(),
            pontuacao_final=parse_decimal(match.group("score")),
            empresa_vocacionada=bool(match.group("voc")),
            resultado=match.group("result"),
            source_file=source_file,
            chamada=chamada,
            ano_chamada=ano,
        )

    match = re.match(r"^(?P<pos>\d{1,3})\s+(?P<body>.+?)\s+(?P<score>\d+(?:,\d+)?)$", text)
    if not match:
        return None

    posicao = int(match.group("pos"))
    body = match.group("body").strip()
    score = parse_decimal(match.group("score"))

    uf = None
    beneficiario = None
    titulo = body
    uf_matches = list(re.finditer(r"\b(" + "|".join(sorted(UF_CODES)) + r")\b", body))
    if uf_matches:
        last = uf_matches[-1]
        uf = last.group(1)
        beneficiario = body[: last.start()].strip()
        titulo = body[last.end() :].strip()

    return ProjectContext(
        posicao=posicao,
        beneficiario=beneficiario,
        cnpj=None,
        uf=uf,
        cpb=None,
        titulo_obra=titulo,
        pontuacao_final=score,
        empresa_vocacionada=None,
        resultado=None,
        source_file=source_file,
        chamada=chamada,
        ano_chamada=ano,
    )


def project_to_row(project: ProjectContext, file_hash: str) -> dict[str, object]:
    return {
        "ano_chamada": project.ano_chamada,
        "chamada": project.chamada,
        "posicao": project.posicao,
        "beneficiario_indireto": project.beneficiario,
        "cnpj_beneficiario": project.cnpj,
        "uf_beneficiario": project.uf,
        "cpb": project.cpb,
        "titulo_obra": project.titulo_obra,
        "chave_titulo": title_key(project.titulo_obra),
        "pontuacao_final": project.pontuacao_final,
        "empresa_vocacionada": project.empresa_vocacionada,
        "resultado": project.resultado,
        "source_file": project.source_file,
        "source_sha256": file_hash,
        "metodo_extracao": "pypdf_text_regex",
    }


def parse_current_pdf(path: Path) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    lines = pdf_lines(path)
    chamada, ano = source_meta(path)
    file_hash = sha256(path)
    results: list[dict[str, object]] = []
    events: list[dict[str, object]] = []
    result_seen: set[tuple[object, object, object]] = set()

    pending_header: list[str] = []
    pending_event: list[str] = []
    current: ProjectContext | None = None
    active = False

    def add_project(project: ProjectContext | None) -> None:
        if project is None:
            return
        key = (project.source_file, project.posicao, project.titulo_obra)
        if key in result_seen:
            return
        result_seen.add(key)
        results.append(project_to_row(project, file_hash))

    def flush_header() -> None:
        nonlocal current, pending_header
        if pending_header:
            current = parse_project_header(pending_header, path.name, chamada, ano)
            add_project(current)
            pending_header = []

    def flush_event() -> None:
        nonlocal pending_event
        if not pending_event or current is None:
            pending_event = []
            return
        parsed = parse_event_text(" ".join(pending_event))
        if parsed:
            events.append(
                {
                    "ano_chamada": current.ano_chamada,
                    "chamada": current.chamada,
                    "posicao_obra": current.posicao,
                    "beneficiario_indireto": current.beneficiario,
                    "cnpj_beneficiario": current.cnpj,
                    "uf_beneficiario": current.uf,
                    "cpb": current.cpb,
                    "titulo_obra": current.titulo_obra,
                    "chave_titulo": title_key(current.titulo_obra),
                    "ano_evento": None,
                    **parsed,
                    "source_file": current.source_file,
                    "source_sha256": file_hash,
                    "metodo_extracao": "pypdf_text_regex",
                    "observacao_metodologica": "Levantamento nao exaustivo: eventos/premios aceitos para pontuacao em chamadas FSA de desempenho artistico.",
                }
            )
        pending_event = []

    for line in lines:
        lowered = norm_text(line)
        if "a classificacao final segue" in lowered or "inscricoes deferidas" in lowered:
            active = True
            continue
        if "anexo i - pontuacao detalhada" in lowered:
            break
        if not active:
            continue
        if lowered.startswith(("cada uma das", "encerrado", "rio de janeiro", "com base no resultado", "divisao dos recursos")):
            flush_event()
            flush_header()
            continue
        if is_rank_line(line):
            flush_event()
            flush_header()
            pending_header = [line]
            current = None
            continue
        if pending_header:
            header_text = clean_line(" ".join(pending_header))
            if line_ends_score(header_text) and (starts_event_fragment(line) or looks_like_event(line)):
                flush_header()
            else:
                pending_header.append(line)
                continue
        if current is None:
            continue
        if pending_event:
            pending_event.append(line)
            if line_ends_score(" ".join(pending_event)):
                flush_event()
            continue
        if starts_event_fragment(line) or looks_like_event(line):
            pending_event = [line]
            if line_ends_score(line):
                flush_event()

    flush_event()
    flush_header()
    results.extend(parse_2024_classification_rows(lines, path, chamada, ano, file_hash, result_seen))
    events.extend(parse_2024_annex_events(lines, path, chamada, ano, file_hash))
    return results, events


def parse_2024_classification_rows(
    lines: list[str],
    path: Path,
    chamada: str,
    ano: int | None,
    file_hash: str,
    result_seen: set[tuple[object, object, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    buffer: list[str] = []
    for line in lines:
        lowered = norm_text(line)
        if "anexo i - pontuacao detalhada" in lowered or "divisao dos recursos" in lowered:
            break
        if is_rank_line(line) or buffer:
            buffer.append(line)
            text = clean_line(" ".join(buffer))
            if re.search(r"\b(Classificada|Desclassificada)\b", text, flags=re.I):
                project = parse_project_header(buffer, path.name, chamada, ano)
                if project is not None:
                    key = (project.source_file, project.posicao, project.titulo_obra)
                    if key not in result_seen:
                        result_seen.add(key)
                        rows.append(project_to_row(project, file_hash))
                buffer = []
    return rows


def parse_title_score(parts: list[str]) -> tuple[str | None, float | None]:
    text = clean_line(" ".join(parts))
    title, score = split_score(text)
    if score is None:
        return None, None
    if any(keyword in norm_text(title) for keyword in EVENT_KEYWORDS):
        return None, None
    return title, score


def parse_2024_annex_events(
    lines: list[str],
    path: Path,
    chamada: str,
    ano: int | None,
    file_hash: str,
) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    try:
        start = next(i for i, line in enumerate(lines) if "anexo i - pontuacao detalhada" in norm_text(line))
    except StopIteration:
        return events

    current_title: str | None = None
    current_score: float | None = None
    current_cpb: str | None = None
    current_year: int | None = None
    pending_title: list[str] = []

    for line in lines[start + 1 :]:
        lowered = norm_text(line)
        if lowered.startswith(("titulo - cpb", "banco regional", "rio de janeiro")):
            continue
        if re.fullmatch(r"B\d{13}", line):
            title, score = parse_title_score(pending_title)
            if title:
                current_title = title
                current_score = score
                current_cpb = line
                current_year = None
            pending_title = []
            continue
        if re.fullmatch(r"(19|20)\d{2}", line):
            if current_cpb:
                current_year = int(line)
            else:
                pending_title.append(line)
            continue
        if looks_like_event(line) and current_title and current_cpb:
            parsed = parse_event_text(line)
            if parsed:
                events.append(
                    {
                        "ano_chamada": ano,
                        "chamada": chamada,
                        "posicao_obra": None,
                        "beneficiario_indireto": None,
                        "cnpj_beneficiario": None,
                        "uf_beneficiario": None,
                        "cpb": current_cpb,
                        "titulo_obra": current_title,
                        "chave_titulo": title_key(current_title),
                        "ano_evento": current_year,
                        **parsed,
                        "source_file": path.name,
                        "source_sha256": file_hash,
                        "metodo_extracao": "pypdf_text_regex",
                        "observacao_metodologica": "Levantamento nao exaustivo: eventos/premios aceitos para pontuacao em chamadas FSA de desempenho artistico.",
                    }
                )
            continue
        if line_ends_score(line) and not looks_like_event(line):
            pending_title = [line]
            current_title = current_title
            continue
        if pending_title and not current_cpb:
            pending_title.append(line)
        elif line and not looks_like_event(line) and not re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", line):
            if line.isupper() or re.search(r"\s+\d+(?:,\d+)?$", line):
                pending_title.append(line)

    return events


def main() -> None:
    all_results: list[dict[str, object]] = []
    all_events: list[dict[str, object]] = []

    for path in sorted(SNAPSHOT.glob("*.pdf")):
        results, events = parse_current_pdf(path)
        all_results.extend(results)
        all_events.extend(events)
        print(f"{path.name}: {len(results)} resultados, {len(events)} eventos")

    results_df = pd.DataFrame(all_results).drop_duplicates(
        subset=["source_file", "posicao", "titulo_obra", "cpb"], keep="first"
    )
    events_df = pd.DataFrame(all_events).drop_duplicates(
        subset=[
            "source_file",
            "titulo_obra",
            "cpb",
            "ano_evento",
            "evento",
            "tipo_pontuacao",
            "pontos_evento",
        ],
        keep="first",
    )

    if not results_df.empty:
        results_df["ano_chamada"] = pd.to_numeric(results_df["ano_chamada"], errors="coerce").astype("Int64")
        results_df["posicao"] = pd.to_numeric(results_df["posicao"], errors="coerce").astype("Int64")
        results_df["pontuacao_final"] = pd.to_numeric(results_df["pontuacao_final"], errors="coerce")
        results_df["empresa_vocacionada"] = results_df["empresa_vocacionada"].astype("boolean")
        results_df = results_df.sort_values(["ano_chamada", "source_file", "posicao"], na_position="last")

    if not events_df.empty:
        events_df["ano_chamada"] = pd.to_numeric(events_df["ano_chamada"], errors="coerce").astype("Int64")
        events_df["posicao_obra"] = pd.to_numeric(events_df["posicao_obra"], errors="coerce").astype("Int64")
        events_df["ano_evento"] = pd.to_numeric(events_df["ano_evento"], errors="coerce").astype("Int64")
        events_df["pontos_evento"] = pd.to_numeric(events_df["pontos_evento"], errors="coerce")
        events_df["evento_internacional_estimado"] = events_df["evento_internacional_estimado"].astype("boolean")
        events_df = events_df.sort_values(
            ["ano_chamada", "titulo_obra", "ano_evento", "evento"],
            na_position="last",
        )

    write_parquet(results_df, "fsa_atas_resultados", OUT)
    results_df.to_csv(OUT / "fsa_atas_resultados.csv", index=False, encoding="utf-8")
    print(f"fsa_atas_resultados.csv  {len(results_df)} linhas")

    write_parquet(events_df, "fsa_atas_festivais", OUT)
    events_df.to_csv(OUT / "fsa_atas_festivais.csv", index=False, encoding="utf-8")
    print(f"fsa_atas_festivais.csv  {len(events_df)} linhas")


if __name__ == "__main__":
    main()
