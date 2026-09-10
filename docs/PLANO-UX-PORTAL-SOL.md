# Plano de execução para o Sol — experiência do portal RIDAB

## 0. Mandato, contexto e ponto de partida

**Objetivo:** implementar as mudanças principais da proposta de experiência aprovada pelo usuário: prévias úteis nos datasets, análise de uma ou várias tabelas no mesmo ambiente, reforma editorial de Brasil no Mundo e ajustes coerentes nas demais abas. Preservar a estrutura dos dados e a mecânica de clicar em tabelas e conectá-las.

**Correção expressa do usuário em 10/09/2026:** o print do Analisar pareceu estático e não autoriza perder dinamismo ou qualquer requisito existente. Ler obrigatoriamente `docs/PARIDADE-ANALISAR-SOL.md` junto deste plano. O inventário desse documento é um mínimo obrigatório, a ser completado com as interações efetivamente disponíveis na interface inicial. Uma funcionalidade que não aparece no mockup continua no escopo se já existe. A migração só termina após demonstração interativa e equivalência funcional comprovada; screenshot e build isolados não bastam.

Este é o plano técnico de implementação, preparado após inspeção do código. A solicitação que originou este arquivo é elaborar o plano para o Sol; nesta etapa não foi implementada a reforma. Ao iniciar a execução a partir dele, trabalhar de forma sequencial, completar as entregas e registrar o andamento para permitir continuação em outras sessões.

- Repositório: `C:\Users\INTEL\Desktop\dados-audiovisual-br`.
- Portal público: `https://riabr-dados.github.io/riab/`.
- Base inspecionada: `main`, commit `a5134af` (`portal: esclarece atualizacao e cobertura dos dados`). Verificar o estado real ao começar; não redefinir o checkout para esse commit.
- Proposta editorial: `outputs/proposta-portal-ux/PLANO.md`.
- Protótipo: `outputs/proposta-portal-ux/prototipo.html`.
- Prints: `outputs/proposta-portal-ux/01-catalogo.png` até `05-dataset-celular.png`.
- Última URL local verificada: `http://127.0.0.1:8876/prototipo.html#dataset`. O arquivo HTML é a referência durável; o processo local pode encerrar.
- O protótipo contém exemplos reais e controles demonstrativos identificados. Não copiar seus controles inativos, números fictícios, marcações de simulação ou o JavaScript da demonstração para produção.
- O usuário pediu anteriormente manter o push para quando o trabalho estiver concluído. Preparar e verificar todas as entregas locais antes de publicar; não executar push intermediário nem upload no HF por causa desta reforma de interface.

**Não reabrir decisões já tomadas:** manter Astro, GitHub Pages, Hugging Face e DuckDB-Wasm. Não migrar para Metabase/Observable, não redesenhar datasets, não repetir a auditoria original, não criar outro projeto ou tarefa. Não há necessidade de agentes paralelos para executar este plano.

## 1. Escopo da primeira reforma

### Obrigatório

1. Navegação final: **Datasets · Analisar · Brasil no Mundo · Mural · Guia · Sobre**.
2. Nomes específicos e seleção consistente das tabelas, mantendo a quantidade no card de cada dataset.
3. Página de dataset com visão geral, seletor de tabelas, prévia quando validada, fonte/método e downloads claros.
4. Prévia editorial para três pilotos de dataset; apresentação funcional sem gráfico para todas as demais tabelas.
5. Um ambiente Analisar: selecionar, filtrar, agrupar, calcular medidas, visualizar, conectar tabelas, inspecionar conexão, exportar e salvar a receita.
6. Preservar as receitas e o acesso ao diagrama existentes, integrando-os à navegação nova.
7. Brasil no Mundo com três recortes e conteúdo real em cada um; pelo menos três leituras reproduzíveis na primeira edição.
8. Ajustes da home, Guia, Mural e Sobre descritos abaixo.
9. Compatibilidade de URLs, verificação de downloads, comportamento móvel e testes focados de consulta/conexão.

### Fora desta entrega

- Curadoria manual de gráficos para todas as 471 tabelas; ela será uma expansão do mecanismo entregue.
- Dossiê unificado de cada filme, deduplicação internacional nova e resolução de títulos por IA.
- Mapa mundial, painel de todos os países ou ranking de circulação sem cobertura apropriada.
- Servidor de consultas, autenticação, contas, colaboração em tempo real, banco novo ou serviço de links curtos.
- Reprocessamento de microdados, alteração de Parquets, conversão de downloads, mudanças nos identificadores ou no agrupamento aprovado dos datasets.
- Nova integração de IA. Preservar as integrações existentes de Gemini, Anthropic e OpenAI e o caminho de pergunta → SQL → execução ao consolidar a interface. Não reduzir a um provedor por conveniência, não ampliar provedores nem trocar modelos como parte da reforma. Falha preexistente de serviço deve ser registrada; ausência de credenciais não equivale a teste aprovado nem autoriza remover a função.

**A primeira entrega só termina quando o caminho completo funcionar e os requisitos existentes estiverem preservados.** Não encerrar após trocar rótulos e instalar gráficos. O recorte de três pilotos limita somente a curadoria de novas prévias; não limita a preservação das funções existentes. Também não condicionar a entrega a produzir gráficos editoriais para o acervo inteiro.

## 2. O que o código atual oferece e onde intervir

