from pathlib import Path

import pandas as pd
import yaml

from pipelines.transform.clean_oca_financeiros import main


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "pipelines/output/cleaned"


def test_oca_financial_sources_are_split_and_reconciled():
    main()
    expected = {
        "fsa_arrecadacao_anual": 13,
        "fsa_editais_lancados": 11,
        "fsa_desembolsos": 5,
        "fomento_valores_liberados_mecanismo": 34,
        "fomento_valores_captados_mecanismo": 124,
        "fomento_editais_programas_premios": 126,
        "condecine_arrecadacao_bruta_anual": 66,
        "condecine_arrecadacao_pos_dru_anual": 66,
        "condecine_arrecadacao_bruta_mensal": 706,
        "condecine_arrecadacao_pos_dru_mensal": 706,
        "condecine_recolhimento_mensal": 469,
        "condecine_recolhimento_mecanismo": 48,
        "condecine_creditos_remessas_exterior": 48,
        "condecine_recolhimento_distribuidoras_art3": 621,
        "condecine_recolhimento_empresas_art3a": 695,
        "condecine_recolhimento_programadoras_art39": 276,
    }
    for table, rows in expected.items():
        frame = pd.read_parquet(OUTPUT / f"{table}.parquet")
        assert len(frame) == rows
        assert frame["fonte_url"].str.startswith("https://www.gov.br/ancine/").all()
        assert frame["hash_arquivo"].str.fullmatch(r"[0-9a-f]{64}").all()


def test_contributor_names_and_original_currencies_are_preserved():
    distributors = pd.read_parquet(OUTPUT / "condecine_recolhimento_distribuidoras_art3.parquet")
    assert distributors["empresa_brasileira"].notna().all()
    assert distributors["empresa_estrangeira_representada"].notna().all()

    programs = pd.read_parquet(OUTPUT / "fomento_editais_programas_premios.parquet")
    assert set(programs["moeda_original"]) == {"BRL", "USD", "EUR"}
    assert "Total" not in set(programs["mecanismo_ou_programa"])


def test_old_mixed_resources_are_absent_from_catalog():
    catalog = yaml.safe_load((ROOT / "catalog/datasets.yaml").read_text(encoding="utf-8"))
    tables = {
        table if isinstance(table, str) else table["name"]
        for dataset in catalog["datasets"]
        for table in dataset.get("cleaned", {}).get("tables", [])
    }
    assert not {"condecine_arrecadacao", "condecine_recolhimento", "fomento_fluxos_financeiros"} & tables
