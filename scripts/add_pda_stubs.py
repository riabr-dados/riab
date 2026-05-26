"""
Registra os 24 datasets do PDA ANCINE que ainda não foram coletados como
stubs em catalog/datasets.yaml com status='pendente_coleta'. Cada stub
contém URL do dados.gov.br pra coleta manual futura.

PDA umbrella passa a contar 31 (matching official) — 7 já coletados +
24 pendentes.
"""
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString as LS
from pathlib import Path

CATALOG = Path("catalog/datasets.yaml")
BASE = "https://dados.gov.br/dados/conjuntos-dados"

# (slug_no_portal, titulo_curto, descricao_curta, categorias, tags_extra)
PDA_STUBS = [
    ("ancine-atividades-economicas-agentes",
     "atividades-economicas-dos-agentes-regulares-registrados-na-ancine",
     "Atividades Econômicas dos Agentes Regulares Registrados na Ancine",
     "Detalhamento das atividades econômicas (CNAE) exercidas pelos agentes regulares "
     "registrados na ANCINE. Complementa o cadastro de agentes econômicos.",
     ["emprego_economia"], ["cnae", "atividades", "agentes"]),

    ("ancine-produtoras-independentes",
     "produtoras-independentes-regulares-registradas-na-ancine",
     "Produtoras Independentes Regulares Registradas na Ancine",
     "Listagem oficial das produtoras audiovisuais brasileiras classificadas como "
     "independentes nos termos da Medida Provisória 2.228-1/2001.",
     ["producao_obras", "emprego_economia"], ["produtoras", "independentes"]),

    ("ancine-canais-programadoras",
     "canais-de-programacao-de-programadoras-ativos-credenciados-na-ancine",
     "Canais de Programação de Programadoras Ativos Credenciados na Ancine",
     "Canais de televisão de prestadores credenciados como Programadoras junto à "
     "ANCINE, ativos no momento da coleta.",
     ["tv_audiencia"], ["canais", "programadoras", "tv"]),

    ("ancine-canais-distribuicao-obrigatoria",
     "canais-de-programacao-de-distribuicao-obrigatoria-ativos-credenciados-na-ancine",
     "Canais de Programação de Distribuição Obrigatória Ativos Credenciados na Ancine",
     "Canais de TV de distribuição obrigatória (must-carry) ativos credenciados na ANCINE.",
     ["tv_audiencia"], ["canais", "distribuicao_obrigatoria", "must_carry"]),

    ("ancine-salas-exibicao-complexos",
     "salas-de-exibicao-e-complexos-registrados-na-ancine",
     "Salas de Exibição e Complexos Registrados na Ancine",
     "Cadastro oficial das salas de cinema e dos complexos exibidores registrados na "
     "ANCINE — uma sala por linha, com vinculação ao complexo e ao exibidor.",
     ["salas_exibicao"], ["salas", "complexos", "exibicao", "cinema"]),

    ("ancine-obras-fomento-indireto",
     "obras-nao-publicitarias-brasileiras-com-fomento-indireto-aprovado-na-ancine-leis-de-incentivo-federa",
     "Obras Brasileiras com Fomento Indireto Aprovado (Leis de Incentivo)",
     "Obras não publicitárias brasileiras que tiveram fomento indireto aprovado pela "
     "ANCINE via leis federais de incentivo fiscal (Lei do Audiovisual e Lei Rouanet).",
     ["fomento", "producao_obras"], ["incentivo_fiscal", "lei_audiovisual"]),

    ("ancine-obras-investimento-fsa",
     "obras-nao-publicitarias-brasileiras-com-investimento-do-fsa",
     "Obras Brasileiras com Investimento do FSA",
     "Obras audiovisuais brasileiras que receberam investimento do Fundo Setorial do "
     "Audiovisual (FSA). Complementa os datasets de projetos FSA.",
     ["fomento", "producao_obras"], ["fsa", "investimento"]),

    ("ancine-pais-origem-obras-br",
     "pais-de-origem-das-obras-nao-publicitarias-brasileiras",
     "País de Origem das Obras Não Publicitárias Brasileiras",
     "Vinculação de cada obra brasileira ao(s) país(es) de origem declarado(s) "
     "(coproduções internacionais reconhecidas).",
     ["producao_obras", "internacional"], ["coproducao", "origem"]),

    ("ancine-obras-estrangeiras-roe",
     "obras-nao-publicitarias-estrangeiras-relacao-de-todos-os-roes-emitidos-excluindo-se-a-categoria-de-r",
     "Obras Não Publicitárias Estrangeiras (ROE)",
     "Registro de Obras Estrangeiras (ROE) emitidos pela ANCINE — todas as obras "
     "audiovisuais não publicitárias estrangeiras com circulação registrada no Brasil.",
     ["producao_obras", "internacional"], ["roe", "obras_estrangeiras"]),

    ("ancine-diretores-obras-estrangeiras",
     "diretores-de-obras-nao-publicitarias-estrangeiras-roe",
     "Diretores de Obras Não Publicitárias Estrangeiras (ROE)",
     "Vínculos diretor-obra para obras estrangeiras com ROE emitido pela ANCINE.",
     ["producao_obras", "internacional"], ["diretores", "roe", "obras_estrangeiras"]),

    ("ancine-produtores-obras-estrangeiras",
     "produtores-de-obras-nao-publicitarias-estrangeiras-roe",
     "Produtores de Obras Não Publicitárias Estrangeiras (ROE)",
     "Vínculos produtor-obra para obras estrangeiras com ROE emitido pela ANCINE.",
     ["producao_obras", "internacional"], ["produtores", "roe"]),

    ("ancine-pais-origem-obras-estrangeiras",
     "pais-de-origem-de-obras-nao-publicitarias-estrangeiras-roe",
     "País de Origem de Obras Estrangeiras (ROE)",
     "País de origem declarado das obras estrangeiras com ROE.",
     ["producao_obras", "internacional"], ["origem", "obras_estrangeiras"]),

    ("ancine-bilheteria-diaria-distribuidoras",
     "relatorio-de-bilheteria-diaria-de-obras-informadas-pelas-distribuidoras",
     "Bilheteria Diária — informações de Distribuidoras",
     "Relatório diário de bilheteria por obra conforme reportado pelas distribuidoras "
     "ao SADIS/ANCINE. Granularidade muito maior que a bilheteria agregada anual.",
     ["bilheteria", "distribuicao"], ["sadis", "diaria", "distribuidoras"]),

    ("ancine-grupos-economicos",
     "relacao-de-grupos-economicos",
     "Relação de Grupos Econômicos",
     "Grupos econômicos identificados pela ANCINE no setor audiovisual brasileiro — "
     "agregação de agentes vinculados por controle societário.",
     ["emprego_economia"], ["grupos_economicos", "concentracao"]),

    ("ancine-crt-obras-nao-publicitarias",
     "crt-obras-nao-publicitarias-registradas",
     "CRT — Obras Não Publicitárias Registradas",
     "Certificados de Registro de Título (CRT) emitidos para obras não publicitárias. "
     "Documento que autoriza a comercialização da obra.",
     ["producao_obras"], ["crt", "certificacao", "registro_titulo"]),

    ("ancine-crt-obras-publicitarias",
     "crt-obras-publicitarias-registradas",
     "CRT — Obras Publicitárias Registradas",
     "Certificados de Registro de Título (CRT) emitidos para obras publicitárias "
     "(filmes publicitários, comerciais).",
     ["producao_obras"], ["crt", "publicidade", "publicitarias"]),

    ("ancine-bilheteria-diaria-exibidoras",
     "relatorio-de-bilheteria-diaria-de-obras-informadas-pelas-exibidoras",
     "Bilheteria Diária — informações de Exibidoras",
     "Relatório diário de bilheteria por obra conforme reportado pelas exibidoras "
     "(salas de cinema) ao SADIS/ANCINE.",
     ["bilheteria", "salas_exibicao"], ["sadis", "diaria", "exibidoras"]),

    ("ancine-fsa-investimento-contratados",
     "projetos--de-investimento-contratados-no-ambito-do-fsa",
     "Projetos de Investimento Contratados — FSA (versão PDA)",
     "Versão PDA do dataset de projetos FSA contratados. Pode haver sobreposição com "
     "ancine-fsa-projetos (mesma informação publicada também no portal FSA).",
     ["fomento"], ["fsa", "investimento", "contratado"]),

    ("ancine-prestacao-contas-processos",
     "relacao-de-processos-em-fase-de-prestacao-de-contas",
     "Processos em Fase de Prestação de Contas",
     "Processos de projetos audiovisuais fomentados que estão em fase de prestação de "
     "contas perante a ANCINE.",
     ["fomento"], ["prestacao_contas", "fomento"]),

    ("ancine-filmagem-estrangeira",
     "filmagem-estrangeira-relacao-de-producao-de-obras-audiovisuais-estrangeiras-em-territorio-nacional",
     "Filmagem Estrangeira em Território Nacional",
     "Produções audiovisuais estrangeiras filmadas em território brasileiro — útil para "
     "estatísticas de service-shoot e atratividade do país como locação.",
     ["producao_obras", "internacional"], ["filmagem", "service_shoot", "estrangeiras"]),

    ("ancine-salas-exibicao-evolucao",
     "salas-de-exibicao---evolucao-anual",
     "Salas de Exibição — Evolução Anual",
     "Série temporal anual da quantidade de salas de exibição registradas no Brasil. "
     "Permite acompanhar a expansão/retração do parque exibidor.",
     ["salas_exibicao"], ["salas", "evolucao_anual", "serie_historica"]),

    ("ancine-lancamentos-distribuidoras",
     "lancamentos-comerciais-por-distribuidoras",
     "Lançamentos Comerciais por Distribuidoras",
     "Listagem de lançamentos comerciais de filmes em salas de cinema brasileiras, "
     "agregada por distribuidora.",
     ["distribuicao", "bilheteria"], ["lancamentos", "distribuidoras", "comercial"]),

    ("ancine-agentes-economicos-estrangeiros",
     "agentes-economicos-estrangeiros",
     "Agentes Econômicos Estrangeiros",
     "Cadastro de agentes econômicos estrangeiros que atuam no mercado audiovisual "
     "brasileiro (registrados na ANCINE).",
     ["emprego_economia", "internacional"], ["agentes", "estrangeiros"]),

    ("ancine-complexos-cinematograficos-evolucao",
     "complexos-cinematograficos---evolucao-anual",
     "Complexos Cinematográficos — Evolução Anual",
     "Série temporal anual da quantidade de complexos exibidores no Brasil "
     "(salas agrupadas por complexo).",
     ["salas_exibicao"], ["complexos", "evolucao_anual"]),
]