| Arquivo existente | Responsabilidade / ação prevista |
|---|---|
| `portal/src/layouts/Base.astro` | Menu desktop/móvel, identidade e links globais |
| `portal/public/global.css` | Tokens visuais, tipografia, estados de foco, componentes comuns |
| `portal/src/lib/catalog.js` | Leitura de datasets, schemas, downloads e datas de snapshot; centralizar descritores de tabelas e contagens |
| `portal/src/lib/hf.js` | Reutilizar URLs de originais, tratados e downloads; eventual revisão opcional deve manter os URLs atuais compatíveis |
| `portal/src/lib/joins.js` | Registro de chaves e sugestões; não confundir a sugestão com garantia de correspondência |
| `portal/src/components/DatasetCard.astro` | Card já possui quantidade de tabelas; preservar, acrescentar nomes pesquisáveis e miniprévia opcional |
| `portal/src/components/ResourceDownloads.astro` | Reutilizar links completos, partes de CSV e notas sobre XLSX |
| `portal/src/components/DataExplorer.astro` | Terceiro editor/engine hoje embutido no dataset; integrar ao ambiente compartilhado e retirar a inicialização automática da visão geral |
| `portal/src/pages/datasets/index.astro` | Busca e filtros existentes, contagens e cards |
| `portal/src/pages/datasets/[slug].astro` | Recursos, schemas, queries padrão, fontes, metodologia e downloads; reordenar preservando o conteúdo |
| `portal/src/pages/explorar.astro` | Campos, filtros tipados, ordenação e consulta de uma tabela; aproveitar na consolidação |
| `portal/src/pages/transformar.astro` | Construtor, receitas, resultado, gráficos, exportação e diagrama; principal base funcional do ambiente Analisar |
| `portal/src/pages/conexoes.astro` | Outra entrada do grafo; manter a rota e alinhar a linguagem com nós que representam tabelas |
| `portal/src/pages/brasil-no-mundo.astro` | Substituir organização centrada em evidências por leituras editoriais; retirar contagens fixas |
| `portal/src/pages/index.astro` | Reduzir repetição do catálogo, derivar destaques e corrigir cobertura histórica |
| `portal/src/pages/consulta.astro` | Docs atual; virar Guia por tarefas, preservando trechos técnicos e âncoras úteis |
| `portal/src/pages/mural.astro`, `sobre.astro` | Ajustes editoriais pequenos, sem apagar a voz autoral |
| `catalog/datasets.yaml`, `schemas/`, `downloads.json`, `joins.yaml` | Entradas existentes; nesta reforma, principalmente leitura e validação |
| `.github/workflows/deploy-portal.yml` | Build estático com Node 22; não tem Parquets locais nem Python provisionado |

**Armadilhas já identificadas:**

- O `buildBuilderSQL()` de Transformar pode gerar `CROSS JOIN` quando falta ponte ou coluna concreta. Corrigir no novo caminho antes de liberá-lo; comentário de aviso no SQL não resolve o problema para o usuário.
- Inspecionar os caminhos ativos equivalentes ao `buildBuilderSQL()`: a correção não pode atingir apenas um botão e deixar outro caminho ativo com o mesmo comportamento. `buildFromClause()` aparece em um bloco `__LEGACY_START__` comentado no arquivo revisado; distinguir código morto de função disponível ao usuário e não ressuscitar esse bloco durante a extração.
- Títulos de várias tabelas são derivados do mesmo `ds.title`. Usar o identificador da tabela e seu schema para desambiguar.
- O índice de datasets soma comprimentos de listas; `getCatalogStats()` usa conjunto de nomes de tabela. Unificar a definição de contagem de tabelas únicas.
- `getLatestSnapshotDate()` lê pastas locais. Em build do GitHub, a disponibilidade desse histórico pode diferir; não inventar data de coleta usando a data do build.
- O evento `riab:resource-changed` e o comando `riab:set-table` ligam o explorer ao detalhe. Preservar durante a transição ou migrar emissor/receptor juntos.
- `scripts/gerar_preview.py` gera `docs/data.js` para um portal legado, a partir de amostras brutas. Não reutilizá-lo como se fosse o gerador de resumos editoriais do Astro.
- `hf.js` aponta para `resolve/main`. Salvar uma receita não garante reprodução histórica: registrar hash/revisão quando conhecidos e não prometer congelamento sem implementá-lo.
- `astro.config.mjs` usa `/` em desenvolvimento e `/riab/` em produção. Validar ambos.

## 3. Arquitetura mínima proposta

Evitar acrescentar outro framework de aplicação. Separar funções de dados/consulta de código que manipula o DOM; reutilizar o que existe, em vez de copiar as páginas grandes para criar um quarto editor.

Novos arquivos sugeridos — os nomes podem ser ajustados, mantendo as responsabilidades:

```text
catalog/portal-presentation.yaml              # títulos e prévias editoriais por tabela
catalog/portal-stories.yaml                   # leituras de Brasil no Mundo e receitas referenciadas
portal/src/lib/presentation.js                # descritores normalizados para build
portal/src/lib/analysis/state.js              # estado, alterações, desfazer, validação
portal/src/lib/analysis/query.js              # compilação das consultas visuais
portal/src/lib/analysis/engine.js             # DuckDB-Wasm, registro lazy, execução/cancelamento
portal/src/lib/analysis/diagnostics.js        # consultas e interpretação da cardinalidade
portal/src/lib/analysis/persistence.js        # receitas locais e portáveis
portal/src/components/TablePicker.astro      # seletor pesquisável
portal/src/components/DatasetPreview.astro   # gráfico/tabela e contexto da prévia
portal/src/components/AnalysisWorkbench.astro
portal/src/components/StoryCard.astro
portal/src/pages/analisar.astro
portal/public/previews/index.json             # manifesto pequeno
portal/public/previews/<preview-id>.json      # resumos pequenos versionados
scripts/build_portal_previews.py
docs/PROGRESSO-UX-PORTAL.md
```

