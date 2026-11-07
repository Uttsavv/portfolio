import { defineConfig } from 'astro/config';

// GitHub Pages: https://uttsavv.github.io/portfolio/
// With a custom domain, set SITE_URL=https://your.domain and BASE_PATH=/ in the workflow.
export default defineConfig({
  site: process.env.SITE_URL || 'https://uttsavv.github.io',
  base: process.env.BASE_PATH || '/portfolio',
  trailingSlash: 'ignore',
  build: { inlineStylesheets: 'always' },
  vite: { build: { assetsInlineLimit: 0, chunkSizeWarningLimit: 700 } },
});
