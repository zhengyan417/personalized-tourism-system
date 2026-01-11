import axios from 'axios'

// 前端测试开关与后端地址选择
// 优先级（高 -> 低）：URL 参数 frontendTest -> localStorage.FRONTEND_TEST -> VUE_APP_FRONTEND_TEST
// baseURL 选择：
//  - TEST:  VUE_APP_API_BASE_URL_TEST || window.location.origin（用于走 devServer Mock 或测试后端）
//  - PROD:  VUE_APP_API_BASE_URL_PROD || VUE_APP_API_BASE_URL || 'http://localhost:5000'

function readBool(val) {
  if (val == null) return undefined
  const s = String(val).toLowerCase().trim()
  if (['1','true','yes','on'].includes(s)) return true
  if (['0','false','no','off'].includes(s)) return false
  return undefined
}

function getRuntimeFrontendTestFlag() {
  try {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search)
      const qp = readBool(params.get('frontendTest'))
      if (qp !== undefined) return qp
      const ls = readBool(window.localStorage.getItem('FRONTEND_TEST'))
      if (ls !== undefined) return ls
    }
  } catch {}
  const env = readBool(process.env.VUE_APP_FRONTEND_TEST)
  return env === undefined ? false : env
}

const FRONTEND_TEST = getRuntimeFrontendTestFlag()

const testBase =
  process.env.VUE_APP_API_BASE_URL_TEST ||
  (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8080')

// 智能后端地址选择：
// 1. 如果设置了环境变量，使用环境变量
// 2. 如果从网络IP访问（非localhost），将后端地址中的localhost替换为当前主机名
// 3. 否则使用默认的localhost:5000
function getSmartProdBase() {
  const envBase = process.env.VUE_APP_API_BASE_URL_PROD || process.env.VUE_APP_API_BASE_URL
  
  if (envBase) {
    // 如果当前页面不是通过localhost访问的，替换后端地址中的localhost
    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname
      if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
        return envBase.replace('localhost', hostname).replace('127.0.0.1', hostname)
      }
    }
    return envBase
  }
  
  // 默认地址
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname
    const port = '5000'
    const protocol = window.location.protocol
    return `${protocol}//${hostname}:${port}`
  }
  
  return 'http://localhost:5000'
}

const prodBase = getSmartProdBase()

const baseURL = FRONTEND_TEST ? testBase : prodBase

// 调试日志：显示实际使用的API地址
console.log('[API Config] FRONTEND_TEST:', FRONTEND_TEST)
console.log('[API Config] Base URL:', baseURL)
if (typeof window !== 'undefined') {
  console.log('[API Config] Current Location:', window.location.href)
  console.log('[API Config] Hostname:', window.location.hostname)
}

const api = axios.create({
  baseURL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true // 携带 Cookie 以保持登录会话
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    // 静默处理401（未登录）和常见的用户错误
    const status = err?.response?.status
    if (status === 401) {
      // 401 未授权是正常的业务场景，不打印错误
      return Promise.reject(err)
    }
    // 其他错误才打印到控制台
    console.error('[API Error]', status, err?.message)
    return Promise.reject(err)
  }
)

export default api