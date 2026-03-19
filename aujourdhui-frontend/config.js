// API 地址：开发用 127.0.0.1，内测/上线改为局域网 IP 或域名
// 内测：创建 .env.test 并设置 VITE_API_BASE=http://你的电脑局域网IP:8000，然后 npm run build:h5 -- --mode test
const envBase = typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE
export const BASE_URL = envBase || 'http://127.0.0.1:8000'
