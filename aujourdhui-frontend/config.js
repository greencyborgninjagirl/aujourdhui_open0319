// API 地址：
// - 开发（vite dev）：默认 http://127.0.0.1:8000
// - 生产构建：未设置 VITE_API_BASE 时用空字符串；request.js 会用 window.location.origin 拼 /api/draw（uni-app 里 PROD 有时不可靠，改用 DEV）
// - 外置后端：设置 VITE_API_BASE=https://...
const env = typeof import.meta !== 'undefined' && import.meta.env ? import.meta.env : {}
const raw = env.VITE_API_BASE
const isDev = !!env.DEV
export const BASE_URL =
  raw !== undefined && raw !== null && String(raw).length > 0
    ? String(raw).replace(/\/$/, '')
    : isDev
      ? 'http://127.0.0.1:8000'
      : ''
