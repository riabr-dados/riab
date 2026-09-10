# Analisar — preservação de funcionalidades e dinamismo

Complemento obrigatório de `docs/PLANO-UX-PORTAL-SOL.md`.

## 1. Instrução do usuário e efeito sobre o plano

O usuário viu um print da proposta e reforçou: **não perder o dinamismo nem qualquer requisito**. A proposta visual não é uma especificação exaustiva e não autoriza uma versão reduzida da aplicação. Esta instrução prevalece sobre qualquer interpretação de “simplificar”, “avançado” ou “primeira entrega” que elimine funções já disponíveis.

Unificar significa compartilhar seleção, consulta, resultados e contexto. A pessoa deve continuar podendo descobrir conexões no grafo, clicar nas tabelas, montar e alterar uma consulta, manipular campos, experimentar filtros e alternar representações. Não entregar só cartões ligados por uma linha fixa, um assistente de passos obrigatórios ou um gráfico com dois filtros predefinidos.

Os itens abaixo foram identificados por leitura do código em `a5134af`. Isso é um inventário inicial, **não evidência de que todos funcionaram em teste de navegador**. O executor deve observar a interface antes da migração e completar a matriz. Funções encontradas no uso e ausentes aqui também devem ser preservadas.

## 2. Comportamento da nova tela

Manter três modos visíveis, sem precisar sair da análise:

- **Montar análise:** biblioteca de tabelas, seleção de campos, montagem/conexões, filtros e resultado.
- **Receitas prontas:** perguntas existentes com dimensões e medidas ajustáveis; abrir uma receita preserva a possibilidade de personalizá-la e inspecionar SQL.
- **Diagrama de relações:** grafo vivo, filtrável, selecionável e reorganizável. Identificar uma relação pode levar à montagem correspondente.

O estado da análise e o estado visual do grafo são relacionados, mas distintos. Mover um nó ou ajustar zoom não deve executar consulta SQL. Alterar coluna ou conexão deve atualizar imediatamente a montagem/SQL gerado e invalidar o resultado, calculando novamente apenas conforme o controle de execução apropriado. Em consultas rápidas, preservar a atualização automática existente com debounce e cancelamento; em consultas pesadas, indicar “resultado precisa ser atualizado” com botão acessível.

Ao trocar de modo, preservar tabela selecionada, filtros, medidas, SQL em edição e resultado correspondente. No grafo, preservar seleção, filtros, zoom e posições durante a sessão, salvo “Reorganizar”. Se abrir outra receita substituir o trabalho, disponibilizar desfazer/recuperar a montagem anterior.

No desktop, manter arraste onde já existe; no celular e teclado, oferecer operações equivalentes. A alternativa acessível complementa o gesto, não é motivo para removê-lo do desktop.

O diagrama é uma das características centrais do produto: deve estar a um clique, com área de trabalho suficiente. Explicações metodológicas podem ser recolhidas; a capacidade de interagir com os dados não pode desaparecer atrás delas.

## 3. Matriz mínima de equivalência

Para cada linha, acrescentar no progresso: **observado no original / destino implementado / teste executado / resultado / evidência**. Não marcar aprovado só porque o código foi movido. Itens que dependem de terceiros podem ter teste de interface/contrato separado da chamada real, com limitação registrada.

