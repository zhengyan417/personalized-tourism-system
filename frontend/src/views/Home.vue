<template>
	<div>
		<BaseMap
			ref="baseMap"
			:center="mapCenter"
			:zoom="11"
			:full-screen="true"
			:offset-top="navbarHeight"
			:markers="markers"
			:selected-id="selectedId"
			:route-mode="activeTab === 'route' && !!routePlanningMode"
			:route-markers="routeMarkersForMap"
			:planned-path="plannedPath"
			@marker-click="onMarkerClick"
			@location-update="onLocationUpdate"
					@route-point-add="onRoutePointAdd"
		/>

		<!-- 左侧功能面板 -->
			<div class="home-panel card shadow-sm" :style="{ top: panelPos.top + 'px', left: panelPos.left + 'px' }">
				<div class="card-header p-2 panel-drag-handle" @mousedown="onDragStart">
				<ul class="nav nav-tabs card-header-tabs small">
					<li class="nav-item"><a class="nav-link" :class="{ active: activeTab==='place' }" href="#" @click.prevent="switchTab('place')">附近</a></li>
					<li class="nav-item"><a class="nav-link" :class="{ active: activeTab==='recommend' }" href="#" @click.prevent="switchTab('recommend')">推荐</a></li>
					<li class="nav-item"><a class="nav-link" :class="{ active: activeTab==='route' }" href="#" @click.prevent="switchTab('route')">路径</a></li>
					<li class="nav-item"><a class="nav-link" :class="{ active: activeTab==='diary' }" href="#" @click.prevent="switchTab('diary')">日记</a></li>
				</ul>
			</div>

			<div class="card-body p-2">
				<!-- 附近 -->
				<div v-if="activeTab==='place'">
								<div class="row g-2 align-items-end mb-2">
									<div class="col-6">
										<label class="form-label">纬度</label>
										<input v-model.number="place.lat" type="number" step="0.0001" class="form-control form-control-sm" />
									</div>
									<div class="col-6">
										<label class="form-label">经度</label>
										<input v-model.number="place.lon" type="number" step="0.0001" class="form-control form-control-sm" />
									</div>
									<div class="col-6">
							<label class="form-label">半径(km)</label>
							<input v-model.number="place.radius" type="number" min="1" max="50" class="form-control form-control-sm" />
						</div>
						<div class="col-6">
							<label class="form-label">类别</label>
							<select v-model="place.category" class="form-select form-select-sm">
								<option value="">全部</option>
								<option v-for="c in place.categories" :key="c" :value="c">{{ c }}</option>
							</select>
						</div>
						<div class="col-12 d-grid gap-2 d-flex">
							<button class="btn btn-primary btn-sm" @click="loadNearby"><span v-if="place.loading" class="spinner-border spinner-border-sm me-1"></span>查询附近</button>
							<button class="btn btn-outline-secondary btn-sm" @click="locate">定位</button>
										<button class="btn btn-outline-secondary btn-sm" @click="syncMapCenter">取地图中心</button>
						</div>
					</div>
					<div class="list-group list-scroll">
						<button v-for="p in place.list" :key="p.id || p.attraction_id || p.name" type="button"
							class="list-group-item list-group-item-action py-2"
							:class="{ active: selectedId === (p.id || p.attraction_id) }"
							@click="focusPlace(p)">
							<div class="d-flex w-100 justify-content-between">
								<small class="fw-bold">{{ p.name }}</small>
								<small v-if="p.distance_km !== undefined" class="text-muted">{{ p.distance_km }} km</small>
							</div>
							<small class="text-muted">{{ p.category || p.type || '-' }}</small>
						</button>
						<div v-if="!place.loading && place.list.length===0" class="text-muted p-2">暂无数据</div>
					</div>
				</div>

				<!-- 推荐 -->
				<div v-else-if="activeTab==='recommend'">
					<div class="input-group input-group-sm mb-2">
						<input v-model.trim="recommend.query" type="text" class="form-control" placeholder="搜索关键词" @keyup.enter="refreshRecommend" />
						<button class="btn btn-outline-primary" @click="refreshRecommend">搜索/推荐</button>
					</div>
					<div class="row g-2 align-items-end mb-2">
						<div class="col-4">
							<label class="form-label">算法</label>
							<select v-model="recommend.prefs.algorithm" class="form-select form-select-sm">
								<option value="content_based">内容</option>
								<option value="collaborative">协同</option>
							</select>
						</div>
						<div class="col-4">
							<label class="form-label">排序</label>
							<select v-model="recommend.prefs.sort_by" class="form-select form-select-sm">
								<option value="score">综合</option>
								<option value="popularity">热度</option>
								<option value="rating">评分</option>
							</select>
						</div>
						<div class="col-4">
							<label class="form-label">Top N</label>
							<input v-model.number="recommend.prefs.top_n" type="number" min="1" max="1000" class="form-control form-control-sm" />
						</div>
						<div class="col-12 d-flex gap-2">
							<button class="btn btn-primary btn-sm" @click="refreshRecommend">应用</button>
							<button class="btn btn-link btn-sm ms-auto" @click="recommend.showAdv = !recommend.showAdv">{{ recommend.showAdv ? '收起' : '更多' }}</button>
						</div>
					</div>
					<div v-if="recommend.showAdv" class="mb-2">
						<div class="small text-muted mb-1">类别（可选）</div>
						<div class="d-flex flex-wrap gap-2 small">
							<label class="form-check-label" v-for="c in recommend.categories" :key="c">
								<input class="form-check-input me-1" type="checkbox" :value="c" v-model="recommend.prefs.categories" /> {{ c }}
							</label>
						</div>
					</div>
					<div class="list-group list-scroll">
						<button v-for="r in recommend.list" :key="getId(r)" type="button"
							class="list-group-item list-group-item-action py-2"
							:class="{ active: selectedId === getId(r) }"
							@click="focusRecommend(r)">
							<div class="d-flex justify-content-between">
								<small class="fw-bold">{{ r.name }}</small>
								<small class="text-muted" v-if="r.rating">评分 {{ r.rating }}</small>
								<small class="text-muted" v-else-if="r.popularity">热度 {{ r.popularity }}</small>
							</div>
							<small class="text-muted">{{ r.type || r.category || '-' }}</small>
						</button>
						<div v-if="!recommend.loading && recommend.list.length===0" class="text-muted p-2">暂无数据</div>
					</div>
				</div>

				<!-- 路径规划 -->
				<div v-else-if="activeTab==='route'">
					<div class="d-flex gap-2 mb-2 flex-wrap">
						<button class="btn btn-sm btn-outline-primary" :class="{ active: routePlanningMode==='setStart' }" @click="setMode('setStart')">设起点</button>
						<button class="btn btn-sm btn-outline-danger" :class="{ active: routePlanningMode==='setEnd' }" @click="setMode('setEnd')">设终点</button>
						<button class="btn btn-sm btn-outline-secondary" :class="{ active: routePlanningMode==='addWaypoint' }" @click="setMode('addWaypoint')">加途经点</button>
						<button class="btn btn-sm btn-outline-warning" @click="clearAllRoute" :disabled="!hasAnyRoutePoint">清空</button>
						<button class="btn btn-sm btn-primary" @click="computeRoute" :disabled="!canPlan || planning">
							<span v-if="planning" class="spinner-border spinner-border-sm me-1"></span>开始规划
						</button>
					</div>
					<div class="route-summary small mb-2" v-if="distanceInfo">
						<span>总距离: {{ distanceInfo.km }} km</span>
						<span class="ms-2">步行: {{ distanceInfo.walkTime }}</span>
						<span class="ms-2">骑行: {{ distanceInfo.bikeTime }}</span>
					</div>
					<ol class="small mb-2 ps-3">
						<li v-if="startPoint">起点: {{ startPoint.latitude }}, {{ startPoint.longitude }}</li>
						<li v-for="(p,i) in waypoints" :key="'w'+i">途经{{ i+1 }}: {{ p.latitude }}, {{ p.longitude }}</li>
						<li v-if="endPoint">终点: {{ endPoint.latitude }}, {{ endPoint.longitude }}</li>
					</ol>
					<div v-if="routeError" class="alert alert-danger py-1 small">{{ routeError }}</div>
				</div>

				<!-- 日记 -->
				<div v-else-if="activeTab==='diary'">
					<div class="mb-2">
						<label class="form-label">标题</label>
						<input v-model.trim="diary.form.title" type="text" class="form-control form-control-sm" placeholder="请输入标题" />
					</div>
					<div class="mb-2">
						<label class="form-label">内容</label>
						<textarea v-model.trim="diary.form.content" rows="4" class="form-control form-control-sm" placeholder="记录你的旅途…"></textarea>
					</div>
					<div class="row g-2 mb-2">
						<div class="col-6">
							<label class="form-label">纬度</label>
							<input v-model.number="diary.form.latitude" type="number" step="0.000001" class="form-control form-control-sm" />
						</div>
						<div class="col-6">
							<label class="form-label">经度</label>
							<input v-model.number="diary.form.longitude" type="number" step="0.000001" class="form-control form-control-sm" />
						</div>
					</div>
					<div class="d-flex gap-2 mb-2">
						<button class="btn btn-sm btn-outline-secondary" @click="locate">使用当前位置</button>
						<button class="btn btn-sm btn-primary ms-auto" :disabled="diary.submitting" @click="submitDiary">
							<span v-if="diary.submitting" class="spinner-border spinner-border-sm me-1"></span>提交
						</button>
					</div>
					<div class="list-group list-scroll">
						<button v-for="d in diary.list" :key="d.id" type="button"
							class="list-group-item list-group-item-action py-2"
							:class="{ active: selectedId === d.id }" @click="selectDiary(d)">
							<div class="d-flex justify-content-between"><small class="fw-bold">{{ d.title }}</small><small class="text-muted">{{ d.date }}</small></div>
							<small class="text-muted ellipsis-1">{{ d.snippet || d.content }}</small>
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- 右上角快捷按钮 -->
		<div class="home-actions">
			<button class="btn btn-sm btn-outline-primary" @click="locate">定位</button>
		</div>
	</div>
