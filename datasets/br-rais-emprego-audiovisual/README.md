# Emprego no Setor Audiovisual - Metodologia ANCINE

Serie factual de empregos formais no setor audiovisual brasileiro,
reconstruida a partir da publicacao oficial ANCINE/OCA e limitada ao que pode
ser criado hoje com dado oficial disponivel.

Esta base preserva duas camadas metodologicas:

1. **publicado_ancine**: reproducao estruturada dos valores publicados pela
   ANCINE/OCA no Apendice 2 do estudo ano-base 2019.
2. **reprocessado_fonte_primaria**: recalculo a partir dos microdados
   RAIS/PDET vigentes, usando o recorte observavel da metodologia ANCINE
   (vinculos ativos em 31/12 nas subclasses CNAE audiovisuais).

A camada publicada continua sendo a referencia para citacao direta do estudo.
A camada reprocessada aumenta a rastreabilidade, pois conecta o indicador aos
microdados primarios e documenta eventuais diferencas de versao da RAIS.

## Fonte oficial

- **Orgao**: ANCINE / Observatorio do Cinema e do Audiovisual
- **Publicacao-base**: Emprego no Setor Audiovisual, ano-base 2019
- **PDF**: <https://www.gov.br/ancine/pt-br/oca/resolveuid/992a10f5cca0463eb9b61541e9ceaba5>
- **Pagina OCA**: <https://www.gov.br/ancine/pt-br/oca/publicacoes-2/outras-publicacoes>
- **Fonte primaria externa**: MTE/PDET - Microdados RAIS
- **FTP RAIS 2019**: <ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/2019/>

## Metodo aplicado

O processo adotado neste dataset foi:

1. inventariar e preservar os PDFs oficiais do OCA;
2. usar como fonte-base o estudo mais recente disponivel, ano-base 2019;
3. transcrever o Apendice 2 para tabela estruturada por ano e por subclasse CNAE;
4. validar a soma das subclasses contra o total anual publicado;
5. manter essa serie como camada `publicado_ancine`;
6. quando houver microdados primarios externos disponiveis, reprocessar o mesmo
   recorte observavel e publicar como camada `reprocessado_fonte_primaria`.

## Reprocessamento RAIS/PDET 2019

O teste nacional de 2019 foi executado sobre os seis arquivos regionais de
vinculos publicos da RAIS/PDET. O filtro aplicado foi:

- `Vinculo Ativo 31/12 = 1`
- subclasses CNAE 2.0 listadas no estudo ANCINE/OCA

Resultado agregado:

| Camada | Empregos formais ativos em 31/12 |
|---|---:|
| `publicado_ancine` | 88.053 |
| `reprocessado_fonte_primaria` | 86.230 |
| diferenca | -1.823 (-2,1%) |

A diferenca e esperada quando a RAIS/PDET vigente nao e exatamente a mesma
extracao usada pela ANCINE. O estudo informa extracao entre 25 e 30/03/2021 e
consolidacao em 15/04/2021; o FTP atual do PDET informa atualizacoes posteriores
nos microdados de 2019.

## Cobertura

- **Serie oficial reconstruida**: 2010-2019
- **Unidade**: empregos formais ativos em 31/12
- **Granularidade maxima disponivel hoje**:
  - `rais_emprego_audiovisual_subclasse_ano.csv`: serie longa por subclasse CNAE/ano
  - `rais_emprego_audiovisual_total_ano.csv`: total anual do setor audiovisual
  - `rais_emprego_audiovisual_subclasse_ano_reprocessado_pdet_2019.csv`: reprocessamento RAIS/PDET vigente para 2019
  - `rais_emprego_audiovisual_comparacao_ancine_pdet_2019.csv`: comparacao subclasse a subclasse entre ANCINE e PDET
  - `rais_emprego_audiovisual_reprocessamento_regioes_pdet_2019.csv`: resumo dos arquivos regionais processados

Os microdados brutos da RAIS/PDET nao sao redistribuidos neste repositorio. O
script [`pipelines/transform/reprocess_rais_emprego_audiovisual.py`](../../pipelines/transform/reprocess_rais_emprego_audiovisual.py)
reprocessa os arquivos oficiais baixados localmente.

## Snapshots disponiveis

- [`2026-05-23`](snapshots/2026-05-23/) - snapshot com PDFs oficiais, tabelas
  factuais publicadas no Apendice 2 do estudo ano-base 2019 e camada
  reprocessada RAIS/PDET para 2019.

Metadados completos em [`datapackage.json`](datapackage.json).
