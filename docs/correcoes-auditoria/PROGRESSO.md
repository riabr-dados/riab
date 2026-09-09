# Execução da auditoria RIDAB

Autorização: executar todas as correções do plano de 08/09/2026. O usuário fará o push no GitHub somente depois da entrega completa. Nenhum dado foi publicado no Hugging Face ou no site durante a implementação.

## Resultado consolidado

- Os 99 registros da auditoria inicial foram reavaliados: 86 estão **Concluídos**, 9 **Concluídos com limitação**, 2 **Documentados** e 2 dependem de ação externa.
- O catálogo contém 112 datasets, dos quais 110 estão publicados, com 471 recursos independentes e 1.019 arquivos de download descritos no manifesto.
- Renúncia Fiscal foi corrigida e reconciliada com 4.315 linhas. Captação foi separada em três tabelas coerentes, com 5.326 projetos, 5.281 combinações projeto-mecanismo e 18.104 combinações projeto-investidor.
- O conjunto editorial passou a usar o nome **Valores Captados/Contratados por Mecanismo**.
- O bloco OCA passou a publicar 16 recursos factuais separados. O BFI passou a publicar 98 tabelas independentes e o CNC, 243 tabelas, preservando arquivo, aba, data e hash da origem.
- Dezesseis conjuntos do PDA da ANCINE receberam snapshots oficiais atuais, foram reprocessados e tiveram proveniência registrada. As correções de valores ausentes preservam identificadores como texto.
- A bilheteria diária foi refeita diretamente dos ZIPs oficiais em UTF-8. Foram preservadas 21.274.038 linhas de distribuidoras e 37.672.799 de exibidoras, particionadas por ano de 2014 a 2026, além de quatro agregados derivados. A contagem dos agregados chama-se `registros_reportados`, pois mede linhas da fonte.
- Todos os recursos publicados têm Parquet, esquema com ordem de colunas compatível e download independente. Tabelas muito grandes usam CSV.GZ particionado; tabelas de até 100 mil linhas também recebem XLSX.
- O portal identifica tabelas derivadas, apresenta suas fontes e scripts de transformação e explica como extrair CSV.GZ.
- A coleta automática busca e transforma a bilheteria diária, recompõe os downloads e executa os testes antes da etapa de envio ao Hugging Face.

## Limitações registradas

- Nove séries argentinas tiveram metadados, cobertura e esquema conferidos no portal oficial do SINCA. O host de arquivos apresentou verificação humana do Cloudflare e impediu a comparação binária automatizada em 09/09/2026. A correção local está concluída e a repetição dessa comparação ficou documentada.
- As duas bases Lumiere continuam acessíveis, mas os snapshots antigos não registram filtros, universo, paginação e data da consulta. Elas precisam ser reexportadas na origem para que a completude possa ser provada.
- `oca-publicacoes-complementares` e `br-comex-bens-audiovisuais` são itens documentais/de planejamento e permanecem fora das contagens de recursos factuais publicados.

## Entregáveis

- Plano e evidências de origem: `outputs/auditoria-pda-20260908/`.
- Acompanhamento por dataset: `docs/correcoes-auditoria/tarefas.csv`.
- Catálogo de downloads com hashes: `catalog/downloads.json`.
- Auditoria das fontes argentinas: `catalog/incaa_sources.yaml`.
- Excel final: `outputs/01a0827c-c716-7520-b995-a3be53ec857e/Auditoria_RIDAB_final_2026-09-09.xlsx`.

A validação final exige a suíte completa de testes, a compilação do portal, a verificação de diferenças do Git e um commit limpo. O push permanece reservado ao usuário.
