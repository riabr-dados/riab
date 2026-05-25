# Reprocessamento com fontes primarias externas

Este repositorio deve preservar duas camadas quando um estudo ANCINE/OCA usa
fontes oficiais externas e a metodologia publicada permite reproducao tecnica.

## Convencao

- `publicado_ancine`: valores exatamente como aparecem no estudo ou anexo da
  ANCINE/OCA, estruturados em CSV. Esta camada e a referencia para citacao
  direta do estudo.
- `reprocessado_fonte_primaria`: valores recalculados a partir da fonte
  primaria externa vigente, mantendo o recorte metodologico observavel no
  estudo ANCINE.
- `comparacao_ancine_fonte_primaria`: tabela de auditoria que explicita a
  diferenca entre as duas camadas.

Quando a fonte primaria vigente divergir da extracao usada pela ANCINE, a
diferenca deve ser publicada, nao escondida. O ganho esperado e rastreabilidade:
URL oficial, script, filtro aplicado, versao/arquivo processado e divergencia
documentada.

## Criterio de aplicacao

Um dataset entra na camada reprocessada somente quando todos os itens abaixo
forem verdadeiros:

1. a fonte primaria oficial externa esta identificada;
2. a metodologia ANCINE explicita o recorte operacional suficiente;
3. os microdados ou tabelas oficiais permitem refazer o indicador;
4. o script consegue gerar a tabela sem redistribuir microdados restritos;
5. a comparacao contra `publicado_ancine` e salva como artefato.

Se algum item faltar, o dataset permanece `publicado_ancine` e recebe status
`planejado`, `planejado_dependente_de_tabulacao` ou
`planejado_dependente_de_fonte`.

## Inventario inicial

| Dataset | Fonte primaria externa | Status | Observacao |
|---|---|---|---|
| `br-rais-emprego-audiovisual` | MTE/PDET microdados RAIS | `implementado_parcial` | Reprocessamento nacional de 2019 implementado. O total recalculado foi 86.230 contra 88.053 publicados pela ANCINE (-2,1%). |
| `ancine-diversidade-audiovisual` | MTE/PDET microdados RAIS | `planejado` | Requer documentar o recorte proprio do estudo de genero e raca antes de comparar com RAIS. |
| `br-pib-audiovisual` | IBGE PAS/PAC e ANATEL | `planejado_dependente_de_tabulacao` | O estudo usa tabulacao especial IBGE por CNAE/porte e estimativas ANCINE para TV por assinatura por cabo. |
| `br-comercio-exterior-servicos-audiovisuais` | MDIC/SISCOSERV por NBS | `planejado_dependente_de_fonte_siscoserv` | O SISCOSERV foi encerrado; e preciso localizar arquivos historicos oficiais equivalentes ao anexo ANCINE. |

## RAIS/PDET 2019

Script:

```powershell
.\.venv\Scripts\python.exe pipelines\transform\reprocess_rais_emprego_audiovisual.py --year 2019 --archive-dir analysis\rais_repro_test
```

Entradas esperadas no `--archive-dir`:

- `RAIS_VINC_PUB_NORTE.7z`
- `RAIS_VINC_PUB_CENTRO_OESTE.7z`
- `RAIS_VINC_PUB_NORDESTE.7z`
- `RAIS_VINC_PUB_SUL.7z`
- `RAIS_VINC_PUB_MG_ES_RJ.7z`
- `RAIS_VINC_PUB_SP.7z`

Fonte oficial:

```text
ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/2019/
```

Filtro aplicado:

- `Vinculo Ativo 31/12 = 1`
- subclasses CNAE 2.0 usadas no estudo ANCINE/OCA

Saidas:

- `rais_emprego_audiovisual_subclasse_ano_reprocessado_pdet_2019.csv`
- `rais_emprego_audiovisual_comparacao_ancine_pdet_2019.csv`
- `rais_emprego_audiovisual_reprocessamento_regioes_pdet_2019.csv`

Os microdados brutos nao devem ser versionados no Git.
