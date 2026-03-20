// API 地址：
// - 开发：默认 http://127.0.0.1:8000
// - 与前端同域（Vercel 同时托管静态页 + /api）：生产构建且未设置 VITE_API_BASE 时用空字符串，请求走相对路径 /api/draw
// - 局域网/ngrok：设置 VITE_API_BASE=https://...
const env = typeof import.meta !== 'undefined' && import.meta.env ? import.meta.env : {}
const raw = env.VITE_API_BASE
const isProd = !!env.PROD
export const BASE_URL =
  raw !== undefined && raw !== null && String(raw).length > 0
    ? String(raw).replace(/\/$/, '')
    : isProd
      ? ''
      : 'http://127.0.0.1:8000'
