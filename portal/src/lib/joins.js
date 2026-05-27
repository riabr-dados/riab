/**
 * Le catalog/joins.yaml e expoe helpers para o portal:
 *  - listJoinableWith(table)  -> lista de tabelas que se ligam a `table` (do mais forte ao mais fraco)
 *  - keysExposedBy(table)     -> mapeamento { CHAVE: [{col, confidence, normalize}] }
 *  - findBridge(t1, t2)       -> bridge entre duas tabelas, ou null
 *  - planJoin([t1, t2, ...])  -> sequencia de joins sugerida com a chave em cada passo
 *
 * Usado em tempo de build (Astro/Node) — nao bundle no client.
 */
import { readFileSync } from "fs";
import { resolve } from "path";
import yaml from "js-yaml";

const JOINS_PATH = resolve("../catalog/joins.yaml");

let _cache = null;

function load() {
  if (_cache) return _cache;
  const raw = readFileSync(JOINS_PATH, "utf-8");
  const doc = yaml.load(raw);
  // index for O(1) access
  const byTable = Object.fromEntries(doc.tables.map((t) => [t.table, t]));
  const bridgesByPair = {};
  const neighbors = {};
  for (const b of doc.bridges) {
    const [a, c] = b.tables;
    const k1 = `${a}|${c}`;
    const k2 = `${c}|${a}`;
    bridgesByPair[k1] = b;
    bridgesByPair[k2] = b;
    (neighbors[a] ??= []).push({ other: c, ...b });
    (neighbors[c] ??= []).push({ other: a, ...b });
  }
  _cache = { doc, byTable, bridgesByPair, neighbors };
  return _cache;
}

/** Strong identifier keys (vs dimensional ANO/PAIS/UF/...) */
export const STRONG_KEYS = new Set([
  "CPB", "CRT", "ROE", "SALIC", "CONTRATO", "PROCESSO",
  "REG_ANCINE", "CNPJ", "CPF", "GRUPO_ECON", "CNAE",
  "PRODUTORA", "DISTRIBUIDORA", "EXIBIDORA",
]);

export function getRegistry() {
  return load().doc;
}

export function getTableMeta(table) {
  return load().byTable[table] ?? null;
}

export function keysExposedBy(table) {
  const meta = getTableMeta(table);
  if (!meta) return {};
  const map = {};
  for (const e of meta.exposes ?? []) {
    (map[e.key] ??= []).push({ col: e.col, confidence: e.confidence, normalize: e.normalize ?? null });
  }
  return map;
}

export function findBridge(a, b) {
  return load().bridgesByPair[`${a}|${b}`] ?? null;
}

/**
 * Para uma tabela, lista vizinhos ordenados:
 *  - chaves fortes primeiro
 *  - dentro de cada chave, maior weight primeiro
 */
export function listJoinableWith(table) {
  const list = load().neighbors[table] ?? [];
  return [...list].sort((x, y) => {
    const sx = STRONG_KEYS.has(x.top_key) ? 1 : 0;
    const sy = STRONG_KEYS.has(y.top_key) ? 1 : 0;
    if (sx !== sy) return sy - sx;
    return (y.weight ?? 0) - (x.weight ?? 0);
  });
}

/**
 * Sugere um plano de join sequencial pra uma lista de tabelas.
 * Cada passo: { from, to, via_keys, top_key, confidence }
 * Comeca pela primeira tabela; para cada proxima, escolhe a melhor bridge
 * com qualquer tabela ja incluida no plano.
 *
 * Retorna { ok: bool, steps: [...], unreachable: [...] }
 */
export function planJoin(tables) {
  if (!tables || tables.length === 0) return { ok: true, steps: [], unreachable: [] };
  if (tables.length === 1) return { ok: true, steps: [], unreachable: [] };

  const { bridgesByPair } = load();
  const inPlan = new Set([tables[0]]);
  const steps = [];
  const queue = tables.slice(1);
  const unreachable = [];

  while (queue.length) {
    let bestIdx = -1;
    let bestBridge = null;
    for (let i = 0; i < queue.length; i++) {
      const t = queue[i];
      // pick the strongest available bridge to anything in plan
      for (const inT of inPlan) {
        const b = bridgesByPair[`${t}|${inT}`];
        if (!b) continue;
        if (!bestBridge || (b.weight ?? 0) > (bestBridge.weight ?? 0)) {
          bestBridge = { ...b, from: inT, to: t };
          bestIdx = i;
        }
      }
    }
    if (bestIdx < 0) {
      // remaining queue items are unreachable from current plan
      unreachable.push(...queue);
      break;
    }
    inPlan.add(queue[bestIdx]);
    steps.push({
      from: bestBridge.from,
      to: bestBridge.to,
      via_keys: bestBridge.via_keys,
      top_key: bestBridge.top_key,
      weight: bestBridge.weight,
    });
    queue.splice(bestIdx, 1);
  }

  return { ok: unreachable.length === 0, steps, unreachable };
}

/** Glossario de chaves carregado do YAML pra usar na UI */
export function keyGlossary() {
  return load().doc._meta?.key_glossary ?? {};
}