Usar um único renderizador compartilhado para linhas e barras, com tabela acessível equivalente. Aproveitar o código de gráficos atual se for adequado após extração. Se precisar de biblioteca, escolher uma só, verificar documentação oficial e justificar a dependência; não instalar uma plataforma de BI para desenhar dois tipos de gráfico.

### 3.1 Descritor comum de tabela

Um descritor deve reunir `tableId`, datasets associados, título legível, descrição, campos/tipos, unidade da linha quando documentada, origem da fonte, links, metadados de download, datas conhecidas e prévia opcional.

Ordem para escolher título: título editorial explícito → título específico documentado no schema → identificador humanizado. O título do dataset pai aparece em linha secundária. Se a unidade da linha não tiver sido validada, não inferir unicidade porque existe uma coluna chamada CPB; mostrar descrição factual ou “consulte os campos e o método”.

Validar se uma entrada editorial aponta para tabela/coluna existente. Preservar tabelas documentais `_fontes`, diferenciando sua função, sem escondê-las do total ou apagá-las.

### 3.2 Prévia editorial e artefatos de build

Para cada prévia, declarar pelo menos:

```yaml
version: 1
tables:
  preco_ingresso:
    title: Preço médio do ingresso
    row_unit: ano de referência
    preview:
      id: preco-ingresso-observado
      title: O ingresso ao longo do tempo
      chart: line
      x: ano
      measures: [pmi_nominal, pmi_real_2024]
      filters:
        - {column: fonte, operator: neq, value: fallback}
      order_by: [{column: ano, direction: asc}]
      note: Registros de apoio que repetem 2024 ficam fora desta prévia.
```

Completar a configuração real com unidades por medida, regras de agregação ou ausência dela, apresentação de nulos, descrição de cobertura e referências. O exemplo não é um schema completo nem autoriza aplicar a mesma regra às outras tabelas.

O gerador lê apenas os Parquets necessários às prévias declaradas; escreve os pequenos JSONs em `portal/public/previews/`. Não reprocessa fontes nem altera tabelas. Registrar tabela(s), hash(s) de entrada, hash da configuração, consulta/filtros, unidade, período observado, data da coleta quando comprovada e momento de geração. São informações distintas.

Os resumos entram no Git junto ao portal: o GitHub Pages precisa construir sem os Parquets ignorados pelo Git. Na CI, verificar consistência de configuração e hashes com `catalog/downloads.json`; não baixar todo o HF para gerar miniaturas. Hash divergente exige regenerar a prévia afetada. Um arquivo opcional ausente pode produzir visão sem gráfico; uma prévia publicada com dados desatualizados em relação ao manifesto deve ser identificada e corrigida antes do release.

Evitar incluir centenas de amostras grandes no bundle. Manifesto pequeno, resumo carregado por tabela ou embutido apenas na página que o usa. A home e o catálogo não inicializam DuckDB.

### 3.3 Estado compartilhado da análise

Definir um contrato versionado, validado na entrada, sem dependência da posição dos elementos HTML:

```js
{
  version: 1,
  title: "Minha análise",
  source: { datasetSlug: null, previewId: null, recipeId: null },
  tables: [{ instanceId: "t1", tableId: "preco_ingresso" }],
  joins: [],
  columns: [],
  metrics: [],
  filters: [],
  groupBy: [],
  sort: [],
  resultLimit: 100,
  view: { type: "table", x: null, y: null, unit: null },
  mode: "visual",
  sqlDraft: null,
  sources: [{ tableId: "preco_ingresso", sha256: "quando conhecido", revision: null }]
}
```

Escolher estruturas explícitas para referência de campo (`instanceId`, `column`), operador, tipo do valor e conexões com uma ou mais colunas. Não interpretar CNPJ/CPB textual como número por parecer numérico. IDs de tabela/coluna devem ser validados contra o catálogo; valores textuais e identificadores SQL precisam de tratamento correto. Não concatenar texto vindo de URL diretamente em SQL/HTML.

Tabela, gráfico, exportação e SQL visual devem derivar desse estado. Gráfico usa o resultado da mesma consulta, não uma agregação escondida de linhas que já passaram por `LIMIT`. Quando uma visualização for top N, mostrar N no recorte. Alterar tabela, filtro, medida ou chave invalida resultado/diagnóstico anterior e mostra que é necessário recalcular.

`mode: sql` preserva uma consulta livre separada. Não é necessário construir um parser reversível de SQL nesta entrega. Se ela não for representável visualmente, informar isso e permitir voltar à última montagem visual preservada; não descartar o SQL sem ação explícita.

### 3.4 Engine e carregamento

Uma instância de DuckDB-Wasm por ambiente de análise, registro de views somente das tabelas necessárias, cache por tabela/versão e controle de concorrência. Não carregar o catálogo inteiro para preparar a interface. Campos e descrições vêm dos schemas no build; só consultar metadados remotos quando necessário.

Preservar seleção antes da engine terminar de carregar. Erro de rede mostra tentar novamente mantendo estado. Novo resultado não pode ser sobrescrito por uma consulta antiga que terminou depois. Oferecer cancelamento real usando a API disponível ou encerramento/recriação do worker com preservação do estado; não apenas esconder um spinner.

