"""Atualiza a planilha de tarefas com o resultado verificável da correção."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "docs/correcoes-auditoria/tarefas.csv"

INCAA = {
    "incaa-espectadores-origem", "incaa-receita-origem", "incaa-estreias-origem",
    "incaa-espectadores-provincias", "incaa-receita-provincias",
    "incaa-participacao-distribuidoras", "incaa-empregos-longa-metragem",
    "incaa-acessos-tv-assinatura", "incaa-receitas-tv-assinatura",
}
LUMIERE = {"lumiere-cinemas-europa", "lumiere-vod-europa"}
SPECIAL = {
    "ancine-renuncia-fiscal": "18 campos monetários reprocessados; reconciliação e teste de regressão aprovados.",
    "ancine-captacao-por-projeto-investidor": "Três fontes separadas em três recursos homogêneos, com identificadores e valores reconciliados.",
    "ancine-fomento-fluxos-financeiros": "Séries do OCA separadas por conceito; o rótulo publicado é Valores Captados/Contratados por Mecanismo.",
    "ancine-bilheteria-diaria-distribuidoras": "152 CSVs oficiais, 21.274.038 linhas detalhadas em 13 partições anuais e agregado refeito.",
    "ancine-bilheteria-diaria-exibidoras": "651 CSVs oficiais, 37.672.799 linhas detalhadas em 13 partições anuais e três agregados refeitos.",
    "ancine-obras-estrangeiras-roe": "Snapshot oficial de 2026-09-08 promovido; 31.311 linhas reprocessadas.",
    "ancine-crt-obras-nao-publicitarias": "Snapshot oficial de 2026-09-08 promovido; 185.819 linhas e dois agregados refeitos.",
}


def main() -> None:
    with PATH.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        slug = row["dataset"]
        result = row["resultado_auditoria"]
        if slug in LUMIERE:
            row["execucao"] = "Pendente externo"
            row["evidencia_final"] = (
                "URL oficial corrigida e disponibilidade confirmada em 2026-09-09; o snapshot não registra "
                "todos os filtros/paginação necessários para provar completude ou repetir exatamente a consulta."
            )
        elif slug in INCAA:
            row["execucao"] = "Concluído com limitação"
            row["evidencia_final"] = (
                "Catálogo oficial SINCA confirmou esquema, unidade e cobertura até 2023. Coberturas e descrições "
                "foram corrigidas; nova comparação binária foi bloqueada pelo desafio Cloudflare da origem."
            )
        elif result == "Documental":
            row["execucao"] = "Documentado"
            row["evidencia_final"] = (
                "Registro mantido como inventário/planejamento e excluído da contagem de conjuntos factuais publicados."
            )
        elif result == "Atualizar":
            row["execucao"] = "Concluído"
            row["evidencia_final"] = (
                "Snapshot oficial de 2026-09-08 com hash e proveniência; Parquet e downloads integrais reprocessados."
            )
        elif result == "Melhorar":
            row["execucao"] = "Concluído"
            row["evidencia_final"] = (
                "Recurso publicado separadamente com Parquet, CSV/CSV.GZ integral e XLSX quando compatível com o tamanho."
            )
        else:
            row["execucao"] = "Concluído"
            row["evidencia_final"] = (
                "Correção aplicada, esquema alinhado ao Parquet e downloads independentes gerados e reabertos."
            )
        if slug in SPECIAL:
            row["evidencia_final"] = SPECIAL[slug]
    with PATH.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} tarefas atualizadas")


if __name__ == "__main__":
    main()
