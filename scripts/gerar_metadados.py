"""Gera datapackage.json, README.md e source.txt para cada dataset.

Lê uma configuração inline com os metadados de cada fonte e produz:
- datasets/<slug>/datapackage.json (current, aponta para snapshot mais recente)
- datasets/<slug>/README.md
- datasets/<slug>/snapshots/<data>/datapackage.json (específico do snapshot)
- datasets/<slug>/snapshots/<data>/source.txt

Idempotente: rodar de novo regenera arquivos.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = ROOT / "datasets"
SNAPSHOT_DATE = "2026-05-19"
NOW_ISO = f"{SNAPSHOT_DATE}T00:00:00Z"

CATALOG = [
    {
        "slug": "ancine-fsa-projetos",
        "title": "ANCINE / FSA — Projetos do Fundo Setorial do Audiovisual",
        "description": (
            "Lista de projetos contratados pelo Fundo Setorial do Audiovisual (FSA), "
            "incluindo categoria de chamada, valores investidos, agentes e situação."
        ),
        "source_title": "ANCINE — Fundo Setorial do Audiovisual",
        "source_url": "https://fsa.ancine.gov.br",
        "status": "ativo",
        "notes": "Atualizado periodicamente. Espelhado a partir do projeto fomento-audiovisual.",
        "files": ["projetos-fsa.csv"],
    },
    {
        "slug": "ancine-renuncia-fiscal",
        "title": "ANCINE — Projetos com renúncia fiscal (Art. 1º, 1ºA, 3º, 3ºA)",
        "description": (
            "Projetos audiovisuais aprovados via mecanismos de renúncia fiscal "
            "federais (Lei do Audiovisual e Lei Rouanet audiovisual)."
        ),
        "source_title": "ANCINE",
        "source_url": "https://www.ancine.gov.br",
        "status": "ativo",
        "notes": "Cobre projetos Art. 1º, 1ºA, 3º e 3ºA.",
        "files": ["projetos-com-renuncia-fiscal.csv"],
    },
    {
        "slug": "ancine-obras-nao-publicitarias",
        "title": "ANCINE / SAV — Obras audiovisuais não publicitárias brasileiras (2002–2026)",
        "description": (
            "Registro oficial de obras audiovisuais não publicitárias brasileiras "
            "registradas na ANCINE, com um arquivo CSV por ano de registro."
        ),
        "source_title": "ANCINE — Superintendência de Análise de Mercado",
        "source_url": "https://dados.gov.br/dataset?q=ancine+obras",
        "status": "ativo",
        "notes": "25 arquivos anuais, 2002 a 2026. Estrutura consistente entre anos.",
        "files": None,  # todos os CSVs da pasta
    },
    {
        "slug": "ancine-agentes-economicos",
        "title": "ANCINE — Agentes econômicos regulares",
        "description": (
            "Cadastro de agentes econômicos regulares do mercado audiovisual brasileiro: "
            "produtoras, distribuidoras, exibidoras."
        ),
        "source_title": "ANCINE",
        "source_url": "https://dados.gov.br/dataset?q=ancine+agentes",
        "status": "ativo",
        "notes": "",
        "files": ["agentes-economicos-regulares.csv"],
    },
    {
        "slug": "ancine-diretores-obras",
        "title": "ANCINE / SAV — Diretores de obras não publicitárias brasileiras",
        "description": "Vínculo entre obras audiovisuais brasileiras e seus diretores.",
        "source_title": "ANCINE — Superintendência de Análise de Mercado",
        "source_url": "https://dados.gov.br/dataset?q=ancine+diretores",
        "status": "ativo",
        "notes": "",
        "files": ["diretores-de-obras-nao-publicitarias-brasileiras.csv"],
    },
    {
        "slug": "ancine-produtores-obras",
        "title": "ANCINE / SAV — Produtores de obras não publicitárias brasileiras",
        "description": "Vínculo entre obras audiovisuais brasileiras e suas produtoras.",
        "source_title": "ANCINE — Superintendência de Análise de Mercado",
        "source_url": "https://dados.gov.br/dataset?q=ancine+produtores",
        "status": "ativo",
        "notes": "",
        "files": ["produtores-de-obras-nao-publicitarias-brasileiras.csv"],
    },
    {
        "slug": "ancine-bilheteria-consolidada",
        "title": "ANCINE / SADIS — Bilheteria brasileira consolidada",
        "description": (
            "Consolidação de bilheteria de filmes brasileiros em salas de cinema, "
            "compilada a partir do SADIS (Sistema ANCINE de Dados de Interesse Setorial)."
        ),
        "source_title": "ANCINE — SADIS",
        "source_url": "https://www.ancine.gov.br",
        "status": "ativo",
        "notes": "Formato XLSX com múltiplas abas.",
        "files": ["bilheteria_brasileira_consolidada.xlsx"],
    },
    {
        "slug": "ancine-bilheteria-agregada-filme-ano",
        "title": "ANCINE / OCA — Bilheteria agregada por filme e ano",
        "description": "Tabela agregada de público e renda por filme e ano de exibição.",
        "source_title": "ANCINE — Observatório do Cinema e do Audiovisual",
        "source_url": "https://oca.ancine.gov.br",
        "status": "intermitente",
        "notes": (
            "OCA tem histórico de quedas e instabilidade. Espelhar esta fonte é "
            "uma das principais motivações deste repositório."
        ),
        "files": ["por_filme_ano.csv"],
    },
    {
        "slug": "ancine-preco-medio-ingresso",
        "title": "ANCINE — Preço médio do ingresso (série histórica)",
        "description": "Série histórica de preço médio do ingresso de cinema no Brasil.",
        "source_title": "ANCINE — OCA",
        "source_url": "https://oca.ancine.gov.br",
        "status": "intermitente",
        "notes": "Série usada para deflação de bilheterias antigas.",
        "files": ["preco_medio_ingresso_ancine.csv"],
    },
    {
        "slug": "ancine-atas-fsa",
        "title": "ANCINE / FSA — Atas oficiais de resultados (PDFs)",
        "description": (
            "Atas oficiais de resultados de chamadas públicas do FSA, em PDF, "
            "incluindo PRODAV 07 (2014, 2015, 2017) e Desempenho Artístico (2018, 2024)."
        ),
        "source_title": "ANCINE — FSA",
        "source_url": "https://fsa.ancine.gov.br/quem-somos/resultados",
        "status": "ativo",
        "notes": "Documentos oficiais em PDF. Fonte primária de seleção e investimento.",
        "files": None,
    },
    {
        "slug": "lumiere-cinemas-europa",
        "title": "Lumiere — Filmes brasileiros em salas de cinema na Europa",
        "description": (
            "Resultado de consulta ao banco Lumiere do Observatório Europeu do "
            "Audiovisual sobre admissões (espectadores) de filmes brasileiros em "
            "salas de cinema em países europeus."
        ),
        "source_title": "European Audiovisual Observatory — Lumiere database",
        "source_url": "https://lumiere.obs.coe.int",
        "status": "ativo",
        "notes": "Snapshot resultante de busca por país de produção = Brasil.",
        "files": ["lumiere_search.xlsx"],
    },
    {
        "slug": "lumiere-vod-europa",
        "title": "Lumiere VOD — Filmes brasileiros em serviços VOD na Europa",
        "description": (
            "Resultado de consulta ao Lumiere VOD do Observatório Europeu sobre "
            "disponibilidade de filmes brasileiros em serviços VOD europeus."
        ),
        "source_title": "European Audiovisual Observatory — Lumiere VOD",
        "source_url": "https://lumiere.obs.coe.int/vod",
        "status": "ativo",
        "notes": "Snapshot resultante de busca por país de produção = Brasil.",
        "files": ["lumiere_vod_search.xlsx"],
    },
    {
        "slug": "ibge-deflator-ipca",
        "title": "IBGE — Deflator IPCA (base 2024)",
        "description": (
            "Série do Índice Nacional de Preços ao Consumidor Amplo (IPCA) usada "
            "como deflator para conversão de valores monetários à base 2024."
        ),
        "source_title": "IBGE — Sistema Nacional de Índices de Preços ao Consumidor",
        "source_url": "https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos/9256-indice-nacional-de-precos-ao-consumidor-amplo.html",
        "status": "ativo",
        "notes": "Série mensal, base 2024.",
        "files": ["deflator_ipca_base2024.csv"],
    },
    # ── CNC France ──────────────────────────────────────────────────────────
    {
        "slug": "cnc-visas-exploitation",
        "title": "CNC — Visas d'exploitation cinématographique (1945–2025)",
        "description": (
            "Lista completa dos visas d'exploitation cinématographique emitidos pelo CNC "
            "desde 1945, cobrindo todos os filmes autorizados para distribuição em salas "
            "na França. Mais de 95.000 registros."
        ),
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/liste-des-visas-dexploitations-cinematographiques-delivres-de-1945-a-2025",
        "status": "ativo",
        "notes": "Licence Ouverte / Open Licence 2.0. Atualizado em nov/2025. CSV ~12MB.",
        "files": None,
    },
    {
        "slug": "cnc-frequentation-salles",
        "title": "CNC — Fréquentation des salles de cinéma",
        "description": (
            "Frequentação das salas de cinema na França: entradas por ano, mês, semana e dia, "
            "sessões e receitas."
        ),
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/frequentation-des-salles-de-cinema",
        "status": "ativo",
        "notes": "Licence Ouverte. Dataset mais baixado do CNC (34K downloads).",
        "files": None,
    },
    {
        "slug": "cnc-etablissements",
        "title": "CNC — Liste des établissements cinématographiques actifs",
        "description": (
            "Cadastro dos estabelecimentos cinematográficos ativos na França: cinemas, "
            "salas, localização, capacidade."
        ),
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/liste-des-etablissements-cinematographiques-actifs-1",
        "status": "ativo",
        "notes": "Licence Ouverte. Atualizado em mai/2026.",
        "files": None,
    },
    {
        "slug": "cnc-films-million-entrees",
        "title": "CNC — Films ayant réalisé plus d'un million d'entrées",
        "description": (
            "Lista de todos os filmes que ultrapassaram 1 milhão de espectadores nas "
            "salas francesas, com bilheteria e detalhes."
        ),
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/films-ayant-realise-plus-dun-million-dentrees",
        "status": "ativo",
        "notes": "Licence Ouverte. 185K downloads — um dos mais populares do CNC.",
        "files": None,
    },
    {
        "slug": "cnc-donnees-internationales",
        "title": "CNC — Données internationales sur le cinéma",
        "description": (
            "Dados comparativos internacionais sobre o mercado cinematográfico: "
            "bilheteria, produção, frequentação e investimento em diversos países."
        ),
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/donnees-internationales-sur-le-cinema",
        "status": "ativo",
        "notes": "Licence Ouverte. Útil para comparação com dados brasileiros.",
        "files": None,
    },
    {
        "slug": "cnc-films-agrees",
        "title": "CNC — Liste des films cinématographiques agréés",
        "description": (
            "Lista dos filmes cinématográficos aprovados (agréés) pelo CNC para fins "
            "de apoio e qualificação. Inclui primeiros filmes de iniciativa francesa."
        ),
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/liste-des-films-cinematographiques-agrees",
        "status": "ativo",
        "notes": "Licence Ouverte. Atualizado em mar/2026.",
        "files": None,
    },
    {
        "slug": "cnc-audience-television",
        "title": "CNC — Audience de la télévision",
        "description": (
            "Duração de escuta da televisão e audiência das cadeias televisivas na França."
        ),
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/audience-de-la-television",
        "status": "ativo",
        "notes": "Licence Ouverte.",
        "files": None,
    },
    {
        "slug": "cnc-films-television",
        "title": "CNC — Films à la télévision",
        "description": "Dados sobre a difusão de filmes na televisão francesa.",
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/films-a-la-television",
        "status": "ativo",
        "notes": "Licence Ouverte.",
        "files": None,
    },
    {
        "slug": "cnc-exportacao-programas-audiovisuais",
        "title": "CNC — Exportation de programmes audiovisuels",
        "description": "Vendas de programas audiovisuais franceses ao exterior (exportação).",
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/exportation-de-programmes-audiovisuels",
        "status": "ativo",
        "notes": "Licence Ouverte.",
        "files": None,
    },
    {
        "slug": "cnc-geographie-cinema",
        "title": "CNC — Géographie du cinéma: équipement et fréquentation",
        "description": (
            "Equipamento e frequentação cinematográfica na França por região, departamento, "
            "commune e unité urbaine (4 arquivos de granularidade territorial diferente)."
        ),
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/geographie-du-cinema-equipement-et-frequentation",
        "status": "ativo",
        "notes": "Licence Ouverte. 4 arquivos: région, département, commune, unité urbaine.",
        "files": None,
    },
    {
        "slug": "cnc-public-vod",
        "title": "CNC — Public de la vidéo à la demande",
        "description": "Público consumidor de VoD na França: perfil, hábitos, plataformas.",
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/public-de-la-video-a-la-demande",
        "status": "ativo",
        "notes": "Licence Ouverte.",
        "files": None,
    },
    {
        "slug": "cnc-referencias-ativas-vod",
        "title": "CNC — Références actives en vidéo à la demande",
        "description": "Programas e referências ativos em plataformas de VoD na França.",
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/references-actives-en-video-a-la-demande",
        "status": "ativo",
        "notes": "Licence Ouverte.",
        "files": None,
    },
    {
        "slug": "cnc-consumo-vod",
        "title": "CNC — Consommation des ménages en vidéo à la demande",
        "description": "Consumo domiciliar de VoD na França: volume, receita e tendências.",
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/consommation-des-menages-en-video-a-la-demande",
        "status": "ativo",
        "notes": "Licence Ouverte. Atualizado em mai/2026.",
        "files": None,
    },
    {
        "slug": "cnc-parc-cinematographique",
        "title": "CNC — Parc cinématographique: données générales",
        "description": "Dados gerais sobre o parque cinematográfico francês: telas, complexos, salas.",
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/parc-cinematographique-donnees-generales",
        "status": "ativo",
        "notes": "Licence Ouverte.",
        "files": None,
    },
    {
        "slug": "cnc-financement-television",
        "title": "CNC — Financement de la télévision",
        "description": "Financiamento da televisão francesa: fontes, volumes, canais.",
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/financement-de-la-television",
        "status": "ativo",
        "notes": "Licence Ouverte.",
        "files": None,
    },
    {
        "slug": "cnc-distribution-salles",
        "title": "CNC — Distribution des films dans les salles de cinéma",
        "description": "Distribuição de filmes nas salas de cinema na França: títulos, distribuidoras, semanas.",
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/distribution-des-films-dans-les-salles-de-cinema",
        "status": "ativo",
        "notes": "Licence Ouverte.",
        "files": None,
    },
    {
        "slug": "cnc-public-films",
        "title": "CNC — Public des films",
        "description": "Perfil do público de filmes nas salas de cinema francesas: sexo, idade, frequência.",
        "source_title": "Centre national du cinéma et de l'image animée (CNC)",
        "source_url": "https://www.data.gouv.fr/datasets/public-des-films",
        "status": "ativo",
        "notes": "Licence Ouverte.",
        "files": None,
    },
    # ── INCAA Argentina ─────────────────────────────────────────────────────
    {
        "slug": "incaa-sector-audiovisual",
        "title": "INCAA / Argentina — Sector Audiovisual (2001–2023)",
        "description": (
            "Dados do setor audiovisual argentino: espectadores e receita por origem do filme, "
            "estrenos por origem, dados por provincia, participação de distribuidoras, "
            "postos de trabalho em longas-metragens e dados de TV por assinatura. "
            "Fontes: INCAA, SICA, ENACOM."
        ),
        "source_title": "Ministerio de Cultura de Argentina — Datos Abiertos de Cultura",
        "source_url": "https://datos.gob.ar/dataset/cultura-sector-audiovisual",
        "status": "ativo",
        "notes": "CC-BY 4.0. Série 2001-2023. 9 arquivos CSV temáticos.",
        "files": None,
    },
    # ── BFI UK ──────────────────────────────────────────────────────────────
    {
        "slug": "bfi-statistical-yearbook-2023",
        "title": "BFI — Statistical Yearbook 2023 (Reino Unido)",
        "description": (
            "Anuário estatístico do British Film Institute (BFI) para o mercado "
            "cinematográfico do Reino Unido: bilheteria, top filmes, UK no mundo, "
            "exibição, vídeo físico/digital, TV, mercado total, audiências, emprego, "
            "empresas, economia do setor. 15 arquivos ODS."
        ),
        "source_title": "British Film Institute (BFI)",
        "source_url": "https://www.bfi.org.uk/industry-data-insights/statistical-yearbook",
        "status": "ativo",
        "notes": "Open Government Licence v3.0. Dados de 2023 (publicados 2024).",
        "files": None,
    },
    # ── ACAU Uruguay ────────────────────────────────────────────────────────
    {
        "slug": "acau-uruguay-apoios-audiovisual",
        "title": "ACAU / Uruguay — Apoios e reembolsos a projetos audiovisuais (2013–2024)",
        "description": (
            "Fundos atribuídos pela Agência de Cinema e Audiovisual do Uruguai (ACAU) "
            "e suas antecessoras (ICAU, INCAU) a projetos audiovisuais uruguaios, "
            "incluindo valor adjudicado, executado, instrumento, fundo, formato, "
            "gênero, destino e situação do projeto."
        ),
        "source_title": "Agencia del Cine y el Audiovisual del Uruguay (ACAU)",
        "source_url": "https://catalogodatos.gub.uy/dataset/acau-fondos-de-acau",
        "status": "ativo",
        "notes": "Catálogo de Datos Abiertos do Uruguay. Dados 2013-2024. ~500KB.",
        "files": None,
    },
]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def guess_format(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower().lstrip(".")
    mediatype = {
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pdf": "application/pdf",
        "json": "application/json",
    }.get(suffix, "application/octet-stream")
    return suffix, mediatype


def build_resources(snapshot_dir: Path, allowed_files: list[str] | None) -> list[dict]:
    resources = []
    files = sorted(p for p in snapshot_dir.iterdir() if p.is_file() and p.name not in {"datapackage.json", "source.txt"})
    if allowed_files is not None:
        files = [p for p in files if p.name in allowed_files]
    for p in files:
        fmt, mediatype = guess_format(p)
        resources.append(
            {
                "name": p.stem.lower().replace("_", "-"),
                "path": str(p.relative_to(snapshot_dir.parent.parent)).replace("\\", "/"),
                "format": fmt,
                "mediatype": mediatype,
                "encoding": "utf-8" if fmt in {"csv", "json"} else "binary",
                "bytes": p.stat().st_size,
                "hash": sha256_of(p),
            }
        )
    return resources


def write_datapackage(dataset_dir: Path, entry: dict, snapshot_date: str) -> None:
    snapshot_dir = dataset_dir / "snapshots" / snapshot_date
    resources = build_resources(snapshot_dir, entry.get("files"))

    pkg = {
        "$schema": "https://specs.frictionlessdata.io/schemas/data-package.json",
        "name": entry["slug"],
        "title": entry["title"],
        "description": entry["description"],
        "version": snapshot_date.replace("-", "."),
        "created": NOW_ISO,
        "homepage": f"https://github.com/SEU-USUARIO/dados-audiovisual-br/tree/main/datasets/{entry['slug']}",
        "licenses": [
            {
                "name": "CC-BY-4.0",
                "title": "Creative Commons Attribution 4.0 International",
                "path": "https://creativecommons.org/licenses/by/4.0/",
            }
        ],
        "sources": [
            {
                "title": entry["source_title"],
                "path": entry["source_url"],
            }
        ],
        "contributors": [
            {
                "title": "dados-audiovisual-br",
                "role": "publisher",
                "path": "https://github.com/SEU-USUARIO/dados-audiovisual-br",
            }
        ],
        "status": {
            "value": entry["status"],
            "options": ["ativo", "intermitente", "alterado", "offline", "descontinuado"],
            "last_checked": snapshot_date,
            "notes": entry["notes"],
        },
        "collection": {
            "method": "manual",
            "script": None,
            "frequency": "ad-hoc",
        },
        "resources": resources,
        "snapshots": [
            {
                "date": snapshot_date,
                "path": f"snapshots/{snapshot_date}/",
                "source_url": entry["source_url"],
                "notes": "Snapshot inicial migrado do projeto fomento-audiovisual.",
            }
        ],
    }

    (dataset_dir / "datapackage.json").write_text(
        json.dumps(pkg, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (snapshot_dir / "datapackage.json").write_text(
        json.dumps(pkg, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    source_txt = (
        f"Dataset: {entry['title']}\n"
        f"Fonte oficial: {entry['source_title']}\n"
        f"URL: {entry['source_url']}\n"
        f"Data do snapshot: {snapshot_date}\n"
        f"Status na data: {entry['status']}\n"
        f"Coleta: manual, espelhamento do projeto fomento-audiovisual\n"
        f"Arquivos:\n" + "\n".join(f"  - {r['name']} ({r['bytes']} bytes, {r['hash']})" for r in resources)
        + "\n"
    )
    (snapshot_dir / "source.txt").write_text(source_txt, encoding="utf-8")


def write_readme(dataset_dir: Path, entry: dict, snapshot_date: str) -> None:
    snapshot_dir = dataset_dir / "snapshots" / snapshot_date
    files = sorted(p for p in snapshot_dir.iterdir() if p.is_file() and p.name not in {"datapackage.json", "source.txt"})
    file_list = "\n".join(f"- `{p.name}` ({p.stat().st_size:,} bytes)" for p in files)

    md = f"""# {entry['title']}

