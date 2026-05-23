# Plano de complementaridade OCA -> RIDAB

Data da pesquisa: 2026-05-23  
Escopo: OCA/ANCINE, especialmente Publicações, cruzado com o catálogo local do RIDAB/RIAB e com fontes oficiais externas para CONDECINE, valor adicionado/PIB, RAIS, comércio exterior e séries históricas da Embrafilme.

## 1. Resumo executivo

O OCA deve entrar no RIDAB em duas camadas diferentes:

1. **Camada de complemento real**, com dados que não aparecem como parquet local e que não são simples agregações já reconstituíveis a partir dos dados abertos da ANCINE: CONDECINE, fluxos fiscais e financeiros antigos, valor adicionado/PIB audiovisual, emprego/RAIS, comércio exterior de serviços audiovisuais, séries históricas da Embrafilme e estudos de diversidade.
2. **Camada de validação**, com tabelas OCA que repetem ou agregam dados já existentes em Dados Abertos ou no RIDAB: agentes econômicos, obras, produtores, diretores, bilheteria por filme/ano, preço médio do ingresso e boa parte dos recortes agregados de cinema.

Minha recomendação é **não transformar cada planilha do OCA em um parquet separado**. O ganho vem de consolidar arquivos dispersos em poucos datasets conceituais, com granularidade clara e metadados de fonte:

- `ancine_condecine_arrecadacao`
- `ancine_fomento_fluxos_financeiros`
- `br_pib_audiovisual`
- `br_rais_emprego_audiovisual`
- `br_comercio_exterior_servicos_audiovisuais`
- `br_comex_bens_audiovisuais`
- `br_embrafilme_historico_exibicao`
- `ancine_diversidade_audiovisual`
- opcionais: `ancine_tv_paga_consolidado` e `ancine_salas_complexos_historico`, preferindo Dados Abertos como fonte primária quando houver cobertura completa.

## 2. Critério de entrada no RIDAB

Use esta regra para cada tabela encontrada:

- **Entra como dataset novo** se não existe no RIDAB e não é apenas uma agregação de um dado aberto já completo.
- **Entra como atualização** se o RIDAB já possui a tabela, mas a fonte OCA traz cobertura posterior ou campo adicional que não pode ser derivado.
- **Não entra como parquet final** se a tabela OCA é uma visão agregada de dado já existente; nesse caso vira teste de consistência.
- **Entra como dataset curado** se a fonte é PDF/estudo histórico sem microdado aberto equivalente, com coluna de confiabilidade e fonte.

## 3. O que o RIDAB já cobre

O catálogo local e os parquets em `pipelines/output/cleaned` já cobrem estes blocos brasileiros:

- `obras.parquet`: Obras não publicitárias brasileiras registradas.
- `diretores_obras.parquet`: diretores vinculados às obras.
- `produtores_obras.parquet`: produtoras vinculadas às obras.
- `agentes_economicos.parquet`: agentes econômicos regulares.
- `bilheteria_por_filme_ano.parquet`: público, renda e sessões por filme/ano.
- `bilheteria_consolidada_br.parquet`: top filmes brasileiros por público.
- `preco_ingresso.parquet`: preço médio do ingresso.
- `fomento_fsa.parquet`: projetos FSA.
- `renuncia_fiscal.parquet`: projetos de renúncia fiscal.
- `deflator_ipca.parquet`: deflator para valores reais.

Portanto, as publicações OCA de agentes/obras e vários recortes de cinema são, em geral, **QA**, não fonte final.

## 4. Fontes oficiais relevantes

### OCA/ANCINE

