"""Gera os dicionários dos recursos financeiros OCA a partir dos Parquets."""
from pathlib import Path

import pyarrow.parquet as pq
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "pipelines/output/cleaned"
SCHEMAS = ROOT / "catalog/schemas"

TABLES = {
    "fsa_arrecadacao_anual": ("ancine-fsa-arrecadacao", "Arrecadação anual do Fundo Setorial do Audiovisual."),
    "fsa_editais_lancados": ("ancine-fsa-editais-lancados", "Valores de editais lançados pelo Fundo Setorial do Audiovisual."),
    "fsa_desembolsos": ("ancine-fsa-desembolsos", "Desembolsos anuais do Fundo Setorial do Audiovisual."),
    "fomento_valores_liberados_mecanismo": ("ancine-fomento-valores-liberados", "Valores anuais liberados por mecanismo de incentivo."),
    "fomento_valores_captados_mecanismo": ("ancine-fomento-valores-captados", "Valores captados ou contratados por mecanismo de incentivo."),
    "fomento_editais_programas_premios": ("ancine-fomento-editais-programas-premios", "Valores anuais de editais, programas e prêmios, com moeda original explícita."),
    "condecine_arrecadacao_bruta_anual": ("ancine-condecine-arrecadacao-bruta", "Arrecadação bruta anual da CONDECINE por modalidade."),
    "condecine_arrecadacao_bruta_mensal": ("ancine-condecine-arrecadacao-bruta", "Arrecadação bruta mensal da CONDECINE por modalidade."),
    "condecine_arrecadacao_pos_dru_anual": ("ancine-condecine-arrecadacao-pos-dru", "Arrecadação anual da CONDECINE após abatimento da DRU."),
    "condecine_arrecadacao_pos_dru_mensal": ("ancine-condecine-arrecadacao-pos-dru", "Arrecadação mensal da CONDECINE após abatimento da DRU."),
    "condecine_recolhimento_mensal": ("ancine-condecine-recolhimento-mensal", "Recolhimento mensal da CONDECINE por mecanismo legal."),
    "condecine_recolhimento_mecanismo": ("ancine-condecine-recolhimento-mecanismo", "Recolhimento anual da CONDECINE por mecanismo legal."),
    "condecine_creditos_remessas_exterior": ("ancine-condecine-creditos-remessas", "Créditos e remessas para o exterior relacionados aos mecanismos da CONDECINE."),
    "condecine_recolhimento_distribuidoras_art3": ("ancine-condecine-distribuidoras-art3", "Recolhimentos do Art. 3º por distribuidora brasileira e empresa estrangeira representada."),
    "condecine_recolhimento_empresas_art3a": ("ancine-condecine-empresas-art3a", "Recolhimentos do Art. 3º-A por empresa remetente e contribuinte estrangeira."),
    "condecine_recolhimento_programadoras_art39": ("ancine-condecine-programadoras-art39", "Recolhimentos do Art. 39 por programadora estrangeira."),
}

DESCRIPTIONS = {
    "periodo": "Período textual exatamente como publicado.",
    "ano_inicio": "Primeiro ano do período.", "ano_fim": "Último ano do período.",
    "ano": "Ano de referência.", "mes": "Mês de referência, de 1 a 12.",
    "tipo_condecine": "Modalidade de CONDECINE publicada pela ANCINE.",
    "mecanismo": "Mecanismo legal ou de incentivo.",
    "mecanismo_ou_programa": "Mecanismo, edital, programa ou prêmio da linha original.",
    "moeda_original": "Moeda declarada pela célula original: BRL, USD ou EUR.",
    "valor_original": "Valor nominal na moeda original, sem conversão cambial.",
    "valor_nominal_brl": "Valor nominal em reais correntes do período.",
    "empresa_estrangeira_representada": "Empresa estrangeira representada.",
    "empresa_brasileira": "Empresa brasileira responsável pelo recolhimento.",
    "empresa_remetente": "Empresa remetente no Brasil.",
    "empresa_estrangeira_contribuinte": "Empresa estrangeira contribuinte.",
    "programadora_estrangeira": "Programadora estrangeira contribuinte.",
    "linha_origem": "Número da linha no arquivo oficial, começando em 1.",
    "fonte_arquivo": "Nome do arquivo oficial usado na extração.",
    "fonte_url": "URL oficial do arquivo de origem.",
    "hash_arquivo": "SHA-256 do arquivo bruto.",
    "data_coleta": "Data do snapshot local da fonte.",
}


def arrow_type(field):
    value = str(field.type)
    return "decimal" if value.startswith("decimal") else value


def main():
    SCHEMAS.mkdir(parents=True, exist_ok=True)
    for table, (source, description) in TABLES.items():
        schema = pq.read_schema(OUTPUT / f"{table}.parquet")
        document = {
            "table": table,
            "description": description,
            "source_raw": source,
            "columns": [{
                "name": field.name,
                "type": arrow_type(field),
                "nullable": field.nullable,
                "description": DESCRIPTIONS.get(field.name, field.name.replace("_", " ").capitalize() + "."),
            } for field in schema],
            "notes": [
                "Cada recurso contém uma única medida e granularidade.",
                "Linhas de total da planilha não são duplicadas na tabela factual.",
                "Valores são decimais; ausências permanecem nulas e não são convertidas em zero.",
            ],
        }
        target = SCHEMAS / f"{table}.yaml"
        target.write_text(yaml.safe_dump(document, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
        print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()