## 4. Plano de trabalho em entregas verificáveis

### E0 — Baseline e registro de progresso

1. Ler este plano e a proposta; inspecionar os quatro prints. Não refazer toda a pesquisa da sessão anterior.
2. Verificar branch, status, instruções locais e dependências. Preservar mudanças do usuário. Se criar branch para a reforma, usar `codex/portal-ux` ou nome equivalente disponível.
3. Registrar commit inicial, contagens e comandos já disponíveis. O estado revisado tinha 110 datasets visíveis e 471 tabelas únicas, mas os números devem ser recalculados, não fixados no código.
4. Executar o build atual uma vez para distinguir falhas preexistentes. Criar `docs/PROGRESSO-UX-PORTAL.md` com entregas, status, decisões e próximo passo.
5. Percorrer as interfaces atuais e completar a matriz de `docs/PARIDADE-ANALISAR-SOL.md`: origem, comportamento, destino novo e evidência de teste. Registrar também as funções não exercitáveis por falta de rede/credencial, separadamente das que passaram.

**Aceite:** baseline conhecido; nenhum arquivo de dados alterado; uma lista objetiva das falhas preexistentes, se existirem. Não abrir nova auditoria para resolvê-las sem relação com esta entrega.

### E1 — Descritores, contagens e navegação das tabelas

1. Implementar o descritor comum e os metadados de apresentação.
2. Centralizar contagens em `catalog.js`: datasets visíveis, tabelas únicas, fontes e origens geográficas. “Europa” é região; usar “origens das fontes” ou distinguir países/região.
3. Estender busca do catálogo para incluir nomes das tabelas e campos descritivos úteis, mantendo categoria/procedência/país existentes.
4. Atualizar labels das listas nas interfaces atuais por meio do mesmo descritor; isso evita perpetuar a duplicação durante a migração.
5. Preservar o card como link único ou estruturar ações sem aninhar botões dentro de um link. Número de tabelas permanece visível, com singular/plural correto.
6. Criar seletor de tabela com busca e grupos, destaque da tabela ativa e identificador técnico secundário. Não expandir 128 fichas completas ao carregar.

**Aceite:** duas tabelas do mesmo dataset são distinguíveis; todos os recursos continuam acessíveis; contagem geral é de IDs únicos; filtro vazio tem mensagem e ação para limpar; pesquisar o nome de uma tabela encontra seu dataset.

### E2 — Prévia e novo detalhe de dataset

1. Implementar gerador/manifesto e componente de prévia descritos em 3.2.
2. Fazer três pilotos:
   - `ancine-preco-medio-ingresso` / `preco_ingresso`: linha, nominal e reais de 2024, filtro de registros `fallback`, período observado 2014–2024 no estado revisado.
   - Dataset que contém `obras`: distribuição por tipo como contagem de registros; só chamar de obras únicas após verificar o identificador. Manter uma amostra legível.
   - Dataset que contém `pib_audiovisual_total_ano` e suas tabelas complementares: escolher a tabela anual para a prévia, apresentar sua unidade original e testar a troca de tabela. Confirmar o slug pelo catálogo. Não somar a tabela total com seus desdobramentos.
3. Integrar no detalhe: título/pergunta, quantidade de tabelas, seletor, **Visão geral / Tabelas / Fonte e método**. Uma única tabela pode usar “Tabela” no singular.
4. Manter as informações existentes sobre camadas metodológicas, derivação, fontes, schemas e downloads. Reorganizá-las; não apagar as explicações de reprocessamento ou tabelas de proveniência.
5. Datas distintas: período observado, publicação na origem, coleta e revisão quando disponíveis. Informação ausente não vira data de hoje.
6. Adicionar “Analisar esta tabela” com estado inicial ou `previewId`. Pode apontar para a nova rota assim que E3 estiver pronta; não publicar uma ação quebrada entre fases.
7. Fora dos pilotos, mostrar contexto e seletor; oferecer amostra sob demanda/tabela de campos e download. Não produzir gráficos automáticos sem medida validada.

**Aceite:** trocar de tabela atualiza contexto, campos, prévia e downloads; nominal/real alteram unidade e valores corretamente; lacunas não viram zero; a primeira tela não carrega DuckDB; downloads completos não se tornam amostras; originais continuam identificados e acessíveis.

### E3 — Construir Analisar reutilizando as funções existentes

1. Extrair o que é compartilhável de Transformar e Explorar para módulos, sem fazer uma reescrita total antes de ter o primeiro fluxo funcionando.
2. Criar `/analisar/`. Entrada vazia oferece tabela ou receita; entrada pelo dataset recebe seleção e recorte. Manter a pessoa no mesmo ambiente quando conecta outra tabela.
3. Biblioteca pesquisável recolhível; montagem com cartões clicáveis; controles **Mostrar / Medir / Agrupar / Filtrar / Ordenar**. Preservar arraste de campos para colunas/filtros/ordenação, oferecendo também alternativas por clique e teclado. Explicar a unidade de cada linha quando conhecida. Biblioteca, montagem e resultado continuam conectados; não converter a experiência em um formulário estático ou sequência obrigatória de páginas.
4. Resultado com **Tabela / Gráfico**, exportação, limite explícito e contagem exibida. Preservar barras horizontais, barras verticais, linhas, ordenação clicando no cabeçalho e refinamento por dimensão/medida das receitas. Não reduzir a dois tipos de apresentação ignorando orientação já disponível; recusar medida/tipo inválido com orientação legível.
5. Migrar receitas existentes, seus títulos/notas e ordenação para configuração reaproveitável. Preservar seu SQL enquanto a equivalência visual não estiver validada, identificando receitas em modo SQL quando necessário.
6. Manter **Montar análise / Receitas prontas / Diagrama de relações** como modos claramente acessíveis no mesmo ambiente, cada um a no máximo um clique de navegação. Preservar zoom, pan, arraste, seleção e destaque de vizinhos, filtros, detalhes das chaves e layouts disponíveis; carregar dados/código do grafo quando aberto. A troca de modo não deve apagar o trabalho. Para tamanho de nó por quantidade de registros, aproveitar `downloads.json` e cache em vez de consultar todos os Parquets; se a contagem for desconhecida, sinalizar. Não usar “avançado” para tornar o diagrama difícil de encontrar ou substituí-lo por uma imagem.
7. Terminar a migração do editor do detalhe: prévia e link para Analisar usam o mesmo estado; não deixar três engines e três conjuntos de regras independentes ativos.

