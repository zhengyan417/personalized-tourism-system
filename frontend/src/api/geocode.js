import axios from 'axios'

const geocodeClient = axios.create({
	baseURL: 'https://nominatim.openstreetmap.org',
	timeout: 15000,
	headers: {
		'Accept': 'application/json',
		'Accept-Language': 'zh-CN'
	}
})

function transformPlace(raw) {
	if (!raw) return null
	const lat = parseFloat(raw.lat)
	const lon = parseFloat(raw.lon)
	if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null
	return {
		id: raw.place_id || raw.osm_id || `${lat},${lon}`,
		title: raw.display_name?.split(',')[0]?.trim() || raw.display_name || raw.name || '未命名地点',
		subtitle: raw.display_name || '',
		type: raw.type || raw.category,
		latitude: lat,
		longitude: lon,
		boundingBox: raw.boundingbox || null
	}
}

export async function searchPlaces(query, options = {}) {
	const text = (query || '').trim()
	if (!text) return []
	const params = {
		q: text,
		format: 'json',
		addressdetails: 1,
		limit: options.limit || 6,
		polygon_geojson: 0
	}
	try {
		const { data } = await geocodeClient.get('/search', { params })
		if (!Array.isArray(data)) return []
		return data.map(transformPlace).filter(Boolean)
	} catch (err) {
		console.warn('[geocode] search failed', err)
		throw err
	}
}
