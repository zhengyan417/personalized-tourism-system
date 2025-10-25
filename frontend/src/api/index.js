import axios from 'axios'

// 同源优先（便于使用 devServer 的内置 Mock），可通过环境变量覆盖
const baseURL =
  process.env.VUE_APP_API_BASE_URL ||
  (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:5000')

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