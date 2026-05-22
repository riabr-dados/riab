"""Transform: datasets INCAA (Instituto Nacional de Cine y Artes Audiovisuales)
Fonte: incaa-sector-audiovisual
Saida: 9 Parquets em pipelines/output/cleaned/
"""
import pandas as pd
from pathlib import Path
from common import latest_snapshot

RAW = Path("datasets")
OUT = Path("pipelines/output/cleaned")
OUT.mkdir(parents=True, exist_ok=True)

SNAP = latest_snapshot(RAW / "incaa-sector-audiovisual")

# Codigos INDEC de provincias argentinas
PROVINCIAS = {
    2:  "Ciudad Autonoma de Buenos Aires",
    6:  "Buenos Aires",
    10: "Catamarca",
    14: "Cordoba",
    18: "Corrientes",
    22: "Chaco",
    26: "Chubut",
    30: "Entre Rios",
    34: "Formosa",
    38: "Jujuy",
    42: "La Pampa",
    46: "La Rioja",
    50: "Mendoza",
    54: "Misiones",
    58: "Neuquen",
    62: "Rio Negro",
    66: "Salta",
    70: "San Juan",
    74: "San Luis",
    78: "Santa Cruz",
    82: "Santa Fe",
    86: "Santiago del Estero",
    90: "Tucuman",
    94: "Tierra del Fuego",
}


def _read(fname):
    df = pd.read_csv(SNAP / fname, encoding="utf-8")
    df.columns = [c.strip() for c in df.columns]
    return df


def _ano(df):
    df = df.copy()
    df["ano"] = pd.to_datetime(df["indice_tiempo"]).dt.year.astype("Int64")
    return df.drop(columns=["indice_tiempo"])


def _int(df, *cols):
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    return df


def _melt_provincias(df, value_col_prefix, value_name):
    """Wide com codigos INDEC → formato longo com codigo e nome da provincia."""
    value_cols = [c for c in df.columns if c.startswith(value_col_prefix)]
    df = df.melt(
        id_vars=["ano"],
        value_vars=value_cols,
        var_name="_col",
        value_name=value_name,
    )
    df["codigo_indec"] = df["_col"].str.extract(r"(\d+)$").astype(int)
    df["provincia"] = df["codigo_indec"].map(PROVINCIAS)
    df[value_name] = pd.to_numeric(df[value_name], errors="coerce").astype("Int64")
    return (
        df[["ano", "codigo_indec", "provincia", value_name]]
        .sort_values(["ano", "codigo_indec"])
        .reset_index(drop=True)
    )


# ── A01: espectadores por origem ──────────────────────────────────────────────
print("Processando incaa_espectadores_origem …")
df = _read("a01-espectadores-cine-origen-film.csv")
df = _ano(df)
df = df.rename(columns={
    "espectadores_films_nacionales":  "espectadores_nacionais",
    "espactadores_films_extranjeros": "espectadores_estrangeiros",
    "festivales_ y_muestras":         "espectadores_festivais",
})
df = _int(df, "espectadores_nacionais", "espectadores_estrangeiros", "espectadores_festivais")
out = OUT / "incaa_espectadores_origem.parquet"
df.to_parquet(out, index=False)
print(f"  -> {out} ({len(df)} linhas)")

# ── A02: receita por origem ───────────────────────────────────────────────────
print("Processando incaa_receita_origem …")
df = _read("a02-recaudacion-cine-nacional-origen-film.csv")
df = _ano(df)
df = df.rename(columns={
    "recaudacion_films_nacionales":       "receita_nacionais",
    "recaudacion_films_extranjeros":      "receita_estrangeiros",
    "recaudacion_festivales_y_muestras":  "receita_festivais",
})
df = _int(df, "receita_nacionais", "receita_estrangeiros", "receita_festivais")
out = OUT / "incaa_receita_origem.parquet"
df.to_parquet(out, index=False)
print(f"  -> {out} ({len(df)} linhas)")

