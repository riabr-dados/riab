# Plano de Geração de Parquets — Sessões Codex

> Execute a partir da **raiz do repositório** com o venv ativado:
> `.venv\Scripts\python.exe pipelines\transform\SCRIPT.py`
>
> Após cada sessão: atualizar `catalog/datasets.yaml` + `pipelines/transform/run_all.py` + rodar `upload_hf.py`.

---

## Convenções obrigatórias

### Estrutura de todo script `clean_*.py`

```python
"""Transform: <fonte>
Saida: pipelines/output/cleaned/<tabela>.parquet
"""
import pandas as pd
from pathlib import Path
from common import latest_snapshot   # ou latest_snapshot_multi para multi-arquivo

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)
```

- `latest_snapshot(RAW / "slug-do-dataset")` → retorna `Path` para o snapshot mais recente
- Saída sempre em `OUT / "nome_tabela.parquet"` (snake_case, sem hífens)
- Print final: `print(f"nome_tabela.parquet  {len(df)} linhas")`

### Atualizar catálogo após cada script

Em `catalog/datasets.yaml`, no dataset correspondente:
```yaml
cleaned:
  tables: [nome_tabela]        # string simples — NÃO usar formato {name: ..., parquet: ...}
```

Para múltiplas tabelas por dataset:
```yaml
cleaned:
  tables: [tabela_a, tabela_b, tabela_c]
```

### Adicionar ao run_all.py

```python
SCRIPTS = [
    ...
    "pipelines/transform/clean_novo.py",   # adicionar aqui
]
```

### Upload HF após cada sessão

```bash
HF_TOKEN=hf_... python pipelines/upload_hf.py
```

---

## Estado atual (pré-sessões)

| Fonte | Parquets prontos |
|-------|-----------------|
| ANCINE/BR | 9 tabelas |
| IBGE/BR | 1 tabela |
| LUMIÈRE/EU | 2 tabelas |
| INCAA/AR | 9 tabelas |
| ACAU/UY | 1 tabela ✅ feito |
| **Total** | **22 tabelas** |

---

## Sessão 1 — CNC simples (9 datasets → 1 script)

**Script:** `pipelines/transform/clean_cnc_simples.py`

Todos os arquivos abaixo têm a mesma estrutura:
- Linhas 0–5: cabeçalho/navegação a ignorar
- Linha 6 (índice 6): nomes das colunas
- Linha 7+: dados
- Encoding: `latin-1` ou `utf-8` — testar com `pd.read_excel(..., header=6)`
- Sheets a ignorar: `Sommaire`, `Définitions`, `Sources`, `Index`

| Dataset slug | Arquivo raw | Sheet(s) de dados | Tabela output |
|---|---|---|---|
| `cnc-frequentation-salles` | `frequentation-salles.xlsx` | `freqciné`, `décompos`, `mois` | `cnc_frequentation_salles` (apenas `freqciné`) |
| `cnc-audience-television` | `audience-television.xlsx` | primeira sheet de dados | `cnc_audience_television` |
| `cnc-public-films` | `public-films.xlsx` | primeira sheet de dados | `cnc_public_films` |
| `cnc-public-vod` | `public-vod.xlsx` | primeira sheet de dados | `cnc_public_vod` |
| `cnc-consumo-vod` | `consumo-menages-vod.xlsx` | primeira sheet de dados | `cnc_consumo_vod` |
| `cnc-referencias-ativas-vod` | `referencias-ativas-vod.xlsx` | primeira sheet de dados | `cnc_referencias_ativas_vod` |
| `cnc-parc-cinematographique` | `parc-cinematographique.xlsx` | primeira sheet de dados | `cnc_parc_cinematographique` |
| `cnc-distribution-salles` | `distribution-films-salles.xlsx` | primeira sheet de dados | `cnc_distribution_salles` |
| `cnc-films-million-entrees` | `films-plus-million-entrees.xlsx` | sheets `2025`, `2024`, `2023`, ... (uma por ano) | `cnc_films_million_entrees` (concat de todos os anos) |

