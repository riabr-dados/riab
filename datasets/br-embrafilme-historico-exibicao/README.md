# Embrafilme - Historico de Exibicao

Serie factual de exibicao cinematografica pre-ANCINE, estruturada a partir de
publicacoes oficiais preservadas no OCA e limitada ao que pode ser criado hoje
com dado oficial disponivel.

Esta base e uma **reconstrucao documental das tabelas publicadas**, nao uma
reestimacao independente da exibicao historica brasileira.

## Fonte oficial

- **Orgao**: ANCINE / Observatorio do Cinema e do Audiovisual
- **Acervo-base**: PDFs historicos Embrafilme preservados no OCA
- **Pagina OCA**: <https://www.gov.br/ancine/pt-br/oca/cinema>

## Metodo aplicado

O processo adotado neste dataset foi:

1. inventariar e preservar os PDFs oficiais historicos;
2. extrair tabelas de espectadores, arrecadacao e lugares oferecidos;
3. estruturar os dados por ano e recorte territorial ou temporal;
4. preservar a unidade original informada pela fonte;
5. publicar somente a serie que hoje pode ser reconstruida de forma verificavel.

## Cobertura

- **Serie oficial reconstruida**: 1982-1987
- **Granularidade maxima disponivel hoje**:
  - `embrafilme_exibicao_territorio_ano.csv`: serie longa por ano, indicador e recorte territorial ou mensal

A renda historica permanece na unidade monetaria nominal informada nos PDFs,
sem atualizacao para reais correntes ou reais constantes.

## Snapshots disponiveis

- [`2026-05-23`](snapshots/2026-05-23/) - snapshot com PDFs oficiais e tabela
  factual reconstruida do acervo historico Embrafilme.

Metadados completos em [`datapackage.json`](datapackage.json).