O OCA é descrito pela ANCINE como espaço de difusão de dados e informações qualificadas, produzido a partir de atividades de fomento, regulação e fiscalização, com dados fornecidos por agentes de mercado e consolidados pela agência: [Sobre o OCA](https://www.gov.br/ancine/pt-br/oca/sobre-o-oca-1).

A página de Publicações organiza os materiais em Mercado Audiovisual Brasileiro, Agentes Econômicos e Obras Audiovisuais, Dados Financeiros e Outras Publicações: [Publicações OCA](https://www.gov.br/ancine/pt-br/oca/publicacoes-2).

A página de Dados Abertos lista os conjuntos publicados no dados.gov.br, incluindo agentes, atividades econômicas, salas/complexos, obras, produtores, diretores, CPB/CRT, bilheteria diária, FSA, renúncia, contribuintes, filmagens estrangeiras, lançamentos comerciais e coproduções: [Dados Abertos OCA/ANCINE](https://www.gov.br/ancine/pt-br/oca/dados-abertos).

### Fontes externas oficiais

- PDET/MTE publica microdados não identificados de RAIS Estabelecimento e Trabalhador em TXT: [Microdados RAIS e CAGED](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatisticas-trabalho/microdados-rais-e-caged).
- IBGE PAS mede produção, receita, custos, pessoal ocupado, salários e valor adicionado por CNAE 2.0: [Pesquisa Anual de Serviços](https://www.ibge.gov.br/estatisticas/economicas/servicos/9028-pesquisa-anual-de-servicos.html) e [SIDRA/PAS](https://sidra.ibge.gov.br/pesquisa/pas/tabelas).
- MDIC publica estatísticas de comércio exterior de serviços, incluindo relatórios recentes e a série SISCOSERV encerrada em 2019: [Estatísticas de Comércio Exterior de Serviços](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/estatisticas-de-comercio-exterior-de-servicos) e [Estatísticas do SISCOSERV](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/estatisticas-do-siscoserv).
- MDIC/Comex Stat publica base bruta mensal de comércio exterior de bens: [Base de Dados Bruta](https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta).

## 5. Matriz de complementaridade

| Tema | Fonte OCA/externa | Status no RIDAB | Decisão |
|---|---|---:|---|
| Agentes econômicos por UF, município, natureza e independência | OCA Agentes Econômicos e Obras | Já há `agentes_economicos` | Não criar parquet novo; usar agregados como QA |
| Obras por CPB, UF, gênero, diretor | OCA Agentes Econômicos e Obras | Já há `obras`, `diretores_obras`, `produtores_obras` | Não criar parquet novo; usar como QA |
| Bilheteria por filme/ano e preço do ingresso | OCA Cinema | Já há `bilheteria_por_filme_ano` e `preco_ingresso` | Só atualizar se a fonte estiver mais recente |
| Salas e complexos | OCA Cinema e Dados Abertos | Lacuna local, mas há Dados Abertos completo | Ingerir de Dados Abertos; OCA só valida/histórico |
| TV paga, canais, pacotes, programação | OCA Televisão e Dados Abertos | Lacuna local | Ingerir se o objetivo for completar RIDAB, preferindo Dados Abertos |
| CONDECINE | OCA Dados Financeiros | Lacuna local | Prioridade alta |
| Fluxos fiscais e financeiros de incentivo | OCA Dados Financeiros | Parcial em `renuncia_fiscal` e `fomento_fsa` | Prioridade alta/média, consolidando fluxos |
| Valor adicionado/PIB audiovisual | OCA Outras Publicações, IBGE PAS/SCN | Lacuna local | Prioridade alta |
| Emprego audiovisual | OCA Outras Publicações, RAIS/PDET | Lacuna local | Prioridade alta |
| Comércio exterior de serviços audiovisuais | OCA Outras Publicações, MDIC/SISCOSERV | Lacuna local | Prioridade alta |
| Comércio exterior de bens audiovisuais | MDIC base bruta Comex | Lacuna local | Prioridade média, com caveat metodológico |
| Embrafilme histórico | OCA Cinema antigo, notícia ANCINE, PDFs | Lacuna local | Prioridade alta, extração com OCR/curadoria |
| Gênero e raça no audiovisual | OCA Outras Publicações | Lacuna local | Prioridade média |
| Filmagens estrangeiras no Brasil | Dados Abertos ANCINE | Lacuna local | Backlog, não é OCA-publicação complementar |

## 6. Datasets recomendados

### 6.1 `ancine_condecine_arrecadacao`

**Objetivo:** consolidar arrecadação da CONDECINE em série anual e mensal, com valores nominais e deflacionados.

**Entradas:**

- OCA Dados Financeiros: "Condecine - Valores Arrecadados - Em Reais (R$) 2007 a 2025", publicado em 08/04/2026.
- OCA Dados Financeiros: "Valores Arrecadados Condecine por Mês" para 2010 a 2025, conforme arquivos listados na página.
- Arquivos legados de Dados Financeiros quando trouxerem anos/campos não presentes na página atual.

**Consolidação:**

- Unificar anual e mensal em uma tabela longa.
- Usar `periodicidade = 'ano' | 'mes'`.
- Preservar recortes de tipo de CONDECINE, fato gerador, segmento ou categoria quando existirem.
- Deflacionar BRL com `deflator_ipca`.
- Guardar `fonte_url`, `fonte_arquivo`, `data_publicacao`, `ano_referencia`, `hash_arquivo`.

**Parquet final:** `pipelines/output/cleaned/condecine_arrecadacao.parquet`

**Colunas mínimas:**

- `periodicidade`
- `ano`
- `mes`
- `data_inicio_periodo`
- `recorte_tipo`
- `recorte_nome`
- `moeda`
- `valor_nominal`
- `valor_brl_nominal`
- `valor_brl_real_base_2024`
- `fonte_arquivo`
- `fonte_url`
- `hash_arquivo`

### 6.2 `ancine_fomento_fluxos_financeiros`

**Objetivo:** transformar as tabelas antigas e dispersas de valores captados, recolhidos, aplicados, liberados e executados em um único dataset de fluxos financeiros do fomento.

**Entradas:**

- Valores Totais Captados por Mecanismo de Incentivo 2006 a 2024.
- Valores Captados por Projeto Incentivado.
- Valores Aportados por Incentivador/Investidor.
- Valores Recolhidos por mecanismo e remessas ao exterior.
- Valores Execução FSA 2007 a 2019.
- Valores Liberados por Mecanismo de Incentivo.
- Editais, programas e prêmios.
- Ibermedia, apoio a festivais, editais de coprodução internacional.

**Consolidação:**

- Unificar fluxos em uma tabela longa com `tipo_fluxo`.
- Relacionar a `renuncia_fiscal` por `salic`, `titulo_projeto`, `cnpj_proponente`.
- Relacionar a `fomento_fsa` por `titulo_projeto`, `cnpj_proponente`, `cnpj_produtora`, `chamada_publica`.
- Manter granularidade original: projeto, mecanismo, investidor/contribuinte, ano ou edital.
- Marcar linhas agregadas com `nivel_agregacao`.

**Parquet final:** `pipelines/output/cleaned/fomento_fluxos_financeiros.parquet`

**Colunas mínimas:**

- `ano`
- `periodo`
- `tipo_fluxo`
- `mecanismo`
- `programa`
- `edital`
- `salic`
- `titulo_projeto`
- `cnpj_proponente`
- `cnpj_investidor_ou_contribuinte`
- `valor_brl_nominal`
- `valor_brl_real_base_2024`
- `nivel_agregacao`
- `fonte_arquivo`
- `hash_arquivo`

### 6.3 `br_pib_audiovisual`

**Objetivo:** produzir uma série do valor adicionado/PIB proxy do audiovisual brasileiro por atividade econômica.

**Entradas:**

- Estudos OCA "Valor Adicionado pelo Setor Audiovisual" para 2013 a 2019.
- IBGE PAS, especialmente tabelas de receita operacional líquida, valor adicionado, salários, pessoal ocupado e número de empresas por CNAE 2.0.
- SIDRA/PAS para série anual 2007-2023.
- Sistema de Contas Nacionais para PIB e valor adicionado total.
- ANATEL/TV paga apenas se necessário para reproduzir metodologia de estudos OCA antigos.

**Mapa CNAE versionado:**

- 5911: atividades de produção cinematográfica, vídeo e televisão.
- 5912: pós-produção.
- 5913: distribuição.
- 5914: exibição cinematográfica.
- 5920: gravação de som e edição musical, se mantida no recorte OCA.
- 6021/6022: televisão aberta e programação/TV por assinatura, com nota metodológica.
- 6319/VoD: somente em cenário expandido, com caveat porque mistura portais e conteúdo na internet.

**Consolidação:**

- Criar tabela de mapeamento `dim_cnae_audiovisual`.
- Separar `recorte = 'estrito' | 'expandido'`.
- Calcular participação no PIB e no valor adicionado total.
- Deflacionar valores para base 2024.
- Comparar totais de 2013-2019 contra estudos OCA como validação.

**Parquet final:** `pipelines/output/cleaned/pib_audiovisual_atividade_ano.parquet`

**Colunas mínimas:**

- `ano`
- `cnae_classe`
- `cnae_descricao`
- `recorte_metodologico`
- `valor_adicionado_brl_nominal`
- `valor_adicionado_brl_real_base_2024`
- `receita_operacional_liquida_brl`
- `salarios_retiradas_remuneracoes_brl`
- `pessoal_ocupado`
- `numero_empresas`
- `pib_brasil_brl`
- `participacao_pib`
- `fonte_primaria`
- `metodologia_versao`

### 6.4 `br_rais_emprego_audiovisual`

**Objetivo:** criar uma base anual de vínculos e remuneração formal do audiovisual, sem dados pessoais, agregada por CNAE, território e perfil ocupacional.

**Entradas:**

- RAIS Trabalhador e RAIS Estabelecimento, PDET/MTE.
- Estudos OCA "Emprego no Setor Audiovisual" como referência metodológica e QA.

**Consolidação:**

- Baixar microdados por ano e preservar raw em snapshots.
- Filtrar pelo mesmo mapa CNAE usado no PIB audiovisual.
- Agregar antes de publicar, sem CPF/PIS e sem identificador individual.
- Unir com `dim_municipio`, `dim_cnae_audiovisual`, `dim_cbo`.
- Gerar indicadores por `ano`, `uf`, `cod_municipio_ibge`, `cnae`, `cbo`, `sexo`, `faixa_idade`, `escolaridade`.

**Parquet final:** `pipelines/output/cleaned/rais_emprego_audiovisual.parquet`

**Colunas mínimas:**

- `ano`
- `uf`
- `cod_municipio_ibge`
- `cnae_subclasse`
- `cnae_descricao`
- `cbo_codigo`
- `cbo_familia`
- `sexo`
- `faixa_idade`
- `escolaridade`
- `vinculos_ativos_31_12`
- `remuneracao_media_dezembro_brl`
- `remuneracao_media_ano_brl`
- `massa_salarial_brl`
- `estabelecimentos`
- `recorte_metodologico`
- `fonte_arquivo`

### 6.5 `br_comercio_exterior_servicos_audiovisuais`

**Objetivo:** consolidar vendas e aquisições internacionais de serviços audiovisuais, com base em SISCOSERV/OCA e estatísticas de serviços do MDIC.

**Entradas:**

- Estudos OCA de Comércio Exterior de Serviços Audiovisuais, especialmente 2015-2019.
- Estatísticas SISCOSERV 2014-2019 por NBS, país, UF e modo de prestação.
- Relatórios/painel MDIC de comércio exterior de serviços para 2020 em diante, quando houver recorte compatível.

**Consolidação:**

- Usar NBS como chave primária de serviço.
- Criar `dim_nbs_audiovisual` com grupos: licenciamento, cessão de direitos, produção/pós-produção, TV aberta, TV paga, VoD e outros serviços audiovisuais.
- Preservar `fluxo = venda | aquisicao`, evitando chamar automaticamente de exportação/importação quando a própria ANCINE alerta para diferença metodológica.
- Separar dados SISCOSERV e dados pós-SISCOSERV em `sistema_origem`.
- Manter flags de sigilo quando o agregado for suprimido.

**Parquet final:** `pipelines/output/cleaned/comercio_exterior_servicos_audiovisuais.parquet`

**Colunas mínimas:**

- `ano`
- `fluxo`
- `nbs_codigo`
- `nbs_descricao`
- `grupo_servico_audiovisual`
- `pais_parceiro`
- `uf`
- `modo_prestacao`
- `valor_usd`
- `qtd_operacoes`
- `qtd_vendedores_adquirentes`
- `sistema_origem`
- `sigilo_flag`
- `fonte_arquivo`

### 6.6 `br_comex_bens_audiovisuais`

**Objetivo:** complementar a dimensão externa com bens físicos ligados ao audiovisual, sem confundir com serviços audiovisuais.

**Entradas:**

- MDIC Base de Dados Bruta de importação/exportação.
- Tabela NCM curada para equipamentos, mídias e materiais ligados a cinema, TV, som, projeção, gravação e reprodução.

**Consolidação:**

- Baixar arquivos mensais de exportação/importação.
- Filtrar NCMs do mapa audiovisual.
- Agregar por mês, NCM, país, UF e fluxo.
- Documentar explicitamente que isto mede bens, não serviços, direitos ou licenciamento.

**Parquet final:** `pipelines/output/cleaned/comex_bens_audiovisuais.parquet`

**Colunas mínimas:**

- `ano`
- `mes`
- `fluxo`
- `ncm`
- `ncm_descricao`
- `grupo_bem_audiovisual`
- `pais`
- `uf`
- `valor_fob_usd`
- `kg_liquido`
- `quantidade_estatistica`
- `fonte_arquivo`

### 6.7 `br_embrafilme_historico_exibicao`

**Objetivo:** recuperar as séries históricas pré-ANCINE e pré-SADIS que estão dispersas em PDFs e estudos.

**Entradas:**

- OCA Cinema antigo: tabelas "Espectadores de Filmes Nacionais e Estrangeiros" da Embrafilme, "Arrecadação", "Lugares Oferecidos", por Brasil, região, UF, capitais/interior e municípios, principalmente 1982-1987.
- Notícia ANCINE de 2007 sobre filmes de maior público, que registra a lacuna 1990-1992 e cita o boletim nº 6 da Divisão de Estatísticas da Embrafilme como fonte para 1970-1986.
- Listagens OCA de filmes brasileiros com mais de 500 mil ou 1 milhão de espectadores, quando disponíveis.

**Consolidação:**

- Separar fatos territoriais de fatos por obra.
- Extrair tabelas por OCR/tabula/camelot quando o PDF não tiver texto tabular.
- Criar coluna `confiabilidade = oficial | oficial_compilado | estimado_documentado | nao_oficial`.
- Preservar notas metodológicas por linha.
- Relacionar obras com `obras.parquet` por título normalizado e ano, mas nunca sobrescrever CPB quando ausente.

**Parquets finais:**

- `pipelines/output/cleaned/embrafilme_exibicao_territorio_ano.parquet`
- `pipelines/output/cleaned/embrafilme_filmes_publico.parquet`

**Colunas mínimas territoriais:**

- `ano`
- `territorio_tipo`
- `territorio_nome`
- `uf`
- `regiao`
- `origem_filme`
- `publico`
- `renda_brl_nominal`
- `lugares_oferecidos`
- `fonte_documento`
- `confiabilidade`

**Colunas mínimas por obra:**

- `ano_lancamento`
- `titulo`
- `titulo_normalizado`
- `direcao`
- `produtora`
- `distribuidora`
- `genero`
- `publico_total`
- `fonte_documento`
- `confiabilidade`

### 6.8 `ancine_diversidade_audiovisual`

**Objetivo:** consolidar indicadores de gênero e raça em obras e profissionais quando a informação estiver em estudos OCA e não for recuperável diretamente nos dados abertos.

**Entradas:**

- OCA Outras Publicações: "Estudo Gênero e Raça no Setor Audiovisual 2011-2021".
- Informes de participação feminina na produção audiovisual brasileira.
- Estudos de diversidade em longas-metragens lançados em salas.

**Consolidação:**

- Extrair tabelas dos PDFs.
- Relacionar por título/ano/CPB quando houver.
- Separar dimensão de pessoa, função e obra.
- Marcar método de inferência/classificação usado pelo estudo.

**Parquet final:** `pipelines/output/cleaned/diversidade_audiovisual_obras_profissionais.parquet`

**Colunas mínimas:**

- `ano`
- `titulo`
- `cpb`
- `funcao`
- `grupo_genero`
- `grupo_raca_cor`
- `quantidade`
- `percentual`
- `metodo_classificacao`
- `fonte_documento`

## 7. Datasets opcionais de Dados Abertos que completam o RIDAB

Estes não são o foco "publicações OCA complementares", porque possuem fonte primária em Dados Abertos. Ainda assim, o RIDAB local não os tem e eles completam bem a cobertura.

### `ancine_tv_paga_consolidado`

Entradas: programação de canais de TV paga, carga horária, obras brasileiras veiculadas, canais, programadoras, pacotes credenciados.  
Saídas: `tv_paga_programacao_horas.parquet`, `tv_paga_canais_programadoras.parquet`, `tv_paga_pacotes.parquet`.

### `ancine_salas_complexos_historico`

Entradas: Salas de Exibição e Complexos Registrados, Salas de Exibição - Evolução Anual, Complexos Cinematográficos - Evolução Anual.  
Saída: `salas_complexos_historico.parquet`.

### `ancine_crt_cpb_roe_complementar`

Entradas: CRT obras publicitárias/não publicitárias, obras estrangeiras ROE, CPB, países de origem, elenco quando disponível.  
Saídas: tabelas dimensionais para registro, circulação e certificados, se o objetivo for ampliar além do núcleo atual.

## 8. Extração

### 8.1 Inventário automático

Criar um coletor para páginas OCA:

- `pipelines/extract/oca_inventory.py`
- Entrada: URLs de seção OCA.
- Saída: `datasets/oca_inventory/snapshot=YYYY-MM-DD/oca_links.parquet`.
- Campos: `secao`, `titulo`, `formato`, `data_publicacao`, `ano_referencia`, `url_arquivo`, `extensao`, `pagina_origem`, `hash_conteudo`.

O inventário evita hard-code de links e permite detectar atualização no gov.br.

### 8.2 Snapshot bruto

Padrão de armazenamento:

```text
datasets/<dataset_slug>/raw/snapshot=YYYY-MM-DD/
  manifest.json
  source_urls.csv
  <arquivo_original>.csv
  <arquivo_original>.xlsx
  <arquivo_original>.pdf
```

O `manifest.json` deve conter:

- URL de origem.
- Data/hora de download.
- SHA-256.
- Tamanho.
- Content-Type.
- Última modificação, quando disponível.
- Licença ou nota de uso.

### 8.3 Leitura por formato

- CSV: detectar encoding, separador e decimal; normalizar para UTF-8.
- XLSX: ler planilhas e áreas nomeadas; rejeitar linhas de título/rodapé por regras versionadas.
- PDF tabular: tentar extração de texto; depois camelot/tabula; depois OCR.
- PDF narrativo: usar apenas quando a tabela estiver explícita ou quando o estudo define metodologia.
- HTML de páginas: parsear links e metadados, não copiar texto manualmente.

## 9. Transformação e consolidação

### 9.1 Normalização comum

Aplicar em todos os datasets:

- Colunas em `snake_case`.
- Datas em ISO.
- Moedas com colunas separadas de valor e moeda.
- CNPJ apenas com dígitos em `cnpj_*`.
- UF em sigla.
- Município com `cod_municipio_ibge` sempre que possível.
- Títulos com `titulo_original`, `titulo_brasil`, `titulo_normalizado`.
- Campos de fonte obrigatórios: `fonte_arquivo`, `fonte_url`, `hash_arquivo`, `data_coleta`.

### 9.2 Chaves canônicas

- Empresa: `cnpj`, `registro_ancine`, `razao_social_normalizada`.
- Obra: `cpb`, `roe`, `crt`, `titulo_normalizado`, `ano_producao`, `ano_lancamento`.
- Território: `cod_municipio_ibge`, `uf`, `regiao`.
- Atividade econômica: `cnae_subclasse`, `cnae_classe`, `recorte_metodologico`.
- Tempo: `ano`, `mes`, `data_inicio_periodo`.

### 9.3 Deflação e moedas

- Usar `deflator_ipca.parquet` para BRL real base 2024.
- Manter valores em dólar sem converter quando a fonte original estiver em USD.
- Se houver conversão cambial, usar uma tabela explícita de câmbio com fonte e data.

## 10. Validação

Cada pipeline deve gerar checks automáticos:

- Contagem de linhas por arquivo e por ano.
- Soma de valores contra total publicado no PDF/XLSX.
- Unicidade da chave declarada.
- Percentual de nulos em campos críticos.
- Checagem de CNPJ e UF.
- Checagem de anos fora da cobertura.
- Comparação OCA agregado x parquet granular, quando a tabela OCA for QA.
- Diferença máxima tolerada para valores monetários após parsing: `0.01` na moeda original.

Resultado esperado:

```text
pipelines/output/quality/<dataset_slug>_quality.json
pipelines/output/quality/<dataset_slug>_source_reconciliation.csv
```

## 11. Documentação

Para cada dataset novo:

```text
catalog/schemas/<table>.yaml
docs/datasets/<dataset_slug>.md
datasets/<dataset_slug>/README.md
```

Cada documentação deve conter:

- Descrição curta.
- O que cada linha representa.
- Cobertura temporal.
- Fonte primária.
- Fontes auxiliares.
- Limitações metodológicas.
- Chave primária.
- Campos obrigatórios.
- Como atualizar.
- Exemplos DuckDB.
- Critério de deduplicação.
- Relação com tabelas existentes.

Adicionar em `catalog/datasets.yaml`:

- `slug`
- `title`
- `description`
- `source_id`
- `coverage`
- `tags`
- `raw`
- `cleaned.tables`
- `related`
- `methodology_notes`

Adicionar em `catalog/sources.yaml`:

- `oca`
- `mte_pdet`
- `ibge_pas`
- `ibge_scn`
- `mdic_siscoserv`
- `mdic_comex`
- `ancine_historico_embrafilme`

## 12. Ordem de execução recomendada

### Sprint 1 - Inventário e CONDECINE

- Criar inventário OCA.
- Baixar Dados Financeiros.
- Implementar `condecine_arrecadacao.parquet`.
- Validar séries anual/mensal.

### Sprint 2 - Fluxos de fomento

- Consolidar valores captados, recolhidos, aportados, liberados e executados.
- Cruzar com `renuncia_fiscal` e `fomento_fsa`.
- Documentar o que é fluxo agregado vs projeto.

### Sprint 3 - PIB e emprego

- Criar `dim_cnae_audiovisual`.
- Extrair IBGE PAS/SIDRA.
- Baixar RAIS por ano.
- Gerar PIB/VA e emprego formal agregados.
- Validar contra estudos OCA de valor adicionado e emprego.

### Sprint 4 - Comércio exterior

- Consolidar SISCOSERV/OCA serviços 2014-2019.
- Criar mapa NBS audiovisual.
- Avaliar painel/relatórios MDIC pós-2020.
- Criar Comex bens como dataset separado, com NCM curado.

### Sprint 5 - Histórico Embrafilme

- Inventariar PDFs antigos de cinema/Embrafilme.
- Extrair tabelas com OCR quando necessário.
- Publicar duas tabelas: territorial/ano e filmes/público.
- Marcar confiabilidade por linha.

### Sprint 6 - Complementos opcionais

- TV paga e salas/complexos a partir de Dados Abertos.
- Diversidade de gênero/raça a partir de estudos OCA.
- CRT/CPB/ROE complementares, se o objetivo virar cobertura regulatória ampla.

## 13. Estrutura final esperada

```text
pipelines/
  extract/
    oca_inventory.py
    download_oca_publications.py
    download_rais.py
    download_ibge_pas.py
    download_mdic_siscoserv.py
    download_mdic_comex.py
  transform/
    clean_condecine.py
    clean_fomento_fluxos.py
    clean_pib_audiovisual.py
    clean_rais_audiovisual.py
    clean_comercio_servicos_av.py
    clean_comex_bens_av.py
    clean_embrafilme.py
  output/
    cleaned/
      condecine_arrecadacao.parquet
      fomento_fluxos_financeiros.parquet
      pib_audiovisual_atividade_ano.parquet
      rais_emprego_audiovisual.parquet
      comercio_exterior_servicos_audiovisuais.parquet
      comex_bens_audiovisuais.parquet
      embrafilme_exibicao_territorio_ano.parquet
      embrafilme_filmes_publico.parquet
      diversidade_audiovisual_obras_profissionais.parquet
    quality/
      *.json
      *_source_reconciliation.csv
```

## 14. Pontos de atenção metodológica

- **CONDECINE:** separar arrecadação de títulos, recolhimento, aplicação e renúncia; são fatos financeiros diferentes.
- **PIB audiovisual:** não chamar de PIB oficial setorial se for reconstruído por CNAE/PAS; nome correto é valor adicionado ou proxy de participação no PIB.
- **RAIS:** publicar agregados, não microdados individuais.
- **SISCOSERV:** usar "vendas" e "aquisições" além de exportação/importação, porque a ANCINE alerta que não é plenamente comparável ao Balanço de Pagamentos.
- **Comex bens:** manter separado de serviços audiovisuais.
- **Embrafilme:** nunca misturar dado oficial, compilado e estimado sem a coluna de confiabilidade.
- **OCA agregados:** quando a fonte completa está em Dados Abertos, o OCA deve servir para reconciliação, não para duplicar tabelas.

## 15. Próxima ação concreta

Começar por `ancine_condecine_arrecadacao`, porque:

- Não existe no RIDAB atual.
- Está em CSV/XLSX no OCA.
- Tem alta relevância tributária.
- Usa infraestrutura já existente: download, limpeza tabular, deflator IPCA e catálogo.

Depois, seguir para `ancine_fomento_fluxos_financeiros`, porque ele complementa `renuncia_fiscal` e `fomento_fsa` sem duplicar esses parquets.

