# RIAB — Repositorio Independente do Audiovisual Brasileiro

Hub de inteligencia de dados do audiovisual brasileiro e internacional.
Dados brutos preservados. Dados tratados em 12 Parquets, livres para consulta.
Custo de hospedagem: zero.

**Portal:** https://riabr-dados.github.io/riab
**Dados (Hugging Face):** https://huggingface.co/datasets/riabr-dados/riab
**Manifesto:** [MANIFESTO.md](MANIFESTO.md)

---

## O que esta aqui

| Camada | Onde | O que |
|--------|------|-------|
| **Raw** | `hf://riabr-dados/riab/raw/` | Dados brutos intocados das fontes oficiais |
| **Cleaned** | `hf://riabr-dados/riab/cleaned/` | Dados tratados em Parquet, tipados, UTF-8 |
| **Catalogo** | `catalog/` | YAML declarativo com 65 datasets |
| **Pipelines** | `pipelines/` | Scripts de transformacao e upload |
| **Portal** | `portal/` | Site Astro gerado automaticamente do catalogo |

## Como usar os dados

### Python — DuckDB (sem baixar nada)

```python
import duckdb
conn = duckdb.connect()
conn.sql("INSTALL httpfs; LOAD httpfs;")
conn.sql("""
    SELECT titulo_original, ano_producao_inicial, tipo_obra
    FROM 'hf://datasets/riabr-dados/riab/cleaned/obras.parquet'
    WHERE tipo_obra = 'CINEMATOGRAFICA'
    ORDER BY ano_producao_inicial DESC
    LIMIT 20
""").show()
```

### Python — pandas

```python
import pandas as pd
df = pd.read_parquet("hf://datasets/riabr-dados/riab/cleaned/obras.parquet")
print(df.head())
```

### R

```r
library(arrow)
obras <- read_parquet("hf://datasets/riabr-dados/riab/cleaned/obras.parquet")
head(obras)
```

### CLI — baixar tudo

```bash
huggingface-cli download riabr-dados/riab \
  --repo-type dataset \
  --include "cleaned/*.parquet"
```

## Estrutura do repositorio

```
riab/
  catalog/
    datasets.yaml      # Catalogo central (65 datasets)
    sources.yaml       # Fontes oficiais (ANCINE, CNC, BFI, INCAA, ACAU, IBGE, Lumiere)
    schemas/           # Schema de cada tabela Parquet (colunas, tipos, chaves)
  pipelines/
    transform/         # Limpeza e conversao para Parquet
    extract/           # Coleta das fontes (em desenvolvimento)
    consolidate/       # Joins entre tabelas
    upload_hf.py       # Publica no Hugging Face
    requirements.txt
  portal/              # Site Astro (GitHub Pages)
  .github/workflows/
    deploy-portal.yml  # Build e deploy automatico
    update-data.yml    # Coleta e transformacao semanal (cron)
  datasets/            # Legado: snapshots brutos (migrando para HF)
  MANIFESTO.md
  LICENSE-code         # MIT
  LICENSE-data         # CC-BY-4.0
```

## Datasets — 65 de 6 paises

Brasil (ANCINE, IBGE, Lumiere), Franca (CNC), Argentina (INCAA),
Reino Unido (BFI), Uruguai (ACAU).

Ver catalogo completo com descricoes e schemas em: https://riabr-dados.github.io/riab/datasets/

## Licenca

- **Dados:** [CC-BY-4.0](LICENSE-data) — use livremente, cite a fonte original
- **Codigo:** [MIT](LICENSE-code)
- **Fontes originais:** cada dataset tem sua propria licenca — ver `catalog/sources.yaml`

Os dados brutos sao publicos por forca da Lei de Acesso a Informacao (Lei 12.527/2011)
e legislacoes equivalentes nos demais paises. Este repositorio acrescenta organizacao,
metadados, versionamento e acessibilidade — nao altera o conteudo das fontes.

## Contribuindo

1. Abra uma [issue](https://github.com/riabr-dados/riab/issues/new/choose) sugerindo novo dataset
2. Submeta um PR com pipeline de extracao ou transformacao
3. Consulte `catalog/datasets.yaml` como referencia de formato

## Citacao

> RIAB — Repositorio Independente do Audiovisual Brasileiro.
> Snapshot de [DATA]. Dados originais: [FONTE].
> Disponivel em: https://huggingface.co/datasets/riabr-dados/riab
