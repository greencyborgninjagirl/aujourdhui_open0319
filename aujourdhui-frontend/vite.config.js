import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

// 保证开发/构建时入口为 main.js，避免请求被回退成 index 导致 MIME 错误
export default defineConfig({
  plugins: [uni()],
  root: process.cwd(),
  server: {
    port: 8080,
    strictPort: false,
    host: true, // 内测时允许局域网访问（手机同 WiFi 可访问）
  },
  build: {
    rollupOptions: {
      input: 'index.html',
      output: {
        entryFileNames: 'js/[name].js',
        chunkFileNames: 'js/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]',
      },
    },
  },
})
