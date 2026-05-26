"""
Adiciona/atualiza campos `categoria` (lista), `procedencia` (string) e
`subfonte` (string opcional) em catalog/datasets.yaml.

procedencia = hierarquia mais alta (filtro principal):
  pda        = Plano de Dados Abertos ANCINE (umbrella — inclui PDA proper +
               SADIS + FSA + OCA + Embrafilme histórico, tudo publicado em
               https://www.gov.br/ancine/pt-br/oca/dados-abertos)
  ibge       = IBGE (PIB, RAIS-OCA estão sob PDA pois publicados via OCA,
               mas Século XX e Deflator são direto IBGE)
  mdic       = Comex Stat / MDIC
  composto   = Derivado multi-fonte
  cnc        = CNC França
  bfi        = BFI Reino Unido
  incaa      = INCAA Argentina
  acau       = ACAU Uruguai
  lumiere    = Lumiere Europa

subfonte = detalhe secundário, exibido no card como "PDA · {subfonte}":
  ancine_pda  = lista oficial PDA (dados.gov.br via ANCINE)
  oca         = publicação OCA / painéis ANCINE
  sadis       = SADIS / SCB
  fsa         = portal FSA
  embrafilme  = PDFs históricos Embrafilme via OCA
"""
from ruamel.yaml import YAML
from pathlib import Path

CATALOG = Path("catalog/datasets.yaml")

