<template>
	<div class="min-h-[calc(100vh-64px)] bg-slate-50 py-8 px-4 lg:px-8">
		<!-- 面包屑导航 -->
		<div class="max-w-7xl mx-auto mb-4">
			<div class="flex items-center gap-2 text-sm text-slate-500">
				<router-link to="/community" class="hover:text-brand-500 transition-colors no-underline">
					<i class="bi bi-people mr-1"></i>旅行社区
				</router-link>
				<i class="bi bi-chevron-right text-xs"></i>
				<span class="text-slate-900 font-medium">
					<i class="bi bi-journal-text mr-1"></i>我的日记
				</span>
			</div>
		</div>

		<div class="max-w-7xl mx-auto space-y-6">
			<div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
				<!-- 左侧：地图 + 日记信息 -->
				<div class="xl:col-span-2 space-y-6">
					<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
						<div class="bg-gradient-to-br from-brand-500 to-brand-600 text-white rounded-3xl p-5 shadow-lg">
							<p class="text-sm/relaxed text-white/70">累计日记</p>
							<p class="text-3xl font-bold">{{ diaryStats.total }}</p>
							<p class="text-xs text-white/70 mt-1">今日新增 {{ diaryStats.today }}</p>
						</div>
						<div class="bg-white rounded-3xl p-5 shadow-lg border border-slate-100">
							<p class="text-sm text-slate-500">定位记录</p>
							<p class="text-3xl font-bold text-slate-900">{{ diaryStats.withLocation }}</p>
							<p class="text-xs text-slate-400 mt-1">含坐标的行程</p>
						</div>
						<div class="bg-white rounded-3xl p-5 shadow-lg border border-slate-100">
							<p class="text-sm text-slate-500">最近记录</p>
							<p class="text-lg font-semibold text-slate-900">{{ diaryStats.latestTitle }}</p>
							<p class="text-xs text-slate-400 mt-1">{{ diaryStats.latestDate }}</p>
						</div>
					</div>

					<div class="bg-white rounded-[32px] shadow-xl border border-slate-100 overflow-hidden">
						<div class="flex flex-wrap items-center justify-between gap-3 px-6 py-4 border-b border-slate-100">
							<div>
								<h3 class="text-lg font-semibold text-slate-900">旅途地图</h3>
								<p class="text-sm text-slate-500">在地图上选择坐标或查看日记足迹。</p>
							</div>
							<div class="flex flex-wrap gap-2">
								<button class="px-3 py-2 rounded-full text-sm font-medium border border-slate-200 text-slate-600 hover:border-brand-500 hover:text-brand-600 transition" @click="useMyLocation">
									<i class="bi bi-geo"></i> 定位到我
								</button>
								<button class="px-3 py-2 rounded-full text-sm font-medium border border-slate-200 text-slate-600 hover:border-rose-300 hover:text-rose-500 transition" :disabled="!selectedId" @click="deleteDiaryEntry">
									<span v-if="deleting" class="inline-flex items-center gap-1"><span class="animate-spin w-3 h-3 border-2 border-rose-200 border-t-transparent rounded-full"></span>处理中</span>
									<span v-else><i class="bi bi-trash"></i> 删除选中</span>
								</button>
							</div>
						</div>
						<div class="relative">
							<BaseMap
								ref="diaryMap"
								:height="520"
								:center="mapCenter"
								:zoom="12"
								:markers="markers"
								:selected-id="selectedId"
								@marker-click="onMarkerClick"
								@location-update="onLocationUpdate"
								@map-click="onMapClick"
							/>
							<div class="absolute bottom-5 right-6 bg-white/90 backdrop-blur px-4 py-2 rounded-full shadow flex items-center gap-2 text-xs text-slate-600">
								<i class="bi bi-info-circle"></i>
								<span>在地图上点击即可为日记拾取坐标</span>
							</div>
						</div>
					</div>

					<div class="bg-white rounded-[32px] shadow-xl border border-slate-100">
						<div class="px-6 py-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
							<div>
								<h3 class="text-lg font-semibold text-slate-900">日记时间线</h3>
								<p class="text-sm text-slate-500">按照时间排序的记忆片段，点击即可在地图上定位。</p>
							</div>
							<div class="flex items-center gap-2 text-xs text-slate-400">
								<i class="bi bi-dot"></i> 共 {{ diaries.length }} 篇
							</div>
						</div>
						<div class="max-h-[420px] overflow-y-auto divide-y divide-slate-100">
							<button v-for="d in diaries" :key="d.id"
								class="w-full text-left px-6 py-4 transition relative"
								:class="selectedId === d.id ? 'bg-brand-50/80' : 'hover:bg-slate-50'"
								@click="selectDiary(d)">
								<div class="flex items-start justify-between gap-3">
									<div>
										<p class="font-semibold text-slate-900 line-clamp-1">{{ d.title }}</p>
										<p class="text-xs text-slate-400 mt-1 flex items-center gap-2">
											<span class="inline-flex items-center gap-1"><i class="bi bi-calendar3"></i>{{ d.date || '-' }}</span>
											<span class="inline-flex items-center gap-1"><i class="bi bi-geo-alt"></i>{{ d.attraction_name || '未关联景点' }}</span>
										</p>
										<p class="text-sm text-slate-500 mt-2 line-clamp-2">{{ d.snippet || d.content || '（无内容）' }}</p>
									</div>
									<div class="text-xs font-medium text-slate-400">{{ d.username || '匿名用户' }}</div>
								</div>
								<span class="absolute top-4 right-6 inline-flex items-center gap-1 text-[10px] font-semibold" :class="selectedId === d.id ? 'text-brand-600' : 'text-slate-300'">
									<i class="bi" :class="selectedId === d.id ? 'bi-pin-angle-fill' : 'bi-pin'">
									</i>
									{{ selectedId === d.id ? '正在查看' : '点击定位' }}
								</span>
							</button>
							<div v-if="diaries.length === 0" class="px-6 py-10 text-center text-slate-400 text-sm">
								<i class="bi bi-journal-plus text-3xl mb-2 block"></i>
								暂无日记，开始记录吧！
							</div>
						</div>
						<div v-if="selectedDiary" class="px-6 py-5 bg-slate-50 border-t border-slate-100">
							<p class="text-xs font-medium text-slate-400 uppercase tracking-[0.2em] mb-2">展开阅读</p>
							<h4 class="text-xl font-semibold text-slate-900 mb-2">{{ selectedDiary.title }}</h4>
							<p class="text-sm text-slate-500 mb-2 flex flex-wrap gap-4">
								<span class="inline-flex items-center gap-1"><i class="bi bi-calendar3"></i>{{ selectedDiary.date || '-' }}</span>
								<span class="inline-flex items-center gap-1"><i class="bi bi-person-circle"></i>{{ selectedDiary.username || '匿名用户' }}</span>
								<span class="inline-flex items-center gap-1"><i class="bi bi-geo-alt-fill"></i>{{ selectedDiary.attraction_name || '未关联景点' }}</span>
							</p>
							<p class="text-base leading-7 text-slate-700 whitespace-pre-line mb-4">{{ selectedDiary.content || selectedDiary.snippet }}</p>
							
							<!-- 点赞和评论区域 -->
							<div class="border-t border-slate-200 pt-4 space-y-4">
								<!-- 点赞按钮 -->
								<div class="flex items-center gap-3">
									<button 
										@click="toggleDiaryLike" 
										:disabled="!userId"
										class="inline-flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors"
										:class="selectedDiary.is_liked ? 'bg-rose-50 border-rose-300 text-rose-600' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'">
										<i class="bi" :class="selectedDiary.is_liked ? 'bi-heart-fill' : 'bi-heart'"></i>
										<span class="font-medium">{{ selectedDiary.is_liked ? '已点赞' : '点赞' }}</span>
										<span class="text-sm">{{ selectedDiary.like_count || 0 }}</span>
									</button>
									<span class="text-sm text-slate-400">
										<i class="bi bi-chat-dots"></i> {{ (selectedDiary.comments || []).length }} 条评论
									</span>
								</div>

								<!-- 评论列表 -->
								<div class="space-y-3">
									<p class="text-sm font-semibold text-slate-700">评论 ({{ (selectedDiary.comments || []).length }})</p>
									<div v-if="(selectedDiary.comments || []).length === 0" class="text-center py-6 text-slate-400 text-sm">
										<i class="bi bi-chat-left-text text-2xl mb-2 block"></i>
										暂无评论，快来抢沙发！
									</div>
									<div v-else class="space-y-2 max-h-60 overflow-y-auto">
										<div v-for="comment in selectedDiary.comments" :key="comment.comment_id" 
											class="bg-white rounded-lg p-3 border border-slate-100">
											<div class="flex items-start justify-between mb-1">
												<span class="text-sm font-semibold text-slate-800">{{ comment.nickname || comment.username }}</span>
												<span class="text-xs text-slate-400">{{ comment.created_at }}</span>
											</div>
											<p class="text-sm text-slate-600">{{ comment.content }}</p>
										</div>
									</div>
								</div>

								<!-- 添加评论 -->
								<div class="flex gap-2">
									<input 
										v-model.trim="commentInput" 
										type="text" 
										:disabled="!userId"
										placeholder="写下你的评论..."
										@keyup.enter="submitComment"
										class="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
									/>
									<button 
										@click="submitComment" 
										:disabled="!userId || !commentInput || commenting"
										class="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
										<span v-if="commenting" class="inline-flex items-center gap-1">
											<span class="animate-spin w-3 h-3 border-2 border-white/40 border-t-transparent rounded-full"></span>
											发送中
										</span>
										<span v-else>发送</span>
									</button>
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- 右侧：创建面板 -->
				<div class="space-y-6">
					<div class="bg-white rounded-[32px] shadow-xl border border-slate-100 p-6 space-y-5">
						<div class="flex items-start justify-between gap-3">
							<div>
								<p class="text-sm uppercase tracking-[0.3em] text-slate-400">NEW ENTRY</p>
								<h3 class="text-2xl font-semibold text-slate-900">写下新的旅程</h3>
								<p class="text-sm text-slate-500">支持绑定地图坐标与景点，方便在智能行程中回溯。</p>
							</div>
							<div class="flex gap-2">
								<button class="px-3 py-2 rounded-full text-xs font-semibold border border-slate-200 text-slate-600 hover:border-brand-500 hover:text-brand-600" @click="useMyLocation" :disabled="!userId">
									使用当前位置
								</button>
								<button class="px-3 py-2 rounded-full text-xs font-semibold border border-slate-200 text-slate-600 hover:border-slate-400" @click="clearForm">清空</button>
							</div>
						</div>
						<div class="space-y-4">
							<div>
								<label class="text-xs font-semibold text-slate-500">标题</label>
								<input v-model.trim="form.title" type="text" :disabled="!userId" placeholder="给旅程起个名字" class="mt-1 w-full rounded-2xl border border-slate-200 px-4 py-2.5 text-sm focus:border-brand-500 focus:ring-2 focus:ring-brand-100" />
							</div>
							<div>
								<label class="text-xs font-semibold text-slate-500">内容</label>
								<textarea v-model.trim="form.content" rows="5" :disabled="!userId" placeholder="记录此刻心情、天气、同行的伙伴…" class="mt-1 w-full rounded-2xl border border-slate-200 px-4 py-2.5 text-sm focus:border-brand-500 focus:ring-2 focus:ring-brand-100"></textarea>
							</div>
							<div>
								<div class="flex items-center justify-between">
									<label class="text-xs font-semibold text-slate-500">关联景点</label>
									<button class="text-xs text-brand-600" type="button" :disabled="attractionLoading" @click="refreshAttractions">
										<span v-if="attractionLoading" class="inline-flex items-center gap-1"><span class="animate-spin w-3 h-3 border-2 border-brand-200 border-t-transparent rounded-full"></span>获取中</span>
										<span v-else>刷新列表</span>
									</button>
								</div>
								<select v-model="form.attraction_id" class="mt-1 w-full rounded-2xl border border-slate-200 px-4 py-2.5 text-sm bg-white focus:border-brand-500" @change="onAttractionChange">
									<option :value="null">未选择</option>
									<option v-for="place in attractions" :key="place.id" :value="place.id">{{ place.name }}</option>
								</select>
								<p class="text-xs text-slate-400 mt-1">选择后会自动填入该景点坐标。</p>
							</div>
							<div class="grid grid-cols-2 gap-3">
								<div>
									<label class="text-xs font-semibold text-slate-500">纬度</label>
									<input v-model.number="form.latitude" type="number" step="0.000001" :disabled="!userId" class="mt-1 w-full rounded-2xl border border-slate-200 px-3 py-2 text-sm bg-slate-50">
								</div>
								<div>
									<label class="text-xs font-semibold text-slate-500">经度</label>
									<input v-model.number="form.longitude" type="number" step="0.000001" :disabled="!userId" class="mt-1 w-full rounded-2xl border border-slate-200 px-3 py-2 text-sm bg-slate-50">
								</div>
							</div>
						</div>
						<div class="pt-2 flex flex-col gap-3">
							<p class="text-xs text-slate-400">提示：可以直接在左侧地图点击拾取经纬度。</p>
							<button class="w-full rounded-2xl bg-brand-600 text-white py-3 text-sm font-semibold flex items-center justify-center gap-2 shadow-lg shadow-brand-600/20 disabled:opacity-50" :disabled="submitting || !userId" @click="submitDiary">
								<span v-if="submitting" class="inline-flex items-center gap-2"><span class="animate-spin w-4 h-4 border-2 border-white/40 border-t-transparent rounded-full"></span>发布中</span>
								<span v-else><i class="bi bi-send"></i> 发布日记</span>
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import BaseMap from '@/components/map/BaseMap.vue'
import { fetchDiaries, fetchDiaryDetail, createDiary, deleteDiary as removeDiary } from '@/api/diary'
import { fetchComments, toggleLike, addComment } from '@/api/community'
import { fetchAllPlaces } from '@/api/place'
import { me } from '@/api/auth'