**Lógica para `cnc-films-million-entrees`** (sheets por ano):
```python
xls = pd.ExcelFile(path)
anos = [s for s in xls.sheet_names if s.strip().isdigit()]
dfs = []
for ano in anos:
    df = xls.parse(ano, header=6)
    df["ano"] = int(ano)
    dfs.append(df)
result = pd.concat(dfs, ignore_index=True)
```

**Normalização padrão de colunas CNC:**
```python
import unicodedata
def norm_col(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return s.strip().lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_").replace("'", "")
df.columns = [norm_col(c) for c in df.columns]
df = df.dropna(how="all").dropna(axis=1, how="all")
```

**Após sessão 1:** atualizar `datasets.yaml` para os 9 datasets acima e adicionar `clean_cnc_simples.py` ao `run_all.py`.

---

## Sessão 2 — CNC complexos (8 datasets → 2–3 scripts)

### 2a — `cnc-visas-exploitation` → `cnc_visas_exploitation`

**Script:** `pipelines/transform/clean_cnc_visas.py`

- Arquivo: `datasets/cnc-visas-exploitation/snapshots/LATEST/visas-exploitation-1945-2025.csv`
- Formato: CSV, separador `;`, encoding `utf-8-sig`, ~95.000 linhas
- Colunas esperadas: numero visa, titre, nationalite, distributeur, date, entrees, etc.
- Normalizar colunas com `norm_col()`, parsear datas, converter entrees para int

### 2b — `cnc-donnees-internationales` → `cnc_donnees_internationales`

**Script:** incluso em `clean_cnc_complexos.py`

- Arquivo: `donnees-internationales-cinema.xlsx`
- Estrutura: cada sheet = 1 país; colunas consistentes entre sheets
- Lógica: iterar sheets (exceto Sommaire/Définitions), ler com `header=6`, adicionar coluna `pays` = nome da sheet, concat

### 2c — `cnc-etablissements` → `cnc_etablissements`

- Arquivo: `etablissements-cinematographiques.xlsx`
- Uma única sheet de dados grande (~2,6 MB)
- Ler com `header=6`, normalizar colunas

### 2d — `cnc-films-agrees` → `cnc_films_agrees`

- Arquivo: `films-agrees-production.xlsx`
- Pode ter sheets por modalidade (produção / distribuição) — verificar
- Se múltiplas sheets: concat com coluna `modalite`

### 2e — `cnc-geographie-cinema` → 4 tabelas

**Script:** `pipelines/transform/clean_cnc_geographie.py`

- 4 arquivos no mesmo snapshot:
  - `geographie-par-commune.xlsx` → `cnc_geographie_commune`
  - `geographie-par-departement.xlsx` → `cnc_geographie_departement`
  - `geographie-par-region.xlsx` → `cnc_geographie_region`
  - `geographie-par-unite-urbaine.xlsx` → `cnc_geographie_urbain`
- Mesma lógica de header=6 para todos

### 2f — XLS antigos (3 datasets) → `clean_cnc_xls.py`

Usar `engine='xlrd'` (instalar se necessário: `pip install xlrd`):

| Dataset slug | Arquivo | Tabela output |
|---|---|---|
| `cnc-financement-television` | `financement-television.xls` | `cnc_financement_television` |
| `cnc-films-television` | `films-television.xls` | `cnc_films_television` |
| `cnc-exportacao-programas-audiovisuais` | `exportacao-programas-audiovisuais.xls` | `cnc_exportacao_programas` |

```python
df = pd.read_excel(path, header=6, engine="xlrd")
```

**Após sessão 2:** atualizar `datasets.yaml` para os 8 datasets CNC restantes.

---

## Sessão 3 — BFI lote 1 (4 datasets)

**Dependência:** `pip install odfpy` (já instalado no venv)

**Script:** `pipelines/transform/clean_bfi_1.py`

