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
									<button 
										@click.stop="handleLike(diary)" 
										class="hover:text-rose-500 transition-colors"
										:class="{ 'text-rose-500': likedDiaries.has(diary.diary_id) }"
									>
										<i class="bi" :class="likedDiaries.has(diary.diary_id) ? 'bi-heart-fill' : 'bi-heart'"></i>
										<span class="ml-1">{{ diary.like_count || 0 }}</span>
									</button>
									<button class="hover:text-brand-500 transition-colors">
										<i class="bi bi-chat"></i>
										<span class="ml-1">{{ diary.comment_count || 0 }}</span>
									</button>
									<button class="hover:text-brand-500 transition-colors">
										<i class="bi bi-eye"></i>
										<span class="ml-1">{{ diary.view_count || 0 }}</span>
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
				<div class="px-6 py-4 border-t border-slate-100 bg-slate-50">
					<div class="flex items-center justify-between mb-3">
						<div class="flex items-center gap-4">
							<button 
								@click="handleLike(selectedDiary)" 
								class="flex items-center gap-1 px-3 py-2 rounded-lg hover:bg-white transition-colors"
								:class="likedDiaries.has(selectedDiary.diary_id) ? 'text-rose-500' : 'text-slate-600 hover:text-rose-500'"
							>
								<i class="bi text-lg" :class="likedDiaries.has(selectedDiary.diary_id) ? 'bi-heart-fill' : 'bi-heart'"></i>
								<span class="text-sm">{{ likedDiaries.has(selectedDiary.diary_id) ? '已点赞' : '点赞' }} ({{ selectedDiary.like_count || 0 }})</span>
							</button>
							<button 
								@click="toggleComments" 
								class="flex items-center gap-1 px-3 py-2 rounded-lg hover:bg-white transition-colors text-slate-600 hover:text-brand-500"
							>
								<i class="bi bi-chat text-lg"></i>
								<span class="text-sm">评论 ({{ selectedDiary.comment_count || 0 }})</span>
							</button>
						</div>
						<button class="flex items-center gap-1 px-3 py-2 rounded-lg hover:bg-white transition-colors text-slate-600 hover:text-brand-500">
							<i class="bi bi-bookmark text-lg"></i>
							<span class="text-sm">收藏</span>
						</button>
					</div>

					<!-- 评论区域 -->
					<div v-if="showComments" class="mt-4 pt-4 border-t border-slate-200">
						<!-- 评论输入框 -->
						<div v-if="isLoggedIn" class="mb-4">
							<textarea 
								v-model="newComment"
								rows="3" 
								class="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 resize-none"
								placeholder="写下你的评论..."
							></textarea>
							<div class="flex justify-end mt-2">
								<button 
									@click="submitComment"
									class="px-4 py-2 bg-brand-500 text-white rounded-lg hover:bg-brand-600 transition-colors text-sm font-medium"
									:disabled="!newComment.trim()"
								>
									发表评论
								</button>
							</div>
						</div>
						<div v-else class="mb-4 p-3 bg-blue-50 text-blue-600 rounded-lg text-sm text-center">
							<i class="bi bi-info-circle mr-1"></i>
							请<router-link to="/login" class="underline font-medium">登录</router-link>后发表评论
						</div>

						<!-- 评论列表 -->
						<div class="space-y-3 max-h-60 overflow-y-auto">
							<div v-if="comments.length === 0" class="text-center py-4 text-slate-400 text-sm">
								<i class="bi bi-chat-square-text text-2xl mb-2 block"></i>
								暂无评论，快来沙发吧！
							</div>
							<div 
								v-for="comment in comments" 
								:key="comment.comment_id"
								class="flex gap-3 p-3 bg-white rounded-lg"
							>
								<img 
									:src="comment.avatar_url || `https://ui-avatars.com/api/?name=${comment.username}&background=0ea5e9&color=fff`" 
									:alt="comment.username"
									class="w-8 h-8 rounded-full object-cover flex-shrink-0"
								>
								<div class="flex-1 min-w-0">
									<div class="flex items-center gap-2 mb-1">
										<span class="font-medium text-sm text-slate-900">{{ comment.nickname || comment.username }}</span>
										<span class="text-xs text-slate-400">{{ formatDate(comment.created_at) }}</span>
									</div>
									<p class="text-sm text-slate-700">{{ comment.content }}</p>
								</div>
							</div>
						</div>
					</div>
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
import { toggleLike, fetchComments, addComment, incrementView } from '@/api/community'

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
		const comments = ref([])
		const newComment = ref('')
		const likedDiaries = ref(new Set())
		const showComments = ref(false)

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

		const isLoggedIn = computed(() => store.getters['auth/isLoggedIn'])

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
				const response = await api.get('/api/community/diaries', {
					params: { page, limit: pagination.value.limit }
				})
				
				console.log('[Community] API响应:', response.data)
				
				if (response.data.success) {
					diaries.value = response.data.diaries || []
					pagination.value = response.data.pagination || { page, limit: pagination.value.limit, total: 0 }
					stats.value.totalDiaries = response.data.pagination?.total || 0
					
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

	const selectDiary = async (diary) => {
			selectedDiary.value = diary
			selectedDiaryId.value = diary.diary_id
			showComments.value = false
			comments.value = []
			newComment.value = ''
			
			// 如果日记有坐标，地图移动到该位置
			
			// 增加浏览量
			try {
				const newViewCount = await incrementView(diary.diary_id)
				// 更新本地显示的浏览量
				diary.view_count = newViewCount
				if (selectedDiary.value.diary_id === diary.diary_id) {
					selectedDiary.value.view_count = newViewCount
				}
			} catch (error) {
				console.error('更新浏览量失败:', error)
			}
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

		// 点赞/取消点赞
		const handleLike = async (diary) => {
			console.log('[Community handleLike] isLoggedIn:', isLoggedIn.value)
			console.log('[Community handleLike] store state:', store.state.auth)
			
			if (!isLoggedIn.value) {
				alert('请先登录')
				return
			}
			try {
				console.log('[Community handleLike] 开始点赞，diary_id:', diary.diary_id)
				const result = await toggleLike(diary.diary_id)
				console.log('[Community handleLike] 点赞结果:', result)
				// 更新本地状态
				if (result.action === 'liked') {
					likedDiaries.value.add(diary.diary_id)
					diary.like_count = (diary.like_count || 0) + 1
				} else {
					likedDiaries.value.delete(diary.diary_id)
					diary.like_count = Math.max(0, (diary.like_count || 0) - 1)
				}
				// 如果当前打开的是这个日记，也更新选中的日记
				if (selectedDiary.value && selectedDiary.value.diary_id === diary.diary_id) {
					selectedDiary.value.like_count = diary.like_count
				}
			} catch (error) {
				console.error('点赞失败:', error)
				alert(error.message || '点赞失败')
			}
		}

		// 加载评论
		const loadComments = async (diaryId) => {
			try {
				comments.value = await fetchComments(diaryId)
			} catch (error) {
				console.error('加载评论失败:', error)
				comments.value = []
			}
		}

		// 提交评论
		const submitComment = async () => {
			if (!isLoggedIn.value) {
				alert('请先登录')
				return
			}
			if (!newComment.value.trim()) {
				alert('评论内容不能为空')
				return
			}
			if (!selectedDiary.value) return

			try {
				await addComment(selectedDiary.value.diary_id, newComment.value)
				newComment.value = ''
				// 重新加载评论
				await loadComments(selectedDiary.value.diary_id)
				// 更新评论数
				selectedDiary.value.comment_count = (selectedDiary.value.comment_count || 0) + 1
				// 更新列表中的评论数
				const diary = diaries.value.find(d => d.diary_id === selectedDiary.value.diary_id)
				if (diary) {
					diary.comment_count = selectedDiary.value.comment_count
				}
		} catch (error) {
			console.error('评论失败:', error)
			alert(error.message || '评论失败')
		}
	}

		// 切换评论显示
		const toggleComments = () => {
			showComments.value = !showComments.value
			if (showComments.value && selectedDiary.value) {
				loadComments(selectedDiary.value.diary_id)
			}
		}

		onMounted(() => {
			console.log('[Community onMounted] Vuex auth state:', store.state.auth)
			console.log('[Community onMounted] isLoggedIn:', isLoggedIn.value)
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
			comments,
			newComment,
			likedDiaries,
			showComments,
			loadPage,
			selectDiary,
			onMarkerClick,
			fitMapBounds,
			formatDate,
			handleLike,
			loadComments,
			submitComment,
			toggleComments
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
