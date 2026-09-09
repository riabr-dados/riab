import zipfile

import pyarrow.parquet as pq

from pipelines.transform.clean_bilheteria_diaria import convert_zip


def test_converte_zip_utf8_e_preserva_granularidade(tmp_path):
    source = tmp_path / "fonte.zip"
    content = (
        "DATA_EXIBICAO;TITULO_BRASIL;CPB_ROE;PUBLICO;RAZAO_SOCIAL_DISTRIBUIDORA\n"
        "01/01/2026;AÇÃO;B1;12;DISTRIBUIDORA Ç\n"
    )
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("bilheteria-diaria-obras-por-distribuidoras-2026-01.csv", content.encode("utf-8"))

    assert convert_zip("distribuidora", source, tmp_path) == {2026: 1}
    table = pq.read_table(tmp_path / "bilheteria_diaria_distribuidora_detalhe_2026.parquet")
    assert table.column("titulo_brasil").to_pylist() == ["AÇÃO"]
    assert table.column("publico").to_pylist() == [12]
    assert table.column("arquivo_origem").to_pylist() == [
        "bilheteria-diaria-obras-por-distribuidoras-2026-01.csv"
    ]


def test_agregados_nao_chamam_linhas_de_sessoes():
    source = ("pipelines/transform/aggregate_bilheteria_diaria.py")
    text = open(source, encoding="utf-8").read()
    assert " AS sessoes" not in text
    assert "AS registros_reportados" in text
