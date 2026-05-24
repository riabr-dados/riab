# PIB do Audiovisual - Metodologia ANCINE

Serie factual de valor adicionado bruto do setor audiovisual brasileiro,
reconstruida a partir da metodologia ANCINE/OCA e limitada ao que pode ser
criado hoje com dado oficial disponivel.

Esta base e uma **reconstrucao documental da publicacao oficial da ANCINE**,
nao uma reestimacao independente a partir de microdados do IBGE.

## Fonte oficial

- **Orgao**: ANCINE / Observatorio do Cinema e do Audiovisual
- **Publicacao-base**: Valor Adicionado pelo Setor Audiovisual, ano-base 2019
- **PDF**: <https://www.gov.br/ancine/pt-br/oca/resolveuid/bd4f7d2608e541608e151c168da6d823>
- **Pagina OCA**: <https://www.gov.br/ancine/pt-br/oca/publicacoes-2/outras-publicacoes>

## Metodo aplicado

A ANCINE mede valor adicionado bruto a precos basicos, nao PIB a precos de
mercado. A formula-base do estudo e:

`valor_adicionado = valor_bruto_da_producao - consumo_intermediario`

O recorte do Anexo 1 cobre empresas com 20 ou mais pessoas ocupadas e classes
CNAE 2.0 selecionadas do audiovisual. A maior parte dos valores vem de
tabulacao especial IBGE/PAS/PAC. Para a classe `61.41-8` a partir de 2015, a
ANCINE usa estimativa por regressao linear via minimos quadrados ordinarios com
assinantes de TV paga da ANATEL e valor adicionado das operadoras de TV por
assinatura.

O processo adotado neste dataset foi:

1. inventariar e preservar os PDFs oficiais do OCA;
2. usar como fonte-base o estudo mais recente disponivel, ano-base 2019;
3. transcrever o Anexo 1 para tabela estruturada por ano e por CNAE;
4. preservar os marcadores de nota da ANCINE (`*`, `**`, `***`) como campos;
5. publicar somente a serie que hoje pode ser reconstruida de forma verificavel.

## Cobertura

- **Serie oficial reconstruida**: 2007-2019
- **Unidade**: R$ 1.000.000 correntes
- **Granularidade maxima disponivel hoje**:
  - `pib_audiovisual_atividade_ano.csv`: serie longa por CNAE/atividade/ano
  - `pib_audiovisual_total_ano.csv`: total anual e participacoes relativas

Nao foi incluida nenhuma extensao proxy apos 2019. A serie publicada aqui para
o dataset termina no ultimo ponto que hoje pode ser reconstruido com a base
oficial ANCINE/OCA disponivel.

Os totais anuais reproduzem os valores publicados pela ANCINE. Ao somar as
linhas por atividade, podem aparecer pequenas diferencas residuais em alguns
anos porque o Anexo 1 publica as atividades com uma casa decimal, enquanto o
total provavelmente foi calculado antes do arredondamento dessas linhas.

## Snapshots disponiveis

- [`2026-05-23`](snapshots/2026-05-23/) - snapshot com PDFs oficiais e tabelas
  factuais reconstruidas pela metodologia ANCINE.

Metadados completos em [`datapackage.json`](datapackage.json).
