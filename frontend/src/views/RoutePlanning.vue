<template>
	<div class="container py-3">
		<div class="d-flex align-items-center justify-content-between mb-2">
			<h2 class="mb-0">路径规划（景点ID导航 + 途经点优化）</h2>
		</div>

		<div class="row g-3">
			<div class="col-12 col-lg-8">
				<BaseMap
					:full-screen="false"
					:height="520"
					:center="center"
					:zoom="12"
					:markers="attractionMarkers"
					:road-path="roadPath"
					:start-attraction-id="selectedStartId"
					:end-attraction-id="selectedEndId"
					@marker-click="onAttractionClick"
				/>
			</div>
			<div class="col-12 col-lg-4 d-flex flex-column gap-3">

				<!-- 景点ID导航表单 -->
				<div class="card">
					<div class="card-header d-flex justify-content-between align-items-center">
						<span>景点ID导航</span>
						<small class="text-muted">选择或输入ID</small>
					</div>
					<div class="card-body">
						<form @submit.prevent="submitIdNavigation" class="row g-2">
							<div class="col-6">
								<label class="form-label">起点ID</label>
								<input v-model.number="formIds.startId" type="number" min="1" class="form-control" :placeholder="selectedStartId ? '已选择: '+selectedStartId : '例如 1'" />
							</div>
							<div class="col-6">
								<label class="form-label">终点ID</label>
								<input v-model.number="formIds.endId" type="number" min="1" class="form-control" :placeholder="selectedEndId ? '已选择: '+selectedEndId : '例如 5'" />
							</div>
							<div class="col-6">
								<label class="form-label">模式</label>
								<select v-model="formIds.profile" class="form-select">
									<option value="driving">驾车</option>
									<option value="cycling">骑行</option>
									<option value="walking">步行</option>
								</select>
							</div>
							<div class="col-6">
								<label class="form-label">导航服务</label>
								<select v-model="formIds.provider" class="form-select">
									<option value="auto">自动（优先高德）</option>
									<option value="amap">高德</option>
									<option value="osrm">OSRM</option>
								</select>
							</div>
							<div class="col-12">
								<label class="form-label">途经点ID (逗号分隔, 可选)</label>
								<input v-model="waypointsInput" type="text" class="form-control" placeholder="例如 3,8,12" @blur="parseWaypointsInput" />
								<div class="small mt-1" v-if="waypointIds.length">
									<span class="me-2">已选途经:</span>
									<span v-for="wid in waypointIds" :key="wid" class="badge rounded-pill text-bg-secondary me-1" style="cursor:pointer" @click="removeWaypoint(wid)">
										{{ wid }} ×
									</span>
								</div>
								<div v-else class="form-text">地图点击第三个及以上点可添加途经；再次点击移除。</div>
							</div>
							<div class="col-12 d-flex gap-2 mt-1">
								<button class="btn btn-sm btn-primary" :disabled="roadLoading">{{ roadLoading ? '请求中…' : '导航' }}</button>
								<button type="button" class="btn btn-sm btn-outline-secondary" @click="resetIdNav" :disabled="roadLoading">清除选择</button>
								<button type="button" class="btn btn-sm btn-outline-success" :disabled="!canOptimize" @click="optimizeSequence">优化访问顺序</button>
							</div>
						</form>
						<div class="mt-3 small">
							<div v-if="roadError" class="alert alert-danger py-2 px-3">{{ roadError }}</div>
							<div v-else-if="roadResult && roadResult.status==='success'" class="alert alert-success py-2 px-3">
								<div class="d-flex justify-content-between align-items-center">
									<div>
										<div><strong>距离:</strong> {{ roadResult.data.distance_km }} km</div>
										<div><strong>耗时:</strong> <span v-if="roadResult.data.duration_min">{{ roadResult.data.duration_min }} 分钟</span><span v-else>未知</span></div>
										<div><strong>步骤数:</strong> {{ roadResult.data.steps || roadResult.data.road_path.length }}</div>
										<div><strong>服务:</strong> {{ formatProvider(roadResult.data.provider) }}</div>
									</div>
									<button @click="toggleSteps" type="button" class="btn btn-sm btn-light">{{ showSteps ? '隐藏步骤' : '查看步骤' }}</button>
								</div>
								<div v-if="roadResult.data.degraded" class="text-warning mt-1">已降级为直线（外部服务不可用）</div>
								<div v-if="roadResult.data.fallback" class="text-warning mt-1">已回退：{{ formatFallback(roadResult.data.fallback) }}</div>
								<div v-if="showSteps && !roadResult.data.degraded" class="steps-list mt-2" style="max-height:220px;overflow:auto;">
									<table class="table table-sm table-bordered mb-0">
										<thead class="table-light">
											<tr>
												<th style="width:48px;">序号</th>
												<th>指令</th>
												<th style="width:100px;">距离(km)</th>
												<th style="width:90px;">耗时(分)</th>
											</tr>
										</thead>
										<tbody>
											<tr v-for="st in (roadResult.data.steps_detail || [])" :key="st.index">
												<td>{{ st.index + 1 }}</td>
												<td class="text-wrap">{{ st.instruction }}</td>
												<td>{{ st.distance_km }}</td>
												<td>{{ st.duration_min }}</td>
											</tr>
											<tr v-if="!(roadResult.data.steps_detail && roadResult.data.steps_detail.length)" class="text-muted">
												<td colspan="4">暂无步骤数据（可能服务不支持或已降级）</td>
											</tr>
										</tbody>
									</table>
								</div>
							</div>
							<div v-else class="text-muted">输入或点击地图选择两个景点ID开始导航。或选择多个途经点后点击“优化访问顺序”。</div>
						</div>
					</div>
					<!-- 多点优化结果展示 -->
					<div v-if="optimizedResult" class="mt-3 optimized-box small">
						<div class="d-flex justify-content-between align-items-center mb-1">
							<strong>访问顺序建议</strong>
							<div class="btn-group btn-group-sm">
								<button type="button" class="btn btn-outline-primary" @click="toggleSequence">{{ showSequence ? '隐藏明细' : '查看路径' }}</button>
								<button type="button" class="btn btn-outline-danger" @click="optimizedResult=null">清除</button>
							</div>
						</div>
						<div v-if="optimizedResult.error" class="text-danger">{{ optimizedResult.error }}</div>
						<div v-else>
							<div class="mb-1">总节点: {{ optimizedResult.nodes }}，总距离: {{ optimizedResult.total_distance_km }} km，算法: {{ optimizedResult.method }}</div>
							<ol v-if="showSequence" class="mb-2 ps-3 route-seq-list">
								<li v-for="(seg, i) in optimizedResult.segments" :key="i">
									第 {{ i+1 }} 步：从 <strong>#{{ seg.from }}</strong> {{ getName(seg.from) }} 到 <strong>#{{ seg.to }}</strong> {{ getName(seg.to) }}，约 {{ seg.distance_km }} km
								</li>
							</ol>
							<div v-if="!showSequence" class="text-muted">点击“查看路径”可展开包含景点名称的逐步路线。</div>
							<div class="text-muted">说明：顺序由起点出发依次访问，其后可在每段之间进行导航请求以获得道路级指令。</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import BaseMap from '@/components/map/BaseMap.vue'
