import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // No rewrite: backend already serves /api/*
      },
    },
  },
  preview: {
    port: 5173,
    host: true,
  }
})
