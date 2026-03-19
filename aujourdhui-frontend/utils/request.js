import { BASE_URL } from '../config.js'

export function request(options) {
  const { url, method = 'GET', data = {} } = options
  const fullUrl = url.startsWith('http') ? url : `${BASE_URL}${url}`
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
        const msg = (err && (err.errMsg || err.message)) && /fail|refused|timeout|error/i.test(String(err.errMsg || err.message))
          ? '抽牌失败，请确认后端已启动（127.0.0.1:8000）'
          : (err && (err.message || err.errMsg)) || '请求失败'
        reject(new Error(typeof msg === 'string' ? msg : '请求失败'))
      },
    })
  })
}
