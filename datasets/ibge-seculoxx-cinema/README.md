# IBGE Século XX — Cinema

Tabelas históricas do IBGE sobre cinema brasileiro (1937-1988), publicadas
nos Anuários Estatísticos do Brasil e digitalizadas no portal
[Estatísticas do Século XX](https://seculoxx.ibge.gov.br/populacionais-sociais-politicas-e-culturais/busca-por-palavra-chave/cultura/629-cinema.html).

## Snapshot atual (2026-05-26)

Esta primeira coleta cobre 6 arquivos com **sessões cinematográficas,
entradas vendidas (público), lotação, filmes exibidos e número de cinemas
por UF**, para os anos 1971, 1974, 1980, 1984 e 1985.

| Arquivo | Ano referência | Conteúdo |
|---|---|---|
| `cultura1974_aeb35.xls` | 1971 | Cinemas 35mm/70mm — lotação, sessões, longa, espectadores |
| `cultura1976m_aeb236.xls` | 1974 | Idem |
| `cultura1976m_aeb236_1.xls` | 1974 | Capitais (mesmo layout) |
| `cultura1983_aeb303.xls` | 1980 | Cinemas — lotação, sessões, longa nac/estr, entradas inteiras/meias |
| `cultura1986m_aeb268.xls` | 1984 | Sessões, entradas vendidas, filmes curta/longa nac/estr |
| `cultura1987_88_aeb33.xls` | 1985 | Idem |

## Pendente

O portal IBGE Século XX tem **~164 tabelas .xls** sobre cinema 1937-1988
(censura, cine-teatros, capitais, vários recortes). Esta coleta inicial
pegou só as séries de cinemas com indicadores compatíveis com nossa tabela
complementar de bilheteria. Lista completa documentada em [FONTES.md](../../FONTES.md).

## Build

```bash
.venv/Scripts/python.exe pipelines/transform/clean_ibge_seculoxx_cinema.py
```

Output: `pipelines/output/cleaned/ibge_seculoxx_cinema.parquet` (long format,
~900 linhas). Integrado em `bilheteria_historica_complementar.parquet`.

## Licença

Dados públicos do IBGE — domínio público, sem restrição de uso.
