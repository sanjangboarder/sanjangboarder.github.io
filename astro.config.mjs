import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://sanjangboarder.github.io',
  trailingSlash: 'always',
  integrations: [
    sitemap()
  ],
});
