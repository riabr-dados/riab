# Arquitetura — RIAB
# Repositorio Independente do Audiovisual Brasileiro

> Hub de inteligencia de dados do audiovisual brasileiro e internacional.
> Dados brutos preservados, dados tratados acessiveis, consulta livre.
> Custo de hospedagem: zero.

---

## Identidade

| | |
|---|---|
| **Nome completo** | Repositorio Independente do Audiovisual Brasileiro |
| **Sigla** | RIAB |
| **Slug GitHub** | `riab` (ou manter `dados-audiovisual-br`) |
| **Slug HF (org)** | `riabr-dados` |
| **Dominio futuro** | riab.org / riab.dev (opcional, GitHub Pages como padrao) |

---

## Diagrama Geral

```
                     RIAB — Repositorio Independente do Audiovisual Brasileiro

  +---------------------------------------------------------------------------+
  |                                                                           |
  |   FONTES OFICIAIS           GITHUB (este repo)          HUGGING FACE      |
  |   ~~~~~~~~~~~~~~~           ~~~~~~~~~~~~~~~~~~          ~~~~~~~~~~~~      |
  |                                                                           |
  |   ANCINE                    catalog/                    riabr-dados/riab    |
  |   CNC (Franca)       +---> datasets.yaml                (dataset repo)   |
  |   BFI (UK)            |     sources.yaml                                  |
  |   INCAA (Argentina)   |     schemas/*.yaml              raw/              |
  |   ACAU (Uruguai)      |                                  ancine-obras/    |
  |   IBGE                |    pipelines/                    ancine-fsa/      |
  |   Lumiere/EU          |     extract/*.py                 cnc-visas/       |
  |                       |     transform/*.py               ...              |
  |                       |     upload_hf.py                                  |
  |                       |                                 cleaned/          |
  |   GitHub Actions      |    .github/workflows/            obras.parquet    |
  |   (cron semanal) -----+     update.yml                   bilheteria.parq  |
  |                       |     deploy.yml                   fomento.parquet  |
  |                       |                                  agentes.parquet  |
  |                       |    portal/        GitHub          mercado_int.parq |
  |                       +--> src/       --> Pages           ...              |
  |                            astro.config                                   |
  |                                                                           |
  +---------------------------------------------------------------------------+

  USUARIO FINAL:
    Browser  --> portal (GitHub Pages) --> preview, busca, download
    Python   --> import duckdb; duckdb.sql("SELECT * FROM 'hf://riabr-dados/riab/cleaned/obras.parquet'")
    R        --> arrow::read_parquet("hf://riabr-dados/riab/cleaned/obras.parquet")
    CLI      --> huggingface-cli download riabr-dados/riab cleaned/obras.parquet
```

---

## Camadas de Dados

### 1. Raw (dados brutos)
**Local:** `hf://riabr-dados/riab/raw/{slug-dataset}/`

Exatamente como veio da fonte oficial. Nenhuma alteracao.
Preserva encoding original, formato original (CSV, XLSX, XLS, ODS, PDF).

Cada subpasta corresponde a um dataset do catalogo:
```
raw/
  ancine-obras-nao-publicitarias/
    obras-nao-pub-brasileiras-2002.csv
    obras-nao-pub-brasileiras-2003.csv
    ...
    obras-nao-pub-brasileiras-2026.csv
  ancine-fsa-projetos/
    projetos-fsa.csv
  ancine-bilheteria-consolidada/
    bilheteria_brasileira_consolidada.xlsx
  cnc-visas-exploitation/
    visas-exploitation-1945-2025.csv
  ...
```

Versionamento: cada commit no HF e um snapshot datado.
O historico Git do HF substitui a estrutura `snapshots/YYYY-MM-DD/`.

### 2. Cleaned (dados tratados)
**Local:** `hf://riabr-dados/riab/cleaned/`

Dados consolidados por **tema** (nao por fonte), em Parquet:

| Arquivo | Descricao | Fontes |
|---------|-----------|--------|
| `obras.parquet` | Registro de obras audiovisuais brasileiras | ancine-obras-nao-publicitarias |
| `diretores.parquet` | Vinculos obra-diretor | ancine-diretores-obras |
| `produtores.parquet` | Vinculos obra-produtora | ancine-produtores-obras |
| `bilheteria_domestica.parquet` | Bilheteria no mercado brasileiro | ancine-bilheteria-consolidada, ancine-bilheteria-agregada |
| `bilheteria_europa.parquet` | Filmes brasileiros em salas europeias | lumiere-cinemas-europa |
| `vod_europa.parquet` | Filmes brasileiros em VoD europeu | lumiere-vod-europa |
| `fomento_fsa.parquet` | Projetos apoiados pelo FSA | ancine-fsa-projetos |
| `renuncia_fiscal.parquet` | Projetos com renuncia fiscal | ancine-renuncia-fiscal |
| `agentes_economicos.parquet` | Empresas do setor audiovisual | ancine-agentes-economicos |
| `preco_ingresso.parquet` | Serie historica do preco do ingresso | ancine-preco-medio-ingresso |
| `deflator_ipca.parquet` | Indice deflator para valores monetarios | ibge-deflator-ipca |
| `cnc_visas.parquet` | Filmes com visa de exploracao na Franca | cnc-visas-exploitation |
| `cnc_frequentacao.parquet` | Frequentacao de salas na Franca | cnc-frequentation-salles |
| `cnc_estabelecimentos.parquet` | Cinemas ativos na Franca | cnc-etablissements |
| `cnc_filmes_milhao.parquet` | Filmes com +1M entradas na Franca | cnc-films-million-entrees |
| `cnc_dados_internacionais.parquet` | Indicadores comparativos entre paises | cnc-donnees-internationales |
| `cnc_filmes_aprovados.parquet` | Filmes com agrement do CNC | cnc-films-agrees |
| `cnc_audiencia_tv.parquet` | Audiencia de filmes na TV francesa | cnc-audience-television |
| `cnc_filmes_tv.parquet` | Filmes na TV francesa | cnc-films-television |
| `cnc_exportacao.parquet` | Exportacao de programas audiovisuais | cnc-exportacao-programas |
| `cnc_geografia.parquet` | Geografia do cinema na Franca | cnc-geographie-cinema |
| `cnc_vod_publico.parquet` | Publico de VoD na Franca | cnc-public-vod |
| `cnc_vod_refs.parquet` | Catalogo de titulos em VoD | cnc-referencias-ativas-vod |
| `cnc_vod_consumo.parquet` | Consumo domestico de VoD | cnc-consumo-vod |
| `cnc_parque.parquet` | Parque cinematografico frances | cnc-parc-cinematographique |
| `cnc_financiamento_tv.parquet` | Financiamento da TV francesa | cnc-financement-television |
| `cnc_distribuicao.parquet` | Distribuicao em salas na Franca | cnc-distribution-salles |
| `cnc_publico_filmes.parquet` | Perfil do publico de cinema | cnc-public-films |
| `incaa_setor.parquet` | Setor audiovisual argentino | incaa-sector-audiovisual |
| `bfi_anuario.parquet` | Anuario estatistico do BFI | bfi-statistical-yearbook-2023 |
| `acau_apoios.parquet` | Apoios audiovisuais do Uruguai | acau-uruguay-apoios |

Convencoes do Parquet tratado:
- Encoding: UTF-8
- Colunas: snake_case, sem acentos
- Tipos: explicitamente definidos no schema YAML
- Datas: formato ISO 8601
- Valores monetarios: float64, moeda indicada em coluna separada
- Nulos: null nativo do Parquet (nao string vazia)
- Chaves de linkagem: obra_id, agente_id quando aplicavel

### 3. Obras Completa (tabela consolidada)
**Local:** `hf://riabr-dados/riab/cleaned/obras_completa.parquet`

Join de obras + diretores + produtores + bilheteria domestica + bilheteria europa.
Uma linha por obra, com colunas agregadas:

```
obra_id | titulo | ano | genero | duracao | diretor | produtora |
publico_br | renda_br | admissoes_eu | paises_eu | fsa_valor | ...
```

Essa e a tabela de maior valor para analistas e pesquisadores.