**Aceite:** abrir a prévia de ingresso no Analisar reproduz seu recorte; filtrar/ordenar/exportar funciona com uma tabela; conectar outra preserva o estado aplicável; remover tabela remove referências inválidas com opção de desfazer; receitas e gráfico de relações continuam acessíveis.

**Demonstração obrigatória de E3/E4:** mostrar a interface operável e executar os roteiros de `PARIDADE-ANALISAR-SOL.md`. Capturar uma gravação curta se houver ferramenta apropriada ou entregar o endereço local e os passos reproduzíveis. Não substituir as abas anteriores por completo antes de cumprir os testes de equivalência. A demonstração é verificação do trabalho autorizado, não uma nova exigência de aprovação para cada etapa.

### E4 — Conexões explícitas e diagnóstico

1. Cada aresta registra instâncias, colunas em ambos os lados, normalização aplicável e tipo de junção. Exibir a escolha; não escolher silenciosamente o primeiro par de colunas se houver ambiguidade.
2. Sugerir por identificadores documentados antes de dimensões ou títulos. Mostrar “sugestão automática” quando a relação vier de heurística do registro. `confidence: high` no registro atual pode significar detecção por nome, não revisão humana.
3. Sem ponte válida, manter tabela como não conectada e orientar a escolher colunas; não gerar `CROSS JOIN` no modo visual. Não substituir ausência de ligação por ligação em ANO/PAIS só porque as colunas coincidem.
4. Normalizações não devem fazer chaves nulas/vazias corresponderem entre si. Manter zeros à esquerda. Correspondência por título deve explicar que é aproximada e não afirmar identidade da obra.
5. Antes de agregações em análise com conexão, calcular diagnóstico do plano e filtros atuais: linhas em cada lado, linhas à esquerda com/sem par, chaves distintas e repetidas, nulos/vazios, multiplicidade e número estimado/exato de linhas resultantes. Indicar claramente se o diagnóstico é amostral; amostra não autoriza conclusão global sobre unicidade.
6. Não materializar um produto grande para contar pares. Agrupar contagens por chave; por chave k, pares de igualdade são `n_esquerda(k) × n_direita(k)`. Tratar chaves compostas como tuplas, sem concatenação ambígua. Para `LEFT JOIN`, acrescentar as linhas sem par e as de chave inválida conforme as regras efetivas.
7. Mostrar amostras de não correspondentes e repetidos. Para N:N ou ampliação de linhas que afete a medida, não oferecer total como se estivesse validado: exigir corrigir chave, escolher agregação prévia com unidade explícita ou continuar na inspeção de linhas. Nunca deduplicar arbitrariamente nem usar `SUM(DISTINCT valor)` como remendo.
8. Filtros de cada entrada e filtros após conexão devem ter semântica explícita. Um filtro da direita aplicado inadvertidamente no `WHERE` pode eliminar linhas que o usuário pediu para manter; compilador e teste devem cobrir isso.
9. Cache de diagnóstico depende de tabelas/versões, filtros, chaves e normalização. Invalidar após alteração. Em várias conexões, avaliar também a multiplicação acumulada no plano, não apenas pares isolados.

**Piloto real:** `obras` e `bilheteria_consolidada_br` pelo CPB, após confirmar os campos e a granularidade efetivos. Não fixar contagens de correspondência no HTML. Se o campo não for adequado no estado vigente, registrar por quê e escolher relação documentada equivalente no catálogo.

**Aceite:** nenhuma ausência de ponte vira produto cartesiano automático; diagnósticos conferem com fixtures controladas e uma relação real; contagens não confundem linhas com chaves; cálculo de totais tem recorte e granularidade explícitos.

### E5 — Receita salva, links e exportações

1. Salvar nome e estado validado no navegador, com namespace/versionamento e tratamento de armazenamento indisponível. Não incluir API keys, resultados completos ou tokens.
2. Exportar/importar receita JSON. Para estados pequenos, oferecer link usando formato versionado no fragmento, com limite documentado de tamanho; para estados maiores, preferir arquivo. Não criar serviço de links curtos.
3. Receita importada/compartilhada abre para inspeção; não executa SQL automaticamente ao visitar o link. Validar nomes/campos e dar erro recuperável se a versão não for suportada.
4. Registrar hashes conhecidos das fontes; se a revisão não puder ser fixada, avisar quando o hash/catalogo divergir e permitir atualizar a receita explicitamente. Não anunciar reprodução histórica garantida sobre `resolve/main`.
5. Manter três ações distintas: **exportar linhas exibidas**, **exportar resultado completo da consulta** e **baixar tabela original/tratada completa**. Transformar já exporta a consulta além do limite da prévia; não perder essa capacidade ao unificar. Compilar a versão sem limite de apresentação a partir do estado, preservando filtros/agregações. Distinguir esse limite de um top N intencional; não remover limites internos de SQL livre com regex. CSV correto para aspas, separadores, quebras de linha, Unicode e identificadores textuais. Tratar volume com progresso/cancelamento ou alternativa equivalente explícita; não trocar silenciosamente a exportação completa por 100 linhas. Downloads completos de uma tabela não substituem o resultado completo de um cruzamento.
6. Gráfico: exportação em SVG ou PNG com título, fonte, unidade e recorte; oferecer tabela correspondente e texto de citação. Uma implementação consistente de imagem é suficiente nesta etapa.

