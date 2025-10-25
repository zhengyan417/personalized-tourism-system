/*
 * 开发环境内置 Mock：后端未就绪时，前端可直接使用 npm run serve 进行联调
 * 提供的端点：
 *  - GET /api/places/nearby
 *  - GET /api/places/categories
 *  - GET /api/recommendations
 *  - GET /api/recommendations/hot
 *  - GET /api/recommendations/search
 */

function genAttractions(centerLat, centerLon, count = 200) {
	const res = []
	for (let i = 0; i < count; i++) {
		const latOff = (Math.random() - 0.5) * 0.5 // ~±0.25°
		const lonOff = (Math.random() - 0.5) * 0.5
		const lat = parseFloat((centerLat + latOff).toFixed(6))
		const lon = parseFloat((centerLon + lonOff).toFixed(6))
		res.push({
			id: i + 1,
			name: `景点-${i + 1}`,
			category: ['景点', '美食', '自然', '历史'][i % 4],
			latitude: lat,
			longitude: lon,
			distance_km: parseFloat((Math.random() * 10).toFixed(2))
		})
	}
	return res
}

/** @type {import('@vue/cli-service').ProjectOptions} */
module.exports = {
	devServer: {
		setupMiddlewares(middlewares, devServer) {
			const app = devServer.app

			// 类别列表
			app.get('/api/places/categories', (req, res) => {
				res.json({ status: 'success', data: ['景点', '美食', '自然', '历史'] })
			})

			// 邻近景点
			app.get('/api/places/nearby', (req, res) => {
				const { lat = 39.9042, lon = 116.4074, radius = 5, category } = req.query
				let data = genAttractions(parseFloat(lat), parseFloat(lon), 220)
				if (category) data = data.filter(d => d.category === category)
				// 简化：不做严格半径过滤，仅返回 count，并附带距离字段
				res.json({ status: 'success', count: data.length, data })
			})

			// 推荐 - 个性化
			app.get('/api/recommendations', (req, res) => {
				const top_n = parseInt(req.query.top_n || '10', 10)
				const list = Array.from({ length: top_n }).map((_, i) => ({
					attraction_id: i + 1,
					name: `推荐景点-${i + 1}`,
					type: ['历史景点', '自然风光'][i % 2],
					score: parseFloat((0.6 + Math.random() * 0.4).toFixed(2)),
					rating: parseFloat((4 + Math.random()).toFixed(1))
				}))
				res.json({ success: true, data: { recommendations: list, algorithm_used: 'mock' } })
			})

			// 推荐 - 热门
			app.get('/api/recommendations/hot', (req, res) => {
				const top_n = parseInt(req.query.top_n || '10', 10)
				const list = Array.from({ length: top_n }).map((_, i) => ({
					attraction_id: i + 1,
					name: `热门景点-${i + 1}`,
					type: ['历史景点', '自然风光'][i % 2],
					popularity: parseFloat((0.7 + Math.random() * 0.3).toFixed(2)),
					rating: parseFloat((4 + Math.random()).toFixed(1))
				}))
				res.json({ success: true, data: { recommendations: list, sort_method: 'rating' } })
			})

			// 推荐 - 搜索
			app.get('/api/recommendations/search', (req, res) => {
				const q = req.query.query || '关键字'
				const list = Array.from({ length: 8 }).map((_, i) => ({
					attraction_id: i + 1,
					name: `${q}-结果-${i + 1}`,
					type: '自然风光',
					relevance_score: parseFloat((0.5 + Math.random() * 0.5).toFixed(2)),
					match_field: 'name'
				}))
				res.json({ success: true, data: { query: q, results: list, total_count: list.length } })
			})

			return middlewares
		}
	}
}
