# dados-audiovisual-br

Hub independente de dados públicos do audiovisual brasileiro, com **snapshots datados** e proveniência rastreável.

Este repositório não substitui as fontes oficiais — espelha, datada e auditavelmente, dados públicos já disponibilizados por órgãos como ANCINE, Observatório Europeu do Audiovisual, IBGE e outros. Existe como salvaguarda contra instabilidade institucional, mudanças silenciosas de metodologia e remoção de dados públicos.

Veja [MANIFESTO.md](MANIFESTO.md) para a motivação completa e [FONTES.md](FONTES.md) para o índice de saúde das fontes vivas.

## Modelo

- **Snapshots datados**: cada dataset é coletado periodicamente e armazenado em pasta `snapshots/YYYY-MM-DD/`. Versões anteriores nunca são sobrescritas.
- **Proveniência completa**: cada snapshot tem um `datapackage.json` (padrão [Frictionless Data](https://frictionlessdata.io)) com URL original, data da coleta, hash SHA256 e licença.
- **Auditabilidade**: comparar dois snapshots do mesmo dataset mostra o que mudou — útil quando uma fonte altera metodologia sem aviso.
- **Sinalização de status**: cada dataset declara se a fonte está ativa, offline, alterada ou descontinuada.

## Estrutura

```
dados-audiovisual-br/
├── README.md
├── MANIFESTO.md              # Motivação e princípios
├── FONTES.md                 # Índice de saúde das fontes vivas
├── LICENSE-data              # CC-BY-4.0 (dados derivados/curadoria)
├── LICENSE-code              # MIT (scripts e schemas)
│
├── datasets/                 # Um diretório por dataset
│   ├── ancine-fsa-projetos/
│   │   ├── README.md
│   │   ├── datapackage.json  # Versão "current" — aponta para snapshot mais recente
│   │   └── snapshots/
│   │       └── 2026-05-19/
│   │           ├── projetos-fsa.csv
│   │           ├── datapackage.json
│   │           └── source.txt
│   ├── ancine-renuncia-fiscal/
│   ├── ancine-obras-nao-publicitarias/
│   ├── ancine-bilheteria/
│   ├── lumiere-cinemas-europa/
│   ├── lumiere-vod-europa/
│   └── ...
│
├── schemas/
│   └── datapackage.template.json
│
├── scripts/                  # Futuros workflows de snapshot automatizado
│
└── docs/                     # Documentação adicional (vai pro GitHub Pages)
```

## Datasets disponíveis

33 datasets de 6 países, cobrindo Brasil, França, Reino Unido, Argentina, Uruguai e dados comparativos internacionais. Detalhes de cada fonte em [FONTES.md](FONTES.md).

**Brasil — ANCINE, IBGE, Lumiere (13 datasets)**

| Dataset | Fonte | Cobertura | Status |
|---|---|---|---|
| `ancine-fsa-projetos` | ANCINE / FSA | até 2026-05 | ativo |
| `ancine-renuncia-fiscal` | ANCINE | até 2026-05 | ativo |
| `ancine-obras-nao-publicitarias` | ANCINE / SAV | 2002–2026 (25 CSVs) | ativo |
| `ancine-agentes-economicos` | ANCINE | até 2026-05 | ativo |
| `ancine-diretores-obras` | ANCINE / SAV | até 2026-05 | ativo |
| `ancine-produtores-obras` | ANCINE / SAV | até 2026-05 | ativo |
| `ancine-bilheteria-consolidada` | ANCINE / SADIS | até 2026 | ativo |
| `ancine-bilheteria-agregada-filme-ano` | ANCINE / OCA | até 2026 | intermitente |
| `ancine-preco-medio-ingresso` | ANCINE / OCA | série histórica | intermitente |
| `ancine-atas-fsa` | ANCINE / FSA (PDFs) | 2014–2024 | ativo |
| `lumiere-cinemas-europa` | Observatório Europeu do Audiovisual | até 2026 | ativo |
| `lumiere-vod-europa` | Observatório Europeu do Audiovisual | até 2026 | ativo |
| `ibge-deflator-ipca` | IBGE | base 2024 | ativo |

**França — CNC (17 datasets, Licence Ouverte)**

| Dataset | Conteúdo |
|---|---|
| `cnc-visas-exploitation` | 95.000+ filmes autorizados 1945–2025 (CSV 12MB) |
| `cnc-frequentation-salles` | Frequentação de salas (entradas, sessões, receita) |
| `cnc-etablissements` | Cadastro de cinemas ativos |
| `cnc-films-million-entrees` | Filmes com mais de 1M de espectadores |
| `cnc-donnees-internationales` | Dados comparativos internacionais |
| `cnc-films-agrees` | Filmes aprovados para apoio público |
| `cnc-audience-television` | Audiência televisiva |
| `cnc-films-television` | Filmes na TV francesa |
| `cnc-exportacao-programas-audiovisuais` | Exportação de programas audiovisuais |
| `cnc-geographie-cinema` | Equipamento e frequentação por região/dpto/commune (4 arquivos) |
| `cnc-public-vod` | Público de VoD |
| `cnc-referencias-ativas-vod` | Referências ativas em plataformas VoD |
| `cnc-consumo-vod` | Consumo domiciliar de VoD |
| `cnc-parc-cinematographique` | Parque cinematográfico geral |
| `cnc-financement-television` | Financiamento da televisão |
| `cnc-distribution-salles` | Distribuição de filmes em salas |
| `cnc-public-films` | Perfil do público de filmes |

**Argentina, Reino Unido, Uruguai (3 datasets)**

| Dataset | Fonte | Cobertura | Status |
|---|---|---|---|
| `incaa-sector-audiovisual` | INCAA / Argentina (9 CSVs) | 2001–2023 | ativo |
| `bfi-statistical-yearbook-2023` | BFI / Reino Unido (15 ODS) | 2023 | ativo |
| `acau-uruguay-apoios-audiovisual` | ACAU / Uruguai | 2013–2024 | ativo |

## Licença

- **Dados**: [CC-BY-4.0](LICENSE-data). Atribuição obrigatória às fontes originais e a este repositório.
- **Código (scripts, schemas)**: [MIT](LICENSE-code).

Os dados brutos são públicos por força da Lei de Acesso à Informação (Lei 12.527/2011). Este repositório acrescenta organização, metadados, versionamento e proveniência — não altera o conteúdo das fontes.

## Como contribuir

(Em construção.) O modelo previsto: cada nova fonte pública entra por PR seguindo o template em `schemas/datapackage.template.json`, com snapshot inicial datado e metadados completos.

## Citação

Se você usar estes dados em pesquisa ou jornalismo, cite a fonte original **e** este repositório, indicando a data do snapshot consultado. Exemplo:

> ANCINE. Projetos FSA. Snapshot de 2026-05-19, espelhado em dados-audiovisual-br. Disponível em: [URL].