| ID | Capacidade a preservar | Origem no código | Aceite no novo Analisar |
|---|---|---|---|
| A01 | Escolher tabela entre todas as publicadas | Explorar: `loadTable`; Transformar: catálogo | Nenhuma restrição aos três pilotos; IDs e nomes distinguíveis |
| A02 | Buscar tabelas e filtrar por chave/país | `renderBuilderCatalog`, filtros do construtor | Filtros combináveis, estado visível e limpeza fácil |
| A03 | Consultar descrição e tipos dos campos | Explorar: `renderFields`; schemas | Contexto continua acessível ao escolher campo |
| A04 | Buscar campo | Explorar: `fp-search` | Busca funciona dentro da tabela/seleção atual |
| A05 | Arrastar campo para colunas, filtros e ordenação | Explorar: `initDropZones` | Arraste real com feedback; alternativa por botão/teclado |
| A06 | Adicionar todas as colunas e remover uma seleção | Explorar: `btn-cols-all`, chips | Seleção completa e remoção individual mantidas |
| A07 | Ordenar ascendente/descendente | Explorar: zona de sort; Transformar: cabeçalhos | Ordenação tipada, direção visível, recorte de ordenação explícito |
| A08 | Operadores compatíveis com tipo, nulos, texto e números | Explorar: `renderFilters`; Transformar: `colKind` | Cobrir todos os operadores ativos iniciais, sem coerção errada de IDs |
| A09 | Limites de exibição e opção “Tudo” | Ambas as páginas | Preservar capacidade sem truncamento silencioso; volume tem feedback/cancelamento |
| A10 | Acrescentar/remover várias tabelas | `addToTrail`, `removeFromTrail` | Montagem e sugestões mudam na hora; referências inválidas são tratadas |
| A11 | Sugerir conexão e explicar chave | `renderBuilderTrail`, `KEY_REGULATION` | Relação selecionável, colunas concretas, sem garantia fictícia de identidade |
| A12 | Selecionar colunas sem obrigar agregação | `buildBuilderSQL` | Consulta de linhas continua possível |
| A13 | Agrupar e adicionar múltiplas métricas | `renderBuilderMetrics`, `renderAggPane` | Preservar operações disponíveis, incluindo COUNT, COUNT DISTINCT, SUM e AVG; inventariar opções ativas adicionais |
| A14 | Editar e executar SQL livre | Explorar e DataExplorer | Editor, execução, cópia e retorno à montagem preservada |
| A15 | Atalho Ctrl+Enter | Explorar/DataExplorer | Atalho executa o editor ativo e não outro contexto |
| A16 | SQL gerado inspecionável/copiável | Transformar: painel SQL | Corresponde ao resultado/estado exibido |
| A17 | Pergunta em português gera SQL | Três interfaces atuais | Acesso opcional, contexto correto e edição antes de reexecutar |
| A18 | Integrações existentes Gemini, Anthropic e OpenAI | Transformar: `nlGenerateSQL` | Preservar opções; não exigir uso de IA para os demais fluxos |
| A19 | Receitas prontas e seus agrupamentos | Array `CRZ` | Todos os IDs e perguntas inventariados têm destino funcional |
| A20 | Refinar receita por dimensão, medida e busca | `ref-dim`, `ref-metric`, `ref-search` | Alterar agrupamento/medida recalcula sem reconstruir a receita |
| A21 | Alternar resultado em tabela e gráfico | `renderView` | Mesmo resultado, sem perder filtros |
| A22 | Barras horizontais, verticais e linha | `renderChart`, `chart-type-bar` | Três opções preservadas quando adequadas; unidade/eixo corretos |
| A23 | Ordenar tabela pelo cabeçalho e ver valores | `renderTable`, `sortedRows` | Tipo respeitado, sem chamar ordenação só da amostra de ordenação global |
| A24 | Exportar resultado completo da consulta | Transformar: `btn-csv`, `stripLimit` | Exportação além da prévia preservada e claramente diferenciada do recorte exibido |
| A25 | CSV do resultado exibido e downloads completos da tabela | Explorar/DataExplorer/ResourceDownloads | Ações distintas; partes de CSV e XLSX mantidas |
| A26 | Estado de carregamento, erro, tempo e quantidade | Barras de status e resultados | Feedback contextual, sem apagar configuração após falha |
| G01 | Ver todo o grafo e selecionar tabela/nó | Transformar: `initDiagram`; Conexões | Grafo interativo real; nós correspondem a tabelas |
| G02 | Destacar vizinhos e limpar seleção | `updateVisibility`; Conexões: `selectNode` | Clique destaca relações, novo clique/fundo limpa conforme padrão |
| G03 | Arrastar nós e reorganizar posições | Transformar: handlers de nós; Cytoscape em Conexões | Nó acompanha gesto, arestas acompanham nó; arraste não dispara clique acidental |
| G04 | Pan e zoom por rolagem e controles | Transformar: `zoomAt`, `applyZoom`; Conexões | Movimento fluido e coordenadas corretas após zoom |
| G05 | Recentrar/reorganizar | `diag-zoom-reset`, Conexões: `reset` | Recupera enquadramento utilizável |
| G06 | Filtros por chave e origem | Ambos os diagramas | Legenda e estado dos filtros presentes; combinação preservada |
| G07 | Filtro “só fortes” e seleção de todas as chaves | Conexões: `only-strong`, `all-keys` | Atalho equivalente; distinguir força heurística de revisão editorial |
| G08 | Tooltip de tabela/chaves e explicação de chave | Transformar: tooltip/keypop | Conteúdo acessível também por foco/clique, sem depender só de hover |
| G09 | Selecionar aresta e ver colunas concretas | Conexões: `selectEdge` | Detalhe mostra o par de tabelas e campos relacionados |
| G10 | Busca e foco no nó encontrado | Conexões: busca/`cy.animate` | Buscar localiza e destaca a tabela no diagrama |
| G11 | Layouts Orgânico, Concêntrico e Físico | Conexões: `layoutCfg`, botões | Manter na rota atual ou prover equivalente funcional explícito no ambiente consolidado |
| G12 | Tamanho dos nós associado ao volume e contagens | Transformar: `fetchRowCounts`, `radiusFromRows` | Preservar informação com legenda; usar manifesto/cache para evitar leituras desnecessárias |
| G13 | Identificação visual de origem e tipo de chave | Ambos os diagramas | Legenda legível, com texto para complementar cor |
| C01 | Seletor de recurso, contexto e consultas relacionadas | Dataset/DataExplorer e eventos `riab:*` | Troca de tabela mantém coerência entre contexto, schema, download e análise |
| C02 | Documentação sobre identificação, normalização e métodos | Links/contexto nas páginas | Continua acessível sem perder a análise |
| C03 | Rotas Explorar, Transformar, Conexões e detalhes | Rotas existentes | Entrada antiga chega ao recurso/contexto correspondente ou fallback claro |