**Aceite:** recarregar/reabrir receita recupera seleção, filtros e visão; versão incompatível não quebra a tela; sem credenciais no JSON/link; download do resultado e download da tabela completa continuam distintos.

### E6 — Primeira edição de Brasil no Mundo

Manter a rota `/brasil-no-mundo/` e usar três recortes: **Cinema e streaming**, **Coproduções e registros**, **Comparações de mercado**. Hero curto; começar com descoberta concreta. Cada leitura declara pergunta, fonte, unidade, período/observação, limite interpretativo e receita reproduzível.

Entregar pelo menos estas três leituras, uma por recorte:

1. **Cinema:** top 5 de `brasil_no_mundo_bilheteria_europa`, ordenando `admissoes_1996_2026`. Título deve dizer “no recorte disponível”; esse campo é acumulado, não público no ano de produção. Não usar `ano_producao` como série anual de exibição. Ranking mundial e decomposição por país não são suportados por essa tabela.
2. **Registros CNC:** leitura de `brasil_no_mundo_obras_franca_cnc` separada por `dataset_origem`/procedimento. Usar lista ou barras de registros por origem, com definição explícita; não somar vistos e agréments como filmes únicos e não transformar `ano` de eventos distintos numa série homogênea. Priorizar transparência do que cada registro documenta.
3. **Mercado BFI:** painel/lista dos indicadores de `brasil_no_mundo_mercado_bfi` com `indicador`, `ano`, `valor`, `unidade` e `tabela_origem`. Nunca plotar medidas de unidades diferentes no mesmo eixo. O recorte contém Brasil; um ranking com outros países requer consultar e validar a tabela original correspondente, portanto não é requisito desta primeira leitura.

Se a revisão permitir uma quarta leitura curta, incluir streaming por países de catálogo a partir de `brasil_no_mundo_vod_europa`. Contar obras distintas dentro da definição documentada, não multiplicar pelos números de plataformas. Um título observado em múltiplos países pode contar em cada país, mas o total territorial não é total de obras únicas. Disponibilidade é referente à data da observação, sem inferência de audiência ou presença atual.

As três leituras mínimas devem funcionar; não entregar uma aba vazia com “em breve”. Se um gráfico não for adequado, entregar uma tabela editorial legível e sua receita. Não confundir esse fallback com inventar uma medida.

“Ver dados desta leitura” abre Analisar com o mesmo filtro, ordenação e medida. “Fonte e limites” fica junto à leitura. Manter caminho para o dataset completo e para menções textuais complementares, retirando sua posição de destaque. Não somar categorias sobrepostas num número de filmes brasileiros no mundo.

**Aceite:** três recortes com conteúdo real, fontes e receitas; nenhum indicador fixo copiado do mockup; gráfico e consulta equivalentes; participação brasileira inclui coproduções conforme a classificação da fonte, explicitado no texto.

### E7 — Home, Guia, Mural, Sobre e migração das rotas

1. **Home:** busca, temas e poucas leituras/receitas de entrada; reduzir o catálogo duplicado. Contagens e destaques derivam das mesmas entradas validadas. Datas não devem ser inferidas a partir do nome de um campo.
2. **Cobertura histórica:** substituir a barra contínua de 1971–2024 por trechos por fonte com lacunas visíveis. 1971 pertence à série complementar/IBGE; Embrafilme cobre 1982–1987 no material revisado. Verificar os anos realmente presentes e a procedência no dado; não atribuir toda a série à Embrafilme. Reutilizar resumos de apresentação, sem editar a série.
3. Remover menções ao preço de operação: “sem custo” na home, “IA GRATUITA” e “grátis” nas interfaces. Não apagar valores monetários dos dados nem reintroduzir a conta de custo no Sobre.
4. **Guia:** reorganizar `/consulta/` por tarefas: baixar, entender campos, visualizar, conectar, citar. Manter exemplos técnicos em seção própria e alinhar exemplos à nova interface. É suficiente mudar o rótulo do menu para Guia mantendo a rota `/consulta/`; não criar migração de rota sem benefício.
5. **Mural:** preservar trabalho, autoria e links existentes. Acrescentar relação com datasets e receita quando houver. Não inventar receita reproduzível para um estudo externo. Evitar filtros vazios com um único trabalho.
6. **Sobre:** preservar manifesto, acrescentar resumo/sumário e atualizar referências às abas antigas. Não reescrever a opinião do autor nem inserir afirmações de autoria técnica sem evidência.
7. Atualizar menu desktop/móvel para Analisar. `/explorar/` e `/transformar/` viram entradas compatíveis para o novo ambiente: preservar parâmetros/âncoras reconhecidos e oferecer fallback compreensível. Em hospedagem estática, usar página de compatibilidade com link funcional mesmo sem JavaScript; não depender de regra de redirect de servidor inexistente.
8. `/conexoes/` continua acessível e leva ao diagrama/contexto equivalente. Corrigir “dataset” para “tabela” quando a unidade dos nós assim exigir.
9. Durante a transição, só remover código antigo quando referências, eventos, receitas e rotas já estiverem cobertos. Evitar manter cópias ativas do mesmo editor indefinidamente.