---

## Catalogo (catalog/)

### datasets.yaml
Fonte unica de verdade. Tudo e gerado a partir dele.

```yaml
datasets:
  - slug: ancine-obras-nao-publicitarias
    title: Obras Nao Publicitarias
    description: >
      Registro oficial de obras audiovisuais brasileiras nao publicitarias.
      Um arquivo CSV por ano de registro (2002-2026), totalizando ~61.360 obras.
    source:
      institution: ANCINE / SAV
      country: BR
      url: https://dados.ancine.gov.br/dados-abertos/
      license: dados-abertos-gov-br
    status: ativo
    coverage: "2002-2026"
    tags: [cinema, obras, registro, brasil, ancine]
    raw:
      path: ancine-obras-nao-publicitarias/
      format: csv
      encoding: latin-1
      delimiter: ";"
      files: 25
      size_bytes: 16000000
    cleaned:
      tables:
        - obras
    related:
      - ancine-diretores-obras
      - ancine-produtores-obras
      - ancine-bilheteria-consolidada
```

### sources.yaml
```yaml
sources:
  - id: ancine
    name: ANCINE — Agencia Nacional do Cinema
    country: BR
    url: https://www.gov.br/ancine/
    data_portal: https://dados.ancine.gov.br/dados-abertos/
    license: dados-abertos-gov-br
    notes: >
      Portal de dados abertos com CSVs periodicamente atualizados.
      Sistema OCA (Observatorio do Cinema e do Audiovisual) intermitente.

  - id: cnc
    name: CNC — Centre National du Cinema et de l'Image Animee
    country: FR
    url: https://www.cnc.fr/
    data_portal: https://www.cnc.fr/professionnels/etudes-et-rapports/statistiques/
    license: licence-ouverte-etalab
    notes: Dados abertos sob Licence Ouverte Etalab 2.0.

  - id: bfi
    name: BFI — British Film Institute
    country: UK
    url: https://www.bfi.org.uk/
    license: open-government-licence

  - id: incaa
    name: INCAA — Instituto Nacional de Cine y Artes Audiovisuales
    country: AR
    url: https://www.argentina.gob.ar/incaa
    license: datos-abiertos-ar

  - id: acau
    name: ACAU — Agencia del Cine y el Audiovisual del Uruguay
    country: UY
    url: https://www.acau.gub.uy/
    license: datos-abiertos-uy

  - id: lumiere
    name: Observatoire Europeen de l'Audiovisuel — Lumiere
    country: EU
    url: https://lumiere.obs.coe.int/
    license: free-access

  - id: ibge
    name: IBGE — Instituto Brasileiro de Geografia e Estatistica
    country: BR
    url: https://www.ibge.gov.br/
    license: dados-abertos-gov-br
```

### schemas/*.yaml
Um arquivo por tabela Parquet, com colunas tipadas, descricoes e chaves.
(Ver exemplos na secao "Schemas Tipados" da proposta anterior.)

---

## Estrutura do Repositorio GitHub

