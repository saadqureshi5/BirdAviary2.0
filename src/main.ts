import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/main.css'

import { initDb } from './services/sqliteService'

// Initialize mobile database if running in Capacitor
initDb().catch(console.error).then(() => {
  const app = createApp(App)

  app.use(createPinia())
  app.use(router)

  app.mount('#app')
})
