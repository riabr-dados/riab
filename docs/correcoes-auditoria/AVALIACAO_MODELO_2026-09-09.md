# Reavaliação do modelo após o limite de uso

Execução observada: turno iniciado em 08/09/2026 às 23:23:46 UTC e interrompido às 23:46:27 UTC. Modelo registrado: gpt-6-astra, esforço high. Duração aproximada: 22 minutos e 41 segundos.

Contadores da conta durante o turno: janela de cinco horas de 36% para 100% (+64 pontos percentuais); semanal de 21% para 31% (+10 pontos). São limites compartilhados da conta, não uma fatura exclusiva deste projeto. Não há medição comparativa com Sol, Terra ou Claude. Não converter esses percentuais para reais ou dólares.

Variação da telemetria de tokens do turno: 4.420.958 tokens de entrada acumulados entre chamadas, dos quais 4.263.296 em cache (96,4%), e 27.549 de saída. Entrada sem cache: 157.662. Esses valores incluem reapresentação do contexto, não representam texto novo nessa quantidade. A entrada por chamada cresceu aproximadamente de 83.715 para 161.609 tokens (1,93 vez). Não é possível determinar, somente por esses contadores, quanto da cota foi causado pelo modelo, contexto, esforço ou outras regras de consumo.

Resultados observados: Renúncia Fiscal corrigida e atualizada para 4.315 linhas; três fontes de captação separadas, com 5.326, 5.281 e 18.104 linhas; correções dos leitores que apagavam NA/N/A em sete conjuntos; CSV/XLSX gerados para quatro recursos; alterações no portal e verificação visual da página local; proteção inicial contra publicar downloads incompletos/desatualizados. A execução integral de testes iniciada antes do limite terminou com 34 testes aprovados em 51,05 segundos, resultado recuperado em 09/09. Um build passou durante a sessão, mas houve alterações posteriores que ainda precisam de novo build.

Cobertura: correções dirigidas a nove dos 99 registros originais (9,1% dos registros, não 9,1% de conclusão ponderada do projeto). Quatro dos 127 recursos do catálogo atual têm downloads gerados (3,1%). O gerador é reaproveitável, portanto essa fração não representa a proporção do esforço de exportação já realizado. A revisão final dos conjuntos e os demais blocos continuam pendentes. Nenhum push/publicação foi feito.

Conclusão: a sessão demonstra utilidade técnica do Astra, mas não demonstra melhor custo-benefício. Retiro a recomendação de Astra como executor único do projeto. Próxima configuração sugerida: GPT-5.6 Sol em Medium para lotes bem definidos; Astra para decisões difíceis e revisão crítica, quando necessário. Essa escolha é uma hipótese operacional a validar, não uma economia percentual já demonstrada.

Procedimento para medir: antes e depois de um lote, registrar modelo/esforço, duração, variação de cota sem reset no intervalo, tarefas aceitas, testes e retrabalho. Evitar outras tarefas na mesma janela de medição. Usar um lote real de complexidade comparável; comparar qualidade antes de consumo. Não repetir toda a implementação apenas para criar um benchmark. Atualizar o progresso ao concluir cada lote e carregar somente as evidências necessárias.

Parte do custo pode vir do método utilizado: leituras extensas, contexto crescente e mudanças em múltiplas frentes antes de concluir a revisão do lote. Trocar somente o modelo não corrige isso. O plano e os arquivos permitem continuidade com outro modelo no mesmo projeto.

Referência de seleção: https://learn.chatgpt.com/docs/models (consultada em 09/09/2026), que recomenda usar o menor esforço suficiente. Nenhum modelo foi alterado automaticamente nesta reavaliação.