# ── A03: estreias por origem ──────────────────────────────────────────────────
print("Processando incaa_estreias_origem …")
df = _read("a03-estrenos-cine-origen-film.csv")
df = _ano(df)
df = df.rename(columns={
    "estrenos_film_nacional":    "estreias_nacionais",
    "estrenos_film_extranjero":  "estreias_estrangeiros",
})
df = _int(df, "estreias_nacionais", "estreias_estrangeiros")
out = OUT / "incaa_estreias_origem.parquet"
df.to_parquet(out, index=False)
print(f"  -> {out} ({len(df)} linhas)")

# ── A04: espectadores por provincia ──────────────────────────────────────────
print("Processando incaa_espectadores_provincias …")
df = _ano(_read("a04-espectadores-cine-nivel-provincial.csv"))
df = _melt_provincias(df, "espect_cine_", "espectadores")
out = OUT / "incaa_espectadores_provincias.parquet"
df.to_parquet(out, index=False)
print(f"  -> {out} ({len(df)} linhas)")

# ── A05: receita por provincia ────────────────────────────────────────────────
# Nota: a05 tem os codigos 90/94 trocados nos nomes das colunas vs padrao INDEC.
# Usamos o codigo numerico como fonte de verdade (consistente com a04).
print("Processando incaa_receita_provincias …")
df = _ano(_read("a05-recaudacion-cine-nivel-provincial.csv"))
df = _melt_provincias(df, "recaud_cine_", "receita")
out = OUT / "incaa_receita_provincias.parquet"
df.to_parquet(out, index=False)
print(f"  -> {out} ({len(df)} linhas)")

# ── A06: participacao de distribuidoras (proporcoes 0–1) ──────────────────────
print("Processando incaa_participacao_distribuidoras …")
df = _read("a06-participacion-espectadores-distribuidora.csv")
df = _ano(df)
df = df.rename(columns={
    "espect_distribuidoras_nacionales":  "proporcao_nacionais",
    "espect_distribuidoras_extranjeras": "proporcao_estrangeiras",
})
df["proporcao_nacionais"]   = pd.to_numeric(df["proporcao_nacionais"],   errors="coerce")
df["proporcao_estrangeiras"] = pd.to_numeric(df["proporcao_estrangeiras"], errors="coerce")
out = OUT / "incaa_participacao_distribuidoras.parquet"
df.to_parquet(out, index=False)
print(f"  -> {out} ({len(df)} linhas)")

# ── A07: empregos em longa-metragem ──────────────────────────────────────────
print("Processando incaa_empregos_longa_metragem …")
df = _read("a07-puestos-trabajo-largometrajes-nacional.csv")
df = _ano(df)
df = df.rename(columns={"puestos_trabajo_largometrajes": "postos_trabalho"})
df = _int(df, "postos_trabalho")
out = OUT / "incaa_empregos_longa_metragem.parquet"
df.to_parquet(out, index=False)
print(f"  -> {out} ({len(df)} linhas)")

# ── A09: acessos tv por assinatura ───────────────────────────────────────────
print("Processando incaa_acessos_tv_assinatura …")
df = _read("a09-accesos-servicios-tv-suscripcion.csv")
df = _ano(df)
df = df.rename(columns={
    "accesos_tv_cable":     "acessos_tv_cabo",
    "accesos_tv_satelital": "acessos_tv_satelite",
})
df = _int(df, "acessos_tv_cabo", "acessos_tv_satelite")
out = OUT / "incaa_acessos_tv_assinatura.parquet"
df.to_parquet(out, index=False)
print(f"  -> {out} ({len(df)} linhas)")

# ── A10: receitas tv por assinatura ──────────────────────────────────────────
print("Processando incaa_receitas_tv_assinatura …")
df = _read("a10-ingresos-servicios-tv-suscripcion.csv")
df = _ano(df)
df = df.rename(columns={
    "ingresos_tv_cable":     "receitas_tv_cabo",
    "ingresos_tv_satelital": "receitas_tv_satelite",
})
df = _int(df, "receitas_tv_cabo", "receitas_tv_satelite")
out = OUT / "incaa_receitas_tv_assinatura.parquet"
df.to_parquet(out, index=False)
print(f"  -> {out} ({len(df)} linhas)")

print("\nINCAA OK.")
