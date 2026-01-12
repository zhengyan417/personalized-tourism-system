/*
 * 开发环境内置 Mock：后端未就绪时，前端可直接使用 npm run serve 进行联调
 * 提供的端点：
 *  - GET /api/places/nearby
 *  - GET /api/places/categories
 *  - GET /api/places/:id
 *  - GET /api/recommendations
 *  - GET /api/recommendations/hot
 *  - GET /api/recommendations/search
 *  - GET /api/diaries
 *  - POST /api/diaries
 *  - GET /api/diaries/:id
 *  - GET /api/route/plan
 */

// ---- 种子数据与工具 ----
let SEED = 20251102
function sRand() { SEED = (SEED * 9301 + 49297) % 233280; return SEED / 233280 }
function pick(arr) { return arr[Math.floor(sRand() * arr.length)] }

function genAttractions(centerLat, centerLon, count = 220) {
	const cats = ['景点', '美食', '自然', '历史']
	const res = []
	for (let i = 0; i < count; i++) {
		const latOff = (sRand() - 0.5) * 0.5
		const lonOff = (sRand() - 0.5) * 0.5
		const lat = parseFloat((centerLat + latOff).toFixed(6))
		const lon = parseFloat((centerLon + lonOff).toFixed(6))
		res.push({
			id: i + 1,
			name: `景点-${i + 1}`,
			category: cats[i % cats.length],
			latitude: lat,
			longitude: lon,
			rating: parseFloat((4 + sRand()).toFixed(1)),
			popularity: parseFloat((0.5 + sRand() * 0.5).toFixed(2)),
			distance_km: parseFloat((sRand() * 10).toFixed(2))
		})
	}
	return res
}

function genDiaries(attractions, count = 18) {
	const res = []
	for (let i = 0; i < count; i++) {
		const a = pick(attractions)
		res.push({
			id: i + 1,
			title: `旅行日记-${i + 1}`,
			snippet: `在 ${a.name} 的美好回忆……`,
			date: new Date(2025, 9, 1 + i).toISOString().slice(0,10),
			latitude: a.latitude,
			longitude: a.longitude
		})
	}
	return res
}

const mockDB = {
	center: { lat: 39.9042, lon: 116.4074 },
	attractions: [],
	diaries: []
}