**Nota sobre inventário:** “Campos livres” no fim de Transformar está em bloco legado comentado. Não contar código morto como funcionalidade ativa e não reativá-lo por acidente. As capacidades de escolher campos no construtor atual estão cobertas por A03–A13.

## 4. Receitas existentes que não podem desaparecer

IDs encontrados no array ativo `CRZ`, a conferir no início da implementação:

| ID estável | Título no código revisado |
|---|---|
| `obras-serie` | 25 anos de produção |
| `quem-dirige` | Quem dirige o Brasil |
| `ficha-tecnica` | Obra + diretor + produtora |
| `obras-bilheteria` | Do registro à tela |
| `br-eu` | Brasil nas telas da Europa |
| `embrafilme-historico` | Cinema antes do mercado |
| `obras-fsa` | Onde vai o FSA |
| `fsa-publico` | FSA que chegou ao público |
| `festivais-fsa` | Premiações internacionais |
| `obras-renuncia` | Lei do Audiovisual |
| `condecine-arrecadacao` | A conta do setor |
| `fluxos-fomento` | Valores captados/contratados |

Preservar IDs para compatibilidade, ainda que o texto exibido seja melhorado. Para o último, usar a preferência expressa do usuário: **Valores Captados/Contratados por mecanismo**. Não reintroduzir “fluxo financeiro” como rótulo do produto.

As receitas devem manter dimensões e medidas alternativas. Preservar a pergunta/possibilidade de análise não significa repetir um erro de soma: quando houver duplicidade de junção, mistura de unidades ou período enganoso, corrigir a consulta e explicar o recorte. Registrar comparação antes/depois e a causa, em vez de retirar a receita ou fingir que os números são equivalentes.

Os dados de festivais obtidos de fontes brasileiras continuam nas receitas e datasets correspondentes. A curadoria Brasil no Mundo pode distinguir sua procedência sem remover esses dados do ambiente de análise.

## 5. O que pode mudar sem reduzir capacidade

- Nome e localização dos controles podem mudar para melhorar clareza. Função deve continuar fácil de encontrar e com destino documentado na matriz.
- Dois códigos que fazem a mesma coisa podem virar um componente. A possibilidade de executar a tarefa por uma entrada já usada precisa ser mantida por integração ou rota compatível.
- Diagrama pode ser carregado sob demanda, sem eliminar zoom, arraste, layouts e informação de volume. Cache/manifesto substituem consultas redundantes, não a informação que elas forneciam.
- Diagnóstico aparece junto à conexão e pode ser recolhido após verificação. Conexão já verificada não pede confirmação a cada clique; mudanças relevantes invalidam o diagnóstico.
- Gráficos precisam informar o recorte: atualmente existe corte de 40 linhas no renderizador. Pode ser corrigido com paginação/seleção/top N explícito, preservando a capacidade de visualizar e exportar o resultado completo.
- Execuções pesadas podem usar limite inicial, cancelamento e aviso de volume. Não perder a opção de consultar/exportar tudo silenciosamente.

Não é requisito preservar um produto cartesiano acidental, uma soma duplicada ou uma falha de exportação. Essas correções devem preservar a intenção da tarefa e ser demonstradas com testes. Se houver dúvida real sobre retirar uma função deliberada, mantê-la em sua rota atual enquanto a alternativa é concluída; não remover unilateralmente.

## 6. Roteiros de demonstração dinâmica antes de substituir as abas

**R1 — Manipular campos de uma tabela**

Abrir um dataset → selecionar tabela → abrir Analisar → buscar um campo → arrastar para colunas → arrastar outro para filtro → alterar valor → escolher ordenação → executar → alternar tabela/barras/linha quando adequado → abrir SQL → exportar linhas exibidas e resultado completo. Verificar que o CSV completo tem as linhas esperadas além do limite da prévia. Repetir as operações essenciais sem arraste.

**R2 — Explorar e manipular o grafo**

