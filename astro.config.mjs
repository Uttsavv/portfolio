import { defineConfig } from 'astro/config';

// GitHub Pages on the custom domain https://heyutsav.com (served from the root).
// To serve from https://uttsavv.github.io/portfolio/ instead, set SITE_URL=https://uttsavv.github.io and BASE_PATH=/portfolio.
export default defineConfig({
  site: process.env.SITE_URL || 'https://heyutsav.com',
  base: process.env.BASE_PATH || '/',
  trailingSlash: 'ignore',
  build: { inlineStylesheets: 'always' },
  vite: { build: { assetsInlineLimit: 0, chunkSizeWarningLimit: 700 } },
});