/** @type {import('@vue/cli-service').ProjectOptions} */
module.exports = {
	devServer: {
		host: '0.0.0.0',  // 允许从网络IP访问
		port: 8080,
		setupMiddlewares(middlewares, devServer) {
			const useMock = process.env.VUE_APP_USE_MOCK === 'true'
			if (!useMock) {
				console.log('[devServer] API mock disabled. Forward requests to real backend.')
				return middlewares
			}

			const app = devServer.app

			// 一次性初始化数据
			if (!mockDB.attractions.length) mockDB.attractions = genAttractions(mockDB.center.lat, mockDB.center.lon, 220)
			if (!mockDB.diaries.length) mockDB.diaries = genDiaries(mockDB.attractions, 18)

			// 类别列表
			app.get('/api/places/categories', (req, res) => {
				res.json({ status: 'success', data: ['景点', '美食', '自然', '历史'] })
			})

			// 邻近景点
			app.get('/api/places/nearby', (req, res) => {
				const lat = parseFloat(req.query.lat) || mockDB.center.lat
				const lon = parseFloat(req.query.lon) || mockDB.center.lon
				const radius = parseFloat(req.query.radius) || 5
				const category = req.query.category

				const data = mockDB.attractions
					.filter(item => !category || item.category === category)
					.filter(item => Math.abs(item.latitude - lat) * 111 <= radius + 2 && Math.abs(item.longitude - lon) * 85 <= radius + 2)

				res.json({ status: 'success', count: data.length, data })
			})

			// 地点详情
			app.get('/api/places/:id', (req, res) => {
				const id = parseInt(req.params.id, 10)
				const found = mockDB.attractions.find(a => a.id === id)
				if (!found) return res.status(404).json({ success: false, message: 'Not Found' })
				res.json({ success: true, data: found })
			})

			// 推荐 - 个性化
			app.get('/api/recommendations', (req, res) => {
				const top_n = parseInt(req.query.top_n || '10', 10)
				const list = mockDB.attractions.slice(0, Math.max(1, top_n)).map((a, i) => ({
					attraction_id: a.id,
					name: a.name,
					type: ['历史景点', '自然风光'][i % 2],
					score: parseFloat((0.6 + sRand() * 0.4).toFixed(2)),
					rating: a.rating,
					latitude: a.latitude,
					longitude: a.longitude
				}))
				res.json({ success: true, data: { recommendations: list, algorithm_used: 'mock' } })
			})

			// 推荐 - 热门
			app.get('/api/recommendations/hot', (req, res) => {
				const top_n = parseInt(req.query.top_n || '10', 10)
				const list = mockDB.attractions.slice(0, Math.max(1, top_n)).map((a, i) => ({
					attraction_id: a.id,
					name: `热门-${a.name}`,
					type: ['历史景点', '自然风光'][i % 2],
					popularity: parseFloat((0.7 + sRand() * 0.3).toFixed(2)),
					rating: a.rating,
					latitude: a.latitude,
					longitude: a.longitude
				}))
				res.json({ success: true, data: { recommendations: list, sort_method: 'rating' } })
			})

			// 推荐 - 搜索
			app.get('/api/recommendations/search', (req, res) => {
				const q = (req.query.query || '').toString().trim()
				const filtered = mockDB.attractions.filter(a => !q || a.name.includes(q))
				const list = filtered.slice(0, 20).map((a, i) => ({
					attraction_id: a.id,
					name: `${q ? q + '-' : ''}${a.name}`,
					type: '自然风光',
					relevance_score: parseFloat((0.5 + sRand() * 0.5).toFixed(2)),
					match_field: 'name',
					latitude: a.latitude,
					longitude: a.longitude
				}))
				res.json({ success: true, data: { query: q, results: list, total_count: list.length } })
			})

			// 日记列表
			app.get('/api/diaries', (req, res) => {
				res.json({ success: true, data: mockDB.diaries })
			})

			// 创建日记
			app.post('/api/diaries', (req, res) => {
				const body = req.body || {}
				const id = mockDB.diaries.length ? mockDB.diaries[mockDB.diaries.length - 1].id + 1 : 1
				const item = {
					id,
					title: body.title || `旅行日记-${id}`,
					snippet: body.snippet || '这是一段测试内容…',
					date: body.date || new Date().toISOString().slice(0,10),
					latitude: body.latitude ?? mockDB.center.lat,
					longitude: body.longitude ?? mockDB.center.lon
				}
				mockDB.diaries.push(item)
				res.status(201).json({ success: true, data: item })
			})

			// 日记详情
			app.get('/api/diaries/:id', (req, res) => {
				const id = parseInt(req.params.id, 10)
				const found = mockDB.diaries.find(d => d.id === id)
				if (!found) return res.status(404).json({ success: false, message: 'Not Found' })
				res.json({ success: true, data: found })
			})

			// 简单路线规划
			app.get('/api/route/plan', (req, res) => {
				const fromLat = parseFloat(req.query.from_lat)
				const fromLon = parseFloat(req.query.from_lon)
				const toLat = parseFloat(req.query.to_lat)
				const toLon = parseFloat(req.query.to_lon)
				if ([fromLat, fromLon, toLat, toLon].some(v => Number.isNaN(v))) {
					return res.status(400).json({ success: false, message: '参数缺失或不合法' })
				}
				const dLat = (toLat - fromLat) * 111
				const dLon = (toLon - fromLon) * 85
				const distance_km = parseFloat(Math.hypot(dLat, dLon).toFixed(2))
				const mid = [
					parseFloat(((fromLat + toLat) / 2 + (sRand() - 0.5) * 0.05).toFixed(6)),
					parseFloat(((fromLon + toLon) / 2 + (sRand() - 0.5) * 0.05).toFixed(6))
				]
				const path = [ [fromLat, fromLon], mid, [toLat, toLon] ]
				res.json({ success: true, data: { distance_km, path } })
			})

			return middlewares
		}
	}
}
