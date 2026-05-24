"""
Gera docs/data.js com amostra de até 200 linhas de cada dataset.
Execute a partir da raiz do repositório: python scripts/gerar_preview.py
"""
import csv
import json
import os
import sys
import unicodedata

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

try:
    import xlrd
    HAS_XLRD = True
except ImportError:
    HAS_XLRD = False

SNAP = "snapshots/2026-05-19"
SAMPLE = 200

def fix(v):
    """Corrige mojibake latin-1/utf-8 em strings."""
    if v is None:
        return ""
    s = str(v).strip()
    try:
        return s.encode("latin-1").decode("utf-8")
    except Exception:
        return s

def safe(v):
    """Converte qualquer valor para string limpa."""
    if v is None:
        return ""
    if isinstance(v, float) and v != v:  # NaN
        return ""
    return str(v).strip()

def read_csv(path, enc="latin-1", delim=";"):
    try:
        with open(path, encoding=enc, errors="replace") as f:
            reader = csv.reader(f, delimiter=delim)
            rows = list(reader)
        if not rows:
            return [], []
        cols = [fix(c) for c in rows[0]]
        data = []
        for row in rows[1:]:
            data.append([fix(c) for c in row])
        return cols, data
    except Exception as e:
        return [], []

def read_xlsx(path, sheet=0):
    if not HAS_OPENPYXL:
        return [], []
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = list(wb.worksheets)[sheet]
        rows = []
        for row in ws.iter_rows(values_only=True):
            rows.append([safe(v) for v in row])
        wb.close()
        if not rows:
            return [], []
        # Find first non-empty header row
        header_idx = 0
        for i, row in enumerate(rows[:5]):
            if any(c for c in row):
                header_idx = i
                break
        cols = [fix(c) for c in rows[header_idx]]
        data = []
        for row in rows[header_idx + 1:]:
            if any(c for c in row):
                data.append([fix(c) for c in row])
        return cols, data
    except Exception as e:
        return [], []

def read_xls(path, sheet=0):
    if not HAS_XLRD:
        return [], []
    try:
        wb = xlrd.open_workbook(path)
        ws = wb.sheets()[sheet]
        rows = []
        for i in range(ws.nrows):
            rows.append([safe(ws.cell_value(i, j)) for j in range(ws.ncols)])
        if not rows:
            return [], []
        cols = [fix(c) for c in rows[0]]
        data = [[fix(c) for c in row] for row in rows[1:] if any(c for c in row)]
        return cols, data
    except Exception as e:
        return [], []

def dataset_entry(cols, data, note=None, filename=None):
    total = len(data)
    sample_data = data[:SAMPLE]
    return {
        "cols": cols,
        "rows": sample_data,
        "total": total,
        "sample": len(sample_data),
        "note": note,
        "file": filename
    }

def no_preview(reason):
    return {"cols": [], "rows": [], "total": 0, "sample": 0, "note": reason, "file": None}

# ── EXTRACTION CONFIG ───────────────────────────────────────