{entry['description']}

## Fonte oficial

- **Órgão**: {entry['source_title']}
- **URL viva**: <{entry['source_url']}>
- **Status na última verificação**: `{entry['status']}` ({snapshot_date})

{entry['notes']}

## Snapshots disponíveis

- [`{snapshot_date}`](snapshots/{snapshot_date}/) — snapshot inicial

## Arquivos no snapshot mais recente

{file_list}

Metadados completos (hash SHA256, schema, tamanho) em [`datapackage.json`](datapackage.json).

## Licença

Dados sob [CC-BY-4.0](../../LICENSE-data). Atribuição obrigatória à fonte original.
"""
    (dataset_dir / "README.md").write_text(md, encoding="utf-8")


def main() -> None:
    for entry in CATALOG:
        dataset_dir = DATASETS_DIR / entry["slug"]
        if not dataset_dir.exists():
            print(f"[skip] {entry['slug']} — diretório não existe ainda")
            continue
        snapshot_dir = dataset_dir / "snapshots" / SNAPSHOT_DATE
        if not snapshot_dir.exists():
            print(f"[skip] {entry['slug']} — snapshot {SNAPSHOT_DATE} não existe")
            continue
        write_datapackage(dataset_dir, entry, SNAPSHOT_DATE)
        write_readme(dataset_dir, entry, SNAPSHOT_DATE)
        print(f"[ok]   {entry['slug']}")


if __name__ == "__main__":
    main()
