# Comercio Exterior de Servicos Audiovisuais - Metodologia ANCINE

Serie factual do comercio exterior brasileiro de servicos audiovisuais,
reconstruida a partir da publicacao oficial ANCINE/OCA e limitada ao que pode
ser criado hoje com dado oficial disponivel.

Esta base e uma **reconstrucao documental da publicacao oficial da ANCINE**,
nao uma reestimacao independente a partir de microdados brutos do SISCOSERV.

## Fonte oficial

- **Orgao**: ANCINE / Observatorio do Cinema e do Audiovisual
- **Publicacao-base**: Comercio Exterior de Servicos Audiovisuais, ano-base 2019
- **PDF**: <https://www.gov.br/ancine/pt-br/oca/resolveuid/5c8cf11479a5472abe8adc08c2bbd1b2>
- **Pagina OCA**: <https://www.gov.br/ancine/pt-br/oca/publicacoes-2/outras-publicacoes>

## Metodo aplicado

O processo adotado neste dataset foi:

1. inventariar e preservar os PDFs oficiais do OCA;
2. usar como fonte-base o estudo mais recente disponivel, ano-base 2019;
3. transcrever o anexo "Dados Primarios, Total e por Servico";
4. estruturar a serie por ano, grupo e codigo NBS;
5. validar a soma dos servicos contra os totais anuais publicados;
6. publicar somente a serie que hoje pode ser reconstruida de forma verificavel.

## Cobertura

- **Serie oficial reconstruida**: 2014-2019
- **Unidade**: USD nominais
- **Granularidade maxima disponivel hoje**:
  - `comercio_exterior_servicos_audiovisuais_servico_ano.csv`: serie longa por servico NBS/ano
  - `comercio_exterior_servicos_audiovisuais_total_ano.csv`: total anual de vendas, aquisicoes e saldo

Nao foi incluida nenhuma extensao posterior a 2019. O proprio estudo registra
o desligamento definitivo do SISCOSERV em 2020, entao o dataset publicado aqui
termina no ultimo ponto que hoje pode ser reconstruido de forma oficial a
partir da publicacao ANCINE/OCA localizada.

## Snapshots disponiveis

- [`2026-05-23`](snapshots/2026-05-23/) - snapshot com PDFs oficiais e tabelas
  factuais reconstruidas do anexo do estudo ano-base 2019.

Metadados completos em [`datapackage.json`](datapackage.json).
