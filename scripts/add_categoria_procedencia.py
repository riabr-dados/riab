"""
Adiciona/atualiza campos `categoria` (lista) e `procedencia` (string) em
catalog/datasets.yaml.

procedencia agora reflete a FONTE REAL (não nível de transformação):
  pda        = Plano de Dados Abertos ANCINE (dados.gov.br via ANCINE)
  oca        = Observatório do Cinema e do Audiovisual / ANCINE
  sadis      = SADIS / Sistema ANCINE de Informações
  fsa        = Fundo Setorial do Audiovisual
  embrafilme = Embrafilme (PDFs históricos, via OCA)
  ibge       = IBGE
  mdic       = Comex Stat / MDIC
  composto   = Derivado de múltiplas fontes (multi-source join)
  cnc        = CNC França
  bfi        = BFI Reino Unido
  incaa      = INCAA Argentina
  acau       = ACAU Uruguai
  lumiere    = Observatório Europeu do Audiovisual
"""
from ruamel.yaml import YAML
from pathlib import Path

CATALOG = Path("catalog/datasets.yaml")

# Lista oficial PDA (gov.br/ancine/pt-br/oca/dados-abertos) — 21 conjuntos:
# 1. Agentes Econômicos Regulares Registrados na Ancine
# 2. Atividades Econômicas dos Agentes Regulares
# 3. Obras Não Publicitárias Brasileiras Registradas na Ancine
# 4. Produtores de Obras Não Publicitárias Brasileiras
# 5. Diretores de Obras Não Publicitárias Brasileiras
# 6. Obras Não Publicitárias Brasileiras com Fomento Indireto Aprovado (Lei...)
# 7. Obras Não Publicitárias Brasileiras com Investimento do FSA
# 8. País de Origem das Obras Não Publicitárias Brasileiras
# 9. Obras Não Publicitárias Estrangeiras (ROE)
# 10. Diretores de Obras Não Publicitárias Estrangeiras (ROE)
# 11. Produtores de Obras Não Publicitárias Estrangeiras (ROE)
# 12. País de Origem de Obras Não Publicitárias Estrangeiras (ROE)
# 13. Relatório de bilheteria diária — distribuidoras
# 14. CRT Obras não publicitárias registradas
# 15. CRT Obras publicitárias registradas
# 16. Relatório de bilheteria diária — exibidoras
# 17. Relação de projetos com valores captados por mecanismo de renúncia fiscal
# 18. Relação de contribuintes que aplicaram em projetos com renúncia fiscal
# 19. Filmagem Estrangeira
# 20. Agentes Econômicos Estrangeiros
# 21. Coproduções Internacionais — Participação Brasileira

