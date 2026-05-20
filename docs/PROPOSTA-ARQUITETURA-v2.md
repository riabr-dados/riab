# Proposta de Arquitetura v2 — Hub de Inteligencia de Dados do Audiovisual

## Visao Geral

Transformar o repositorio de um **arquivo de snapshots** em um **hub de inteligencia de dados**,
inspirado no basedosdados.org, com dados brutos + dados tratados + camada de consulta,
usando apenas infraestrutura gratuita.

```
+------------------------------------------------------------------+
|                    INFRAESTRUTURA (custo zero)                    |
|                                                                   |
|  GitHub          Hugging Face          GitHub Pages               |
|  (codigo +       (datasets grandes     (portal web                |
|   metadados +     em Parquet/CSV,       estatico com               |
|   pipelines)      versionados,          busca, preview,            |
|                   ate 50 GB gratis)     documentacao)              |
+------------------------------------------------------------------+
```

---

## 1. Problema da arquitetura atual

| Aspecto | Hoje | Limitacao |
|---------|------|-----------|
| Armazenamento | CSVs/XLSX dentro do Git | GitHub limita arquivos a 100 MB; repo fica pesado |
| Formato | CSV latin-1, XLSX, XLS, ODS, PDF | Nao e queryavel; cada formato exige tratamento diferente |
| Transformacao | Nenhuma ("sem reinterpretacao") | Dados brutos sao inacessiveis para quem nao sabe limpar |
| Portal | HTML estatico com dados embutidos | data.js cresce com cada dataset; nao escala |
| API | Nenhuma | Impossivel consultar programaticamente |
| Catalogacao | Hardcoded no JS | Adicionar dataset exige editar HTML |

---

## 2. Nova Arquitetura Proposta

### Camada 1 — Dados Brutos (raw)
**Onde:** Hugging Face Dataset repo (`dados-audiovisual-br/raw`)

- Exatamente como vem da fonte (CSV, XLSX, PDF, ODS)
- Preserva o principio de "espelhar, nao substituir"
- Versionado pelo HF (cada commit = snapshot)
- Sem limite pratico de tamanho (50 GB gratis)
- Substitui a pasta `datasets/*/snapshots/` do GitHub

### Camada 2 — Dados Tratados (cleaned)
**Onde:** Hugging Face Dataset repo (`dados-audiovisual-br/cleaned`)

- Dados padronizados em **Parquet** (colunas tipadas, UTF-8, nomes normalizados)
- Um arquivo Parquet por tabela logica (ex: `obras.parquet`, `bilheteria.parquet`)
- Schema documentado e estavel
- Linkagem entre tabelas (obra_id como chave comum)
- **Isso e o diferencial**: acessibilidade real aos dados

### Camada 3 — Metadados e Catalogacao
**Onde:** GitHub (este repo)

```
dados-audiovisual-br/
  catalog/
    datasets.yaml           # Catalogo central: nome, descricao, fonte, tags, HF path
    sources.yaml            # Registro de fontes (ANCINE, CNC, BFI, etc.)
    schemas/
      obras.yaml            # Schema de cada tabela tratada
      bilheteria.yaml
      fomento.yaml
      ...
  pipelines/
    extract/                # Scripts que baixam dados das fontes
      ancine_obras.py
      ancine_fsa.py
      cnc_visas.py
      ...
    transform/              # Scripts que limpam e padronizam para Parquet
      clean_obras.py
      clean_bilheteria.py
      clean_fsa.py
      ...
    upload_hf.py            # Publica no Hugging Face
  .github/
    workflows/
      update_raw.yml        # Cron: baixa novos snapshots e envia ao HF
      update_cleaned.yml    # Cron: re-processa e publica Parquet
      deploy_portal.yml     # Build e deploy do portal no GitHub Pages
  portal/                   # Site estatico (GitHub Pages)
    index.html
    dataset/[slug].html     # Pagina por dataset (gerada no build)
    api/                    # "API" estatica: JSONs pre-gerados
      catalog.json
      preview/
        obras.json          # Primeiras 500 linhas em JSON
        bilheteria.json
        ...
  docs/
    guia-contribuicao.md
    dicionario-dados.md
    fontes.md
  README.md
  MANIFESTO.md
```

### Camada 4 — Portal Web (GitHub Pages)
**Onde:** GitHub Pages (gratis, dominio customizavel)

