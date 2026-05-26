# Bilheteria — Série Histórica Complementar

Série histórica de bilheteria/exibição brasileira **complementar** às duas
oficiais já publicadas no projeto:

- `ancine-bilheteria-consolidada` (SADIS, top filmes BR 2009→)
- `ancine-bilheteria-agregada-filme-ano` (OCA/SCB, por filme/ano 2014→)

Esta tabela **não substitui nem corrige** as duas oficiais. Existe para
cobrir lacunas anteriores a 2009/2014 e para oferecer um recorte agregado
útil em análises de série longa.

## Fontes incluídas (versão atual)

| Fonte | Período | Origem | Granularidade nesta tabela |
|---|---|---|---|
| Embrafilme — histórico de exibição | 1982-1987 | OCA / ANCINE (PDFs reprocessados) | Brasil + por UF + por região + faixa de habitantes, por origem (nac/estr/total) |
| IBGE Século XX — cinema | 1971, 1974, 1980, 1984, 1985 | IBGE (Anuários, .xls) | Brasil + por UF, indicadores agregados |
| OCA — Listagem de Filmes Brasileiros Lançados 1995-2024 | 1995-2024 | OCA / ANCINE (XLSX oficial) | Agregada por ano (só Brasil) |

**Cross-validation:** 1984 e 1985 têm dupla cobertura (Embrafilme + IBGE) —
útil para validar série temporal.

## Fontes pendentes (próximas iterações)

Documentadas em [FONTES.md](../../FONTES.md):

- **IBGE Século XX** — restantes ~158 tabelas .xls 1937-1988
  (censura, cine-teatros, capitais, anos intermediários).
- **IBGE MUNIC** — presença de salas por município, 1999+.
- **Cinemateca Brasileira / Filmografia** — ~56 mil títulos desde 1897.

## Schema

Long format: `(ano, origem_filme, territorio_tipo, territorio_nome, uf,
indicador, valor, unidade_original, fonte, fonte_documento, confiabilidade)`.

Indicadores cobertos hoje: `publico`, `renda_brl_nominal`,
`lugares_oferecidos`, `cinemas_cadastrados`, `cinemas_com_arrecadacao`,
`filmes_lancados`.

Ver [`catalog/schemas/bilheteria_historica_complementar.yaml`](../../catalog/schemas/bilheteria_historica_complementar.yaml).

## Build

```bash
.venv/Scripts/python.exe pipelines/transform/clean_bilheteria_historica_complementar.py
```

Pré-requisito: `pipelines/output/cleaned/embrafilme_exibicao_territorio_ano.parquet`
deve existir (gerado por `clean_oca_complementos.py`).

## Limitações conhecidas

- A linha OCA 1995-2024 agrega público **acumulado** por filme (cobertura
  histórica acumulada até a data de publicação do levantamento, ABR/2025).
  Não é estritamente o público anual do ano de lançamento — filmes mais
  antigos podem ter público acumulado em anos posteriores ao lançamento.
- IBGE Século XX 1971/1974 cobre **apenas cinemas 35mm/70mm** nesta extração;
  os PDFs originais também trazem cine-teatros (ainda não parseados).
- IBGE não desagrega público por origem do filme — só os contadores de
  filmes nacionais vs estrangeiros estão separados.
- Embrafilme cobre apenas cinemas que reportavam ao órgão; IBGE faz censo
  mais amplo. Para 1985, IBGE indica 99.1M espectadores; Embrafilme indica
  91.3M (nac+estr). Diferença típica de ~8%.
