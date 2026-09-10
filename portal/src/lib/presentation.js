import { readFileSync } from "fs";
import { resolve } from "path";
import yaml from "js-yaml";

const PRESENTATION_PATH = resolve("../catalog/portal-presentation.yaml");
const PREVIEWS_PATH = resolve("public/previews");

let cache = null;

function load() {
  if (!cache) cache = yaml.load(readFileSync(PRESENTATION_PATH, "utf-8"));
  return cache;
}

export function getTablePresentation(table) {
  return load()?.tables?.[table] ?? null;
}

export function getPreview(table) {
  const presentation = getTablePresentation(table);
  const id = presentation?.preview?.id;
  if (!id) return null;
  try {
    return JSON.parse(readFileSync(resolve(PREVIEWS_PATH, `${id}.json`), "utf-8"));
  } catch (error) {
    if (error.code === "ENOENT") return null;
    throw error;
  }
}

export function getBrasilStories() {
  try {
    return JSON.parse(
      readFileSync(resolve(PREVIEWS_PATH, "brasil-no-mundo.json"), "utf-8"),
    ).stories ?? [];
  } catch (error) {
    if (error.code === "ENOENT") return [];
    throw error;
  }
}
