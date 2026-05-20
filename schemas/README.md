# Schemas

Templates de metadados seguidos por cada dataset deste repositório.

## datapackage.template.json

Modelo baseado na especificação [Frictionless Data Package](https://specs.frictionlessdata.io/data-package/), com extensões para o caso de uso de salvaguarda:

- **`status`** — bloco que descreve a saúde da fonte original (ativo, intermitente, alterado, offline, descontinuado) e quando foi verificada pela última vez.
- **`collection`** — como o snapshot foi obtido (manual, GitHub Actions, scrape, API) e periodicidade alvo.
- **`snapshots`** — lista de coletas datadas com URL exata de origem e notas de mudança.

Esses três blocos são o coração da camada de auditabilidade. Toda nova fonte deve preenchê-los.

## Convenção de pastas por dataset

```
datasets/<slug-do-dataset>/
├── README.md                       # Descrição humana, schema das colunas, links
├── datapackage.json                # Aponta para o snapshot mais recente (current)
└── snapshots/
    ├── 2026-05-19/
    │   ├── <arquivo-original>      # Exatamente como veio da fonte
    │   ├── datapackage.json        # Específico daquele snapshot
    │   └── source.txt              # URL exata + comando de download + data
    └── 2026-08-19/
        └── ...
```

Snapshots passados nunca são modificados. O `datapackage.json` na raiz do dataset sempre reflete o snapshot mais recente.
