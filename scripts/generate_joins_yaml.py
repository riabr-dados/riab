"""
Gera catalog/joins.yaml a partir dos schemas + portal/src/data/grafo.json.

Para cada tabela visivel do catalogo:
 - lista colunas reais
 - detecta chaves canonicas (CPB, CNPJ, SALIC, ROE, ...) por regex
 - marca confidence (high/medium) + funcao de normalizacao recomendada

Tambem deriva "bridges" (pares de tabelas que compartilham >=1 chave forte)
a partir do grafo gerado para /conexoes.

Uso: .venv/Scripts/python.exe scripts/generate_joins_yaml.py
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = ROOT / "catalog" / "schemas"
CATALOG = ROOT / "catalog" / "datasets.yaml"
SOURCES = ROOT / "catalog" / "sources.yaml"
GRAFO = ROOT / "portal" / "src" / "data" / "grafo.json"
OUT = ROOT / "catalog" / "joins.yaml"


KEY_RULES = [
    ("CPB",           r"(?:^|_)cpb(?:_|$)|^codigo_obra$|^numero_cpb$", None,          "high"),
    ("CPB",           r"registro_obra(?!_estrang)",                    None,          "medium"),
    ("CRT",           r"(?:^|_)crt(?:_|$)|^numero_crt$",                None,          "high"),
    ("ROE",           r"(?:^|_)roe(?:_|$)|registro_obra_estrangeira",   None,          "high"),
    ("CNPJ",          r"cnpj",                                          "digits_only", "high"),
    ("CPF",           r"(?:^|_)cpf(?:_|$)",                             "digits_only", "high"),
    ("SALIC",         r"^salic$|^pronac$|^numero_pronac$",              None,          "high"),
    ("SALIC",         r"salic|pronac",                                  None,          "medium"),
    ("CONTRATO",      r"contrato|numero_contrato",                      None,          "medium"),
    ("PROCESSO",      r"^processo$|^numero_processo$|^n_processo$",      None,          "high"),
    ("REG_ANCINE",    r"registro_ancine",                               None,          "high"),
    ("TITULO_OBRA",   r"^titulo$|^titulo_obra$|^titulo_original$|^titulo_filme$|^title$", "titulo_norm", "high"),
    ("TITULO_OBRA",   r"nome_obra|titre",                               "titulo_norm", "medium"),
    ("PRODUTORA",     r"^produtora$|^nome_produtora$|^razao_social_produtora$", "titulo_norm", "high"),
    ("PRODUTORA",     r"produtora_principal|^produtor$",                "titulo_norm", "medium"),
    ("DISTRIBUIDORA", r"^distribuidora$|^nome_distribuidora$",          "titulo_norm", "high"),
    ("EXIBIDORA",     r"^exibidora$|^nome_exibidora$",                  "titulo_norm", "high"),
    ("GRUPO_ECON",    r"grupo_economico",                               None,          "high"),
    ("PAIS",          r"^pais$|^pais_origem$|^country$|^iso3$",         None,          "high"),
    ("PAIS",          r"^pais_|nationalite|^pays$|nation_region",        None,          "medium"),
    ("UF",            r"^uf$|^estado$|^uf_requerente$|^cod_uf$",         None,          "high"),
    ("MUNICIPIO",     r"^municipio$|^codigo_municipio$|^cod_munic$|^cidade$", None,    "high"),
    ("MUNICIPIO",     r"commune|ville",                                  None,          "medium"),
    ("ANO",           r"^ano$|^ano_referencia$|^ano_lancamento$|^ano_producao$|^year$|^annee$", None, "high"),
    ("CNAE",          r"^cnae$|^cnae_classe$|^cnae_subclasse$",          None,          "high"),
    ("CNAE",          r"cnae|codigo_atividade",                          None,          "medium"),
    ("GENERO",        r"^genero$|^genre$",                              None,          "high"),
    ("CLASSIFICACAO", r"classificacao_(?:obra|agente)",                  None,          "high"),
]

# Keys that are "strong" identifiers (vs dimensional like ANO/PAIS/UF)
STRONG_KEYS = {"CPB","CRT","ROE","SALIC","CONTRATO","PROCESSO","REG_ANCINE","CNPJ","CPF","GRUPO_ECON","CNAE","PRODUTORA","DISTRIBUIDORA","EXIBIDORA"}


def load_catalog_visible():
    catalog = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    sources = {s["id"]: s for s in yaml.safe_load(SOURCES.read_text(encoding="utf-8"))["sources"]}
    table_to_ds = {}
    for d in catalog["datasets"]:
        if d.get("hidden"):
            continue
        for t in d.get("cleaned", {}).get("tables") or []:
            name = t if isinstance(t, str) else t.get("name")
            table_to_ds[name] = d
    return table_to_ds, sources


def load_columns():
    return {
        sf.stem: [str(c["name"]) for c in yaml.safe_load(sf.read_text(encoding="utf-8")).get("columns", [])]
        for sf in SCHEMAS_DIR.glob("*.yaml")
    }


def detect_keys(cols):
    """For one table, returns list of {key, col, confidence, normalize} entries."""
    matched = []
    seen_pairs = set()
    for col in cols:
        cl = col.lower()
        for key, pat, norm, conf in KEY_RULES:
            if (col, key) in seen_pairs:
                continue
            if re.search(pat, cl):
                row = {"key": key, "col": col, "confidence": conf}
                if norm:
                    row["normalize"] = norm
                matched.append(row)
                seen_pairs.add((col, key))
                break
    matched.sort(key=lambda r: (r["key"], r["col"]))
    return matched


def main():
    table_to_ds, sources = load_catalog_visible()
    tables_cols = load_columns()

    # Filter columns to visible tables only
    tables_cols = {t: cols for t, cols in tables_cols.items() if t in table_to_ds}

    registry = []
    for table in sorted(tables_cols):
        ds = table_to_ds[table]
        src = sources.get(ds.get("source_id"))
        country = (src or {}).get("country", "??")
        exposes = detect_keys(tables_cols[table])
        registry.append({
            "table": table,
            "_dataset": ds["slug"],
            "_country": country,
            "_source": ds.get("source_id"),
            "_title": ds.get("title") or table,
            "_columns_count": len(tables_cols[table]),
            "exposes": exposes,
        })

    # Bridges: derive from grafo.json
    bridges = []
    if GRAFO.exists():
        grafo = json.loads(GRAFO.read_text(encoding="utf-8"))
        for e in grafo["edges"]:
            d = e["data"]
            bridges.append({
                "tables": [d["source"], d["target"]],
                "via_keys": d["keys"],
                "top_key": d["top_key"],
                "weight": d["weight"],
                "_origin": "auto-detected",
            })
        bridges.sort(key=lambda b: (-b["weight"], b["tables"][0]))

    out = {
        "version": "0.1.0",
        "_meta": {
            "generated_at": "2026-05-27",
            "description": (
                "Key registry: para cada tabela do RIDAB, declara que chaves canonicas ela expoe "
                "e por quais colunas. Usado pelo /transformar e /conexoes para sugerir junções automaticas."
            ),
            "how_to_use": [
                "1. Cada entrada em 'tables' lista as chaves expostas pela tabela.",
                "2. 'confidence': high (regex bate o nome canonico) / medium (regex parcial) / curated (revisado humano).",
                "3. 'normalize': titulo_norm = lower + strip non-alphanumeric. digits_only = strip nao-digitos. null = sem normalizacao.",
                "4. 'bridges' lista pares de tabelas com as chaves em comum, derivado automaticamente do grafo.",
                "5. Para corrigir uma detecao errada: marque confidence: curated + ajuste manualmente. Esse script preserva entradas curated (TODO).",
            ],
            "key_glossary": {
                "CPB": "Certificado de Produto Brasileiro — identificador unico de obra audiovisual brasileira (ANCINE)",
                "CRT": "Certificado de Registro de Titulo — emitido para obras publicitarias e nao publicitarias",
                "ROE": "Registro de Obra Estrangeira — equivalente ao CPB para obras estrangeiras distribuidas no BR",
                "CNPJ": "Cadastro Nacional de Pessoa Juridica — identificador empresarial BR",
                "CPF": "Cadastro de Pessoa Fisica",
                "SALIC": "Numero do projeto cultural na Lei Rouanet / Pronac / SALIC",
                "CONTRATO": "Numero de contrato administrativo",
                "PROCESSO": "Numero de processo administrativo",
                "REG_ANCINE": "Registro de agente economico na ANCINE",
                "TITULO_OBRA": "Titulo da obra (junção fuzzy via normalizacao)",
                "PRODUTORA": "Nome de produtora (junção fuzzy)",
                "DISTRIBUIDORA": "Nome de distribuidora (junção fuzzy)",
                "EXIBIDORA": "Nome de exibidora (junção fuzzy)",
                "GRUPO_ECON": "Nome de grupo economico",
                "PAIS": "Pais (ISO ou nome) — dimensao compartilhada",
                "UF": "Unidade Federativa BR",
                "MUNICIPIO": "Municipio (nome ou codigo IBGE)",
                "ANO": "Ano de referencia (dimensao temporal)",
                "CNAE": "Classificacao Nacional de Atividades Economicas",
                "GENERO": "Genero da obra",
                "CLASSIFICACAO": "Classificacao indicativa ou classificacao de agente",
            },
        },
        "tables": registry,
        "bridges": bridges,
    }

    class IndentDumper(yaml.SafeDumper):
        def increase_indent(self, flow=False, indentless=False):
            return super().increase_indent(flow, False)

    OUT.write_text(
        yaml.dump(out, allow_unicode=True, sort_keys=False, default_flow_style=False, Dumper=IndentDumper, width=140),
        encoding="utf-8",
    )

    print(f"OK: {len(registry)} tabelas, {len(bridges)} pares-ponte gravados em {OUT.relative_to(ROOT)}")

    key_counts = Counter()
    for r in registry:
        for e in r["exposes"]:
            key_counts[e["key"]] += 1
    print("\nOcorrencias de cada chave (entre todas as tabelas):")
    for k, c in key_counts.most_common():
        marker = "*" if k in STRONG_KEYS else " "
        print(f"  {marker} {k:<15} {c:>4}")

    weak_only = []
    for r in registry:
        keys = {e["key"] for e in r["exposes"]}
        if not (keys & STRONG_KEYS):
            weak_only.append((r["table"], sorted(keys)))
    print(f"\nTabelas sem chave forte (so dimensoes ou fuzzy): {len(weak_only)}")
    for t, ks in weak_only[:15]:
        print(f"  {t:<55} {ks}")
    if len(weak_only) > 15:
        print(f"  ... e mais {len(weak_only) - 15}")


if __name__ == "__main__":
    sys.exit(main() or 0)