```
riab/  (ou dados-audiovisual-br/)
|
+-- catalog/
|   +-- datasets.yaml          # Catalogo central
|   +-- sources.yaml           # Fontes oficiais
|   +-- schemas/
|       +-- obras.yaml
|       +-- bilheteria_domestica.yaml
|       +-- fomento_fsa.yaml
|       +-- ...
|
+-- pipelines/
|   +-- extract/               # Baixar dados das fontes
|   |   +-- ancine_obras.py
|   |   +-- ancine_fsa.py
|   |   +-- cnc_visas.py
|   |   +-- ...
|   +-- transform/             # Limpar e converter para Parquet
|   |   +-- clean_obras.py
|   |   +-- clean_bilheteria.py
|   |   +-- clean_fsa.py
|   |   +-- ...
|   +-- consolidate/           # Gerar tabelas consolidadas (joins)
|   |   +-- obras_completa.py
|   +-- upload_hf.py           # Publicar raw e cleaned no HF
|   +-- generate_previews.py   # Gerar JSONs de preview para o portal
|   +-- requirements.txt
|
+-- portal/                    # Astro (static site)
|   +-- src/
|   |   +-- layouts/
|   |   |   +-- Base.astro
|   |   +-- pages/
|   |   |   +-- index.astro           # Home: catalogo, stats, busca
|   |   |   +-- dataset/
|   |   |   |   +-- [slug].astro      # Pagina por dataset (dinamica)
|   |   |   +-- consulta.astro        # Guia de como consultar (snippets)
|   |   |   +-- sobre.astro           # Manifesto + metodologia
|   |   +-- components/
|   |   |   +-- DatasetCard.astro
|   |   |   +-- DataTable.astro
|   |   |   +-- SearchBar.astro
|   |   |   +-- CodeSnippet.astro
|   |   |   +-- StatsBar.astro
|   |   |   +-- FilterChips.astro
|   |   +-- content/
|   |   |   +-- datasets/             # Gerado a partir de catalog/datasets.yaml
|   |   +-- styles/
|   |       +-- global.css
|   +-- public/
|   |   +-- api/
|   |   |   +-- catalog.json          # Catalogo em JSON (gerado no build)
|   |   |   +-- preview/
|   |   |       +-- obras.json         # Primeiras 500 linhas
|   |   |       +-- bilheteria.json
|   |   |       +-- ...
|   |   +-- favicon.svg
|   +-- astro.config.mjs
|   +-- package.json
|
+-- .github/
|   +-- workflows/
|   |   +-- update-data.yml           # Cron: extract + transform + upload HF
|   |   +-- deploy-portal.yml         # Build Astro + deploy GitHub Pages
|   +-- ISSUE_TEMPLATE/
|       +-- novo-dataset.yml
|       +-- bug.yml
|
+-- datasets/                  # LEGADO — sera migrado para HF
|   +-- (pastas atuais, removidas apos migracao)
|
+-- MANIFESTO.md
+-- README.md
+-- LICENSE-code               # MIT
+-- LICENSE-data               # CC-BY-4.0
+-- .gitignore
```

---

## Portal Astro — Paginas

### Home (index.astro)
- Header: "RIAB — Repositorio Independente do Audiovisual Brasileiro"
- Barra de stats: N datasets, N paises, N fontes, N registros totais
- Busca full-text (Fuse.js client-side)
- Filtros: pais, fonte, formato, status
- Grid de cards (um por dataset), gerado do YAML
- Secao "Como usar" com snippets Python/R/DuckDB

### Pagina de Dataset ([slug].astro)
- Titulo, descricao, fonte, status, cobertura temporal
- Badges: pais, formato, tags
- Preview interativo: tabela com as primeiras N linhas do Parquet
- Download: links diretos para raw (HF) e cleaned (HF)
- Snippets de codigo para carregar o dado
- Schema: colunas, tipos, descricoes
- Datasets relacionados

### Consulta (consulta.astro)
- Tutorial passo a passo: Python, R, DuckDB, CLI
- Exemplos reais com os dados do RIAB
- Link para notebooks de exemplo

### Sobre (sobre.astro)
- Manifesto (adaptado)
- Metodologia
- Governanca
- Como contribuir

---

## Fluxo de Dados Detalhado

```
1. EXTRACT (pipelines/extract/)
   Fonte oficial --[download]--> raw/{slug}/arquivo.csv
   - Scripts Python por fonte
   - Detecta se houve mudanca (hash)
   - Se mudou: commit no HF com mensagem datada

2. TRANSFORM (pipelines/transform/)
   raw/{slug}/arquivo.csv --[pandas/pyarrow]--> cleaned/{tema}.parquet
   - Padroniza encoding para UTF-8
   - Converte colunas para tipos corretos
   - Normaliza nomes de colunas (snake_case, sem acento)
   - Trata nulos
   - Valida contra schema YAML

3. CONSOLIDATE (pipelines/consolidate/)
   cleaned/obras.parquet + cleaned/diretores.parquet + ... --> cleaned/obras_completa.parquet
   - Joins por obra_id
   - Agrega metricas (publico total, renda total, paises de exibicao)

4. PREVIEW (pipelines/generate_previews.py)
   cleaned/{tema}.parquet --> portal/public/api/preview/{tema}.json
   - Primeiras 500 linhas em JSON compacto
   - Usado pelo portal para preview interativo

5. PUBLISH
   - Upload para HF (upload_hf.py)
   - Build Astro + deploy GitHub Pages (GitHub Actions)
```

