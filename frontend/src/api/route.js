import api from './index'

// 简单双点路线规划（使用 mock 或后端的 /api/route/plan）
// from/to: { latitude, longitude }
export async function planSimple(from, to) {
	if (!from || !to) return null
	const params = {
		from_lat: from.latitude,
		from_lon: from.longitude,
		to_lat: to.latitude,
		to_lon: to.longitude
	}
	const { data } = await api.get('/api/route/plan', { params })
	if (data?.success && data?.data) return data.data
	return null
}

