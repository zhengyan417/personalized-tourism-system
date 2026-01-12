<template>
	<div class="min-h-[calc(100vh-64px)] bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50">
		<!-- 头部Banner -->
		<div class="bg-gradient-to-r from-brand-500 to-brand-600 text-white py-12 px-4">
			<div class="max-w-7xl mx-auto">
				<div class="flex flex-col md:flex-row items-center justify-between gap-6">
					<div>
						<h1 class="text-4xl font-bold mb-2">
							<i class="bi bi-people-fill mr-3"></i>旅行社区
						</h1>
						<p class="text-brand-100 text-lg">发现精彩旅程，分享你的故事</p>
					</div>
					<div class="flex items-center gap-6 text-sm">
						<div class="text-center">
							<div class="text-3xl font-bold">{{ stats.totalDiaries }}</div>
							<div class="text-brand-100">篇日记</div>
						</div>
						<div class="text-center">
							<div class="text-3xl font-bold">{{ stats.totalUsers }}</div>
							<div class="text-brand-100">位旅行者</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- 主内容区 -->
		<div class="max-w-7xl mx-auto px-4 py-8">
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
				<!-- 左侧：日记列表 -->
				<div class="lg:col-span-2 space-y-4">
					<!-- 筛选栏 -->
					<div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-4 flex flex-wrap items-center justify-between gap-4">
						<div class="flex items-center gap-2">
							<button 
								v-for="tab in tabs" 
								:key="tab.value"
								@click="currentTab = tab.value"
								class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
								:class="currentTab === tab.value ? 'bg-brand-500 text-white shadow-md' : 'text-slate-600 hover:bg-slate-100'"
							>
								<i :class="tab.icon" class="mr-1"></i>
								{{ tab.label }}
							</button>
						</div>
						<router-link 
							v-if="isLoggedIn" 
							to="/diary" 
							class="px-4 py-2 bg-gradient-to-r from-brand-500 to-brand-600 text-white rounded-lg text-sm font-medium hover:shadow-lg transition-all no-underline"
						>
							<i class="bi bi-pencil-square mr-1"></i> 写日记
						</router-link>
					</div>

					<!-- 加载状态 -->
					<div v-if="loading" class="space-y-4">
						<div v-for="i in 3" :key="i" class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 animate-pulse">
							<div class="h-4 bg-slate-200 rounded w-3/4 mb-4"></div>
							<div class="h-3 bg-slate-200 rounded w-full mb-2"></div>
							<div class="h-3 bg-slate-200 rounded w-5/6"></div>
						</div>
					</div>

					<!-- 日记卡片列表 -->
					<div v-else class="space-y-4">
						<div 
							v-for="diary in diaries" 
							:key="diary.diary_id"
							class="bg-white rounded-2xl shadow-sm border border-slate-200 hover:shadow-xl hover:border-brand-200 transition-all duration-300 overflow-hidden group cursor-pointer"
							@click="selectDiary(diary)"
						>
							<!-- 卡片头部：用户信息 -->
							<div class="px-6 pt-6 pb-4 flex items-center justify-between">
								<div class="flex items-center gap-3">
									<img 
										:src="diary.user_avatar || `https://ui-avatars.com/api/?name=${diary.username}&background=0ea5e9&color=fff`" 
										:alt="diary.username"
										class="w-12 h-12 rounded-full object-cover border-2 border-brand-100"
									>
									<div>
										<div class="font-semibold text-slate-900">{{ diary.username }}</div>
										<div class="text-xs text-slate-400">{{ formatDate(diary.date) }}</div>
									</div>
								</div>
								<button class="opacity-0 group-hover:opacity-100 transition-opacity text-slate-400 hover:text-brand-500">
									<i class="bi bi-three-dots-vertical"></i>
								</button>
							</div>

							<!-- 卡片主体：标题和内容 -->
							<div class="px-6 pb-4">
								<h3 class="text-xl font-bold text-slate-900 mb-2 group-hover:text-brand-600 transition-colors">
									{{ diary.title }}
								</h3>
								<p class="text-slate-600 text-sm line-clamp-3 leading-relaxed">
									{{ diary.snippet || diary.content }}
								</p>
							</div>

							<!-- 地点标签 -->
							<div v-if="diary.attraction_name" class="px-6 pb-4">
								<span class="inline-flex items-center gap-1 px-3 py-1 bg-brand-50 text-brand-600 rounded-full text-xs font-medium">
									<i class="bi bi-geo-alt-fill"></i>
									{{ diary.attraction_name }}
								</span>
							</div>

							<!-- 卡片底部：互动数据 -->
							<div class="px-6 py-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-sm text-slate-500">
								<div class="flex items-center gap-4">
									<button class="hover:text-rose-500 transition-colors">
										<i class="bi bi-heart"></i>
										<span class="ml-1">0</span>
									</button>
									<button class="hover:text-brand-500 transition-colors">
										<i class="bi bi-chat"></i>
										<span class="ml-1">0</span>
									</button>
									<button class="hover:text-brand-500 transition-colors">
										<i class="bi bi-eye"></i>
										<span class="ml-1">0</span>
									</button>
								</div>
								<button class="hover:text-brand-500 transition-colors">
									<i class="bi bi-bookmark"></i>
								</button>
							</div>
						</div>

						<!-- 空状态 -->
						<div v-if="diaries.length === 0" class="bg-white rounded-2xl shadow-sm border border-slate-200 p-12 text-center">
							<i class="bi bi-journal-x text-6xl text-slate-300 mb-4"></i>
							<p class="text-slate-500 text-lg mb-2">暂无日记</p>
							<p class="text-slate-400 text-sm">成为第一个分享旅行故事的人吧！</p>
						</div>
					</div>

					<!-- 分页 -->
					<div v-if="pagination.total > pagination.limit" class="flex justify-center mt-6">
						<div class="flex items-center gap-2">
							<button 
								@click="loadPage(pagination.page - 1)"
								:disabled="pagination.page === 1"
								class="px-4 py-2 rounded-lg border border-slate-200 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors"
							>
								<i class="bi bi-chevron-left"></i> 上一页
							</button>
							<span class="px-4 py-2 text-sm text-slate-600">
								第 {{ pagination.page }} / {{ Math.ceil(pagination.total / pagination.limit) }} 页
							</span>
							<button 
								@click="loadPage(pagination.page + 1)"
								:disabled="pagination.page * pagination.limit >= pagination.total"
								class="px-4 py-2 rounded-lg border border-slate-200 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors"
							>
								下一页 <i class="bi bi-chevron-right"></i>
							</button>
						</div>
					</div>
				</div>

				<!-- 右侧：地图 + 侧边栏 -->
				<div class="space-y-4">
					<!-- 地图卡片 -->
					<div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden sticky top-20">
						<div class="px-4 py-3 border-b border-slate-100 flex items-center justify-between">
							<h3 class="font-semibold text-slate-900">
								<i class="bi bi-map mr-2 text-brand-500"></i>旅行足迹
							</h3>
							<button 
								@click="fitMapBounds"
								class="text-xs text-brand-500 hover:text-brand-600 transition-colors"
							>
								<i class="bi bi-arrows-fullscreen"></i> 适应视图
							</button>
						</div>
						<div class="relative">
							<BaseMap
								ref="communityMap"
								:height="400"
								:center="mapCenter"
								:zoom="10"
								:markers="mapMarkers"
								:selected-id="selectedDiaryId"
								@marker-click="onMarkerClick"
							/>
							<div class="absolute bottom-3 left-3 right-3 bg-white/90 backdrop-blur px-3 py-2 rounded-lg shadow text-xs text-slate-600">
								<i class="bi bi-pin-map-fill text-brand-500 mr-1"></i>
								{{ diaries.length }} 个地点
							</div>
						</div>
					</div>

					<!-- 快速导航 -->
					<div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-4">
						<h3 class="font-semibold text-slate-900 mb-3">
							<i class="bi bi-compass mr-2 text-brand-500"></i>快速导航
						</h3>
						<div class="space-y-2">
							<router-link 
								to="/" 
								class="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors text-sm text-slate-700 no-underline"
							>
								<span><i class="bi bi-map mr-2"></i>行程规划</span>
								<i class="bi bi-chevron-right text-xs text-slate-400"></i>
							</router-link>
							<router-link 
								to="/diary" 
								class="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors text-sm text-slate-700 no-underline"
							>
								<span><i class="bi bi-journal-text mr-2"></i>我的日记</span>
								<i class="bi bi-chevron-right text-xs text-slate-400"></i>
							</router-link>
							<router-link 
								v-if="isLoggedIn"
								to="/profile" 
								class="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors text-sm text-slate-700 no-underline"
							>
								<span><i class="bi bi-person mr-2"></i>个人中心</span>
								<i class="bi bi-chevron-right text-xs text-slate-400"></i>
							</router-link>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- 日记详情弹窗 -->
		<div 
			v-if="selectedDiary" 
			class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
			@click.self="selectedDiary = null"
		>
			<div class="bg-white rounded-3xl shadow-2xl max-w-3xl w-full max-h-[85vh] overflow-hidden">
				<!-- 弹窗头部 -->
				<div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between sticky top-0 bg-white z-10">
					<div class="flex items-center gap-3">
						<img 
							:src="selectedDiary.user_avatar || `https://ui-avatars.com/api/?name=${selectedDiary.username}&background=0ea5e9&color=fff`" 
							:alt="selectedDiary.username"
							class="w-10 h-10 rounded-full object-cover border-2 border-brand-100"
						>
						<div>
							<div class="font-semibold text-slate-900">{{ selectedDiary.username }}</div>
							<div class="text-xs text-slate-400">{{ formatDate(selectedDiary.date) }}</div>
						</div>
					</div>
					<button 
						@click="selectedDiary = null"
						class="w-8 h-8 rounded-full hover:bg-slate-100 transition-colors flex items-center justify-center text-slate-400 hover:text-slate-600"
					>
						<i class="bi bi-x-lg"></i>
					</button>
				</div>

				<!-- 弹窗内容 -->
				<div class="px-6 py-6 overflow-y-auto max-h-[calc(85vh-200px)]">
					<h2 class="text-2xl font-bold text-slate-900 mb-4">{{ selectedDiary.title }}</h2>
					
					<!-- 地点信息 -->
					<div v-if="selectedDiary.attraction_name || selectedDiary.latitude" class="mb-4 flex flex-wrap gap-2">
						<span v-if="selectedDiary.attraction_name" class="inline-flex items-center gap-1 px-3 py-1 bg-brand-50 text-brand-600 rounded-full text-sm font-medium">
							<i class="bi bi-geo-alt-fill"></i>
							{{ selectedDiary.attraction_name }}
						</span>
						<span v-if="selectedDiary.latitude" class="inline-flex items-center gap-1 px-3 py-1 bg-slate-100 text-slate-600 rounded-full text-xs font-mono">
							<i class="bi bi-crosshair"></i>
							{{ selectedDiary.latitude.toFixed(4) }}, {{ selectedDiary.longitude.toFixed(4) }}
						</span>
					</div>

					<!-- 日记内容 -->
					<div class="prose prose-slate max-w-none">
						<p class="text-slate-700 leading-relaxed whitespace-pre-wrap">{{ selectedDiary.content }}</p>
					</div>
				</div>

				<!-- 弹窗底部：互动 -->
				<div class="px-6 py-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
					<div class="flex items-center gap-4">
						<button class="flex items-center gap-1 px-3 py-2 rounded-lg hover:bg-white transition-colors text-slate-600 hover:text-rose-500">
							<i class="bi bi-heart text-lg"></i>
							<span class="text-sm">点赞</span>
						</button>
						<button class="flex items-center gap-1 px-3 py-2 rounded-lg hover:bg-white transition-colors text-slate-600 hover:text-brand-500">
							<i class="bi bi-chat text-lg"></i>
							<span class="text-sm">评论</span>
						</button>
					</div>
					<button class="flex items-center gap-1 px-3 py-2 rounded-lg hover:bg-white transition-colors text-slate-600 hover:text-brand-500">
						<i class="bi bi-bookmark text-lg"></i>
						<span class="text-sm">收藏</span>
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import BaseMap from '@/components/map/BaseMap.vue'
import api from '@/api'

