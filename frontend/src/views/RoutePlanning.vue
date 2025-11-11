<template>
	<div class="container py-3">
		<div class="d-flex align-items-center justify-content-between mb-2">
			<h2 class="mb-0">路径规划</h2>
			<div class="btn-group">
				<button class="btn btn-sm" :class="routeMode ? 'btn-primary' : 'btn-outline-primary'" @click="toggleRouteMode">
					{{ routeMode ? '绘制中…(点击地图添加点)' : '开始绘制' }}
				</button>
				<button class="btn btn-sm btn-outline-secondary" :disabled="routeMarkers.length===0" @click="undoPoint">撤销</button>
				<button class="btn btn-sm btn-outline-danger" :disabled="routeMarkers.length===0" @click="clearPoints">清空</button>
			</div>
		</div>

		<div class="row g-3">
			<div class="col-12 col-lg-8">
				<BaseMap
					:full-screen="false"
					:height="520"
					:center="center"
					:zoom="12"
					:markers="[]"
					:route-mode="routeMode"
					:route-markers="routeMarkers"
					@route-point-add="onRoutePointAdd"
				/>
			</div>
			<div class="col-12 col-lg-4">
				<div class="card">
					<div class="card-header">路径点 ({{ routeMarkers.length }})</div>
					<ul class="list-group list-group-flush small" style="max-height: 480px; overflow:auto;">
						<li v-for="(p, idx) in routeMarkers" :key="idx" class="list-group-item d-flex justify-content-between align-items-center">
							<span>#{{ idx+1 }} ({{ p.latitude.toFixed(6) }}, {{ p.longitude.toFixed(6) }})</span>
							<button class="btn btn-sm btn-outline-danger" @click="removeAt(idx)">删除</button>
						</li>
						<li v-if="routeMarkers.length===0" class="list-group-item text-muted">点击地图以添加路径点</li>
					</ul>
					<div class="card-footer d-flex justify-content-end gap-2">
						<button class="btn btn-sm btn-outline-secondary" :disabled="routeMarkers.length<2" @click="reverseRoute">反转顺序</button>
						<!-- 预留：调用后端 /api/route/plan 进行线路计算 -->
					</div>
				</div>
			</div>
		</div>
	</div>
	</template>

<script>
import BaseMap from '@/components/map/BaseMap.vue'

export default {
	name: 'RoutePlanning',
	components: { BaseMap },
	data() {
		return {
			center: [39.9042, 116.4074],
			routeMode: true,
			routeMarkers: []
		}
	},
	methods: {
		onRoutePointAdd(point) {
			// 父组件持有路径点状态，以便联动其他 UI
			this.routeMarkers = [...this.routeMarkers, point]
			this.$emit && this.$emit('route-markers-change', this.routeMarkers)
		},
		toggleRouteMode() {
			this.routeMode = !this.routeMode
		},
		undoPoint() {
			if (this.routeMarkers.length === 0) return
			this.routeMarkers = this.routeMarkers.slice(0, -1)
			this.$emit && this.$emit('route-markers-change', this.routeMarkers)
		},
		clearPoints() {
			this.routeMarkers = []
			this.$emit && this.$emit('route-markers-change', this.routeMarkers)
		},
		removeAt(idx) {
			this.routeMarkers = this.routeMarkers.filter((_, i) => i !== idx)
			this.$emit && this.$emit('route-markers-change', this.routeMarkers)
		},
		reverseRoute() {
			this.routeMarkers = [...this.routeMarkers].reverse()
			this.$emit && this.$emit('route-markers-change', this.routeMarkers)
		}
	}
}
</script>
