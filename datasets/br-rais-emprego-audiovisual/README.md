# Emprego no Setor Audiovisual - Metodologia ANCINE

Serie factual de empregos formais no setor audiovisual brasileiro,
reconstruida a partir da publicacao oficial ANCINE/OCA e limitada ao que pode
ser criado hoje com dado oficial disponivel.

Esta base e uma **reconstrucao documental da publicacao oficial da ANCINE**,
nao uma reestimacao independente a partir dos microdados da RAIS.

## Fonte oficial

- **Orgao**: ANCINE / Observatorio do Cinema e do Audiovisual
- **Publicacao-base**: Emprego no Setor Audiovisual, ano-base 2019
- **PDF**: <https://www.gov.br/ancine/pt-br/oca/resolveuid/992a10f5cca0463eb9b61541e9ceaba5>
- **Pagina OCA**: <https://www.gov.br/ancine/pt-br/oca/publicacoes-2/outras-publicacoes>

## Metodo aplicado

O processo adotado neste dataset foi:

1. inventariar e preservar os PDFs oficiais do OCA;
2. usar como fonte-base o estudo mais recente disponivel, ano-base 2019;
3. transcrever o Apendice 2 para tabela estruturada por ano e por subclasse CNAE;
4. validar a soma das subclasses contra o total anual publicado;
5. publicar somente a serie que hoje pode ser reconstruida de forma verificavel.

## Cobertura

- **Serie oficial reconstruida**: 2010-2019
- **Unidade**: empregos formais ativos em 31/12
- **Granularidade maxima disponivel hoje**:
  - `rais_emprego_audiovisual_subclasse_ano.csv`: serie longa por subclasse CNAE/ano
  - `rais_emprego_audiovisual_total_ano.csv`: total anual do setor audiovisual

O dataset publicado inclui somente a serie oficial que hoje pode ser
reconstruida com base documental ANCINE/OCA, sem redistribuir microdados da
RAIS.

## Snapshots disponiveis

- [`2026-05-23`](snapshots/2026-05-23/) - snapshot com PDFs oficiais e tabelas
  factuais reconstruidas do Apendice 2 do estudo ano-base 2019.

Metadados completos em [`datapackage.json`](datapackage.json).
