/**
 * URLs para assets no Hugging Face.
 * Org: riabr-dados  |  Repo: riab  |  Tipo: dataset
 */

const HF_ORG = "riabr-dados";
const HF_REPO = "riab";
const HF_BASE = `https://huggingface.co/datasets/${HF_ORG}/${HF_REPO}/resolve/main`;

export function rawUrl(slug, filename) {
  return `${HF_BASE}/raw/${slug}/${filename}`;
}

export function cleanedUrl(table) {
  return `${HF_BASE}/cleaned/${table}.parquet`;
}

/** Snippet DuckDB para uma tabela cleaned */
export function duckdbSnippet(table) {
  return `import duckdb
conn = duckdb.connect()
conn.sql("INSTALL httpfs; LOAD httpfs;")
df = conn.sql("""
    SELECT *
    FROM '${cleanedUrl(table)}'
    LIMIT 1000
""").df()
print(df.head())`;
}

/** Snippet pandas para uma tabela cleaned */
export function pandasSnippet(table) {
  return `import pandas as pd
df = pd.read_parquet(
    "${cleanedUrl(table)}"
)
print(df.head())`;
}

/** Snippet R para uma tabela cleaned */
export function rSnippet(table) {
  return `library(arrow)
df <- read_parquet(
  "${cleanedUrl(table)}"
)
head(df)`;
}

/** Snippet CLI para baixar raw de um dataset */
export function cliSnippet(slug) {
  return `huggingface-cli download ${HF_ORG}/${HF_REPO} \\
  --repo-type dataset \\
  --include "raw/${slug}/*"`;
}
