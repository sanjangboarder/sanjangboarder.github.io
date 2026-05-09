import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://your-username.github.io', // 나중에 실제 주소로 변경 필요
  base: '/github_blog', // 저장소 이름에 맞춰 변경 가능
  integrations: [sitemap()],
});