**Aceite:** navegação consistente; URLs antigas úteis; manifesto e downloads preservados; sem promessa de gratuidade operacional; cobertura histórica não insinua continuidade inexistente.

### E8 — Verificação final e entrega

Executar a matriz abaixo, corrigir falhas relacionadas às mudanças, capturar prints reais e atualizar o progresso. A revisão final deve mostrar comportamento funcionando, não apenas mockups.

Não é necessário atualizar Hugging Face se só mudaram portal, metadados de apresentação e resumos no Git. Justificar qualquer necessidade diferente antes de executar um processo de publicação de dados. Build aprovado não significa site publicado.

## 5. Testes e critérios que realmente importam

### Lógica com fixtures pequenas

Usar `node:test` para funções JS puras se isso evitar dependência adicional. Adicionar scripts npm adequados; o projeto atualmente só tem `dev`, `build` e `preview`. Testes de consultas podem usar a engine real com pequenos dados locais. Não criar snapshots enormes de HTML nem testar detalhes de CSS sem comportamento associado.

| Caso | Resultado esperado |
|---|---|
| Tabela sem configuração de gráfico | Visão informativa e downloads funcionam; gráfico não é inventado |
| Tabela/coluna inválida na configuração | Validação aponta o identificador e a configuração afetada |
| Mesmo identificador em dois datasets | Contagem geral usa tabela única; ambos os datasets mantêm seus vínculos |
| Ingresso com linhas `fallback` | Prévia exclui essas linhas; download completo não é alterado |
| Texto com aspas e CPB com zero à esquerda | Filtro e exportação preservam valor e tipo |
| Ano faltante ou valor nulo | Sem substituição implícita por zero; linha do gráfico não atravessa uma lacuna sem explicação |
| Duas tabelas sem conexão | Modo visual não compila `CROSS JOIN` automaticamente |
| Conexão com chaves nulas/vazias | Não cria correspondência entre ausências |
| Mudança de chave/filtro | Diagnóstico e resultado anteriores são invalidados |
| Resposta antiga chegando depois da nova | Resultado atual não é sobrescrito |
| `LEFT JOIN` com filtro da tabela direita | Comportamento corresponde à opção de manter linhas explicitada na interface |
| Estado/receita salvo e recuperado | Mesmas tabelas, filtros, visão e versão; nenhuma credencial |

Fixture concreta de cardinalidade: esquerda com chaves `[A, A, B, C, null]`; direita `[A, A, B, D, null]`. Com igualdade apenas entre chaves válidas: 3 linhas da esquerda com par, 2 sem par, 5 pares internos e 7 linhas no `LEFT JOIN`. A chave A repete dos dois lados; contagens de chaves distintas são diferentes das contagens de linhas. Acrescentar um caso com chave vazia normalizada e outro com chave composta. Um limite de exibição não pode alterar esse diagnóstico global sem identificação de amostragem.

### Fluxos no navegador

1. Catálogo → pesquisa pelo nome de tabela → dataset → escolher outra tabela → abrir Analisar → voltar sem perder contexto relevante.
2. Ingresso → alternar nominal/real → comparar a tabela correspondente → exportar o recorte → abrir o download completo correto.
3. Analisar → duas tabelas → escolher chave → conferir diagnóstico → ajustar/inspecionar → gráfico e tabela → exportar.
4. Fonte sem ponte → mensagem acionável, sem query cartesiana escondida.
5. Brasil no Mundo → cada uma das três leituras → abrir dados → reproduzir números/recorte.
6. Salvar, recarregar e importar receita; recusar formato inválido sem perder análise aberta.
7. Navegar por teclado: filtros, seletor, conexão e abas sem exigir arraste.
8. Testar erro de rede/engine, cancelamento e nova tentativa mantendo estado.
9. Abrir as rotas antigas e os links no build de produção sob `/riab/`.

Playwright pode ser usado para smoke tests e screenshots. No ambiente atual há runtime disponível fora do projeto; se criar um script permanente, não fixar o caminho pessoal `C:\Users\INTEL\...` no código versionado. Usar configuração/descoberta ou dependência de desenvolvimento apropriada. Não levar ferramentas de teste para o bundle do portal.

### Regressão do acervo e build

Comandos de referência, após confirmar os caminhos e dependências reais:

```powershell
# A partir de portal/, instalar somente se necessário para reproduzir o lockfile.
npm ci
npm run build

# A partir da raiz; estes testes já existem.
.\.venv\Scripts\python.exe -m pytest tests/test_catalog_integrity.py tests/test_downloads.py tests/test_release_downloads.py -q
```

Os testes de integridade dependem dos Parquets locais. Se faltarem, registrar exatamente a dependência ausente; não classificar como aprovado, não baixar o acervo inteiro por reflexo e não usar a falta para ocultar regressão no código do portal. Em ambiente completo, executar a bateria focada ao final. Rodar novamente somente após alterações relevantes ou falha.

Validar que `catalog/downloads.json` e Parquets não mudaram por causa da apresentação. Revalidar links de amostras representativas: CSV simples, XLSX, CSV multipartes/grande e arquivo original. Preservar notas de XLSX não disponível.