# (categorias, procedencia, subfonte_opcional)
MAP = {
    # BR / ANCINE — PDA proper (lista oficial em dados.gov.br)
    "ancine-obras-nao-publicitarias": (["producao_obras"], "pda", "ancine_pda"),
    "ancine-diretores-obras": (["producao_obras"], "pda", "ancine_pda"),
    "ancine-produtores-obras": (["producao_obras"], "pda", "ancine_pda"),
    "ancine-agentes-economicos": (["emprego_economia"], "pda", "ancine_pda"),
    "ancine-renuncia-fiscal": (["fomento"], "pda", "ancine_pda"),
    "ancine-captacao-por-projeto-investidor": (["fomento"], "pda", "ancine_pda"),
    "ancine-coproducao-internacional-projetos": (["fomento", "internacional"], "pda", "ancine_pda"),
    # BR / ANCINE — OCA (publicações OCA, painéis ANCINE)
    "ancine-bilheteria-agregada-filme-ano": (["bilheteria"], "pda", "oca"),
    "ancine-condecine-arrecadacao": (["fomento"], "pda", "oca"),
    "ancine-condecine-recolhimento": (["fomento"], "pda", "oca"),
    "ancine-fomento-fluxos-financeiros": (["fomento"], "pda", "oca"),
    "ancine-ibermedia-projetos": (["fomento", "internacional"], "pda", "oca"),
    "ancine-apoio-festivais-internacionais": (["fomento", "internacional"], "pda", "oca"),
    "ancine-premio-adicional-renda": (["fomento"], "pda", "oca"),
    "ancine-filmes-lancados-captacao": (["producao_obras", "fomento"], "pda", "oca"),
    "ancine-preco-medio-ingresso": (["bilheteria"], "pda", "oca"),
    "oca-publicacoes-complementares": (["fontes_metadados"], "pda", "oca"),
    "br-pib-audiovisual": (["emprego_economia"], "pda", "oca"),
    "br-rais-emprego-audiovisual": (["emprego_economia"], "pda", "oca"),
    "br-comercio-exterior-servicos-audiovisuais": (["emprego_economia"], "pda", "oca"),
    "ancine-diversidade-audiovisual": (["diversidade"], "pda", "oca"),
    # BR / ANCINE — SADIS
    "ancine-bilheteria-consolidada": (["bilheteria"], "pda", "sadis"),
    # BR / ANCINE — FSA
    "ancine-fsa-projetos": (["fomento"], "pda", "fsa"),
    "ancine-atas-fsa": (["fomento", "fontes_metadados"], "pda", "fsa"),
    "ancine-festivais-fsa": (["fomento"], "pda", "fsa"),
    # BR / ANCINE — Embrafilme histórico (via OCA)
    "br-embrafilme-historico-exibicao": (["bilheteria", "salas_exibicao"], "pda", "embrafilme"),
    # BR / Outras fontes (fora do PDA)
    "br-comex-bens-audiovisuais": (["emprego_economia"], "mdic", None),
    "ibge-seculoxx-cinema": (["bilheteria", "salas_exibicao"], "ibge", None),
    "ibge-deflator-ipca": (["emprego_economia"], "ibge", None),
    "br-bilheteria-historica-complementar": (["bilheteria"], "composto", None),
    # Composto multi-país
    "brasil-no-mundo": (["internacional"], "composto", None),
    # EU
    "lumiere-cinemas-europa": (["bilheteria", "internacional"], "lumiere", None),
    "lumiere-vod-europa": (["vod_streaming", "internacional"], "lumiere", None),
    # FR / CNC
    "cnc-visas-exploitation": (["producao_obras"], "cnc", None),
    "cnc-frequentation-salles": (["bilheteria"], "cnc", None),
    "cnc-etablissements": (["salas_exibicao"], "cnc", None),
    "cnc-films-million-entrees": (["bilheteria"], "cnc", None),
    "cnc-donnees-internationales": (["internacional"], "cnc", None),
    "cnc-films-agrees": (["producao_obras"], "cnc", None),
    "cnc-audience-television": (["tv_audiencia"], "cnc", None),
    "cnc-films-television": (["tv_audiencia"], "cnc", None),
    "cnc-exportacao-programas-audiovisuais": (["emprego_economia", "internacional"], "cnc", None),
    "cnc-geographie-cinema": (["salas_exibicao"], "cnc", None),
    "cnc-public-vod": (["vod_streaming"], "cnc", None),
    "cnc-referencias-ativas-vod": (["vod_streaming"], "cnc", None),
    "cnc-consumo-vod": (["vod_streaming"], "cnc", None),
    "cnc-parc-cinematographique": (["salas_exibicao"], "cnc", None),
    "cnc-financement-television": (["tv_audiencia"], "cnc", None),
    "cnc-distribution-salles": (["distribuicao"], "cnc", None),
    "cnc-public-films": (["bilheteria"], "cnc", None),
    # AR / INCAA
    "incaa-espectadores-origem": (["bilheteria"], "incaa", None),
    "incaa-receita-origem": (["bilheteria"], "incaa", None),
    "incaa-estreias-origem": (["producao_obras"], "incaa", None),
    "incaa-espectadores-provincias": (["bilheteria", "salas_exibicao"], "incaa", None),
    "incaa-receita-provincias": (["bilheteria"], "incaa", None),
    "incaa-participacao-distribuidoras": (["distribuicao"], "incaa", None),
    "incaa-empregos-longa-metragem": (["emprego_economia"], "incaa", None),
    "incaa-acessos-tv-assinatura": (["tv_audiencia"], "incaa", None),
    "incaa-receitas-tv-assinatura": (["tv_audiencia"], "incaa", None),
    # UK / BFI
    "bfi-publicos-cinema": (["bilheteria"], "bfi", None),
    "bfi-bilheteria-2023": (["bilheteria"], "bfi", None),
    "bfi-exibicao-cinematografica": (["salas_exibicao"], "bfi", None),
    "bfi-educacao-cinematografica": (["fontes_metadados"], "bfi", None),
    "bfi-empresas-industria": (["emprego_economia"], "bfi", None),
    "bfi-emprego-industria": (["emprego_economia"], "bfi", None),
    "bfi-video-digital": (["vod_streaming"], "bfi", None),
    "bfi-video-fisico": (["vod_streaming"], "bfi", None),
    "bfi-filmes-televisao": (["tv_audiencia"], "bfi", None),
    "bfi-investimento-publico": (["fomento"], "bfi", None),
    "bfi-certificacao-obras": (["producao_obras"], "bfi", None),
    "bfi-top-filmes-2023": (["bilheteria"], "bfi", None),
    "bfi-economia-do-cinema": (["emprego_economia"], "bfi", None),
    "bfi-mercado-cinematografico": (["bilheteria", "distribuicao"], "bfi", None),
    "bfi-talentos-britanicos-mundo": (["internacional"], "bfi", None),
    # UY / ACAU
    "acau-uruguay-apoios-audiovisual": (["fomento"], "acau", None),
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
        cats, proc, subf = MAP[slug]
        ds["categoria"] = cats
        ds["procedencia"] = proc
        if subf is not None:
            ds["subfonte"] = subf
        elif "subfonte" in ds:
            del ds["subfonte"]

    if missing:
        print("[ERRO] slugs no catalog sem classificacao:")
        for s in missing:
            print(f"  - {s}")
        return 1

    yaml.dump(doc, CATALOG.open("w", encoding="utf-8"))
    from collections import Counter
    proc_counts = Counter(ds["procedencia"] for ds in doc["datasets"])
    sub_counts = Counter(ds.get("subfonte") for ds in doc["datasets"] if ds.get("subfonte"))
    print(f"[OK] {len(doc['datasets'])} datasets atualizados")
    print("\nFonte primaria (procedencia):")
    for k, v in sorted(proc_counts.items(), key=lambda x: -x[1]):
        print(f"  {k:12s} {v}")
    print("\nSub-fonte (apenas dentro do PDA):")
    for k, v in sorted(sub_counts.items(), key=lambda x: -x[1]):
        print(f"  {k:12s} {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
