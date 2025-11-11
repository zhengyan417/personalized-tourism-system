import api from './index'

export async function fetchDiaries(params = {}) {
  // 支持 user_id 传参；mock 会忽略
  const { data } = await api.get('/api/diaries', { params })
  // 兼容不同返回结构
  if (data?.success && Array.isArray(data.data)) return data.data
  if (data?.status === 'success' && Array.isArray(data.data)) return data.data
  return []
}

export async function fetchDiaryDetail(id) {
  const { data } = await api.get(`/api/diaries/${id}`)
  if (data?.success) return data.data
  if (data?.status === 'success') return data.data
  return null
}

export async function createDiary(payload) {
  // 兼容后端字段（content）与 mock 字段（snippet、latitude、longitude）
  const body = {
    user_id: payload.user_id ?? 1,
    attraction_id: payload.attraction_id ?? null,
    title: payload.title,
    // 尽量同时发送 content 与 snippet，以适配不同后端/Mock
    content: payload.content,
    snippet: payload.content,
    date: payload.date, // 可选
    latitude: payload.latitude,
    longitude: payload.longitude
  }
  const { data } = await api.post('/api/diaries', body)
  if (data?.success) return data.data
  if (data?.status === 'success') return data.data
  return null
}