export default {
	name: 'Community',
	components: { BaseMap },
	setup() {
		const store = useStore()
		const diaries = ref([])
		const loading = ref(false)
		const selectedDiary = ref(null)
		const selectedDiaryId = ref(null)
		const currentTab = ref('latest')
		const communityMap = ref(null)

		const pagination = ref({
			page: 1,
			limit: 20,
			total: 0
		})

		const stats = ref({
			totalDiaries: 0,
			totalUsers: 0
		})

		const tabs = [
			{ value: 'latest', label: '最新', icon: 'bi-clock-history' },
			{ value: 'hot', label: '热门', icon: 'bi-fire' },
			{ value: 'nearby', label: '附近', icon: 'bi-geo-alt' }
		]

		const isLoggedIn = computed(() => store.getters.isLoggedIn)

		const mapCenter = computed(() => {
			if (diaries.value.length > 0) {
				const firstDiary = diaries.value.find(d => d.latitude && d.longitude)
				if (firstDiary) {
					return [firstDiary.latitude, firstDiary.longitude]
				}
			}
			return [39.9042, 116.4074] // 默认北京
		})

		const mapMarkers = computed(() => {
			return diaries.value
				.filter(d => d.latitude && d.longitude)
				.map(d => ({
					id: d.diary_id,
					lat: d.latitude,
					lng: d.longitude,
					title: d.title,
					type: 'diary'
				}))
		})

		const loadDiaries = async (page = 1) => {
			loading.value = true
			try {
				console.log('[Community] 开始加载日记，页码:', page)
				const response = await api.get('/api/diaries/public', {
					params: { page, limit: pagination.value.limit }
				})
				
				console.log('[Community] API响应:', response.data)
				
				if (response.data.success) {
					diaries.value = response.data.data || []
					pagination.value.page = page
					pagination.value.total = response.data.total || 0
					stats.value.totalDiaries = response.data.total || 0
					
					// 统计用户数（去重）
					const uniqueUsers = new Set(diaries.value.map(d => d.user_id))
					stats.value.totalUsers = uniqueUsers.size
					
					console.log('[Community] 加载成功，日记数:', diaries.value.length)
				} else {
					console.warn('[Community] API返回success=false')
				}
			} catch (error) {
				console.error('[Community] 加载社区日记失败:', error)
				if (error.response) {
					console.error('[Community] 错误响应:', error.response.data)
				}
			} finally {
				loading.value = false
			}
		}

		const loadPage = (page) => {
			if (page < 1) return
			loadDiaries(page)
		}

		const selectDiary = (diary) => {
			selectedDiary.value = diary
			selectedDiaryId.value = diary.diary_id
			
			// 如果日记有坐标，地图移动到该位置
			if (diary.latitude && diary.longitude && communityMap.value && communityMap.value.map) {
				try {
					communityMap.value.map.panTo([diary.latitude, diary.longitude], { animate: false })
					communityMap.value.map.setZoom(14)
				} catch (e) {
					console.warn('地图移动失败', e)
				}
			}
		}

		const onMarkerClick = (markerId) => {
			const diary = diaries.value.find(d => d.diary_id === markerId)
			if (diary) {
				selectDiary(diary)
			}
		}

		const fitMapBounds = () => {
			if (communityMap.value && communityMap.value.map && mapMarkers.value.length > 0) {
				try {
					const bounds = mapMarkers.value.map(m => [m.lat, m.lng])
					communityMap.value.map.fitBounds(bounds, { padding: [50, 50], animate: false })
				} catch (e) {
					console.warn('地图适应边界失败', e)
				}
			}
		}

		const formatDate = (dateStr) => {
			if (!dateStr) return '未知时间'
			const date = new Date(dateStr)
			const now = new Date()
			const diff = now - date
			const days = Math.floor(diff / (1000 * 60 * 60 * 24))
			
			if (days === 0) return '今天'
			if (days === 1) return '昨天'
			if (days < 7) return `${days}天前`
			return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
		}

		onMounted(() => {
			loadDiaries()
		})

		return {
			diaries,
			loading,
			selectedDiary,
			selectedDiaryId,
			currentTab,
			pagination,
			stats,
			tabs,
			isLoggedIn,
			mapCenter,
			mapMarkers,
			communityMap,
			loadPage,
			selectDiary,
			onMarkerClick,
			fitMapBounds,
			formatDate
		}
	}
}
</script>

<style scoped>
.line-clamp-3 {
	display: -webkit-box;
	-webkit-line-clamp: 3;
	-webkit-box-orient: vertical;
	overflow: hidden;
}

.prose {
	max-width: none;
}

.prose p {
	margin-bottom: 1em;
}
</style>
