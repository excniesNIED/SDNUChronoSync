import { defineConfig } from 'astro/config';
import vue from '@astrojs/vue';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
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
  build: {
    assets: 'assets'
  }
});