- Gerado estaticamente a partir de `catalog/datasets.yaml`
- Cada dataset tem pagina propria com:
  - Descricao e metadados
  - Preview interativo (tabela com busca/filtro/sort)
  - Links diretos para download (raw no HF)
  - Links para Parquet tratado (HF)
  - Snippet de codigo (Python/R) para carregar o dado
  - Historico de snapshots
- Busca client-side (lunr.js ou similar)
- Zero backend

### Camada 5 — Consulta Programatica
**Onde:** Hugging Face + DuckDB

Qualquer pessoa pode consultar os dados tratados diretamente:

```python
# Python — via Hugging Face datasets
from datasets import load_dataset
ds = load_dataset("dados-audiovisual-br/cleaned", "obras")
df = ds["train"].to_pandas()

# Python — via DuckDB direto do Parquet remoto
import duckdb
duckdb.sql("""
  SELECT titulo, ano, genero, COUNT(*) as n
  FROM 'hf://datasets/dados-audiovisual-br/cleaned/obras.parquet'
  GROUP BY titulo, ano, genero
  ORDER BY ano DESC
""")

# R
library(arrow)
df <- read_parquet("hf://datasets/dados-audiovisual-br/cleaned/obras.parquet")
```

Isso elimina a necessidade de API propria. O Hugging Face serve os Parquets via HTTP.

---

## 3. Fluxo de Dados

```
Fonte oficial          GitHub Actions          Hugging Face
(ANCINE, CNC, ...)     (cron semanal)          (storage)
       |                     |                      |
       |   1. extract/       |                      |
       +-------------------->|   2. push raw         |
                             +--------------------->| raw/
                             |                      |
                             |   3. transform/       |
                             +--------------------->| cleaned/
                             |                      |
                             |   4. build portal     |
                             +----> GitHub Pages
```

---

## 4. Catalogo Declarativo (datasets.yaml)

Cada dataset e descrito uma unica vez. O portal, os previews e a documentacao
sao todos gerados a partir deste arquivo:

```yaml
- slug: ancine-obras-nao-publicitarias
  title: Obras Nao Publicitarias
  description: >
    Registro oficial de obras audiovisuais brasileiras nao publicitarias.
    Um arquivo CSV por ano de registro.
  source:
    institution: ANCINE / SAV
    country: BR
    url: https://dados.ancine.gov.br/
    license: dados-abertos-gov-br
  status: ativo
  coverage: 2002-2026
  raw:
    hf_repo: dados-audiovisual-br/raw
    path: ancine-obras-nao-publicitarias/
    format: csv
    encoding: latin-1
    delimiter: ";"
  cleaned:
    hf_repo: dados-audiovisual-br/cleaned
    tables:
      - name: obras
        file: obras.parquet
        rows: 61360
        schema_ref: schemas/obras.yaml
  tags: [cinema, obras, registro, brasil]
  related: [ancine-diretores-obras, ancine-produtores-obras]
```

---

## 5. Schemas Tipados (schemas/obras.yaml)

```yaml
table: obras
description: Registro de obras audiovisuais brasileiras
columns:
  - name: obra_id
    type: string
    description: Identificador unico da obra (numero de registro ANCINE)
    primary_key: true
  - name: titulo_original
    type: string
    description: Titulo original da obra
  - name: titulo_brasil
    type: string
    description: Titulo no Brasil (quando diferente do original)
  - name: ano_producao
    type: int32
    description: Ano de producao
  - name: genero
    type: string
    description: Genero principal
    categories: [ficcao, documentario, animacao, experimental, ...]
  - name: duracao_minutos
    type: int32
    description: Duracao em minutos
  - name: situacao
    type: string
    description: Situacao do registro
foreign_keys:
  - column: obra_id
    references: diretores.obra_id
  - column: obra_id
    references: produtores.obra_id
```

---

## 6. O que muda no Manifesto

O principio "sem reinterpretacao" se aplica apenas a **camada raw**.
A camada cleaned e explicitamente uma transformacao documentada e reproduzivel:

| Principio atual | Como fica |
|-----------------|-----------|
| "Nao tratamos, nao limpamos" | Raw: intocado. Cleaned: tratado com scripts abertos e reproduziveis |
| "Dado entra como saiu da fonte" | Raw preserva isso. Cleaned agrega valor |
| Snapshots datados | Raw no HF e versionado por commit. Cleaned tem versao semantica |

