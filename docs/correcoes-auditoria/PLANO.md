# Plano de execução das correções do RIDAB

Referência: auditoria de 08/09/2026, site https://riabr-dados.github.io/riab/ e repositório https://github.com/riabr-dados/riab.

Pasta confirmada: `C:/Users/INTEL/Desktop/dados-audiovisual-br`.

**Escolha do agente.** Recomendo Codex com GPT-6 Astra para executar neste ambiente, com esforço alto nas correções de dados e extra alto nas decisões de modelagem mais ambíguas. A vantagem específica é a continuidade: repositório, originais, comparações e evidências já estão disponíveis. Não foi feito um teste comparativo Codex versus Claude neste projeto; portanto, esta recomendação não estabelece superioridade geral. Claude Code com Opus 5 é uma alternativa adequada para executar este mesmo plano e uma boa escolha para revisão independente. Se o usuário já tiver acesso apenas ao Claude, não há evidência nesta auditoria que justifique comprar outra assinatura.

A documentação da OpenAI recomenda Astra para trabalhos complexos que envolvem várias etapas e ferramentas; a Anthropic apresenta Opus 5 para programação e trabalhos longos com agentes. Essas são descrições dos fabricantes, não uma avaliação comparativa independente. Fontes consultadas em 08/09/2026: [modelos da OpenAI](https://learn.chatgpt.com/docs/models) e [Claude Opus](https://www.anthropic.com/claude/opus). Disponibilidade depende da conta. A configuração de esforço acima é uma recomendação operacional, sem medição de custo ou tempo neste repositório.

**Objetivo e alcance.** Corrigir e tornar reproduzível a cadeia origem → bruto preservado → tabela tratada → catálogo → download. Cobrir os 99 registros atuais, incluindo 94 publicados e 5 ocultos, de todas as procedências. A separação de conjuntos pode aumentar o número de cartões e recursos; não preservar artificialmente a contagem de 99. A auditoria encontrou 45 registros classificados como Corrigir, 14 Atualizar, 27 Melhorar, 11 Não conclusivo e 2 Documental. Essas categorias são prioridades de trabalho, não uma contagem de erros independentes.

**Entradas obrigatórias.** Ler `Auditoria_completa_RIDAB_2026-09-08.xlsx`, principalmente Datasets, Recursos, Grupos e Cobertura PDA; usar `report_data.json`, `cleaned_validation.json`, `global_analysis.json` e `bilheteria_comparison.json` para localizar evidências. Os arquivos estão nesta mesma pasta. Preservar o relatório original e produzir nova versão ao final. Não tratar os scripts exploratórios da auditoria como validadores de produção prontos: revisar regras e reproduzir cada achado antes de corrigir.

**1. Fixar a referência e transformar a auditoria em tarefas rastreáveis.**

Registrar o commit inicial, a versão do catálogo publicado e a data dos arquivos baixados. Trabalhar em uma branch de correções, preservando alterações existentes. Aproveitar downloads já concluídos, conferindo integridade antes de reutilizá-los. Criar uma lista de tarefas com identificador do achado, dataset, recurso, evidência, mudança proposta, teste de aceitação e situação. Manter o vínculo de cada um dos 99 registros com sua destinação, mesmo quando um cartão virar vários.

Separar duas perguntas na validação: o tratamento reproduz corretamente o bruto daquela versão? A versão do bruto está atualizada em relação à fonte? Comparar versões diferentes sem essa distinção pode confundir atualização com corrupção.

Entrega: referência reproduzível e lista completa de tarefas. Aceite: todos os 99 registros têm destinação e critério de encerramento; nenhuma pendência some por renomeação ou divisão de cartão.

**2. Corrigir primeiro as perdas de dados P0.**

Em `pipelines/transform/clean_renuncia.py`, corrigir a conversão dos 18 campos monetários: moeda, separadores brasileiros, espaços, zeros e ausências. Preferir representação decimal exata ou centavos quando compatível com o restante da cadeia. Não substituir falhas de leitura por zero. Registrar valores não interpretados e impedir a publicação silenciosa de uma coluna que perdeu seus valores.

Reprocessar primeiro o mesmo bruto que gerou os 4.215 registros auditados. Comparar os 18 campos célula a célula com uma referência obtida independentemente da função corrigida. Só depois incorporar a origem mais recente, cuja contagem pode mudar novamente desde a auditoria. Uma soma de controle é complementar; sozinha não comprova fidelidade.

Em `pipelines/transform/clean_oca_complementos.py`, restaurar nomes e identificadores disponíveis nas três fontes de captação. Preservar CNPJ como texto, incluindo zeros iniciais, sem inventar CNPJ quando o original traz apenas um nome. Definir três recursos distintos: aportes por investidor, captação por projeto e investidor, e captação por projeto. Preservar datas, UF e demais campos pertinentes à unidade de cada tabela. Auditar as 150.917 linhas antigas e justificar qualquer diferença após a correção.

Entrega: recursos corrigidos e testes de regressão com exemplos reais. Aceite: nenhum valor monetário interpretável é perdido; todos os identificadores presentes na origem têm correspondência rastreável; campos ausentes na origem permanecem explicitamente ausentes.

**3. Definir e aplicar a separação dos conjuntos.**

Para cada recurso, escrever o que uma linha representa, quais são as chaves, o período, as medidas, as unidades e a procedência. Usar `catalog/datasets.yaml`, os esquemas existentes e `catalog/joins.yaml`. Evitar uma migração geral de arquitetura quando uma alteração localizada resolver o problema.

Separar fluxos de fomento em captado, liberado e editais. Separar totais anuais e detalhes mensais da Condecine, além dos recortes com unidades distintas. Nos dados BFI e CNC, mapear cada tabela ou bloco relevante do original; remover títulos, notas e rodapés das linhas factuais e preservá-los como documentação. Harmonizar cabeçalhos e tipos antes de concatenar anos. Verificar abas não representadas, especialmente quando o tratamento atual seleciona apenas a primeira.

Regra editorial: um cartão deve representar um conjunto coerente e oferecer downloads independentes por tabela. Quando houver conceitos independentes, criar cartões próprios, eventualmente agrupados numa coleção. Um Excel pode incluir uma tabela de dados e seu dicionário; não deve reunir várias tabelas factuais independentes no mesmo download. Anos da mesma tabela podem ser unidos com uma coluna de ano. Indicadores diferentes só podem compartilhar uma estrutura longa se unidade, definição e chave forem explícitas e isso fizer sentido analítico.

Entrega: mapa cartão antigo → cartões e recursos novos, dicionários e tratamentos atualizados. Aceite: cada recurso tem unidade de observação inequívoca; não mistura totais e detalhes de modo que induza dupla contagem; links antigos continuam levando a uma página que explica a mudança.

**4. Atualizar as fontes e fechar as comparações restantes.**

Revisar as demais correções do PDA, inclusive títulos literais `NA` convertidos em ausência. Definir tokens de ausência por campo e fonte; não aplicar uma substituição global de `NA`/`N/A`. Preservar codificação, datas, códigos e identificadores.

Na bilheteria, incorporar os arquivos novos e as revisões dos existentes. A auditoria encontrou 19 arquivos novos na origem; verificar a situação na data da execução. Publicar os detalhes diários particionados e manter agregados anuais como produtos separados. Conferir público e renda por partição e ano. Revisar a coluna `sessoes`: contagem de linhas não comprova contagem de sessões. Usar essa denominação somente se a definição da origem sustentar o cálculo.

Em CNC, BFI, ACAU, INCAA, Lumiere e demais bases brasileiras, validar a fidelidade em todas as tabelas, incluindo as que tiveram somente conferência estrutural ou de arquivos na primeira auditoria. Para extrações de PDF, comparar totais e amostras documentadas em cada tabela, com revisão visual dos blocos ambíguos. Nos dados derivados, documentar e testar fórmulas, filtros e denominadores. Preservar moedas e unidades originais; qualquer conversão deve ser um produto documentado separado.

Tentar recuperar os nove CSVs argentinos por rotas oficiais e refazer as exportações Lumiere com filtros e cobertura documentados. Quando a origem continuar inacessível, manter o último arquivo rastreável e registrar a limitação. Não declarar equivalência, completude ou atualização por inferência.

Entrega: manifestos com URL, data, hash, versão, cobertura, transformações e resultado das comparações. Aceite: cada recurso é validado ou tem uma pendência concreta, visível e justificada. A correção do projeto não depende de fingir que uma fonte externa bloqueada foi validada.

**5. Entregar downloads completos e trabalháveis.**

Atualizar `portal/src/pages/datasets/[slug].astro`, `portal/src/components/DataExplorer.astro`, `portal/src/lib/hf.js` e a leitura do catálogo conforme necessário. Cada recurso deve apontar para o arquivo exato, não apenas para uma pasta de arquivos brutos.

Oferecer CSV integral em UTF-8, XLSX quando o tamanho permitir e Parquet como alternativa analítica. Para bases grandes, disponibilizar partições identificadas por período, com arquivos completos e manifesto. Nunca cortar silenciosamente os dados para caber no Excel. Garantir que identificadores permaneçam texto no XLSX; documentar tipos e importação do CSV. Não alterar o conteúdo factual para contornar a interpretação automática do Excel.

Distinguir claramente “Baixar tabela completa” e “Exportar resultado da consulta”. Mostrar a quantidade de linhas retornadas e avisar quando a prévia ou consulta usa limite. XLSX deve ter uma única tabela factual, filtros, cabeçalho e dicionário acessível. Mostrar período, atualização, fonte e tamanho do download.

Entrega: catálogo e interface atualizados, arquivos de distribuição gerados. Aceite: baixar e reabrir os arquivos verifica a mesma quantidade de registros e o mesmo conteúdo lógico do recurso canônico; testar todos os links publicados automaticamente e o fluxo de navegador em casos representativos, incluindo tabela grande, dividida e consulta limitada.

**6. Fazer a atualização automática buscar dados novos e validar antes de publicar.**

Ajustar `.github/workflows/update-data.yml`: hoje o fluxo transforma snapshots locais e publica; falta uma etapa explícita de obtenção de fontes novas. Implementar coleta → preservação do bruto → transformação → validação → geração dos downloads → publicação da versão aprovada → atualização do catálogo. Fazer o seletor de dataset realmente restringir a execução quando utilizado.

Adicionar retomada, cache, tentativas limitadas e detecção de respostas HTML disfarçadas de planilha. Registrar revisões retroativas das fontes. Bloquear publicação do recurso afetado quando houver perda inesperada de valores, mudança incompatível de esquema, arquivo incompleto ou comparação reprovada. Uma falha de origem deve preservar a última versão válida e registrar a data da tentativa, sem alterar falsamente a data de atualização dos dados.

Entrega: fluxo reproduzível, validações e histórico por versão. Aceite: executar duas vezes com a mesma origem produz o mesmo conteúdo lógico; uma origem alterada é detectada; uma falha simulada não substitui dados válidos por dados vazios.

**7. Reauditar, revisar e preparar a publicação.**

Dividir as alterações em entregas revisáveis: P0; catálogo e separações; demais fontes e bilheteria; downloads; automação. Para cada entrega, anexar o problema reproduzido, a diferença antes/depois e os testes. Executar os testes Python pertinentes e o build do portal. Revisar joins, consultas e páginas que dependam dos recursos renomeados.

Se houver segundo agente disponível, pedir revisão independente dos P0 e das regras de agregação, com acesso aos originais e aos testes. Essa revisão é opcional e não substitui a reconciliação dos dados. Um teste comparativo entre Codex e Claude, se desejado, deve usar a mesma correção de Renúncia Fiscal, a mesma referência e os mesmos critérios, medindo fidelidade, regressões, tempo e intervenções; não somente qualidade aparente do código.

Gerar novo Excel com situação anterior, situação final, recursos substitutos, testes executados, evidências e pendências externas. Preparar uma versão de demonstração e instruções para retornar à versão anterior. A execução inicial deste plano termina com código, dados e relatório prontos para revisão; publicar a versão pública quando essa ação estiver autorizada.

**Critérios finais de conclusão.** Os P0 foram resolvidos com comparação independente; cada conjunto tem destinação rastreável; nenhuma tabela mistura conceitos incompatíveis; downloads completos foram reabertos e conferidos; atualizações não podem publicar perdas silenciosas; as limitações restantes estão identificadas por fonte e recurso. “OK” só se aplica ao escopo efetivamente verificado. Não marcar o projeto inteiro como plenamente validado enquanto houver comparações materiais não concluídas.

**Instrução de partida para Codex ou Claude Code.**

> Execute este plano no repositório informado. Comece lendo o Excel e as evidências locais, confirme cada achado e implemente primeiro as duas correções P0. Preserve os originais e alterações existentes. Entregue correções acompanhadas de comparações de dados e testes que detectem a perda observada. Depois avance pelas etapas restantes, mantendo uma lista de progresso por dataset. Use os critérios de aceite para decidir quando uma etapa terminou. Não invente dados ou declare verificações que não executou. Quando uma fonte estiver bloqueada, registre a pendência e prossiga com o trabalho independente. Prepare a versão revisável antes da publicação pública.
