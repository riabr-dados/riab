# Índice de fontes vivas

Tabela de saúde das fontes públicas espelhadas neste repositório. Atualizada a cada snapshot ou verificação manual.

**Legenda de status:**
- `ativo` — fonte acessível, dados sendo atualizados normalmente
- `intermitente` — fonte sai do ar com frequência mas volta
- `alterado` — fonte ainda existe mas mudou estrutura/metodologia recentemente (ver notas)
- `offline` — fonte fora do ar; aguardando retorno
- `descontinuado` — fonte oficialmente encerrada

## ANCINE

| Dataset | URL viva | Órgão | Última verificação | Status | Notas |
|---|---|---|---|---|---|
| Projetos FSA | https://fsa.ancine.gov.br | ANCINE / FSA | 2026-05-19 | ativo | Plano de Dados Abertos vigente |
| Renúncia fiscal (Art. 1º, 1ºA, 3º, 3ºA) | https://www.ancine.gov.br | ANCINE | 2026-05-19 | ativo | |
| Obras não publicitárias brasileiras | https://dados.gov.br | ANCINE / SAV | 2026-05-19 | ativo | Cobertura 2002–2026, um arquivo por ano |
| Agentes econômicos regulares | https://dados.gov.br | ANCINE | 2026-05-19 | ativo | |
| Diretores de obras não publicitárias | https://dados.gov.br | ANCINE / SAV | 2026-05-19 | ativo | |
| Produtores de obras não publicitárias | https://dados.gov.br | ANCINE / SAV | 2026-05-19 | ativo | |
| Bilheteria consolidada | https://www.ancine.gov.br | ANCINE / SADIS | 2026-05-19 | ativo | |
| Bilheteria agregada por filme/ano | https://oca.ancine.gov.br | ANCINE / OCA | 2026-05-19 | intermitente | OCA tem histórico de quedas. **Principal motivador deste projeto.** |
| Preço médio do ingresso | https://oca.ancine.gov.br | ANCINE / OCA | 2026-05-19 | intermitente | Série histórica |
| Atas oficiais FSA (PDFs) | https://fsa.ancine.gov.br | ANCINE / FSA | 2026-05-19 | ativo | PRODAV 07/2014, 07/2015, 07/2017, Desempenho Artístico 2018, 2024 |

## Observatório Europeu do Audiovisual (Lumiere)

| Dataset | URL viva | Órgão | Última verificação | Status | Notas |
|---|---|---|---|---|---|
| Cinemas Europa (filmes brasileiros) | https://lumiere.obs.coe.int | Council of Europe / EAO | 2026-05-19 | ativo | Espectadores, países, anos |
| VOD Europa (filmes brasileiros) | https://lumiere.obs.coe.int/vod | Council of Europe / EAO | 2026-05-19 | ativo | Disponibilidade por plataforma e país |

## IBGE

| Dataset | URL viva | Órgão | Última verificação | Status | Notas |
|---|---|---|---|---|---|
| Deflator IPCA (base 2024) | https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos/9256-indice-nacional-de-precos-ao-consumidor-amplo.html | IBGE | 2026-05-19 | ativo | Série mensal |

## Lacunas conhecidas (a cobrir em contribuições futuras)

- **SICA (Sistema ANCINE de Informações)** — dados de salas, exibidores, distribuidoras
- **Salic / MinC** — incentivo cultural federal (parte do audiovisual)
- **Editais e prestações de contas do FSA** — granularidade abaixo do nível "projeto"
- **Acervos da Cinemateca Brasileira** — catálogos públicos
- **IBGE — POF, MUNIC (cultura), PNAD contínua módulos culturais**
- **Observatório Ibero-Americano do Audiovisual (CAACI)**
- **Dados de festivais nacionais e internacionais** — só os públicos
- **Dados de plataformas VoD com presença regulatória no Brasil** — quando a regulamentação avançar
- **OpenAlex / citações acadêmicas** — pesquisa sobre audiovisual brasileiro

## Como reportar uma fonte caída ou alterada

Abra uma issue no repositório com:
1. Dataset afetado
2. URL que falhou
3. Comportamento observado (404, timeout, dados claramente diferentes, etc.)
4. Data da observação

O status será atualizado nesta tabela e, se for alteração de conteúdo, um novo snapshot será coletado para registrar o estado atual.
