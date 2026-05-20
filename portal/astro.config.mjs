import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://riabr-dados.github.io",
  base: "/riab/",
  output: "static",
  build: {
    assets: "_assets",
  },
});