Todos os ODS estão em: `datasets/bfi-statistical-yearbook-2023/snapshots/LATEST/`

Estrutura dos ODS:
- Sheets `Index` e `F*` (figuras/gráficos): ignorar
- Sheets `T*` (tabelas): contêm dados
- Header variável por sheet — inspecionar com `header=None` para encontrar linha de início
- Estratégia: ler com `header=None`, identificar a linha onde há ≥3 células não-nulas como cabeçalho

```python
def find_header_row(df_raw, min_cols=3):
    for i, row in df_raw.iterrows():
        filled = row.dropna()
        if len(filled) >= min_cols and not str(filled.iloc[0]).startswith("Return"):
            return i
    return 0

def read_bfi_sheet(xls, sheet):
    raw = xls.parse(sheet, header=None)
    hrow = find_header_row(raw)
    df = xls.parse(sheet, header=hrow)
    df = df.dropna(how="all").dropna(axis=1, how="all")
    return df
```

| Arquivo ODS | Sheet(s) de dados | Tabela output |
|---|---|---|
| `uk-film-market.ods` | `T1`, `T2`, `T3` (concat ou primeira) | `bfi_uk_film_market` |
| `top-films-2023.ods` | `T1` (top 20 filmes) | `bfi_top_films_2023` |
| `uk-film-economy.ods` | `T1` | `bfi_uk_film_economy` |
| `box-office-2023.ods` | `T1`, `T2` (principais) | `bfi_box_office_2023` |

---

## Sessão 4 — BFI lote 2 (4 datasets)

**Script:** `pipelines/transform/clean_bfi_2.py`

| Arquivo ODS | Tabela output |
|---|---|
| `audiences.ods` | `bfi_audiences` |
| `exhibition.ods` | `bfi_exhibition` |
| `film-industry-employment.ods` | `bfi_emprego_industria` |
| `film-industry-companies.ods` | `bfi_empresas_industria` |

---

## Sessão 5 — BFI lote 3 (4 datasets)

**Script:** `pipelines/transform/clean_bfi_3.py`

| Arquivo ODS | Tabela output |
|---|---|
| `film-on-digital-video.ods` | `bfi_video_digital` |
| `film-on-physical-video.ods` | `bfi_video_fisico` |
| `film-on-television.ods` | `bfi_filmes_televisao` |
| `public-investment-in-film.ods` | `bfi_investimento_publico` |

---

## Sessão 6 — BFI lote 4 (3 datasets) + fechar

**Script:** `pipelines/transform/clean_bfi_4.py`

| Arquivo ODS | Tabela output |
|---|---|
| `screen-sector-certification.ods` | `bfi_certificacao_obras` |
| `uk-films-talent-worldwide.ods` | `bfi_talentos_mundo` |
| `film-education.ods` | `bfi_educacao_cinematografica` |

**Ao concluir sessão 6:**
1. Rodar `run_all.py` completo para validar todos os parquets
2. Rodar `upload_hf.py` com `HF_TOKEN`
3. Confirmar no portal `/explorar/` que todos os grupos aparecem

---

## Estado esperado ao final

| Fonte | Tabelas |
|-------|---------|
| ANCINE/BR | 9 |
| IBGE/BR | 1 |
| LUMIÈRE/EU | 2 |
| INCAA/AR | 9 |
| ACAU/UY | 1 |
| CNC/FR | 18 (9 simples + 5 complexos + 4 geographie/XLS) |
| BFI/UK | 15 |
| **Total** | **55** |

O explorador em `/explorar/` exibirá todos automaticamente via `catalog/datasets.yaml`.

---

## Checklist pós-sessão

- [ ] Script gerou parquet sem erro
- [ ] `catalog/datasets.yaml` atualizado com `cleaned.tables`
- [ ] Script adicionado a `run_all.py`
- [ ] `upload_hf.py` executado
- [ ] Página do dataset no portal mostra explorador SQL funcional
- [ ] `/explorar/` lista a nova tabela na sidebar
