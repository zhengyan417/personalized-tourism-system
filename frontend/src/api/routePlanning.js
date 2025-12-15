import api from './index'

// 调用后端路径规划接口 POST /api/route/plan
// payload: { start_id, end_id, waypoint_ids: [] }
export async function planRoute(payload) {
  const { data } = await api.post('/api/route/plan', payload)
  if (data?.success) return data.data
  throw new Error(data?.message || '路径规划失败')
}
