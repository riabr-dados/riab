/**
 * Carrega e normaliza o catalogo de datasets a partir do YAML.
 * Usado em tempo de build pelo Astro (Node.js).
 */
import { readFileSync, readdirSync } from "fs";
import { resolve } from "path";
import yaml from "js-yaml";

const CATALOG_PATH = resolve("../catalog/datasets.yaml");
const SOURCES_PATH = resolve("../catalog/sources.yaml");
const DOWNLOADS_PATH = resolve("../catalog/downloads.json");
const DATASETS_PATH = resolve("../datasets");

export function getDownloads(table) {
  try {
    return JSON.parse(readFileSync(DOWNLOADS_PATH, 'utf-8')).resources[table] ?? null;
  } catch (error) {
    if (error.code === 'ENOENT') return null;
    throw error;
  }
}

function loadCatalog() {
  const raw = readFileSync(CATALOG_PATH, "utf-8");
  const { datasets } = yaml.load(raw);
  return datasets;
}

function loadSources() {
  const raw = readFileSync(SOURCES_PATH, "utf-8");
  const { sources } = yaml.load(raw);
  return Object.fromEntries(sources.map((s) => [s.id, s]));
}

export function getDatasets() {
  const datasets = loadCatalog();
  const sources = loadSources();
  return datasets
    .filter((ds) => !ds.hidden)
    .map((ds) => ({
      ...ds,
      source: sources[ds.source_id] ?? null,
    }));
}

export function getDataset(slug) {
  return getDatasets().find((ds) => ds.slug === slug) ?? null;
}

export function getLatestSnapshotDate(dataset) {
  const rawPath = (dataset.raw?.path ?? `${dataset.slug}/`).replace(/^raw\//, "").replace(/[\\/]$/, "");
  try {
    return readdirSync(resolve(DATASETS_PATH, rawPath, "snapshots"), { withFileTypes: true })
      .filter((entry) => entry.isDirectory() && /^\d{4}-\d{2}-\d{2}$/.test(entry.name))
      .map((entry) => entry.name)
      .sort()
      .at(-1) ?? null;
  } catch {
    return null;
  }
}

/** Estatisticas agregadas para o header do portal */
export function getCatalogStats(datasets) {
  const paises = new Set(datasets.map((ds) => ds.source?.country).filter(Boolean));
  const tabelas = new Set(
    datasets.flatMap((ds) =>
      (ds.cleaned?.tables ?? []).map((table) =>
        typeof table === "string" ? table : table.name
      )
    )
  );
  const fontes = new Set(
    datasets
      .filter((ds) => ds.source?.kind !== "derived")
      .map((ds) => ds.source_id)
      .filter(Boolean)
  );
  return {
    total_datasets: datasets.length,
    total_tabelas: tabelas.size,
    total_paises: paises.size,
    total_fontes: fontes.size,
  };
}

/** Carrega o schema YAML de uma tabela especifica */
export function getTableSchema(table) {
  try {
    const path = resolve(`../catalog/schemas/${table}.yaml`);
    const raw = readFileSync(path, "utf-8");
    return yaml.load(raw);
  } catch {
    return null;
  }
}

/** Gera contexto compacto de schema para o prompt de linguagem natural */
export function buildSchemaContext(table) {
  const schema = getTableSchema(table);
  if (!schema) return "";
  const cols = (schema.columns ?? [])
    .map((c) => `- ${c.name} (${c.type}): ${c.description}${c.categories ? ". Valores possiveis: " + c.categories.join(", ") : ""}`)
    .join("\n");
  return `Tabela: ${table}\nDescricao: ${schema.description?.trim() ?? ""}\nColunas:\n${cols}`;
}

/** Retorna datasets agrupados por pais */
export function byCountry(datasets) {
  const map = {};
  for (const ds of datasets) {
    const c = ds.source?.country ?? "??";
    if (!map[c]) map[c] = [];
    map[c].push(ds);
  }
  return map;
}
