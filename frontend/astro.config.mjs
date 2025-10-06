import { defineConfig } from 'astro/config';
import vue from '@astrojs/vue';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  // 网站URL，用于生成canonical链接和sitemap
  // 部署时请更新为实际域名
  site: process.env.SITE_URL || 'https://sxty.hxcn.space',
  output: 'static',
  integrations: [
    vue({
      appEntrypoint: '/src/pages/_app'
    }),
    tailwind()
  ],
  server: {
    port: 4321,
    host: true
  },
  vite: {
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false
        }
      }
    }
  },
  build: {
    assets: 'assets'
  }
});
