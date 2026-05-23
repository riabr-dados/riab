import { defineConfig } from "astro/config";

const isDev = process.env.NODE_ENV === "development";

export default defineConfig({
  site: "https://riabr-dados.github.io",
  base: isDev ? "/" : "/riab/",
  output: "static",
  build: {
    assets: "_assets",
  },
});
