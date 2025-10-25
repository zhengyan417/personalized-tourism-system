<template>
	<div class="container-fluid">
		<div class="row g-3 align-items-end mb-3">
			<div class="col-12 col-md-2">
				<label class="form-label">纬度</label>
				<input v-model.number="lat" type="number" step="0.0001" class="form-control" />
			</div>
			<div class="col-12 col-md-2">
				<label class="form-label">经度</label>
				<input v-model.number="lon" type="number" step="0.0001" class="form-control" />
			</div>
			<div class="col-12 col-md-2">
				<label class="form-label">半径(km)</label>
				<input v-model.number="radius" type="number" min="1" max="50" class="form-control" />
			</div>
			<div class="col-12 col-md-3">
				<label class="form-label">类别</label>
				<select v-model="category" class="form-select">
					<option value="">全部类别</option>
					<option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
				</select>
			</div>
			<div class="col-12 col-md-3 d-grid">
				<button class="btn btn-primary" @click="loadNearby">查询附近</button>
			</div>
		</div>

		<div class="row g-3">
			<div class="col-12 col-lg-4">
				<div class="list-group list-scroll">
					<button
						v-for="p in places"
						:key="p.id || p.attraction_id || p.name"
						type="button"
						class="list-group-item list-group-item-action"
						:class="{ active: selectedId === (p.id || p.attraction_id) }"
						@click="selectPlace(p)"
					>
						<div class="d-flex w-100 justify-content-between">
							<h6 class="mb-1">{{ p.name || p.title || '未命名景点' }}</h6>
							<small v-if="p.distance_km !== undefined">{{ p.distance_km }} km</small>
						</div>
						<small class="text-muted">{{ p.category || p.type || '未知类别' }}</small>
					</button>
					<div v-if="places.length === 0" class="text-muted p-3">暂无数据，请调整参数后重试。</div>
				</div>
			</div>

			<div class="col-12 col-lg-8">
				<BaseMap
					:center="[lat, lon]"
					:zoom="11"
					:height="600"
					:markers="markers"
					:selectedId="selectedId"
					@marker-click="onMarkerClick"
				/>
			</div>
		</div>
	</div>
</template>

<script>
import BaseMap from '../components/map/BaseMap.vue'
import { fetchNearbyPlaces, fetchCategories } from '../api/place'

export default {
	name: 'PlaceQuery',
	components: { BaseMap },
	data() {
		return {
			lat: 39.9042,
			lon: 116.4074,
			radius: 5,
			category: '',
			categories: [],
			places: [],
			selectedId: null
		}
	},
	computed: {
		markers() {
			return this.places
				.filter(p => typeof p.latitude === 'number' && typeof p.longitude === 'number')
				.map(p => ({
					id: p.id ?? p.attraction_id ?? p.name,
					name: p.name || p.title || '未命名景点',
					latitude: p.latitude,
					longitude: p.longitude,
					popup: `${p.name || p.title || '未命名景点'}${p.distance_km !== undefined ? ` · ${p.distance_km}km` : ''}`
				}))
		}
	},
	async mounted() {
		this.categories = await fetchCategories()
		await this.loadNearby()
	},
	methods: {
		async loadNearby() {
			try {
				const places = await fetchNearbyPlaces({ lat: this.lat, lon: this.lon, radius: this.radius, category: this.category || undefined, limit: 500 })
				this.places = places
				if (this.places.length > 0) {
					const first = this.places[0]
					this.selectedId = first.id || first.attraction_id
				}
			} catch (e) {
				console.error('加载邻近景点失败', e)
				this.places = []
			}
		},
		selectPlace(p) {
			this.selectedId = p.id || p.attraction_id
		},
		onMarkerClick(p) {
			this.selectedId = p.id || p.attraction_id
		}
	}
}
</script>

<style scoped>
.list-scroll {
	max-height: calc(100vh - 220px);
	overflow: auto;
}
</style>
