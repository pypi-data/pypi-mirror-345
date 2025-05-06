import { defineUserConfig } from "vuepress";
import { hopeTheme } from "vuepress-theme-hope";
import sidebar from "./sidebar.js";

import { viteBundler } from '@vuepress/bundler-vite'

export default defineUserConfig({
  lang: "en-US",
  title: "PSQLPy",
  description: "PSQLPy Documentation",

  bundler: viteBundler(),

  theme: hopeTheme({
    repo: "psqlpy-python/psqlpy",

    repoLabel: "GitHub",

    repoDisplay: true,

    sidebar,

    hostname: "https://psqlpy-python.github.io/",

    plugins: {
      readingTime: false,

      copyCode: {
        showInMobile: true,
      },

      searchPro: {
        indexContent: true,
        autoSuggestions: false,
      },

      mdEnhance: {
        tabs: true,
        mermaid: true,
        chart: true,
      },

      sitemap: {
        changefreq: "daily",
        sitemapFilename: "sitemap.xml",
      },

    },
  }),
});
