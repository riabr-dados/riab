"""
Adiciona campos `categoria` (lista) e `procedencia` (string) em catalog/datasets.yaml.
Preserva ordem e comentários via ruamel.yaml.
"""
from ruamel.yaml import YAML
from pathlib import Path

CATALOG = Path("catalog/datasets.yaml")

# Mapeamento slug -> (categorias, procedencia)
# Procedencia: pda_intacto | limpeza_leve | derivado
MAP = {
    # BR / ANCINE
    "ancine-obras-nao-publicitarias": (["producao_obras"], "limpeza_leve"),
    "ancine-diretores-obras": (["producao_obras"], "limpeza_leve"),
    "ancine-produtores-obras": (["producao_obras"], "limpeza_leve"),
    "ancine-bilheteria-consolidada": (["bilheteria"], "pda_intacto"),
    "ancine-bilheteria-agregada-filme-ano": (["bilheteria"], "pda_intacto"),
    "ancine-fsa-projetos": (["fomento"], "limpeza_leve"),
    "ancine-renuncia-fiscal": (["fomento"], "limpeza_leve"),
    "ancine-condecine-arrecadacao": (["fomento"], "limpeza_leve"),
    "ancine-condecine-recolhimento": (["fomento"], "limpeza_leve"),
    "ancine-fomento-fluxos-financeiros": (["fomento"], "derivado"),
    "ancine-ibermedia-projetos": (["fomento", "internacional"], "limpeza_leve"),
    "ancine-coproducao-internacional-projetos": (["fomento", "internacional"], "limpeza_leve"),
    "ancine-apoio-festivais-internacionais": (["fomento", "internacional"], "limpeza_leve"),
    "ancine-premio-adicional-renda": (["fomento"], "limpeza_leve"),
    "ancine-filmes-lancados-captacao": (["producao_obras", "fomento"], "limpeza_leve"),
    "ancine-captacao-por-projeto-investidor": (["fomento"], "limpeza_leve"),
    "ancine-agentes-economicos": (["emprego_economia"], "limpeza_leve"),
    "ancine-preco-medio-ingresso": (["bilheteria"], "pda_intacto"),
    "ancine-atas-fsa": (["fomento", "fontes_metadados"], "derivado"),
    "ancine-festivais-fsa": (["fomento"], "derivado"),
    "oca-publicacoes-complementares": (["fontes_metadados"], "pda_intacto"),
    # BR / IBGE / outras BR
    "br-pib-audiovisual": (["emprego_economia"], "derivado"),
    "br-rais-emprego-audiovisual": (["emprego_economia"], "derivado"),
    "br-comercio-exterior-servicos-audiovisuais": (["emprego_economia"], "derivado"),
    "br-comex-bens-audiovisuais": (["emprego_economia"], "limpeza_leve"),
    "br-embrafilme-historico-exibicao": (["bilheteria", "salas_exibicao"], "derivado"),
    "ibge-seculoxx-cinema": (["bilheteria", "salas_exibicao"], "derivado"),
    "br-bilheteria-historica-complementar": (["bilheteria"], "derivado"),
    "ancine-diversidade-audiovisual": (["diversidade"], "derivado"),
    "ibge-deflator-ipca": (["emprego_economia"], "pda_intacto"),
    # EU
    "lumiere-cinemas-europa": (["bilheteria", "internacional"], "limpeza_leve"),
    "lumiere-vod-europa": (["vod_streaming", "internacional"], "limpeza_leve"),
    # Brasil no Mundo
    "brasil-no-mundo": (["internacional"], "derivado"),
    # FR / CNC
    "cnc-visas-exploitation": (["producao_obras"], "pda_intacto"),
    "cnc-frequentation-salles": (["bilheteria"], "pda_intacto"),
    "cnc-etablissements": (["salas_exibicao"], "pda_intacto"),
    "cnc-films-million-entrees": (["bilheteria"], "pda_intacto"),
    "cnc-donnees-internationales": (["internacional"], "pda_intacto"),
    "cnc-films-agrees": (["producao_obras"], "pda_intacto"),
    "cnc-audience-television": (["tv_audiencia"], "pda_intacto"),
    "cnc-films-television": (["tv_audiencia"], "pda_intacto"),
    "cnc-exportacao-programas-audiovisuais": (["emprego_economia", "internacional"], "pda_intacto"),
    "cnc-geographie-cinema": (["salas_exibicao"], "pda_intacto"),
    "cnc-public-vod": (["vod_streaming"], "pda_intacto"),
    "cnc-referencias-ativas-vod": (["vod_streaming"], "pda_intacto"),
    "cnc-consumo-vod": (["vod_streaming"], "pda_intacto"),
    "cnc-parc-cinematographique": (["salas_exibicao"], "pda_intacto"),
    "cnc-financement-television": (["tv_audiencia"], "pda_intacto"),
    "cnc-distribution-salles": (["distribuicao"], "pda_intacto"),
    "cnc-public-films": (["bilheteria"], "pda_intacto"),
    # AR / INCAA
    "incaa-espectadores-origem": (["bilheteria"], "limpeza_leve"),
    "incaa-receita-origem": (["bilheteria"], "limpeza_leve"),
    "incaa-estreias-origem": (["producao_obras"], "limpeza_leve"),
    "incaa-espectadores-provincias": (["bilheteria", "salas_exibicao"], "limpeza_leve"),
    "incaa-receita-provincias": (["bilheteria"], "limpeza_leve"),
    "incaa-participacao-distribuidoras": (["distribuicao"], "limpeza_leve"),
    "incaa-empregos-longa-metragem": (["emprego_economia"], "limpeza_leve"),
    "incaa-acessos-tv-assinatura": (["tv_audiencia"], "limpeza_leve"),
    "incaa-receitas-tv-assinatura": (["tv_audiencia"], "limpeza_leve"),
    # UK / BFI
    "bfi-publicos-cinema": (["bilheteria"], "derivado"),
    "bfi-bilheteria-2023": (["bilheteria"], "derivado"),
    "bfi-exibicao-cinematografica": (["salas_exibicao"], "derivado"),
    "bfi-educacao-cinematografica": (["fontes_metadados"], "derivado"),
    "bfi-empresas-industria": (["emprego_economia"], "derivado"),
    "bfi-emprego-industria": (["emprego_economia"], "derivado"),
    "bfi-video-digital": (["vod_streaming"], "derivado"),
    "bfi-video-fisico": (["vod_streaming"], "derivado"),
    "bfi-filmes-televisao": (["tv_audiencia"], "derivado"),
    "bfi-investimento-publico": (["fomento"], "derivado"),
    "bfi-certificacao-obras": (["producao_obras"], "derivado"),
    "bfi-top-filmes-2023": (["bilheteria"], "derivado"),
    "bfi-economia-do-cinema": (["emprego_economia"], "derivado"),
    "bfi-mercado-cinematografico": (["bilheteria", "distribuicao"], "derivado"),
    "bfi-talentos-britanicos-mundo": (["internacional"], "derivado"),
    # UY / ACAU
    "acau-uruguay-apoios-audiovisual": (["fomento"], "limpeza_leve"),
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
        print("[ERRO] slugs no catalog mas sem classificacao:")
        for s in missing:
            print(f"  - {s}")
        return 1

    extras = set(MAP.keys()) - {ds["slug"] for ds in doc["datasets"]}
    if extras:
        print("[WARN] slugs em MAP mas nao no catalog:", extras)

    yaml.dump(doc, CATALOG.open("w", encoding="utf-8"))
    print(f"[OK] {len(doc['datasets'])} datasets atualizados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
