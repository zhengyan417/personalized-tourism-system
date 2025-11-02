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

const prodBase =
  process.env.VUE_APP_API_BASE_URL_PROD ||
  process.env.VUE_APP_API_BASE_URL ||
  'http://localhost:5000'

const baseURL = FRONTEND_TEST ? testBase : prodBase

const api = axios.create({
  baseURL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    // 统一错误打印，页面可根据需要再处理
    console.error('[API Error]', err?.response?.status, err?.message)
    return Promise.reject(err)
  }
)

export default api