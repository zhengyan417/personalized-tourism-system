import api from './index'

export async function fetchRecommendations(params = {}) {
	const { data } = await api.get('/api/recommendations', { params })
	return data?.data?.recommendations || []
}

export async function fetchHotRecommendations(params = {}) {
	const { data } = await api.get('/api/recommendations/hot', { params })
	return data?.data?.recommendations || []
}

export async function searchRecommendations(params = {}) {
	const { data } = await api.get('/api/recommendations/search', { params })
	return data?.data?.results || []
}