</template>

<script>
import BaseMap from '../components/map/BaseMap.vue'
import { fetchNearbyPlaces, fetchCategories } from '../api/place'
import { fetchRecommendations, searchRecommendations } from '../api/recommendation'
import { planSimple } from '../api/route'
import { fetchDiaries, fetchDiaryDetail, createDiary } from '../api/diary'

export default {
	name: 'Home',
	components: { BaseMap },
	data() {
		return {
			navbarHeight: 56,
			activeTab: 'place',
			mapCenter: [39.9042, 116.4074],
				panelPos: { top: 64, left: 12 },
				dragging: { active: false, startX: 0, startY: 0, baseTop: 64, baseLeft: 12 },
			selectedId: null,
			// 路径
			routeMode: false,
			routeInfo: null,
			planning: false,
			// 附近
			place: { lat: 39.9042, lon: 116.4074, radius: 5, category: '', categories: [], list: [], loading: false },
			// 推荐
			recommend: { query: '', list: [], loading: false, showAdv: false, categories: ['历史景点','自然风光','景点','美食','自然','历史'], prefs: { algorithm: 'content_based', sort_by: 'score', top_n: 100, categories: [] } },
			// 日记
			diary: { list: [], selected: null, submitting: false, form: { title: '', content: '', latitude: null, longitude: null } }
		}
	},
	computed: {
		markers() {
			if (this.activeTab === 'place') {
				return (this.place.list || []).filter(p => typeof p.latitude==='number' && typeof p.longitude==='number')
					.map(p => ({ id: p.id ?? p.attraction_id ?? p.name, name: p.name, latitude: p.latitude, longitude: p.longitude, popup: p.name }))
			}
			if (this.activeTab === 'recommend') {
				return (this.recommend.list || []).filter(r => typeof r.latitude==='number' && typeof r.longitude==='number')
					.map(r => ({ id: this.getId(r), name: r.name, latitude: r.latitude, longitude: r.longitude, popup: r.name }))
			}
			if (this.activeTab === 'diary') {
				return (this.diary.list || []).filter(d => typeof d.latitude==='number' && typeof d.longitude==='number')
					.map(d => ({ id: d.id, name: d.title, latitude: d.latitude, longitude: d.longitude, popup: `${d.title} · ${d.date||''}` }))
			}
			if (this.activeTab === 'route') {
				const m = []
				if (this.startPoint) m.push({ id: 'start', name: '起点', latitude: this.startPoint.latitude, longitude: this.startPoint.longitude, popup: '起点', color: '#2ecc71' })
				this.waypoints.forEach((w, idx) => m.push({ id: 'wp'+idx, name: '途经'+(idx+1), latitude: w.latitude, longitude: w.longitude, popup: '途经点 '+(idx+1), color: '#f39c12' }))
				if (this.endPoint) m.push({ id: 'end', name: '终点', latitude: this.endPoint.latitude, longitude: this.endPoint.longitude, popup: '终点', color: '#e74c3c' })
				return m
			}
			return []
		}
		,
		// Vuex state helpers
		startPoint() { return this.$store.state.routePlanning.startPoint },
		endPoint() { return this.$store.state.routePlanning.endPoint },
		waypoints() { return this.$store.state.routePlanning.waypoints },
		routePlanningMode() { return this.$store.state.routePlanning.currentMode },
		hasAnyRoutePoint() { return !!(this.startPoint || this.endPoint || (this.waypoints && this.waypoints.length)) },
		canPlan() { return !!(this.startPoint && this.endPoint) },
		plannedPath() { return this.$store.state.routePlanning.calculatedRoute?.path || [] },
		routeMarkersForMap() {
			// 防御性构建：避免对非数组/非对象使用 push 导致运行时错误
			try {
				const out = []
				if (this.startPoint && typeof this.startPoint === 'object') out.push(this.startPoint)
				const wps = Array.isArray(this.waypoints) ? this.waypoints : (this.waypoints ? [this.waypoints] : [])
				wps.forEach(w => { if (w && typeof w === 'object') out.push(w) })
				if (this.endPoint && typeof this.endPoint === 'object') out.push(this.endPoint)
				return out.filter(p => p && typeof p.latitude === 'number' && typeof p.longitude === 'number')
					.map(p => ({ latitude: p.latitude, longitude: p.longitude }))
			} catch (e) {
				console.warn('[Home] routeMarkersForMap 构造失败，返回空数组', e)
				return []
			}
		},
		distanceInfo() {
			const total = this.$store.state.routePlanning.calculatedRoute?.total_distance
			if (!total || isNaN(total)) return null
			const km = Number(total).toFixed(2)
			const walkHours = total / 5
			const bikeHours = total / 15
			const format = (h) => {
				const hours = Math.floor(h)
				const mins = Math.round((h - hours) * 60)
				return hours ? `${hours}h${mins}m` : `${mins}m`
			}
			return { km, walkTime: format(walkHours), bikeTime: format(bikeHours) }
		},
		routeError() { return this.$store.state.routePlanning.error }
	},
	async mounted() {
		// 初始化类别、附近与推荐、日记
		this.place.categories = await fetchCategories()
			// 初始将输入与中心同步
			this.place.lat = this.mapCenter[0]; this.place.lon = this.mapCenter[1]
			await Promise.all([this.loadNearby(), this.refreshRecommend(), this.loadDiaries()])
	},
	methods: {
			// 面板拖动
			onDragStart(e) {
				this.dragging.active = true
				this.dragging.startX = e.clientX
				this.dragging.startY = e.clientY
				this.dragging.baseTop = this.panelPos.top
				this.dragging.baseLeft = this.panelPos.left
				window.addEventListener('mousemove', this.onDragging)
				window.addEventListener('mouseup', this.onDragEnd)
			},
			onDragging(e) {
				if (!this.dragging.active) return
				const dx = e.clientX - this.dragging.startX
				const dy = e.clientY - this.dragging.startY
				const top = Math.max(8, Math.min(window.innerHeight - 120, this.dragging.baseTop + dy))
				const left = Math.max(8, Math.min(window.innerWidth - 360, this.dragging.baseLeft + dx))
				this.panelPos = { top, left }
			},
			onDragEnd() {
				this.dragging.active = false
				window.removeEventListener('mousemove', this.onDragging)
				window.removeEventListener('mouseup', this.onDragEnd)
			},
		switchTab(tab) { this.activeTab = tab },
		locate() { this.$refs.baseMap?.locateUser?.(false) },
		onLocationUpdate(pos) {
			if (!pos) return
			// 更新默认地图中心与日记坐标
			this.mapCenter = [pos.latitude, pos.longitude]
				// 同步到“附近”输入
				this.place.lat = pos.latitude
				this.place.lon = pos.longitude
			if (this.activeTab === 'diary') {
				this.diary.form.latitude = pos.latitude
				this.diary.form.longitude = pos.longitude
			}
		},
		onMarkerClick(item) {
			if (!item) return
			this.selectedId = item.id
		},
		// --- 附近 ---
			async loadNearby() {
			this.place.loading = true
			try {
					const lat = this.place.lat ?? this.mapCenter[0]
					const lon = this.place.lon ?? this.mapCenter[1]
					const list = await fetchNearbyPlaces({ lat, lon, radius: this.place.radius, category: this.place.category || undefined, limit: 200 })
				this.place.list = list
				if (list.length) this.selectedId = list[0].id || list[0].attraction_id
			} catch (e) {
				console.error('加载附近失败', e)
				this.place.list = []
			} finally { this.place.loading = false }
		},
		focusPlace(p) {
			this.selectedId = p.id || p.attraction_id
			if (typeof p.latitude==='number' && typeof p.longitude==='number') this.mapCenter = [p.latitude, p.longitude]
		},
			syncMapCenter() {
				this.place.lat = this.mapCenter[0]
				this.place.lon = this.mapCenter[1]
			},
		// --- 推荐 ---
		getId(it) { return it.attraction_id || it.id || it.name },
		async refreshRecommend() {
			this.recommend.loading = true
			try {
				let list = []
				if (this.recommend.query && this.recommend.query.trim()) {
					list = await searchRecommendations({ query: this.recommend.query, limit: this.recommend.prefs.top_n || 100 })
				} else {
					list = await fetchRecommendations({ user_id: 1, top_n: this.recommend.prefs.top_n || 100, algorithm: this.recommend.prefs.algorithm })
					if (this.recommend.prefs.sort_by && this.recommend.prefs.sort_by !== 'score') {
						const key = this.recommend.prefs.sort_by
						list = [...list].sort((a, b) => (b[key] || 0) - (a[key] || 0))
					}
				}
				if (this.recommend.prefs.categories?.length) {
					list = list.filter(d => this.recommend.prefs.categories.includes(d.type) || this.recommend.prefs.categories.includes(d.category))
				}
				this.recommend.list = list
				const first = list.find(it => typeof it.latitude==='number' && typeof it.longitude==='number')
				if (first) { this.selectedId = this.getId(first); this.mapCenter = [first.latitude, first.longitude] }
			} catch (e) {
				console.error('加载推荐失败', e)
				this.recommend.list = []
			} finally { this.recommend.loading = false }
		},
		focusRecommend(r) {
			this.selectedId = this.getId(r)
			if (typeof r.latitude==='number' && typeof r.longitude==='number') this.mapCenter = [r.latitude, r.longitude]
		},
		// --- 路径 ---
		setMode(mode) { this.$store.commit('routePlanning/setMode', mode) },
		clearAllRoute() { this.$store.commit('routePlanning/clearAll') },
		onRoutePointAdd(p) {
			const mode = this.routePlanningMode
			if (!mode) return
			const point = { ...p, id: `${Date.now()}-${Math.random()}` }
			if (mode === 'setStart') this.$store.commit('routePlanning/setStart', point)
			else if (mode === 'setEnd') this.$store.commit('routePlanning/setEnd', point)
			else if (mode === 'addWaypoint') this.$store.commit('routePlanning/addWaypoint', point)
		},
		generateRouteRequest() {
			return {
				start_id: this.startPoint?.id,
				end_id: this.endPoint?.id,
				waypoint_ids: this.waypoints.map(w => w.id)
			}
		},
		async computeRoute() {
			if (!this.canPlan) return
			const payload = this.generateRouteRequest()
			this.planning = true
			this.$store.commit('routePlanning/setLoading', true)
			this.$store.commit('routePlanning/setError', '')
			try {
				const { planRoute } = await import('../api/routePlanning.js')
				const data = await planRoute(payload)
				this.$store.commit('routePlanning/setCalculatedRoute', data)
			} catch (e) {
				console.error('规划失败', e)
				this.$store.commit('routePlanning/setError', e.message || '规划失败')
				alert(e.message || '规划失败')
			} finally {
				this.planning = false
				this.$store.commit('routePlanning/setLoading', false)
			}
		},
		// --- 日记 ---
		async loadDiaries() {
			try {
				const list = await fetchDiaries({ user_id: 1 })
				this.diary.list = Array.isArray(list) ? list : []
			} catch (e) { console.error('加载日记失败', e); this.diary.list = [] }
		},
		async submitDiary() {
			if (!this.diary.form.title || !this.diary.form.content) return
			this.diary.submitting = true
			try {
				const created = await createDiary({
					user_id: 1,
					title: this.diary.form.title,
					content: this.diary.form.content,
					latitude: this.diary.form.latitude,
					longitude: this.diary.form.longitude
				})
				if (created) {
					this.diary.list = [created, ...this.diary.list]
					this.activeTab = 'diary'
					this.selectedId = created.id
					if (typeof created.latitude==='number' && typeof created.longitude==='number') this.mapCenter = [created.latitude, created.longitude]
					this.diary.form = { title: '', content: '', latitude: null, longitude: null }
				}
			} catch (e) { console.error('创建日记失败', e) } finally { this.diary.submitting = false }
		},
		async selectDiary(d) {
			try {
				const detail = await fetchDiaryDetail(d.id)
				this.diary.selected = detail || d
			} catch { this.diary.selected = d }
			this.selectedId = d.id
			if (typeof d.latitude==='number' && typeof d.longitude==='number') this.mapCenter = [d.latitude, d.longitude]
		}
	}
}
</script>

<style scoped>
.home-panel {
	position: fixed;
	top: 64px;
	left: 12px;
	width: 340px;
	max-height: calc(100vh - 80px);
	overflow: hidden;
	z-index: 1020;
}
.home-panel .card-body { overflow: auto; max-height: calc(100vh - 140px); }
.list-scroll { max-height: 56vh; overflow: auto; }
.ellipsis-1 { display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }
.home-actions { position: fixed; top: 64px; right: 12px; z-index: 1020; display: flex; gap: 8px; }
</style>