### Visual, acessibilidade e desempenho

- Capturar catálogo, dataset simples, dataset com várias tabelas, Analisar e Brasil no Mundo em desktop; dataset/Analisar em 390 px.
- Inspecionar imagens, não apenas gerá-las. Ajustar textos cortados, eixos ilegíveis, estados vazios e foco.
- Manter identidade existente; tipografia final deve conversar com `global.css`. O mockup é guia de hierarquia, não obrigação de substituir fontes ou redesenhar a marca.
- Gráficos têm título, unidade, legenda quando necessária e tabela alternativa. Cor não é a única informação.
- Em telas menores, controles viram seções/painéis; diagrama tem alternativa em lista. Rolagem horizontal pode existir dentro de tabela larga, não na página inteira.
- Registrar tempo até prévia e primeiro resultado em teste frio, browser/aparelho e tamanho transferido. Não prometer desempenho não medido.
- Confirmar no tráfego que catálogo e visão geral não iniciam DuckDB nem leem Parquets completos. Um filtro visual não dispara consultas pesadas por tecla sem controle.
- Build de produção deve continuar executável no workflow sem dados locais. Se acrescentar validador Node de prévias, integrá-lo ao script de build/prebuild de modo reproduzível.

## 6. Ordem de execução, controle de esforço e continuidade

Dependências principais: **E0 → E1 → E2 → E3 → E4 → E5 → E6 → E7 → E8**. Correções editoriais simples de E7 podem entrar antes, mas a navegação final só aponta para fluxos funcionais.

E3/E4 concentram o maior risco técnico. Concluir um fluxo vertical de uma tabela e uma conexão antes de extrair todos os modos avançados. O gerador e os pilotos de prévia devem estar consolidados antes de aplicar a apresentação a todo o catálogo. Se uma abstração exigir reescrever tudo, reduzir a abstração e preservar o caminho existente até a substituição estar verificada.

Manter no progresso, ao fim de cada entrega ou sessão:

```text
Base/branch:
Entrega atual:
Concluído (com arquivos):
Testes executados e resultado:
Comportamentos ainda não verificados:
Decisões tomadas e motivo:
Próximo passo concreto:
Publicação: não iniciada / preparada / realizada, com evidência
```

Registrar progresso para evitar nova leitura completa do repositório em cada sessão. Fazer commits locais por entrega coerente quando apropriado; nunca usar `git add .` para incluir automaticamente outputs, logs e material de outras tarefas. Selecionar arquivos. Não incluir credenciais, caches, Parquets ou dumps de auditoria no commit da interface.

Não pedir confirmação para escolhas rotineiras já cobertas: componentes, nomes de módulos, ajustes de acessibilidade, reaproveitamento de funções, estados de erro e testes. Se surgir uma decisão que exija alterar dados aprovados ou infraestrutura, concluir o trabalho independente e apresentar a necessidade concreta, sem executar migração silenciosa.

## 7. Definição de pronto

- [ ] A pessoa entende uma tabela a partir da página de dataset e entra na análise sem reconstruir a seleção.
- [ ] O catálogo inteiro continua navegável; tabelas múltiplas têm nomes distintos, quantidade e downloads corretos.
- [ ] Três pilotos têm prévias corretas, legíveis e reproduzíveis; os demais têm apresentação funcional sem gráficos inventados.
- [ ] Uma ou várias tabelas usam o mesmo ambiente e resultado; o clique/conexão foi preservado.
- [ ] Matriz de equivalência funcional concluída, incluindo arrastes, diagrama interativo, layouts, filtros, receitas, SQL, provedores existentes e exportação integral da consulta; demonstração navegável realizada.
- [ ] Nenhum caminho visual cria produto cartesiano automaticamente ao faltar relação.
- [ ] Diagnóstico, filtros, agregações, nulos e exportação passaram pelos testes focados.
- [ ] Receita salva/portável funciona e identifica limites de versionamento das fontes.
- [ ] Brasil no Mundo tem três recortes reais e ao menos três leituras reproduzíveis.
- [ ] Home, Guia, Mural e Sobre estão coerentes; custos operacionais não são argumento de apresentação.
- [ ] Rotas antigas e base `/riab/` funcionam; sem links ou controles demonstrativos em produção.
- [ ] Build, testes aplicáveis e revisão visual concluídos, com limitações remanescentes explícitas.
- [ ] Estrutura dos datasets, tabelas e downloads aprovados preservada.
- [ ] Relato final informa o que mudou, evidências, commits locais e situação real de publicação, sem confundir protótipo, build e deploy.

## 8. Mensagem curta para iniciar a execução com o Sol

> Execute `docs/PLANO-UX-PORTAL-SOL.md` e `docs/PARIDADE-ANALISAR-SOL.md`, no projeto `C:\Users\INTEL\Desktop\dados-audiovisual-br`. As mudanças principais de UX estão autorizadas. Preserve dados e downloads aprovados, a identidade do RIDAB e todas as funcionalidades/interações existentes. O usuário reforçou que não aceita perder o dinamismo do Analisar: o print é só referência visual. Complete a matriz de equivalência e demonstre a interface funcionando antes de substituir as abas atuais. Comece pelo estado atual do Git, siga E0–E8 e mantenha `docs/PROGRESSO-UX-PORTAL.md` atualizado. Não refaça a auditoria, não migre plataforma e não publique parcialmente. Conclua e verifique o conjunto antes de preparar o push; esta reforma de interface não requer upload no Hugging Face.
