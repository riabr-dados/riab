# Progresso da reforma de experiência do portal

Base: `main` em `a5134af`. Execução: `codex/portal-ux`. Publicado no `main` em 2026-09-10 (fast-forward; deploy do GitHub Pages).

## Entrega concluída

- Catálogo e detalhe: descritor comum de 471 tabelas; contagem de tabelas por dataset; busca por nome de dataset e tabela; carregamento progressivo de 80 itens; limpeza de filtros; seletor de recurso e links contextuais para análise.
- Leitura imediata dos dados: manifesto reprodutível e três prévias editoriais (`preco_ingresso`, `obras`, `pib_audiovisual_total_ano`), com SVG, unidade, fonte, período, ressalva e tabela acessível.
- Analisar: uma entrada reúne montagem de cruzamentos, 12 conexões prontas e diagrama. Todas as tabelas continuam consultáveis individualmente; os Parquets são carregados sob demanda. O quarto modo leva ao explorador de campos, preservando seleção, arraste, filtros tipados, SQL livre, exportação e integrações de IA já existentes enquanto essas ferramentas avançadas permanecem em `/explorar/`.
- Montagem: busca e filtros de catálogo, escolha explícita de chave, colunas sem agregação, múltiplas métricas, filtros, limites, inspeção de SQL, tabela/gráfico, salvamento local, download e importação de receita. Mudanças na montagem invalidam o resultado anterior.
- Segurança analítica: cruzamento sem ponte é bloqueado; chaves vazias não coincidem; o diagnóstico de cardinalidade calcula chaves coincidentes, linhas de cada lado, pares resultantes e expansão muitos-para-muitos.
- Compatibilidade: `/transformar/` encaminha consulta e fragmento para `/analisar/`; `/explorar/` continua disponível e recebeu navegação de retorno para o ambiente consolidado.
- Brasil no Mundo: reconstruído como três leituras — circulação de obras, coproduções/registros e Brasil como mercado — com visualização, fonte, unidade, ressalva e caminho para reprodução.
- Home: cobertura temporal separa IBGE, Embrafilme, OCA, ANCINE e FSA e explicita a descontinuidade do levantamento do IBGE.
- Guia, Mural e Sobre: Guia começa pelas tarefas; Mural aponta para análises e datasets relacionados; Sobre ganhou navegação interna sem perder o manifesto.
- Linguagem: removidas as menções a preço de operação e gratuidade solicitadas; a receita passou a se chamar “Valores Captados/Contratados por mecanismo”.

## Evidência executada

- `npm run build`: aprovado, 120 páginas geradas.
- `python -m pytest tests/test_portal_previews.py tests/test_catalog_integrity.py tests/test_downloads.py tests/test_release_downloads.py -q`: 9 testes aprovados.
- Integridade: nenhum arquivo em `data/`, `catalog/schemas/` ou `catalog/downloads.json` foi alterado.
- Navegador, catálogo: 471 tabelas reconhecidas, somente 80 cartões iniciais no DOM e expansão progressiva; busca por “diretores de obras” encontrou as duas tabelas esperadas.
- Navegador, consulta simples: seleção apenas de `titulo` retornou 100 linhas; o resultado abriu em tabela e o gráfico ficou indisponível por não haver medida numérica.
- Navegador, estado: receita salva foi restaurada após recarga; retirar uma coluna apagou o resultado obsoleto e exibiu o aviso de nova execução.
- Navegador, conexão real: `obras` + `diretores_obras`, pela chave CPB, encontrou 57.514 chaves coincidentes, 57.514 linhas à esquerda, 71.359 à direita e 71.359 pares. A interface informou ausência de expansão muitos-para-muitos nas chaves coincidentes e repetição máxima de `1 × 31`.
- Navegador, Brasil no Mundo: as três abas alternaram conteúdo e o caminho contextual abriu a tabela `brasil_no_mundo_bilheteria_europa` no Analisar.
- Busca de texto: não restam afirmações de “zero reais”, preço zero ou custo zero; a ocorrência de “preço de ingresso” no Guia descreve corretamente a escolha do índice de deflação.

## Preservação de funcionalidades

A consolidação não removeu a área avançada antes de existir equivalência integral. O construtor e as receitas ficam em `/analisar/`; operações de campos, ordenação, filtros, SQL livre, atalhos, exportações e provedores de IA continuam em `/explorar/`, acessível como quarto modo com a tabela atual na URL. O inventário completo e os roteiros de regressão estão em `docs/PARIDADE-ANALISAR-SOL.md`.

Chamadas reais de IA dependem das credenciais do usuário e ficaram fora das evidências. Se a CDN do DuckDB estiver indisponível, o estado e o catálogo continuam visíveis, mas a consulta remota depende do restabelecimento da rede.

Nenhuma atualização do Hugging Face foi feita. Esta reforma altera interface, documentação e pequenas prévias derivadas; não altera os Parquets publicados.

## Revisão antes da publicação (2026-09-10)

- Corrigido `ReferenceError: BUILDER_KEY_COLORS` ao abrir `/analisar/?table=…` (vindo de dataset, Brasil no Mundo ou redirecionamento de `/transformar/`): a constante passou a ser declarada antes da seleção inicial pela URL. Verificado no navegador sem erro de console.
- `outputs/proposta-portal-ux/` (protótipo, capturas e logs locais) entrou no `.gitignore`.
- Pendência conhecida, anterior a esta reforma: `tests/test_pda_updated_snapshots.py` falha no Windows porque `core.autocrlf=true` converte os CSVs para CRLF e altera o sha256. Solução sugerida: `.gitattributes` com `*.csv -text`.