Abrir Diagrama → filtrar origem e chave → buscar tabela → selecionar nó e observar vizinhos → arrastar nó com zoom aplicado → mover o canvas → selecionar aresta e ler campos → trocar layout → recentrar → adicionar relação à montagem. Voltar ao diagrama e verificar preservação de contexto durante a sessão. Se os layouts continuarem na rota Conexões, testar também essa entrada e seu retorno ao Analisar.

**R3 — Construir e alterar uma conexão real**

Escolher primeira tabela → adicionar segunda → conferir sugestão e escolher chave → observar ligação e diagnóstico → adicionar campos/medida → executar → mudar filtro → ver invalidação e recalcular → remover segunda tabela → desfazer. Não basta que os cartões mudem de cor: SQL, resultado e exportação precisam refletir a montagem.

**R4 — Refinar receita existente**

Abrir uma receita de produção e outra de fomento → alternar dimensões e medidas → pesquisar no recorte → atualizar → ordenar pelo cabeçalho → mudar orientação do gráfico → copiar SQL. Conferir as doze receitas por inventário e executar consultas representativas de cada padrão de junção/medida, além de validar campos de todas.

**R5 — Continuidade e modo avançado**

Modificar uma montagem → alternar Montar/Receitas/Diagrama sem perda silenciosa → editar SQL → executar por Ctrl+Enter → voltar ao estado visual preservado → salvar → recarregar → restaurar. Para IA, testar escolha dos três provedores e tratamento de credencial/erro; chamada real somente com credencial já autorizada, sem gravá-la em evidências ou receitas.

## 7. Evidência exigida e condição de conclusão

A entrega deve ter uma **prévia realmente navegável**, com os roteiros acima reproduzíveis, além dos prints. Gravação curta pode complementar, caso a ferramenta esteja disponível; não é necessário gastar tempo construindo infraestrutura de vídeo. Documentar URL/comando de inicialização e passos de uso para que a demonstração sobreviva à queda do servidor local.

Usar testes de navegador para ações e estado: arraste muda posição/seleção; zoom/pan alteram viewport; clicar numa chave muda visibilidade; alterar montagem muda consulta/resultado; CSV completo confere com a consulta. Prints sozinhos não verificam isso.

Não exigir que o usuário descubra a regressão após publicação. Para cada requisito, apresentar evidência e destino. Pendência ou integração não testada fica declarada, sem ser marcada como concluída. Se uma função ainda não foi migrada, sua implementação atual continua acessível; a unificação integral só é considerada pronta após terminar a matriz.

**Condição adicional de pronto:** o usuário consegue fazer as tarefas que já fazia, preservando a interação direta com tabelas e conexões, e encontra os novos recursos sem perder os anteriores.

## 8. Destino executado

A migração adotou uma transição compatível: `/analisar/` concentra descoberta, construção, receitas e diagrama; `/explorar/` permanece como quarto modo para as operações avançadas de campos e SQL. Assim, a nova entrada não reduz a interface dinâmica já publicada enquanto a base de código ainda possui dois motores especializados.

| Grupo | Destino | Evidência desta entrega |
|---|---|---|
| A01–A02 | Catálogo do construtor em `/analisar/` | 471 tabelas; busca; filtros por chave e país; carregamento progressivo e limpeza de filtros testados no navegador |
| A03–A09 | Quarto modo `/explorar/` com tabela na URL | Implementação anterior preservada; retorno para Analisar acrescentado; build da rota aprovado |
| A10–A13 | Montagem em `/analisar/` | Inclusão/remoção, escolha de chave, consulta sem agregação, métricas, filtros e limites exercitados; resultado anterior é invalidado ao mudar a montagem |
| A14–A18 | `/explorar/` | Editor SQL, Ctrl+Enter e provedores existentes preservados; chamadas externas não executadas sem credenciais |
| A19–A26 | Conexões prontas e resultados em `/analisar/` | 12 IDs preservados; tabela/gráfico, SQL, estado, tempo, receita local/download/importação e consulta textual testados; downloads integrais continuam no detalhe e no explorador |
| G01–G13 | Diagrama em `/analisar/` | Motor interativo existente incorporado na nova navegação e compilado; controles e ligações permanecem disponíveis |
| C01–C03 | Detalhe, Guia e rotas compatíveis | Seletor de tabela e links contextuais implementados; `/transformar/` redireciona preservando query/hash; `/explorar/` segue acessível |

O diagnóstico real de `obras` com `diretores_obras` pela chave CPB concluiu com 57.514 chaves coincidentes e 71.359 pares, sem expansão muitos-para-muitos. A receita salva e o estado de uma consulta textual também foram recuperados após recarga. Esses testes complementam o build e os testes automatizados registrados em `docs/PROGRESSO-UX-PORTAL.md`.
