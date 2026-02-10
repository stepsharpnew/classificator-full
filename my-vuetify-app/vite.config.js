import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vite';

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
//  base: './',
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': {
       target: 'http://192.168.1.60:8080',
       changeOrigin: true,
       rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