---

## 7. Vantagens sobre basedosdados.org

| basedosdados.org | dados-audiovisual-br |
|------------------|----------------------|
| BigQuery (Google Cloud) | Hugging Face + DuckDB (zero custo) |
| Nicho generalista | Foco no audiovisual = profundidade |
| Depende de infra centralizada | Git + HF = descentralizado, forkavel |
| Contribuicao via PR no BigQuery | Contribuicao via PR no GitHub + HF |

---

## 8. Stack Tecnica

| Componente | Tecnologia | Custo |
|------------|------------|-------|
| Codigo e metadados | GitHub | Gratis |
| Storage de dados | Hugging Face Datasets | Gratis (ate 50 GB) |
| Portal web | GitHub Pages | Gratis |
| CI/CD | GitHub Actions | Gratis (2000 min/mes) |
| Processamento | Python + pandas + pyarrow | Gratis |
| Consulta | DuckDB + HF Hub | Gratis |
| Busca no portal | lunr.js (client-side) | Gratis |

---

## 9. Fases de Implementacao

### Fase 1 — Fundacao (semana 1-2)
- [ ] Criar org `dados-audiovisual-br` no Hugging Face
- [ ] Criar repos HF: `raw` e `cleaned`
- [ ] Migrar dados brutos atuais para HF `raw`
- [ ] Definir `catalog/datasets.yaml` com os 33 datasets existentes
- [ ] Criar pipeline de transform para 3 datasets-piloto:
      obras, bilheteria, fsa-projetos

### Fase 2 — Tratamento (semana 3-4)
- [ ] Pipelines de transform para todos os datasets CSV/XLSX
- [ ] Schemas tipados para cada tabela Parquet
- [ ] Linkagem obra_id entre tabelas (obras <-> diretores <-> produtores <-> bilheteria)
- [ ] Tabela consolidada `obras_completa.parquet` (join de todas)
- [ ] Upload automatizado para HF

### Fase 3 — Portal (semana 5-6)
- [ ] Redesign do portal a partir do YAML do catalogo
- [ ] Pagina individual por dataset
- [ ] Snippets de codigo (Python/R/DuckDB)
- [ ] Preview com primeiras N linhas do Parquet
- [ ] Busca full-text client-side
- [ ] Deploy via GitHub Pages

### Fase 4 — Automacao (semana 7-8)
- [ ] GitHub Actions para coleta periodica (extract)
- [ ] GitHub Actions para re-processamento (transform)
- [ ] GitHub Actions para deploy do portal
- [ ] Notificacoes de mudanca nas fontes

### Fase 5 — Comunidade
- [ ] Guia de contribuicao
- [ ] Template para adicionar novo dataset
- [ ] Issue templates
- [ ] Integracao com Zenodo (DOI)

---

## 10. Decisoes em Aberto (para discutir)

1. **Org vs. user no HF?**
   Criar `huggingface.co/dados-audiovisual-br` (org) ou usar conta pessoal?
   Recomendacao: org, para nao depender de uma pessoa.

2. **Monorepo vs. multi-repo no HF?**
   - Opcao A: Um unico dataset repo com subpastas (mais simples)
   - Opcao B: Um repo por dataset (mais modular, mas mais repos para manter)
   Recomendacao: Opcao A para comecar, migrar para B se escalar muito.

3. **Granularidade do Parquet?**
   - Opcao A: Um Parquet por "tabela logica" (obras, bilheteria, fomento...)
   - Opcao B: Um Parquet por dataset original (espelha 1:1)
   Recomendacao: Opcao A — o valor esta na consolidacao.

4. **Portal: framework ou vanilla?**
   - Opcao A: HTML/JS puro (como hoje, mas gerado)
   - Opcao B: Astro/11ty (static site generator)
   Recomendacao: Astro — gera paginas por dataset automaticamente a partir do YAML.

5. **Nome do projeto?**
   - `dados-audiovisual-br` (atual, focado no Brasil)
   - `dados-audiovisual` (sem sufixo, ja que inclui dados internacionais)
   - `hub-audiovisual` ou `cinedata`
   O escopo ja e internacional. Vale repensar o nome?
