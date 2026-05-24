# Diversidade Audiovisual - Tabelas Oficiais ANCINE

Serie factual parcial de diversidade no setor audiovisual brasileiro,
reconstruida a partir da publicacao oficial ANCINE/OCA e limitada ao que pode
ser criado hoje com dado oficial disponivel de forma verificavel.

Esta base e uma **reconstrucao documental das tabelas publicadas**, nao uma
reestimacao independente nem uma reproducao integral da planilha anexa citada
no estudo.

## Fonte oficial

- **Orgao**: ANCINE / Observatorio do Cinema e do Audiovisual
- **Publicacao-base**: Estudo Genero e Raca no Setor Audiovisual 2011-2021
- **PDF**: <https://www.gov.br/ancine/pt-br/oca/resolveuid/7e062995b4ed488fb68616ad39e3e81e>
- **Pagina OCA**: <https://www.gov.br/ancine/pt-br/oca/publicacoes-2/outras-publicacoes>

## Metodo aplicado

O processo adotado neste dataset foi:

1. inventariar e preservar os PDFs oficiais do OCA;
2. usar como fonte-base o estudo mais recente disponivel, publicado em 2023;
3. transcrever as Tabelas 1 e 2 da secao de emprego formal baseada em RAIS;
4. publicar somente as tabelas hoje verificaveis diretamente no PDF.

## Cobertura

- **Serie oficial reconstruida**: 2011-2021
- **Unidade**: empregos formais ativos em 31/12
- **Granularidade maxima publicada hoje neste dataset**:
  - `diversidade_audiovisual_emprego_sexo_ano.csv`: serie longa por ano e sexo
  - `diversidade_audiovisual_emprego_raca_ano.csv`: serie longa por ano e raca ou cor

Importante: este dataset publica apenas a parte do estudo que hoje pode ser
reconstruida diretamente do PDF. O proprio estudo informa a existencia de
planilha anexa para detalhamentos adicionais, que nao foi inventariada neste
snapshot. Os totais anuais desta publicacao nao devem ser confundidos com o
dataset `br-rais-emprego-audiovisual`, porque o estudo de diversidade aplica um
recorte proprio para a secao de RAIS.

## Snapshots disponiveis

- [`2026-05-23`](snapshots/2026-05-23/) - snapshot com PDFs oficiais e tabelas
  factuais reconstruidas das Tabelas 1 e 2 do estudo 2011-2021.

Metadados completos em [`datapackage.json`](datapackage.json).
