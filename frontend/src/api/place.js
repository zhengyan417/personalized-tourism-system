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

// 根据名称搜索景点
export async function searchAttractionByName(name) {
	try {
		const { data } = await api.get('/api/attractions/search', {
			params: { name: name }
		})
		if (data?.status === 'success' && Array.isArray(data.data) && data.data.length > 0) {
			return data.data[0] // 返回第一个匹配结果
		}
	} catch (e) {
		console.warn('[searchAttractionByName] error', name, e.message)
	}
	return null
}

// 批量搜索景点
export async function searchAttractions(names) {
	const results = []
	for (const name of names) {
		const attraction = await searchAttractionByName(name)
		if (attraction) {
			results.push({
				name: attraction.name,
				latitude: attraction.latitude,
				longitude: attraction.longitude,
				category: attraction.type || attraction.category,
				description: attraction.description || attraction.facilities || '',
				source: 'ai'
			})
		}
	}
	return results
}
