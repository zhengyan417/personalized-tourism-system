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
// 改为传递景点名称而非坐标，或直接调用导航服务
export async function planSimple(from, to, waypoints = []) {
	if (!from || !to) return null
	// 如果传入的是坐标对象，使用道路导航
	if (from.latitude !== undefined && to.latitude !== undefined) {
		// 内联调用导航API
		const params = {
			start_lat: from.latitude,
			start_lon: from.longitude,
			end_lat: to.latitude,
			end_lon: to.longitude,
			profile: 'driving'
		}
		
		// 添加waypoints参数
		if (waypoints && waypoints.length > 0) {
			// 将waypoints格式化为 "lat,lon;lat,lon" 格式
			const waypointsStr = waypoints
				.filter(wp => wp.latitude !== undefined && wp.longitude !== undefined)
				.map(wp => `${wp.latitude},${wp.longitude}`)
				.join(';')
			if (waypointsStr) {
				params.waypoints = waypointsStr
			}
		}
		
		try {
			const { data } = await api.get('/api/routes/navigate', { params })
			if (data && !data.error) {
				return {
					status: 'success',
					route: [from.name || from.label || '起点', to.name || to.label || '终点'],
					distance_km: data.data?.distance_km || data.summary?.distance_km || 0,
					provider: data.data?.provider || data.provider,
					...data
				}
			}
		} catch (err) {
			console.error('导航失败:', err)
		}
		return null
	}
	// 否则按景点名称调用原API
	const params = {
		start: from.name || from,
		end: to.name || to
	}
	try {
		const { data } = await api.get('/api/routes/plan', { params })
		if (data?.status === 'success') return data
	} catch (err) {
		console.error('路径规划失败:', err)
	}
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


