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
| Bilheteria consolidada | https://www.ancine.gov.br | ANCINE / SADIS | 2026-05-19 | ativo | Top filmes BR 2009→presente, com `Fonte` por linha (Anuário 2009-2013, SADIS 2014+) |
| Bilheteria agregada por filme/ano | https://oca.ancine.gov.br | ANCINE / OCA | 2026-05-19 | intermitente | 2014→presente, todos países (SCB/SADIS publicado no OCA). OCA tem histórico de quedas. **Principal motivador deste projeto.** |
| Listagem de Filmes Brasileiros Lançados 1995-2024 | https://www.gov.br/ancine/pt-br/oca | ANCINE / OCA | 2026-05-23 | ativo | Série longa **só filmes BR**, com público e renda acumulados por filme. Agregada na `bilheteria_historica_complementar`. |
| Embrafilme (histórico exibição 1971-1987) | https://www.gov.br/ancine/pt-br/oca | ANCINE / OCA (Embrafilme) | 2026-05-23 | ativo | 13 PDFs com público, renda em cruzados e lugares oferecidos por UF/região/faixa de habitantes. |
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
| IBGE Século XX — cinema (1937-1988) | https://seculoxx.ibge.gov.br/populacionais-sociais-politicas-e-culturais/busca-por-palavra-chave/cultura/629-cinema.html | IBGE | 2026-05-26 | ativo (parcial) | ~164 tabelas .xls totais; 6 já extraídas (1971, 1974, 1980, 1984, 1985) cobrindo cinemas, sessões, entradas vendidas, filmes exibidos por UF. Integrada a `bilheteria_historica_complementar`. Restantes pendentes. |
| IBGE MUNIC — salas de cinema por município (1999+) | https://www.ibge.gov.br/estatisticas/sociais/educacao/10586-pesquisa-de-informacoes-basicas-municipais.html | IBGE | 2026-05-26 | identificado | Cobertura municipal anual sobre presença de salas. **Pendente de extração.** |
| Cinemateca Brasileira — Filmografia (1897+) | https://bases.cinemateca.org.br/ | Cinemateca Brasileira / MinC | 2026-05-26 | identificado | ~56 mil títulos, longa/média/curta. Cobre lacunas pré-1995. Acesso por consulta web; sem download em lote oficial — **pendente de viabilidade técnica**. |

## CNC — Centre national du cinéma et de l'image animée (França)

| Dataset | URL viva | Última verificação | Status |
|---|---|---|---|
| Visas d'exploitation 1945–2025 | https://www.data.gouv.fr/datasets/liste-des-visas-dexploitations-cinematographiques-delivres-de-1945-a-2025 | 2026-05-19 | ativo |
| Fréquentation des salles | https://www.data.gouv.fr/datasets/frequentation-des-salles-de-cinema | 2026-05-19 | ativo |
| Établissements cinématographiques actifs | https://www.data.gouv.fr/datasets/liste-des-etablissements-cinematographiques-actifs-1 | 2026-05-19 | ativo |
| Films >1M d'entrées | https://www.data.gouv.fr/datasets/films-ayant-realise-plus-dun-million-dentrees | 2026-05-19 | ativo |
| Données internationales | https://www.data.gouv.fr/datasets/donnees-internationales-sur-le-cinema | 2026-05-19 | ativo |
| Films agréés (produção) | https://www.data.gouv.fr/datasets/liste-des-films-cinematographiques-agrees | 2026-05-19 | ativo |
| Audience de la télévision | https://www.data.gouv.fr/datasets/audience-de-la-television | 2026-05-19 | ativo |
| Films à la télévision | https://www.data.gouv.fr/datasets/films-a-la-television | 2026-05-19 | ativo |
| Exportation programmes audiovisuels | https://www.data.gouv.fr/datasets/exportation-de-programmes-audiovisuels | 2026-05-19 | ativo |
| Géographie du cinéma (4 níveis territoriais) | https://www.data.gouv.fr/datasets/geographie-du-cinema-equipement-et-frequentation | 2026-05-19 | ativo |
| Public de la VoD | https://www.data.gouv.fr/datasets/public-de-la-video-a-la-demande | 2026-05-19 | ativo |
| Références actives VoD | https://www.data.gouv.fr/datasets/references-actives-en-video-a-la-demande | 2026-05-19 | ativo |
| Consommation ménages VoD | https://www.data.gouv.fr/datasets/consommation-des-menages-en-video-a-la-demande | 2026-05-19 | ativo |
| Parc cinématographique | https://www.data.gouv.fr/datasets/parc-cinematographique-donnees-generales | 2026-05-19 | ativo |
| Financement de la télévision | https://www.data.gouv.fr/datasets/financement-de-la-television | 2026-05-19 | ativo |
| Distribution des films en salles | https://www.data.gouv.fr/datasets/distribution-des-films-dans-les-salles-de-cinema | 2026-05-19 | ativo |
| Public des films | https://www.data.gouv.fr/datasets/public-des-films | 2026-05-19 | ativo |