---

## GitHub Actions

### update-data.yml (cron: semanal)
```yaml
name: Atualizar dados
on:
  schedule:
    - cron: '0 6 * * 1'  # segunda 6h UTC
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r pipelines/requirements.txt
      - run: python pipelines/extract/run_all.py
      - run: python pipelines/transform/run_all.py
      - run: python pipelines/consolidate/obras_completa.py
      - run: python pipelines/generate_previews.py
      - run: python pipelines/upload_hf.py
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "dados: atualiza previews [bot]"
          file_pattern: portal/public/api/preview/*.json
```

### deploy-portal.yml
```yaml
name: Deploy portal
on:
  push:
    branches: [main]
    paths: ['portal/**', 'catalog/**']
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - run: cd portal && npm ci && npm run build
      - uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: portal/dist
```

---

## Consulta Programatica

### Python (pandas)
```python
import pandas as pd
df = pd.read_parquet(
    "hf://datasets/riabr-dados/riab/cleaned/obras.parquet"
)
print(df.head())
```

### Python (DuckDB — SQL direto)
```python
import duckdb
conn = duckdb.connect()
conn.sql("""
    INSTALL httpfs; LOAD httpfs;
    SELECT titulo_original, ano_producao, genero,
           COUNT(*) as total
    FROM 'https://huggingface.co/datasets/riabr-dados/riab/resolve/main/cleaned/obras.parquet'
    WHERE ano_producao >= 2020
    GROUP BY ALL
    ORDER BY total DESC
    LIMIT 20
""").show()
```

### Python (Hugging Face datasets)
```python
from datasets import load_dataset
ds = load_dataset("riabr-dados/riab", data_files="cleaned/obras.parquet")
df = ds["train"].to_pandas()
```

### R
```r
library(arrow)
obras <- read_parquet(
  "https://huggingface.co/datasets/riabr-dados/riab/resolve/main/cleaned/obras.parquet"
)
head(obras)
```

### CLI
```bash
# Baixar um Parquet especifico
huggingface-cli download riabr-dados/riab cleaned/obras.parquet

# Baixar todos os dados tratados
huggingface-cli download riabr-dados/riab --include "cleaned/*.parquet"

# Baixar dados brutos de uma fonte
huggingface-cli download riabr-dados/riab --include "raw/ancine-obras-nao-publicitarias/*"
```

---

## Decisoes Travadas

| Decisao | Escolha | Motivo |
|---------|---------|--------|
| HF org ou pessoal | **Org** (`riabr-dados`) | Nao depende de uma pessoa |
| HF mono ou multi-repo | **Monorepo** | Simples, um unico ponto de acesso |
| Granularidade Parquet | **Por tema** | O valor esta na consolidacao |
| Portal framework | **Astro** | Gera paginas por dataset, SSG puro, rapido |
| Nome | **Repositorio Independente do Audiovisual Brasileiro (RIAB)** | Identidade propria |

---

## Migracao da Arquitetura Atual

### O que permanece
- MANIFESTO.md (atualizado com principio de dados tratados)
- LICENSE-code, LICENSE-data
- .gitignore

### O que migra
- `datasets/*/snapshots/` --> HF `raw/`
- `docs/index.html` + `docs/data.js` --> `portal/` (Astro)
- `scripts/gerar_preview.py` --> `pipelines/generate_previews.py`
- `schemas/` --> `catalog/schemas/`

### O que e novo
- `catalog/datasets.yaml` e `sources.yaml`
- `pipelines/extract/`, `transform/`, `consolidate/`
- `portal/` (Astro)
- `.github/workflows/`
- Dados Parquet no HF

### O que e removido (apos migracao)
- `datasets/` (dados vao pro HF)
- `docs/index.html`, `docs/data.js` (portal novo no Astro)
- `scripts/gerar_preview.py` (substituido)
