<template>
	<div class="container py-3">
		<!-- 未登录提示 -->
		<div v-if="!userId" class="alert alert-warning d-flex align-items-center justify-content-between" role="alert">
			<div>
				<i class="bi bi-exclamation-triangle-fill me-2"></i>
				您还未登录，请先登录后才能创建和查看日记
			</div>
			<router-link to="/login" class="btn btn-sm btn-primary">前往登录</router-link>
		</div>
		
		<div class="row g-3">
			<div class="col-12 col-lg-5">
				<div class="card mb-3">
					<div class="card-header d-flex align-items-center justify-content-between">
						<strong>新增日记</strong>
						<div class="btn-group">
							<button class="btn btn-sm btn-outline-primary" @click="useMyLocation" :disabled="!userId">使用当前位置</button>
							<button class="btn btn-sm btn-outline-secondary" @click="clearForm">清空</button>
						</div>
					</div>
					<div class="card-body">
						<div class="mb-2">
							<label class="form-label">标题</label>
							<input v-model.trim="form.title" type="text" class="form-control" placeholder="请输入标题" :disabled="!userId" />
						</div>
						<div class="mb-2">
							<label class="form-label">内容</label>
							<textarea v-model.trim="form.content" class="form-control" rows="5" placeholder="记录你的旅途…" :disabled="!userId"></textarea>
						</div>
						<div class="mb-2">
							<label class="form-label">关联景点</label>
							<div class="input-group">
								<select v-model="form.attraction_id" class="form-select" @change="onAttractionChange">
									<option :value="null">未选择</option>
									<option
										v-for="place in attractions"
										:key="place.id"
										:value="place.id"
									>
										{{ place.name }}
									</option>
								</select>
								<button class="btn btn-outline-secondary" type="button" :disabled="attractionLoading" @click="refreshAttractions">
									<span v-if="attractionLoading" class="spinner-border spinner-border-sm me-1"></span>刷新
								</button>
							</div>
							<div class="form-text text-muted">选择景点后可自动带入该景点的坐标。</div>
						</div>
						<div class="row g-2">
							<div class="col-6">
								<label class="form-label">纬度</label>
								<input v-model.number="form.latitude" type="number" step="0.000001" class="form-control" :disabled="!userId" />
							</div>
							<div class="col-6">
								<label class="form-label">经度</label>
								<input v-model.number="form.longitude" type="number" step="0.000001" class="form-control" :disabled="!userId" />
							</div>
						</div>
						<div class="form-text text-muted">可直接在右侧地图点击选点，坐标会自动填入。</div>
					</div>
					<div class="card-footer d-flex justify-content-end gap-2">
						<button class="btn btn-primary" :disabled="submitting || !userId" @click="submitDiary">
							<span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>提交
						</button>
					</div>
				</div>

				<div class="card">
					<div class="card-header d-flex justify-content-between align-items-center">
						<span>我的日记 ({{ diaries.length }})</span>
						<button
							class="btn btn-sm btn-outline-danger"
							:disabled="!selectedId || deleting"
							@click="deleteDiaryEntry"
						>
							<span v-if="deleting" class="spinner-border spinner-border-sm me-1"></span>删除
						</button>
					</div>
					<ul class="list-group list-group-flush list-scroll">
						<li v-for="d in diaries" :key="d.id" class="list-group-item list-group-item-action"
								:class="{ active: selectedId === d.id }" @click="selectDiary(d)">
							<div class="d-flex justify-content-between align-items-center">
								<strong>{{ d.title }}</strong>
								<small class="text-muted">{{ d.date || '-' }}</small>
							</div>
							<div class="text-muted small mb-1">
								<i class="bi bi-person-circle"></i> {{ d.username || '匿名用户' }}
								<span class="ms-2"><i class="bi bi-geo-alt"></i> {{ d.attraction_name || '未关联景点' }}</span>
							</div>
							<div class="text-muted small ellipsis-2">
								{{ d.snippet || d.content || '（无内容）' }}
							</div>
						</li>
						<li v-if="diaries.length === 0" class="list-group-item text-muted">暂无日记</li>
					</ul>
					<div v-if="selectedDiary" class="card-body border-top">
						<h6 class="mb-2">{{ selectedDiary.title }}</h6>
						<div class="text-muted small mb-2">
							<i class="bi bi-calendar3"></i> {{ selectedDiary.date || '-' }}
							<span class="ms-3"><i class="bi bi-person-circle"></i> {{ selectedDiary.username || '匿名用户' }}</span>
						</div>
						<div class="text-primary small mb-2">
							<i class="bi bi-geo-alt-fill"></i> {{ selectedDiary.attraction_name || '未关联景点' }}
						</div>
						<p class="mb-0 white-prewrap">{{ selectedDiary.content || selectedDiary.snippet }}</p>
					</div>
				</div>
			</div>

			<div class="col-12 col-lg-7">
				<BaseMap
					ref="diaryMap"
					:height="720"
					:center="mapCenter"
					:zoom="12"
					:markers="markers"
					:selected-id="selectedId"
					@marker-click="onMarkerClick"
					@location-update="onLocationUpdate"
					@map-click="onMapClick"
				/>
			</div>
		</div>
	</div>
</template>

<script>
import BaseMap from '@/components/map/BaseMap.vue'
import { fetchDiaries, fetchDiaryDetail, createDiary, deleteDiary as removeDiary } from '@/api/diary'
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
					this.userId = data.data.user_id
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
			// 若需要获取更详细信息
			try {
				const detail = await fetchDiaryDetail(d.id)
				this.selectedDiary = detail || d
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
		}
	}
}
</script>

<style scoped>
.list-scroll { max-height: calc(100vh - 280px); overflow: auto; }
.ellipsis-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.white-prewrap { white-space: pre-wrap; }
</style>