import { fetchRoadRoute } from '@/api/route'
import { fetchAllPlaces } from '@/api/place'

export default {
	name: 'RoutePlanning',
	components: { BaseMap },
	data() {
		return {
			center: [39.9042, 116.4074],
			attractionMarkers: [],
			selectedStartId: null,
			selectedEndId: null,
			roadPath: [],
			showSteps: false,
			showSequence: false,
			// 多点途经：维护原始 ID 数组与输入框字符串
			waypointIds: [], // 数字 ID 列表（不含起终点）
			waypointsInput: '', // 文本框，逗号 / 空格分隔
			formIds: {
				startId: null,
				endId: null,
				profile: 'driving',
				provider: 'auto'
			},
			roadLoading: false,
			roadResult: null,
			roadError: '',
			optimizedResult: null
		}
	},
	mounted() {
		this.loadAttractions()
	},
		computed: {
			canOptimize() {
				return !!(this.selectedStartId && this.waypointIds.length)
			}
		},
	methods: {
		formatProvider(provider) {
			const mapping = {
				amap: '高德导航',
				osrm: 'OSRM',
				auto: '自动'
			}
			if (!provider) return '未指定'
			const key = String(provider).toLowerCase()
			return mapping[key] || provider
		},
		formatFallback(fallback) {
			if (!fallback) return ''
			if (typeof fallback === 'string') return fallback
			if (typeof fallback === 'object') {
				return Object.entries(fallback).map(([k, v]) => `${k}: ${v}`).join('；')
			}
			return String(fallback)
		},
		async loadAttractions() {
			try {
				const rows = await fetchAllPlaces()
				this.attractionMarkers = rows.filter(r => typeof r.latitude === 'number' && typeof r.longitude === 'number').map(r => ({
					id: r.attraction_id || r.id,
					name: r.name,
					latitude: r.latitude,
					longitude: r.longitude,
					popup: `${r.name} (#${r.attraction_id || r.id})`
				}))
			} catch (e) {
				console.warn('[loadAttractions] failed', e.message)
			}
		},
		onAttractionClick(mk) {
			const id = mk.id
			// 交互逻辑：
			// 1. 未选择起点 -> 设为起点
			// 2. 已有起点但无终点 -> 且点击的不是起点 -> 设为终点并自动导航（无途经点时）
			// 3. 已有起终点：
			//    a) 点击起点或终点 -> 重置为新的起点，清空终点与途经
			//    b) 点击其他 -> 作为途经点（切换添加/移除）
			if (this.selectedStartId == null) {
				this.selectedStartId = id
				this.formIds.startId = id
				return
			}
			if (this.selectedEndId == null && id !== this.selectedStartId) {
				this.selectedEndId = id
				this.formIds.endId = id
				// 若没有途经点则立即导航；有的话用户可能继续添加 -> 不自动提交
				if (this.waypointIds.length === 0) this.submitIdNavigation()
				return
			}
			// 已有起终点
			if (id === this.selectedStartId || id === this.selectedEndId) {
				// 重置为新的起点
				this.selectedStartId = id
				this.formIds.startId = id
				this.selectedEndId = null
				this.formIds.endId = null
				this.waypointIds = []
				this.syncWaypointsInput()
				this.roadPath = []
				this.roadResult = null
				return
			}
			// 切换途经点
			const sid = String(id)
			const exists = this.waypointIds.some(w => String(w) === sid)
			if (exists) {
				this.waypointIds = this.waypointIds.filter(w => String(w) !== sid)
			} else {
				this.waypointIds = [...this.waypointIds, id]
			}
			this.syncWaypointsInput()
		},
		async submitIdNavigation() {
			this.roadError = ''
			this.roadResult = null
			const startId = this.formIds.startId ?? this.selectedStartId
			const endId = this.formIds.endId ?? this.selectedEndId
			if (!startId || !endId) {
				this.roadError = '起点或终点ID未填写/选择'
				return
			}
			const startPlace = this.attractionMarkers.find(m => String(m.id) === String(startId))
			const endPlace = this.attractionMarkers.find(m => String(m.id) === String(endId))
			if (!startPlace || !endPlace) {
				this.roadError = 'ID对应的景点不存在或无坐标'
				return
			}
			// 解析途经点坐标
			const waypointPlaces = this.waypointIds
				.map(id => this.attractionMarkers.find(m => String(m.id) === String(id)))
				.filter(Boolean)
			const waypointCoords = waypointPlaces.map(p => [p.latitude, p.longitude])
			this.roadLoading = true
			try {
				const r = await fetchRoadRoute(
					startPlace.latitude,
					startPlace.longitude,
					endPlace.latitude,
					endPlace.longitude,
					{ profile: this.formIds.profile, waypoints: waypointCoords, provider: this.formIds.provider }
				)
				if (r.error) {
					this.roadError = r.error
				} else {
					this.roadResult = r
					if (r.status === 'success' && r.data && Array.isArray(r.data.road_path)) {
						this.roadPath = r.data.road_path
					}
				}
			} catch (e) {
				this.roadError = e.message || '请求失败'
			} finally {
				this.roadLoading = false
			}
		},
		resetIdNav() {
			this.formIds.startId = null
			this.formIds.endId = null
			this.formIds.profile = 'driving'
			this.formIds.provider = 'auto'
			this.roadPath = []
			this.roadResult = null
			this.roadError = ''
			this.selectedStartId = null
			this.selectedEndId = null
			this.waypointIds = []
			this.syncWaypointsInput()
		},
		// 手动清除当前起终点选择（可在后续UI中绑定按钮）
		clearSelections() {
			this.selectedStartId = null
			this.selectedEndId = null
			this.waypointIds = []
			this.syncWaypointsInput()
		},
		// 解析输入框字符串 -> waypointIds
		parseWaypointsInput() {
			const raw = this.waypointsInput
			if (!raw) {
				this.waypointIds = []
				return
			}
			const parts = raw.split(/[,;\s]+/).map(s => s.trim()).filter(Boolean)
			const nums = []
			for (const p of parts) {
				const n = Number(p)
				if (!Number.isInteger(n)) continue
				if (n === this.selectedStartId || n === this.selectedEndId) continue
				if (!nums.includes(n)) nums.push(n)
			}
			this.waypointIds = nums
		},
		syncWaypointsInput() {
			if (!this.waypointIds.length) {
				this.waypointsInput = ''
				return
			}
			this.waypointsInput = this.waypointIds.join(',')
		},
		removeWaypoint(id) {
			this.waypointIds = this.waypointIds.filter(w => String(w) !== String(id))
			this.syncWaypointsInput()
		},
		toggleSteps() {
			this.showSteps = !this.showSteps
		},
		async optimizeSequence() {
			if (!this.selectedStartId || this.waypointIds.length === 0) return
			// 若用户也选了终点，将终点加入优化集合末尾（算法会自行排序）；如果希望终点固定，可后端扩展
			const toVisit = [...this.waypointIds]
			if (this.selectedEndId && !toVisit.includes(this.selectedEndId)) toVisit.push(this.selectedEndId)
			try {
				const { fetchOptimizedSequence } = await import('@/api/route')
				const r = await fetchOptimizedSequence(this.selectedStartId, toVisit)
				if (r.error || r.status === 'error') {
					this.optimizedResult = { error: r.error || r.message }
				} else {
					this.optimizedResult = r.data
				}
			} catch (e) {
				this.optimizedResult = { error: e.message || '优化失败' }
			}
		},
		formatOptimizedStep(idx, seg) {
			// 旧格式备用
			return `第 ${idx + 1} 步：从 #${seg.from} 到 #${seg.to}，约 ${seg.distance_km} km`
		},
		getName(id) {
			const m = this.attractionMarkers.find(x => String(x.id) === String(id))
			return m ? `(${m.name})` : ''
		},
		toggleSequence() {
			this.showSequence = !this.showSequence
		}
	}
}
</script>

<style scoped>
.steps-list table td, .steps-list table th { white-space: nowrap; }
.optimized-box { border: 1px solid #d1e7dd; background:#f0fdf4; padding:8px 12px; border-radius:6px; }
</style>
