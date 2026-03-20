import { BASE_URL } from '../config.js'

function resolveApiUrl(path) {
  if (path.startsWith('http')) return path
  // 生产构建 BASE_URL 为空时，用当前页面 origin，避免相对路径在部分 H5 环境下异常
  const base =
    BASE_URL ||
    (typeof window !== 'undefined' && window.location && window.location.origin
      ? window.location.origin
      : '')
  return `${base}${path.startsWith('/') ? path : `/${path}`}`
}

export function request(options) {
  const { url, method = 'GET', data = {} } = options
  const fullUrl = resolveApiUrl(url)
  const header = {}
  if (method.toUpperCase() === 'POST') {
    header['content-type'] = 'application/json'
  }
  return new Promise((resolve, reject) => {
    uni.request({
      url: fullUrl,
      method,
      data,
      header,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          const msg = (res.data && (res.data.detail || res.data.message)) || `请求失败 ${res.statusCode}`
          reject(new Error(typeof msg === 'string' ? msg : JSON.stringify(msg)))
        }
      },
      fail: (err) => {
        const hint =
          typeof window !== 'undefined' && window.location && /127\.0\.0\.1|localhost/.test(String(window.location.hostname || ''))
            ? '抽牌失败，请确认本机已运行 uvicorn（127.0.0.1:8000）'
            : '抽牌失败，请稍后重试或检查网络（Vercel 需能访问 /api/draw）'
        const msg = (err && (err.errMsg || err.message)) && /fail|refused|timeout|error/i.test(String(err.errMsg || err.message))
          ? hint
          : (err && (err.message || err.errMsg)) || '请求失败'
        reject(new Error(typeof msg === 'string' ? msg : '请求失败'))
      },
    })
  })
}