Todos sob **Licence Ouverte / Open Licence 2.0**. Fonte: data.gouv.fr.

## INCAA — Argentina

| Dataset | URL viva | Última verificação | Status |
|---|---|---|---|
| Setor audiovisual (espectadores, receita, estrenos, emprego, TV) 2001–2023 | https://datos.gob.ar/dataset/cultura-sector-audiovisual | 2026-05-19 | ativo |
| Produtoras e distribuidoras audiovisuais | https://datos.cultura.gob.ar/dataset/0560ef96-55ca-4026-b70a-d638e1541c05 | 2026-05-19 | ativo |

CC-BY 4.0. Fontes: INCAA, SICA, ENACOM.

## BFI — British Film Institute (Reino Unido)

| Dataset | URL viva | Última verificação | Status |
|---|---|---|---|
| Statistical Yearbook 2023 (15 arquivos ODS) | https://www.bfi.org.uk/industry-data-insights/statistical-yearbook | 2026-05-19 | ativo |

Open Government Licence v3.0. Cobre bilheteria, exibição, vídeo, TV, emprego, economia.

## ACAU — Agência de Cinema e Audiovisual (Uruguai)

| Dataset | URL viva | Última verificação | Status |
|---|---|---|---|
| Apoios e reembolsos a projetos audiovisuais 2013–2024 | https://catalogodatos.gub.uy/dataset/acau-fondos-de-acau | 2026-05-19 | ativo |

Catálogo de Datos Abiertos do Uruguai.

## Fontes identificadas mas não coletáveis automaticamente

| Instituição | País | Razão | URL |
|---|---|---|---|
| FFA Filmförderungsanstalt | Alemanha | Dados apenas em PDF (sem CSV/XLSX estruturado) | https://www.ffa.de/marktdaten.html |
| KOFIC / KOBIS | Coreia do Sul | API REST disponível mas requer cadastro para chave | https://www.kobis.or.kr/kobisopenapi |
| IMCINE | México | Portal dados.gob.mx retornando 403; datasets individuais com URLs instáveis | https://datos.gob.mx/busca/organization/imcine |
| ICAA | Espanha | Estatísticas disponíveis mas acesso direto via HTTPS com certificado inválido | https://www.cultura.gob.es/cultura/areas/cine/datos.html |
| ICA | Portugal | Anuários estatísticos em PDF apenas (sem dados estruturados) | https://www.ica-ip.pt/pt/downloads/publicacoes/ |
| Screen Australia | Austrália | Dados em painel interativo (Fact Finders) sem download direto em CSV | https://www.screenaustralia.gov.au/fact-finders |
| Telefilm Canada | Canadá | Relatórios anuais em PDF; open.canada.ca com cobertura limitada | https://telefilm.ca/en |
| Proimágenes Colombia | Colômbia | Dados interativos (Cine en Cifras), sem download em CSV | https://www.proimagenescolombia.com/visualizaciondatos.php |

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
