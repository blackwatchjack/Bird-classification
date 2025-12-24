import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // 允许局域网访问
    port: 5173,      // 前端开发端口
    proxy: {
      // 匹配所有以 /api 开头的请求
      '/api': {
        target: 'http://127.0.0.1:8000', // 你的 FastAPI 后端地址
        changeOrigin: true,               // 允许跨域
        // 如果后端接口没有 /api 前缀，可以进行路径重写
        // rewrite: (path) => path.replace(/^\/api/, '') 
      }
    }
  }
})