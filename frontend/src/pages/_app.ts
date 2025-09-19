import { createApp } from 'vue';
import { createPinia } from 'pinia';
import type { App } from 'vue';

export default function (App: any) {
  const app = createApp(App);
  const pinia = createPinia();
  
  app.use(pinia);
  
  return app;
}
