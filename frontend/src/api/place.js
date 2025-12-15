import api from './index'

// 邻近查询
export async function fetchNearbyPlaces({ lat, lon, radius = 5, category, limit = 200 }) {
	const params = { lat, lon, radius }
	if (category) params.category = category
	const { data } = await api.get('/api/places/nearby', { params })
	if (data?.status === 'success' && Array.isArray(data.data)) return data.data.slice(0, limit)
	return []
}

// 全量景点（用于地图渲染）
export async function fetchAllPlaces({ category, keyword } = {}) {
	const params = {}
	if (category) params.category = category
	if (keyword) params.keyword = keyword
	try {
		const { data } = await api.get('/api/places/', { params })
		if (data?.status === 'success' && Array.isArray(data.data)) return data.data
	} catch (e) {
		console.warn('[fetchAllPlaces] error', e.message)
	}
	return []
}

export async function fetchCategories() {
	try {
		const { data } = await api.get('/api/places/categories')
		return data?.data || []
	} catch {
		return ['景点', '美食', '自然', '历史']
	}
}

