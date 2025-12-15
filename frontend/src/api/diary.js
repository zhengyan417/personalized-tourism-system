import api from './index'

function normalizeListResponse(data) {
  if (data?.success && Array.isArray(data.data)) return data.data
  if (Array.isArray(data?.data?.items)) return data.data.items
  if (Array.isArray(data?.diaries)) return data.diaries
  return []
}

function normalizeItemResponse(data) {
  if (data?.success) return data.data
  if (data?.status === 'success') return data.data
  return null
}

export async function fetchDiaries(params = {}) {
  const { data } = await api.get('/api/diaries', { params })
  return normalizeListResponse(data)
}

export async function fetchDiaryDetail(id) {
  const { data } = await api.get(`/api/diaries/${id}`)
  return normalizeItemResponse(data)
}

export async function createDiary(payload) {
  const body = {
    user_id: payload.user_id ?? 1,
    attraction_id: payload.attraction_id ?? null,
    title: payload.title,
    content: payload.content,
    latitude: payload.latitude,
    longitude: payload.longitude
  }
  const { data } = await api.post('/api/diaries', body)
  return normalizeItemResponse(data)
}

export async function updateDiary(id, payload) {
  const sanitized = { ...payload }
  if ('user_id' in sanitized) delete sanitized.user_id
  const { data } = await api.put(`/api/diaries/${id}`, sanitized)
  return normalizeItemResponse(data)
}

export async function deleteDiary(id) {
  const { data } = await api.delete(`/api/diaries/${id}`)
  if (data?.success) return true
  if (data?.status === 'success') return true
  return false
}
