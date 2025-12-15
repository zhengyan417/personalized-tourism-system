<template>
	<div class="container-fluid">
		<div class="row g-3 mb-3">
			<div class="col-12 col-lg-8">
				<SearchBox v-model="query" @search="onSearch" @reset="onResetSearch" />
			</div>
		</div>

		<div class="row g-3">
			<div class="col-12 col-lg-4 order-2 order-lg-1">
				<PreferencesPanel v-model="prefs" :categories="categories" @apply="refresh" />

				<div class="mt-3">
					<div class="d-flex align-items-center mb-2 gap-2">
						<h5 class="mb-0">推荐结果</h5>
						<span v-if="loading" class="spinner-border spinner-border-sm text-primary" role="status"></span>
					</div>

					<div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
					<div v-else-if="list.length === 0 && !loading" class="text-muted">暂无数据</div>

					<VirtualList
						v-else
						:items="list"
						:itemHeight="cardHeight"
						:height="600"
						:buffer="6"
						:itemKey="item => item.attraction_id || item.id || item.name"
					>
						<template #default="{ item, index }">
							<div class="card mb-2" :class="{ 'border-primary': index < 10 }" @mouseenter="hoverId = getId(item)" @mouseleave="hoverId = null">
								<div class="card-body d-flex gap-3">
									<div class="rank" :class="{ top: index < 10 }">{{ index + 1 }}</div>
									<div class="flex-grow-1">
										<div class="d-flex justify-content-between align-items-center">
											<h6 class="mb-1">{{ item.name }}</h6>
											<span v-if="item.rating" class="badge bg-success">评分 {{ item.rating }}</span>
											<span v-else-if="item.popularity" class="badge bg-info text-dark">热度 {{ item.popularity }}</span>
										</div>
										<div class="text-muted small">{{ item.type || '未知类别' }}</div>
										<div class="mt-1">
											<button class="btn btn-sm btn-outline-primary me-2" @click="focusItem(item)">定位</button>
											<button class="btn btn-sm btn-outline-secondary" @click="viewDetail(item)">详情</button>
										</div>
									</div>
								</div>
							</div>
						</template>
					</VirtualList>
				</div>
			</div>

			<div class="col-12 col-lg-8 order-1 order-lg-2">
				<BaseMap
					:center="mapCenter"
					:zoom="11"
					:height="700"
					:markers="markers"
					:selected-id="selectedId"
					@marker-click="onMarkerClick"
				/>
			</div>
		</div>
	</div>
</template>

<script>
import BaseMap from '../components/map/BaseMap.vue'
import SearchBox from '../components/recommendation/SearchBox.vue'
import PreferencesPanel from '../components/recommendation/PreferencesPanel.vue'
import VirtualList from '../components/recommendation/VirtualList.vue'
import { fetchRecommendations, fetchHotRecommendations, searchRecommendations } from '../api/recommendation'

export default {
	name: 'Recommendation',
	components: { BaseMap, SearchBox, PreferencesPanel, VirtualList },
	data() {
		return {
			query: '',
			prefs: { algorithm: 'content_based', sort_by: 'score', top_n: 30, categories: [] },
			categories: ['历史景点','自然风光','景点','美食','自然','历史'],
			list: [],
			loading: false,
			error: '',
			selectedId: null,
			hoverId: null,
			cardHeight: 96,
			mapCenter: [39.9042, 116.4074]
		}
	},
	computed: {
		markers() {
			return (this.list || []).filter(it => typeof it.latitude === 'number' && typeof it.longitude === 'number')
				.map(it => ({
					id: this.getId(it),
					name: it.name,
					latitude: it.latitude,
					longitude: it.longitude,
					popup: `${it.name}${it.rating ? ' · 评分 ' + it.rating : it.popularity ? ' · 热度 ' + it.popularity : ''}`
				}))
		}
	},
	async mounted() {
		await this.refresh()
	},
	methods: {
		getId(it) { return it.attraction_id || it.id || it.name },
		async refresh() {
			this.loading = true; this.error = ''
			try {
				let data = []
				if (this.query && this.query.trim()) {
					data = await searchRecommendations({ query: this.query, limit: this.prefs.top_n })
				} else {
					// 个性化推荐（后端未就绪时，devServer 提供 mock）
					data = await fetchRecommendations({ user_id: 1, top_n: this.prefs.top_n, algorithm: this.prefs.algorithm })
					if (this.prefs.sort_by && this.prefs.sort_by !== 'score') {
						const key = this.prefs.sort_by
						data = [...data].sort((a, b) => (b[key] || 0) - (a[key] || 0))
					}
				}
				// 类别过滤（如数据无类别字段则忽略）
				if (this.prefs.categories?.length) {
					data = data.filter(d => this.prefs.categories.includes(d.type) || this.prefs.categories.includes(d.category))
				}
				this.list = data
				this.selectedId = this.list[0] ? this.getId(this.list[0]) : null
				const first = this.list.find(it => typeof it.latitude === 'number' && typeof it.longitude === 'number')
				if (first) this.mapCenter = [first.latitude, first.longitude]
			} catch (e) {
				this.error = '加载推荐失败：' + (e?.message || '未知错误')
				this.list = []
			} finally {
				this.loading = false
			}
		},
		onSearch() { this.refresh() },
		onResetSearch() { this.query = ''; this.refresh() },
		focusItem(item) {
			this.selectedId = this.getId(item)
			if (typeof item.latitude === 'number' && typeof item.longitude === 'number') {
				this.mapCenter = [item.latitude, item.longitude]
			}
		},
		onMarkerClick(item) {
			this.selectedId = this.getId(item)
		},
		viewDetail(item) {
			// 预留：可跳转到详情页或弹出对话框
			console.log('view detail', item)
		}
	}
}
</script>

<style scoped>
.rank {
	width: 28px; height: 28px; border-radius: 50%;
	display: inline-flex; align-items: center; justify-content: center;
	background: #e9ecef; color: #333; font-weight: 600;
}
.rank.top { background: #0d6efd; color: #fff; }
</style>
