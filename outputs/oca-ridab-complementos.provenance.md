# Proveniência - Plano OCA -> RIDAB

Data: 2026-05-23  
Workspace: `C:\Users\INTEL\Desktop\dados-audiovisual-br`  
Artefato final: `outputs/oca-ridab-complementos.md`

## Fontes web oficiais consultadas

| Fonte | URL | Uso no relatório |
|---|---|---|
| Sobre o OCA | https://www.gov.br/ancine/pt-br/oca/sobre-o-oca-1 | Definição institucional do OCA e seções principais |
| Publicações OCA | https://www.gov.br/ancine/pt-br/oca/publicacoes-2 | Estrutura das publicações |
| Dados Abertos OCA/ANCINE | https://www.gov.br/ancine/pt-br/oca/dados-abertos | Matriz de duplicidade e lacunas |
| Agentes Econômicos e Obras Audiovisuais | https://www.gov.br/ancine/pt-br/oca/publicacoes-2/agentes-economicos-e-obras-audiovisuais | Identificação de agregados derivados de obras/agentes |
| Dados Financeiros | https://www.gov.br/ancine/pt-br/oca/publicacoes-2/dados-financeiros | CONDECINE e fluxos financeiros/fomento |
| Mercado Audiovisual Brasileiro | https://www.gov.br/ancine/pt-br/oca/publicacoes-2/mercado-audiovisual-brasileiro | Estrutura de cinema, televisão, VoD e outros segmentos |
| Cinema OCA | https://www.gov.br/ancine/pt-br/oca/publicacoes-2/mercado-audiovisual-brasileiro/cinema | Cinema atual, salas, complexos, bilheteria, distribuição |
| Televisão OCA | https://www.gov.br/ancine/pt-br/oca/publicacoes-2/mercado-audiovisual-brasileiro/televisao | TV paga, canais, programadoras, pacotes |
| Outras Publicações OCA | https://www.gov.br/ancine/pt-br/oca/publicacoes-2/outras-publicacoes | Valor adicionado, emprego, comércio exterior, diversidade |
| Arquivos antigos de cinema | https://www.gov.br/ancine/pt-br/oca/publicacoes-teste-ii/mercado-audiovisual-brasileiro/arquivos-cinema | Séries Embrafilme e histórico pré-SADIS |
| Notícia ANCINE sobre filmes de maior público | https://www.gov.br/ancine/pt-br/assuntos/noticias/ancine-divulga-estudo-sobre-filmes-de-maior-publico-do-cinema-brasileiro | Contexto de lacunas 1970-1992 e fonte Embrafilme/Concine |
| Microdados RAIS e CAGED | https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatisticas-trabalho/microdados-rais-e-caged | Fonte de emprego formal |
| IBGE PAS | https://www.ibge.gov.br/estatisticas/economicas/servicos/9028-pesquisa-anual-de-servicos.html | Fonte estrutural de VA, receita, pessoal ocupado, salários |
| SIDRA/PAS | https://sidra.ibge.gov.br/pesquisa/pas/tabelas | Tabelas PAS por CNAE 2.0 |
| Valor Adicionado OCA 2019 | https://www.gov.br/ancine/pt-br/oca/publicacoes/arquivos.pdf/valor_adicionado_2019_25-01-2022.pdf | Metodologia e QA do PIB/VA audiovisual |
| MDIC Comércio Exterior de Serviços | https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/estatisticas-de-comercio-exterior-de-servicos | Fonte de serviços pós-2020 e SISCOSERV |
| MDIC SISCOSERV | https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/estatisticas-do-siscoserv | Dados de serviços 2014-2019 |
| Comércio Exterior Serviços Audiovisuais OCA 2019 | https://www.gov.br/ancine/pt-br/oca/publicacoes/arquivos.pdf/comercio_exterior_de_servicos_audiovisuais_ano-base_2019.pdf | Metodologia de serviços audiovisuais e caveats |
| MDIC Base de Dados Bruta | https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta | Comércio exterior de bens |

## Arquivos locais consultados

| Arquivo | Uso |
|---|---|
| `README.md` | Estrutura do projeto, camada raw/cleaned/catalog/pipelines |
| `FONTES.md` | Fontes já espelhadas e lacunas conhecidas |
| `catalog/datasets.yaml` | Datasets já catalogados no RIDAB |
| `pipelines/output/cleaned/*.parquet` | Parquets efetivamente existentes |

## Decisões metodológicas

1. OCA agregados de obras/agentes/cinema não devem virar parquets quando já deriváveis de Dados Abertos ou de parquets existentes.
2. CONDECINE entra como prioridade porque não existe parquet local equivalente.
3. Valor adicionado/PIB deve ser reconstruído com IBGE PAS/SCN e validado contra estudos OCA, com nota de que é proxy/metodologia setorial.
4. RAIS deve ser publicada apenas agregada, sem microdados individuais.
5. Comércio exterior de serviços e comércio exterior de bens devem ser datasets separados.
6. Embrafilme deve ter coluna de confiabilidade, porque o próprio histórico ANCINE registra lacunas e reconstruções documentais.

## Lacunas residuais

- Não foi feito download dos arquivos OCA nesta etapa; o produto é um plano de extração/consolidação.
- A lista NCM para bens audiovisuais precisa ser curada na implementação.
- A lista NBS audiovisual deve ser extraída dos estudos OCA/SISCOSERV e versionada.
- O recorte CNAE audiovisual precisa ser fixado em `dim_cnae_audiovisual` antes da produção de PIB e RAIS.

