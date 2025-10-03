import { defineConfig } from 'astro/config';
import vue from '@astrojs/vue';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
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
