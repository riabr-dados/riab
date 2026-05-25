"""
Teste minimo do reprocessamento RAIS/PDET.

Verifica que:
- A resolucao de colunas por nome funciona quando o header da RAIS muda de
  ordem entre anos (cenario real: 2018 vs 2019 do PDET tiveram layouts
  diferentes).
- A agregacao por subclasse CNAE preserva o filtro Vinculo Ativo 31/12 = 1.
- O reprocessamento mantem a tabela de comparacao com a camada publicada.

Roda com pytest a partir da raiz do projeto. Nao depende dos microdados
reais da RAIS: usa um fixture sintetico de 10 linhas em memoria.
"""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pytest

from pipelines.transform import reprocess_rais_emprego_audiovisual as rais


def _csv_bytes(header: list[str], rows: list[list[str]]) -> bytes:
    out = io.StringIO()
    out.write(";".join(header) + "\n")
    for row in rows:
        out.write(";".join(row) + "\n")
    return out.getvalue().encode("latin1")


def test_resolve_columns_header_padrao_2019():
    # Header do PDET RAIS 2019 (35 colunas omitidas no meio para o teste).
    header = ";".join(
        ["Bairros SP"] * 11
        + ["Vínculo Ativo 31/12"]
        + ["X"] * 24
        + ["CNAE 2.0 Subclasse"]
    ).encode("latin1") + b"\n"
    active_idx, cnae_idx, _ = rais.resolve_columns(header)
    assert active_idx == 11
    assert cnae_idx == 36


def test_resolve_columns_header_reordenado():
    # Caso em que MTE/PDET trocar a ordem em uma versao futura: o script
    # tem que continuar achando as colunas pelo nome.
    header = "Vínculo Ativo 31/12;CNAE 2.0 Subclasse;Outras".encode("latin1") + b"\n"
    active_idx, cnae_idx, _ = rais.resolve_columns(header)
    assert active_idx == 0
    assert cnae_idx == 1


def test_resolve_columns_header_sem_acento():
    header = "Vinculo Ativo 31/12;CNAE 2.0 Subclasse".encode("latin1") + b"\n"
    active_idx, cnae_idx, _ = rais.resolve_columns(header)
    assert active_idx == 0
    assert cnae_idx == 1


def test_resolve_columns_falha_clara_quando_coluna_some():
    header = b"Coluna1;Coluna2;Coluna3\n"
    with pytest.raises(RuntimeError, match="Vinculo Ativo 31/12"):
        rais.resolve_columns(header)


def test_build_reprocessed_inclui_camada_e_fonte():
    df = rais.build_reprocessed(2019, {raw: 1 for raw in rais.SUBCLASSES})
    assert (df["camada_metodologica"] == "reprocessado_fonte_primaria").all()
    assert (df["fonte_url"].str.startswith("ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/2019")).all()
    assert (df["metodo_reprocessamento"] == "vinculo_ativo_31_12_por_subclasse_cnae_ancine").all()
    assert len(df) == len(rais.SUBCLASSES)
