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

/**
 * Nome específico de uma tabela dentro do dataset.
 * O schema é a fonte editorial preferida; o título do dataset continua visível
 * como contexto, mas não pode tornar dezenas de tabelas indistinguíveis.
 */
export function getTableLabel(table, dataset = null) {
  const schema = getTableSchema(table);
  const explicit = schema?.title ?? schema?.label;
  if (explicit) return String(explicit).trim();

  const special = [
    [/_reprocessamento_regioes_pdet_\d{4}$/, "Arquivos regionais RAIS/PDET"],
    [/_comparacao_ancine_pdet_(\d{4})$/, "Comparação ANCINE × PDET $1"],
    [/_reprocessado_pdet_(\d{4})$/, "Reprocessamento RAIS/PDET $1"],
    [/_total_ano$/, "Total anual"],
    [/_subclasse_ano$/, "Por subclasse CNAE e ano"],
    [/_atividade_ano$/, "Por atividade e ano"],
    [/_servico_ano$/, "Por serviço e ano"],
    [/_fontes$/, "Fontes e proveniência"],
  ];
  for (const [pattern, label] of special) {
    const match = table.match(pattern);
    if (match) return label.replace("$1", match[1] ?? "");
  }

  const humanized = table
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toLocaleUpperCase("pt-BR"));
  const datasetTitle = dataset?.title?.trim();
  return datasetTitle && (dataset?.cleaned?.tables?.length ?? 0) === 1
    ? datasetTitle
    : humanized;
}

/** Descritores compartilhados pelo catálogo, detalhe e ambiente Analisar. */
export function getTableDescriptors(datasets = getDatasets()) {
  const descriptors = new Map();
  for (const dataset of datasets) {
    for (const resource of dataset.cleaned?.tables ?? []) {
      const table = typeof resource === "string" ? resource : resource.name;
      if (!table) continue;
      const schema = getTableSchema(table);
      const current = descriptors.get(table);
      const descriptor = current ?? {
        table,
        label: getTableLabel(table, dataset),
        description: schema?.description?.trim() ?? dataset.description?.trim() ?? "",
        schema,
        datasets: [],
      };
      descriptor.datasets.push({ slug: dataset.slug, title: dataset.title });
      descriptors.set(table, descriptor);
    }
  }
  return [...descriptors.values()];
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
