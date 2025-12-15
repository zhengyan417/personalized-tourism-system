import api from './index'

// 辅助：规范错误对象结构，区分网络级错误 / 服务端错误 / 业务错误
function normalizeAxiosError(err) {
	if (!err) return { type: 'unknown', message: '未知错误' }
	if (err.response) {
		return {
			type: 'http',
			status: err.response.status,
			message: err.response.data?.message || err.message || `HTTP ${err.response.status}`
		}
	}
	if (err.request) {
		return { type: 'network', message: 'Network Error: 无响应 (可能后端未启动 / CORS / 端口错误)' }
	}
	return { type: 'config', message: err.message || '请求配置错误' }
}

// 旧版简单规划（保留占位，可按需求删除或改造）
export async function planSimple(from, to) {
	if (!from || !to) return null
	const params = {
		from_lat: from.latitude,
		from_lon: from.longitude,
		to_lat: to.latitude,
		to_lon: to.longitude
	}
	const { data } = await api.get('/api/route/plan', { params })
	if (data?.status === 'success') return data
	return null
}

// 新增：最短路径（基于后端 Dijkstra）
// startId / endId: 景点主键；maxDistanceKm: 构边阈值（可选）
export async function fetchShortestRoute(startId, endId, maxDistanceKm = 50) {
	if (!startId || !endId) {
		return { error: 'startId 与 endId 必填' }
	}
	try {
		const params = { start_id: startId, end_id: endId, max_distance_km: maxDistanceKm }
		const { data } = await api.get('/api/routes/shortest', { params })
		return data
	} catch (err) {
		return { error: err.message || '请求失败' }
	}
}

// 组合：批量尝试多目标（示例扩展，可用于后续多段规划）
export async function batchShortest(fromId, toIds = [], maxDistanceKm = 50) {
	const out = []
	for (const tid of toIds) {
		const r = await fetchShortestRoute(fromId, tid, maxDistanceKm)
		out.push({ target: tid, result: r })
	}
	return out
}

// 新增：道路真实导航（使用后端 /api/routes/navigate，后端调用 OSRM）
export async function fetchRoadRoute(startLat, startLon, endLat, endLon, opts = {}) {
	if ([startLat,startLon,endLat,endLon].some(v => typeof v !== 'number')) {
		return { error: '起终点坐标缺失或格式错误' }
	}
	const params = {
		start_lat: startLat,
		start_lon: startLon,
		end_lat: endLat,
		end_lon: endLon,
		profile: opts.profile || 'driving'
	}
	if (Array.isArray(opts.waypoints) && opts.waypoints.length) {
		// waypoints: [[lat,lon],...] -> 用分号拼接
		params.waypoints = opts.waypoints.map(p => p.join(',')).join(';')
	}
	if (opts.provider) params.provider = opts.provider
	try {
		const { data } = await api.get('/api/routes/navigate', { params })
		return data
	} catch (e) {
		const info = normalizeAxiosError(e)
		return { error: info.message, _error: info }
	}
}

// 新增：多点优化顺序（固定起点 + 任意访问点顺序）
// startId: 起点景点ID
// pointIds: 其余待访问景点ID数组（可包含终点）
export async function fetchOptimizedSequence(startId, pointIds = []) {
	if (!startId) return { error: 'startId 必填' }
	const clean = (Array.isArray(pointIds) ? pointIds : []).filter(pid => pid && pid !== startId)
	const params = {
		start_id: startId,
		point_ids: clean.join(',')
	}
	try {
		const { data } = await api.get('/api/routes/optimize', { params })
		return data
	} catch (e) {
		const info = normalizeAxiosError(e)
		return { error: info.message, _error: info }
	}
}