export default {
	name: 'TravelDiary',
	components: { BaseMap },
	data() {
		return {
			userId: null,
			diaries: [],
			selectedId: null,
			selectedDiary: null,
			submitting: false,
			draftCoord: null,
			commentInput: '',
			commenting: false,
			deleting: false,
			form: {
				title: '',
				content: '',
				attraction_id: null,
				latitude: null,
				longitude: null
			},
			mapCenter: [39.9042, 116.4074],
			attractions: [],
			attractionLoading: false
		}
	},
	computed: {
		markers() {
			const arr = (this.diaries || [])
				.filter(d => typeof d.latitude === 'number' && typeof d.longitude === 'number')
				.map(d => ({
					id: d.id,
					name: d.title,
					latitude: d.latitude,
					longitude: d.longitude,
					popup: `${d.title}${d.date ? ' · ' + d.date : ''}${d.attraction_name ? '\n' + d.attraction_name : ''}`
				}))
			if (this.draftCoord && typeof this.draftCoord.latitude === 'number' && typeof this.draftCoord.longitude === 'number') {
				arr.push({
					id: '__draft__',
					name: '新日记位置',
					latitude: this.draftCoord.latitude,
					longitude: this.draftCoord.longitude,
					popup: '新日记（未保存）'
				})
			}
			return arr
		},
		diaryStats() {
			const list = Array.isArray(this.diaries) ? this.diaries : []
			const total = list.length
			const withLocation = list.filter(d => typeof d.latitude === 'number' && typeof d.longitude === 'number').length
			const today = (() => {
				const todayStr = new Date().toISOString().slice(0, 10)
				return list.filter(d => d?.date && String(d.date).slice(0, 10) === todayStr).length
			})()
			const sorted = [...list].sort((a, b) => {
				const aTime = a?.date ? new Date(a.date).getTime() : 0
				const bTime = b?.date ? new Date(b.date).getTime() : 0
				return bTime - aTime
			})
			const latest = sorted[0]
			return {
				total,
				withLocation,
				today,
				latestTitle: latest?.title || '暂无记录',
				latestDate: latest?.date || '等待记录'
			}
		}
	},
	async mounted() {
		await this.loadCurrentUser()
		if (this.userId) {
			await Promise.all([this.loadDiaries(), this.loadAttractions()])
		}
	},
	methods: {
		async loadCurrentUser() {
			try {
				const { data } = await me()
				if (data && data.status === 'success' && data.data) {
					// 后端返回的是 id，不是 user_id
					this.userId = data.data.id || data.data.user_id
					console.log('用户已登录:', this.userId)
				} else {
					// 未登录，但不立即跳转，让用户可以查看页面
					console.warn('用户未登录')
					this.userId = null
				}
			} catch (e) {
				console.error('获取用户信息失败', e)
				// 网络错误或其他问题，不强制跳转
				this.userId = null
			}
		},
		async loadAttractions() {
			this.attractionLoading = true
			try {
				const rows = await fetchAllPlaces()
				this.attractions = rows.map(r => ({
					id: r.attraction_id || r.id,
					name: r.name,
					latitude: typeof r.latitude === 'number' ? r.latitude : null,
					longitude: typeof r.longitude === 'number' ? r.longitude : null
				}))
				if (this.form.attraction_id) this.onAttractionChange()
			} catch (e) {
				console.warn('加载景点列表失败', e)
			} finally {
				this.attractionLoading = false
			}
		},
		refreshAttractions() {
			this.loadAttractions()
		},
		onAttractionChange() {
			if (this.form.attraction_id == null || this.form.attraction_id === '') {
				return
			}
			const selected = this.attractions.find(p => String(p.id) === String(this.form.attraction_id))
			if (selected && selected.latitude != null && selected.longitude != null) {
				this.form.latitude = selected.latitude
				this.form.longitude = selected.longitude
				this.draftCoord = { latitude: selected.latitude, longitude: selected.longitude }
				this.mapCenter = [selected.latitude, selected.longitude]
			}
		},
		async loadDiaries() {
			if (!this.userId) return []
			const params = { user_id: this.userId }
			try {
				const list = await fetchDiaries(params)
				this.diaries = Array.isArray(list) ? list : []
				if (this.diaries.length) {
					this.selectedId = this.diaries[0].id
					this.selectedDiary = this.diaries[0]
					const firstWithCoord = this.diaries.find(d => typeof d.latitude === 'number' && typeof d.longitude === 'number')
					if (firstWithCoord) this.mapCenter = [firstWithCoord.latitude, firstWithCoord.longitude]
				} else {
					this.selectedId = null
					this.selectedDiary = null
				}
				return this.diaries
			} catch (e) {
				console.error('加载日记失败', e)
				this.diaries = []
				this.selectedId = null
				this.selectedDiary = null
				return []
			}
		},
		async submitDiary() {
			if (!this.userId) {
				// 用户未登录，页面上已有提示条
				return
			}
			if (!this.form.title || !this.form.content) return
			this.submitting = true
			try {
				const payload = {
					user_id: this.userId,
					title: this.form.title,
					content: this.form.content,
					attraction_id: this.form.attraction_id,
					latitude: this.form.latitude ?? this.draftCoord?.latitude,
					longitude: this.form.longitude ?? this.draftCoord?.longitude
				}
				const created = await createDiary(payload)
				if (created) {
					const newId = created.id ?? created.diary_id
					await this.loadDiaries()
					if (newId) {
						const found = this.diaries.find(d => String(d.id) === String(newId))
						if (found) {
							this.selectedId = found.id
							this.selectedDiary = found
							if (typeof found.latitude === 'number' && typeof found.longitude === 'number') {
								this.mapCenter = [found.latitude, found.longitude]
							}
						}
					}
					this.clearForm()
					this.draftCoord = null
				}
			} catch (e) {
				console.error('创建日记失败', e)
			} finally {
				this.submitting = false
			}
		},
		clearForm() {
			this.form.title = ''
			this.form.content = ''
			this.form.attraction_id = null
			this.form.latitude = null
			this.form.longitude = null
		},
		async selectDiary(d) {
			this.selectedId = d.id
			// 获取详细信息
			try {
				const detail = await fetchDiaryDetail(d.id)
				this.selectedDiary = detail || d
				// 加载评论
				await this.loadComments()
			} catch (e) {
				console.error('获取日记详情失败', e)
				this.selectedDiary = d
			}
		},
		onMarkerClick(d) {
			if (!d) return
			const found = this.diaries.find(x => String(x.id) === String(d.id))
			this.selectedId = d.id
			this.selectedDiary = found || d
		},
		onLocationUpdate(pos) {
			if (!pos) return
			this.form.latitude = pos.latitude
			this.form.longitude = pos.longitude
		},
		useMyLocation() {
			this.$refs.diaryMap?.locateUser?.(false)
		},
		onMapClick(pt) {
			if (!pt) return
			this.draftCoord = { latitude: pt.latitude, longitude: pt.longitude }
			this.form.latitude = pt.latitude
			this.form.longitude = pt.longitude
			// 平滑移动中心
			this.mapCenter = [pt.latitude, pt.longitude]
		},
		async deleteDiaryEntry() {
			if (!this.selectedId || this.deleting) return
			if (typeof window !== 'undefined' && !window.confirm('确定删除当前选中日记吗？')) return
			this.deleting = true
			try {
				const ok = await removeDiary(this.selectedId)
				if (ok) {
					this.diaries = this.diaries.filter(d => String(d.id) !== String(this.selectedId))
					this.selectedId = this.diaries[0]?.id ?? null
					this.selectedDiary = this.diaries[0] ?? null
				}
			} catch (e) {
				console.error('删除日记失败', e)
			} finally {
				this.deleting = false
			}
		},
		// 加载评论
		async loadComments() {
			if (!this.selectedDiary) return
			try {
				const comments = await fetchComments(this.selectedDiary.id)
				this.selectedDiary.comments = comments
			} catch (e) {
				console.error('加载评论失败', e)
				this.selectedDiary.comments = []
			}
		},
		// 点赞/取消点赞
		async toggleDiaryLike() {
			if (!this.userId || !this.selectedDiary) return
			try {
				const result = await toggleLike(this.selectedDiary.id)
				this.selectedDiary.like_count = result.likeCount
				this.selectedDiary.is_liked = result.action === 'liked'
			} catch (e) {
				console.error('点赞操作失败', e)
			}
		},
		// 提交评论
		async submitComment() {
			if (!this.userId || !this.selectedDiary || !this.commentInput) return
			this.commenting = true
			try {
				const comment = await addComment(this.selectedDiary.id, this.commentInput)
				// 添加到评论列表
				if (!this.selectedDiary.comments) {
					this.selectedDiary.comments = []
				}
				this.selectedDiary.comments.push(comment)
				this.commentInput = ''
			} catch (e) {
				console.error('添加评论失败', e)
			} finally {
				this.commenting = false
			}
		}
	}
}
</script>


