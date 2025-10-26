import api from './index'

export async function fetchNearbyPlaces({ lat, lon, radius = 5, category, limit = 200 }) {
	const params = { lat, lon, radius, limit }
	if (category) params.category = category
	const { data } = await api.get('/api/places/nearby', { params })
	// 预期 data: { status: 'success', count, data: [ ... ] }
	if (data?.status === 'success' && Array.isArray(data.data)) return data.data
	return []
}

export async function fetchCategories() {
	// 若后端暂未实现类别接口，可返回静态占位
	try {
		const { data } = await api.get('/api/places/categories')
		return data?.data || []
	} catch {
		return ['景点', '美食', '自然', '历史']
	}
}