MAP = {
    # BR / ANCINE — PDA
    "ancine-obras-nao-publicitarias": (["producao_obras"], "pda"),
    "ancine-diretores-obras": (["producao_obras"], "pda"),
    "ancine-produtores-obras": (["producao_obras"], "pda"),
    "ancine-agentes-economicos": (["emprego_economia"], "pda"),
    "ancine-renuncia-fiscal": (["fomento"], "pda"),
    "ancine-captacao-por-projeto-investidor": (["fomento"], "pda"),
    "ancine-coproducao-internacional-projetos": (["fomento", "internacional"], "pda"),
    # BR / ANCINE — OCA (publicações OCA / painéis, não-PDA)
    "ancine-bilheteria-agregada-filme-ano": (["bilheteria"], "oca"),
    "ancine-condecine-arrecadacao": (["fomento"], "oca"),
    "ancine-condecine-recolhimento": (["fomento"], "oca"),
    "ancine-fomento-fluxos-financeiros": (["fomento"], "oca"),
    "ancine-ibermedia-projetos": (["fomento", "internacional"], "oca"),
    "ancine-apoio-festivais-internacionais": (["fomento", "internacional"], "oca"),
    "ancine-premio-adicional-renda": (["fomento"], "oca"),
    "ancine-filmes-lancados-captacao": (["producao_obras", "fomento"], "oca"),
    "ancine-preco-medio-ingresso": (["bilheteria"], "oca"),
    "oca-publicacoes-complementares": (["fontes_metadados"], "oca"),
    # BR / ANCINE — SADIS
    "ancine-bilheteria-consolidada": (["bilheteria"], "sadis"),
    # BR / ANCINE — FSA
    "ancine-fsa-projetos": (["fomento"], "fsa"),
    "ancine-atas-fsa": (["fomento", "fontes_metadados"], "fsa"),
    "ancine-festivais-fsa": (["fomento"], "fsa"),
    # BR / Outras fontes
    "br-pib-audiovisual": (["emprego_economia"], "oca"),
    "br-rais-emprego-audiovisual": (["emprego_economia"], "oca"),
    "br-comercio-exterior-servicos-audiovisuais": (["emprego_economia"], "oca"),
    "br-comex-bens-audiovisuais": (["emprego_economia"], "mdic"),
    "br-embrafilme-historico-exibicao": (["bilheteria", "salas_exibicao"], "embrafilme"),
    "ibge-seculoxx-cinema": (["bilheteria", "salas_exibicao"], "ibge"),
    "br-bilheteria-historica-complementar": (["bilheteria"], "composto"),
    "ancine-diversidade-audiovisual": (["diversidade"], "oca"),
    "ibge-deflator-ipca": (["emprego_economia"], "ibge"),
    # EU
    "lumiere-cinemas-europa": (["bilheteria", "internacional"], "lumiere"),
    "lumiere-vod-europa": (["vod_streaming", "internacional"], "lumiere"),
    # Composto multi-país
    "brasil-no-mundo": (["internacional"], "composto"),
    # FR / CNC
    "cnc-visas-exploitation": (["producao_obras"], "cnc"),
    "cnc-frequentation-salles": (["bilheteria"], "cnc"),
    "cnc-etablissements": (["salas_exibicao"], "cnc"),
    "cnc-films-million-entrees": (["bilheteria"], "cnc"),
    "cnc-donnees-internationales": (["internacional"], "cnc"),
    "cnc-films-agrees": (["producao_obras"], "cnc"),
    "cnc-audience-television": (["tv_audiencia"], "cnc"),
    "cnc-films-television": (["tv_audiencia"], "cnc"),
    "cnc-exportacao-programas-audiovisuais": (["emprego_economia", "internacional"], "cnc"),
    "cnc-geographie-cinema": (["salas_exibicao"], "cnc"),
    "cnc-public-vod": (["vod_streaming"], "cnc"),
    "cnc-referencias-ativas-vod": (["vod_streaming"], "cnc"),
    "cnc-consumo-vod": (["vod_streaming"], "cnc"),
    "cnc-parc-cinematographique": (["salas_exibicao"], "cnc"),
    "cnc-financement-television": (["tv_audiencia"], "cnc"),
    "cnc-distribution-salles": (["distribuicao"], "cnc"),
    "cnc-public-films": (["bilheteria"], "cnc"),
    # AR / INCAA
    "incaa-espectadores-origem": (["bilheteria"], "incaa"),
    "incaa-receita-origem": (["bilheteria"], "incaa"),
    "incaa-estreias-origem": (["producao_obras"], "incaa"),
    "incaa-espectadores-provincias": (["bilheteria", "salas_exibicao"], "incaa"),
    "incaa-receita-provincias": (["bilheteria"], "incaa"),
    "incaa-participacao-distribuidoras": (["distribuicao"], "incaa"),
    "incaa-empregos-longa-metragem": (["emprego_economia"], "incaa"),
    "incaa-acessos-tv-assinatura": (["tv_audiencia"], "incaa"),
    "incaa-receitas-tv-assinatura": (["tv_audiencia"], "incaa"),
    # UK / BFI
    "bfi-publicos-cinema": (["bilheteria"], "bfi"),
    "bfi-bilheteria-2023": (["bilheteria"], "bfi"),
    "bfi-exibicao-cinematografica": (["salas_exibicao"], "bfi"),
    "bfi-educacao-cinematografica": (["fontes_metadados"], "bfi"),
    "bfi-empresas-industria": (["emprego_economia"], "bfi"),
    "bfi-emprego-industria": (["emprego_economia"], "bfi"),
    "bfi-video-digital": (["vod_streaming"], "bfi"),
    "bfi-video-fisico": (["vod_streaming"], "bfi"),
    "bfi-filmes-televisao": (["tv_audiencia"], "bfi"),
    "bfi-investimento-publico": (["fomento"], "bfi"),
    "bfi-certificacao-obras": (["producao_obras"], "bfi"),
    "bfi-top-filmes-2023": (["bilheteria"], "bfi"),
    "bfi-economia-do-cinema": (["emprego_economia"], "bfi"),
    "bfi-mercado-cinematografico": (["bilheteria", "distribuicao"], "bfi"),
    "bfi-talentos-britanicos-mundo": (["internacional"], "bfi"),
    # UY / ACAU
    "acau-uruguay-apoios-audiovisual": (["fomento"], "acau"),
}


def main():
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096
    doc = yaml.load(CATALOG)

    missing = []
    for ds in doc["datasets"]:
        slug = ds["slug"]
        if slug not in MAP:
            missing.append(slug)
            continue
        cats, proc = MAP[slug]
        ds["categoria"] = cats
        ds["procedencia"] = proc

    if missing:
        print("[ERRO] slugs no catalog sem classificacao:")
        for s in missing:
            print(f"  - {s}")
        return 1

    yaml.dump(doc, CATALOG.open("w", encoding="utf-8"))
    # Resumo
    from collections import Counter
    counts = Counter(ds["procedencia"] for ds in doc["datasets"])
    print(f"[OK] {len(doc['datasets'])} datasets atualizados")
    print("Distribuicao por procedencia:")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {k:12s} {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