def build_stub(slug, portal_slug, title, desc, categorias, tags_extra):
    return {
        "slug": slug,
        "title": title,
        "description": LS(desc + "\n"),
        "source_id": "ancine",
        "status": "pendente_coleta",
        "coverage": "—",
        "tags": ["brasil", "ancine", "pda"] + list(tags_extra),
        "raw": {
            "path": f"{slug}/",
            "format": "csv_pendente",
            "files": 0,
            "size_bytes": 0,
            "url_origem": f"{BASE}/{portal_slug}",
        },
        "cleaned": {
            "tables": [],
            "notes": LS(
                "Dataset listado no Plano de Dados Abertos da ANCINE mas ainda nao "
                "foi coletado para o RIDAB. Coleta pendente — ver url_origem para "
                "download manual via dados.gov.br.\n"
            ),
        },
        "categoria": list(categorias),
        "procedencia": "pda",
        "subfonte": "ancine_pda",
    }


def main():
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096
    doc = yaml.load(CATALOG)

    existing = {ds["slug"] for ds in doc["datasets"]}
    added = 0
    for slug, portal_slug, title, desc, cats, tags_extra in PDA_STUBS:
        if slug in existing:
            continue
        stub = build_stub(slug, portal_slug, title, desc, cats, tags_extra)
        doc["datasets"].append(stub)
        added += 1

    yaml.dump(doc, CATALOG.open("w", encoding="utf-8"))
    print(f"[OK] {added} stubs PDA adicionados (total catalog: {len(doc['datasets'])})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
