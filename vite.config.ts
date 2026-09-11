import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'
import { readFileSync } from 'fs'

const host = process.env.TAURI_DEV_HOST
const isProduction = process.env.NODE_ENV === 'production'
const pkg = JSON.parse(readFileSync(resolve(__dirname, 'package.json'), 'utf-8'))

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],

  define: {
    // Inject app version from package.json for the update checker
    __APP_VERSION__: JSON.stringify(pkg.version),
  },

  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },

  clearScreen: false,

  esbuild: {
    target: 'es2022',
  },

  server: {
    port: 1420,
    strictPort: true,
    host: host || false,
    hmr: host
      ? { protocol: 'ws', host, port: 1430 }
      : undefined,
    watch: {
      ignored: ['**/src-tauri/**', '**/backend/**'],
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8008',
        changeOrigin: true,
      },
      '/uploads': {
        target: 'http://127.0.0.1:8008',
        changeOrigin: true,
      },
    },
  },

  envPrefix: ['VITE_', 'TAURI_ENV_*'],

  build: {
    target: 'es2022',
    minify: !process.env.TAURI_ENV_DEBUG ? 'esbuild' : false,
    sourcemap: !!process.env.TAURI_ENV_DEBUG,
  },
})