def extract_all(base="datasets"):
    previews = {}

    def snap(slug):
        return os.path.join(base, slug, SNAP)

    # ancine-fsa-projetos
    f = os.path.join(snap("ancine-fsa-projetos"), "projetos-fsa.csv")
    cols, data = read_csv(f, enc="latin-1")
    previews["ancine-fsa-projetos"] = dataset_entry(cols, data, filename="projetos-fsa.csv")

    # ancine-renuncia-fiscal
    f = os.path.join(snap("ancine-renuncia-fiscal"), "projetos-com-renuncia-fiscal.csv")
    cols, data = read_csv(f, enc="latin-1")
    previews["ancine-renuncia-fiscal"] = dataset_entry(cols, data, filename="projetos-com-renuncia-fiscal.csv")

    # ancine-obras-nao-publicitarias — usar 2025 (ano mais recente completo)
    f = os.path.join(snap("ancine-obras-nao-publicitarias"), "obras-nao-pub-brasileiras-2025.csv")
    cols, data = read_csv(f, enc="latin-1")
    note = "Exibindo amostra do arquivo 2025. Dataset completo: 25 arquivos anuais (2002–2026), ~61.360 obras."
    previews["ancine-obras-nao-publicitarias"] = dataset_entry(cols, data, note=note, filename="obras-nao-pub-brasileiras-2025.csv")

    # ancine-agentes-economicos
    f = os.path.join(snap("ancine-agentes-economicos"), "agentes-economicos-regulares.csv")
    cols, data = read_csv(f, enc="latin-1")
    previews["ancine-agentes-economicos"] = dataset_entry(cols, data, filename="agentes-economicos-regulares.csv")

    # ancine-diretores-obras
    f = os.path.join(snap("ancine-diretores-obras"), "diretores-de-obras-nao-publicitarias-brasileiras.csv")
    cols, data = read_csv(f, enc="latin-1")
    previews["ancine-diretores-obras"] = dataset_entry(cols, data, filename="diretores-de-obras-nao-publicitarias-brasileiras.csv")

    # ancine-produtores-obras
    f = os.path.join(snap("ancine-produtores-obras"), "produtores-de-obras-nao-publicitarias-brasileiras.csv")
    cols, data = read_csv(f, enc="latin-1")
    previews["ancine-produtores-obras"] = dataset_entry(cols, data, filename="produtores-de-obras-nao-publicitarias-brasileiras.csv")

    # ancine-bilheteria-consolidada
    f = os.path.join(snap("ancine-bilheteria-consolidada"), "bilheteria_brasileira_consolidada.xlsx")
    cols, data = read_xlsx(f)
    previews["ancine-bilheteria-consolidada"] = dataset_entry(cols, data, filename="bilheteria_brasileira_consolidada.xlsx")

    # ancine-bilheteria-agregada-filme-ano
    f = os.path.join(snap("ancine-bilheteria-agregada-filme-ano"), "por_filme_ano.csv")
    if not os.path.exists(f):
        # find any csv
        d = snap("ancine-bilheteria-agregada-filme-ano")
        csvs = [x for x in os.listdir(d) if x.endswith(".csv")]
        f = os.path.join(d, csvs[0]) if csvs else None
    if f and os.path.exists(f):
        cols, data = read_csv(f, enc="latin-1")
        previews["ancine-bilheteria-agregada-filme-ano"] = dataset_entry(cols, data, filename=os.path.basename(f))
    else:
        previews["ancine-bilheteria-agregada-filme-ano"] = no_preview("Arquivo CSV não encontrado no snapshot.")

    # ancine-preco-medio-ingresso
    f = os.path.join(snap("ancine-preco-medio-ingresso"), "preco_medio_ingresso_ancine.csv")
    if not os.path.exists(f):
        d = snap("ancine-preco-medio-ingresso")
        csvs = [x for x in os.listdir(d) if x.endswith(".csv")]
        f = os.path.join(d, csvs[0]) if csvs else None
    if f and os.path.exists(f):
        cols, data = read_csv(f, enc="latin-1")
        previews["ancine-preco-medio-ingresso"] = dataset_entry(cols, data, filename=os.path.basename(f))
    else:
        previews["ancine-preco-medio-ingresso"] = no_preview("Arquivo CSV não encontrado no snapshot.")

    # ancine-atas-fsa — resultados derivados dos PDFs
    f = os.path.join("pipelines", "output", "cleaned", "fsa_atas_resultados.csv")
    if os.path.exists(f):
        cols, data = read_csv(f, enc="utf-8", delim=",")
        note = "Amostra da tabela fsa_atas_resultados extraida dos PDFs oficiais."
        previews["ancine-atas-fsa"] = dataset_entry(cols, data, note=note, filename="fsa_atas_resultados.csv")
    else:
        previews["ancine-atas-fsa"] = no_preview("Parquet/CSV tratado ainda nao encontrado. Rode pipelines/transform/clean_atas_fsa.py.")

    # ancine-festivais-fsa — participacao brasileira em festivais, fonte brasileira
    f = os.path.join("pipelines", "output", "cleaned", "fsa_atas_festivais.csv")
    if os.path.exists(f):
        cols, data = read_csv(f, enc="utf-8", delim=",")
        note = "Amostra da tabela fsa_atas_festivais extraida dos PDFs oficiais; levantamento nao exaustivo."
        previews["ancine-festivais-fsa"] = dataset_entry(cols, data, note=note, filename="fsa_atas_festivais.csv")
    else:
        previews["ancine-festivais-fsa"] = no_preview("Parquet/CSV tratado ainda nao encontrado. Rode pipelines/transform/clean_atas_fsa.py.")

    cleaned_csv_previews = {
        "ancine-condecine-arrecadacao": (
            "condecine_arrecadacao.csv",
            "Amostra da tabela condecine_arrecadacao consolidada a partir do OCA Dados Financeiros.",
        ),
        "ancine-fomento-fluxos-financeiros": (
            "fomento_fluxos_financeiros.csv",
            "Amostra da tabela fomento_fluxos_financeiros; layouts heterogeneos preservam fonte_arquivo e titulo_publicacao.",
        ),
        "br-pib-audiovisual": (
            "pib_audiovisual_fontes.csv",
            "Inventario de fontes OCA para a futura tabela factual de PIB/valor adicionado audiovisual.",
        ),
        "br-rais-emprego-audiovisual": (
            "rais_emprego_audiovisual_fontes.csv",
            "Inventario de fontes OCA para a futura agregacao RAIS do audiovisual.",
        ),
        "br-comercio-exterior-servicos-audiovisuais": (
            "comercio_exterior_servicos_audiovisuais_fontes.csv",
            "Inventario de fontes OCA/SISCOSERV para comercio exterior de servicos audiovisuais.",
        ),
        "br-comex-bens-audiovisuais": (
            "comex_bens_audiovisuais_fontes.csv",
            "Inventario da fonte MDIC/Comex Stat para futura tabela factual de bens audiovisuais por NCM.",
        ),
        "br-embrafilme-historico-exibicao": (
            "embrafilme_exibicao_territorio_ano.csv",
            "Amostra da tabela Embrafilme extraida de PDFs tabulares do OCA.",
        ),
        "ancine-diversidade-audiovisual": (
            "diversidade_audiovisual_fontes.csv",
            "Inventario de fontes OCA para futura tabela factual de diversidade audiovisual.",
        ),
    }
    for slug, (filename, note) in cleaned_csv_previews.items():
        f = os.path.join("pipelines", "output", "cleaned", filename)
        if os.path.exists(f):
            cols, data = read_csv(f, enc="utf-8", delim=",")
            previews[slug] = dataset_entry(cols, data, note=note, filename=filename)
        else:
            previews[slug] = no_preview(f"CSV tratado {filename} ainda nao encontrado. Rode pipelines/transform/clean_oca_complementos.py.")

    # lumiere-cinemas-europa
    f = os.path.join(snap("lumiere-cinemas-europa"), "lumiere_search.xlsx")
    cols, data = read_xlsx(f)
    previews["lumiere-cinemas-europa"] = dataset_entry(cols, data, filename="lumiere_search.xlsx")

    # lumiere-vod-europa
    f = os.path.join(snap("lumiere-vod-europa"), "lumiere_vod_search.xlsx")
    cols, data = read_xlsx(f)
    previews["lumiere-vod-europa"] = dataset_entry(cols, data, filename="lumiere_vod_search.xlsx")

    # ibge-deflator-ipca
    d = snap("ibge-deflator-ipca")
    csvs = [x for x in os.listdir(d) if x.endswith(".csv")]
    if csvs:
        f = os.path.join(d, csvs[0])
        cols, data = read_csv(f, enc="utf-8")
        if not cols:
            cols, data = read_csv(f, enc="latin-1")
        previews["ibge-deflator-ipca"] = dataset_entry(cols, data, filename=csvs[0])
    else:
        previews["ibge-deflator-ipca"] = no_preview("CSV não encontrado.")

    # CNC XLSX datasets
    cnc_xlsx = {
        "cnc-frequentation-salles":         "frequentation-salles.xlsx",
        "cnc-etablissements":               "etablissements-cinematographiques.xlsx",
        "cnc-films-million-entrees":        "films-plus-million-entrees.xlsx",
        "cnc-donnees-internationales":      "donnees-internationales-cinema.xlsx",
        "cnc-films-agrees":                 "films-agrees-production.xlsx",
        "cnc-audience-television":          "audience-television.xlsx",
        "cnc-public-vod":                   "public-vod.xlsx",
        "cnc-referencias-ativas-vod":       "referencias-ativas-vod.xlsx",
        "cnc-consumo-vod":                  "consumo-menages-vod.xlsx",
        "cnc-parc-cinematographique":       "parc-cinematographique.xlsx",
        "cnc-distribution-salles":          "distribution-films-salles.xlsx",
        "cnc-public-films":                 "public-films.xlsx",
    }
    for slug, fname in cnc_xlsx.items():
        f = os.path.join(snap(slug), fname)
        if os.path.exists(f):
            cols, data = read_xlsx(f)
            previews[slug] = dataset_entry(cols, data, filename=fname)
        else:
            # try any xlsx in dir
            d = snap(slug)
            xlsxs = [x for x in os.listdir(d) if x.endswith(".xlsx")]
            if xlsxs:
                f = os.path.join(d, xlsxs[0])
                cols, data = read_xlsx(f)
                previews[slug] = dataset_entry(cols, data, filename=xlsxs[0])
            else:
                previews[slug] = no_preview("Arquivo XLSX não encontrado.")

    # cnc-geographie-cinema — usar primeiro arquivo (region)
    d = snap("cnc-geographie-cinema")
    xlsxs = sorted(x for x in os.listdir(d) if x.endswith(".xlsx"))
    if xlsxs:
        f = os.path.join(d, xlsxs[0])
        cols, data = read_xlsx(f)
        note = f"Exibindo amostra de {xlsxs[0]}. Dataset contém 4 arquivos (region, département, commune, UDA)."
        previews["cnc-geographie-cinema"] = dataset_entry(cols, data, note=note, filename=xlsxs[0])
    else:
        previews["cnc-geographie-cinema"] = no_preview("Arquivos XLSX não encontrados.")

    # CNC XLS datasets
    cnc_xls = {
        "cnc-films-television":                 "films-television.xls",
        "cnc-exportacao-programas-audiovisuais": "exportacao-programas-audiovisuais.xls",
        "cnc-financement-television":            "financement-television.xls",
    }
    for slug, fname in cnc_xls.items():
        f = os.path.join(snap(slug), fname)
        if os.path.exists(f) and HAS_XLRD:
            cols, data = read_xls(f)
            previews[slug] = dataset_entry(cols, data, filename=fname)
        else:
            xls = [x for x in os.listdir(snap(slug)) if x.endswith(".xls")]
            if xls and HAS_XLRD:
                f = os.path.join(snap(slug), xls[0])
                cols, data = read_xls(f)
                previews[slug] = dataset_entry(cols, data, filename=xls[0])
            else:
                previews[slug] = no_preview("Formato XLS — instale xlrd para visualização." if not HAS_XLRD else "Arquivo não encontrado.")

    # cnc-visas-exploitation — CSV grande, usar utf-8 com BOM
    f = os.path.join(snap("cnc-visas-exploitation"), "visas-exploitation-1945-2025.csv")
    cols, data = read_csv(f, enc="utf-8-sig", delim=";")
    if not cols:
        cols, data = read_csv(f, enc="utf-8", delim=";")
    note = f"Exibindo amostra de {SAMPLE} de ~95.000+ registros. Arquivo completo: 12 MB."
    previews["cnc-visas-exploitation"] = dataset_entry(cols, data, note=note, filename="visas-exploitation-1945-2025.csv")

    # incaa-sector-audiovisual — primeiro CSV (espectadores)
    d = snap("incaa-sector-audiovisual")
    csvs = sorted(x for x in os.listdir(d) if x.endswith(".csv"))
    if csvs:
        f = os.path.join(d, csvs[0])
        cols, data = read_csv(f, enc="utf-8")
        if not cols:
            cols, data = read_csv(f, enc="latin-1")
        note = f"Exibindo '{csvs[0]}'. Dataset contém {len(csvs)} arquivos CSV (espectadores, recaudación, estrenos, empleo, etc.)."
        previews["incaa-sector-audiovisual"] = dataset_entry(cols, data, note=note, filename=csvs[0])
    else:
        previews["incaa-sector-audiovisual"] = no_preview("CSV não encontrado.")

    # bfi-statistical-yearbook-2023 — ODS sem suporte
    previews["bfi-statistical-yearbook-2023"] = no_preview(
        "Formato ODS — instale odfpy para visualização. Dataset contém 15 arquivos (bilheteria, exibição, emprego, etc.)."
    )

    # acau-uruguay-apoios-audiovisual
    d = snap("acau-uruguay-apoios-audiovisual")
    csvs = [x for x in os.listdir(d) if x.endswith(".csv")]
    if csvs:
        f = os.path.join(d, csvs[0])
        cols, data = read_csv(f, enc="utf-8")
        if not cols:
            cols, data = read_csv(f, enc="latin-1")
        previews["acau-uruguay-apoios-audiovisual"] = dataset_entry(cols, data, filename=csvs[0])
    else:
        previews["acau-uruguay-apoios-audiovisual"] = no_preview("CSV não encontrado.")

    return previews

if __name__ == "__main__":
    os.makedirs("docs", exist_ok=True)
    print("Extraindo amostras de dados...", flush=True)
    previews = extract_all()

    ok = sum(1 for v in previews.values() if v["total"] > 0)
    skip = len(previews) - ok
    print(f"  {ok} datasets com dados / {skip} sem preview tabular")

    js = "window.DATASET_PREVIEWS = " + json.dumps(previews, ensure_ascii=False, separators=(",", ":")) + ";\n"

    out = "docs/data.js"
    with open(out, "w", encoding="utf-8") as f:
        f.write(js)

    size_kb = os.path.getsize(out) / 1024
    print(f"  docs/data.js gerado ({size_kb:.0f} KB)")

    for slug, v in previews.items():
        note_short = (v["note"] or "")[:60]
        status = f"{v['sample']}/{v['total']} linhas" if v["total"] > 0 else f"SEM PREVIEW — {note_short}"
        print(f"  {slug}: {status}")
