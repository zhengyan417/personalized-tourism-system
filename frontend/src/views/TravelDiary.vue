<template>
	<div class="container py-3">
		<div class="row g-3">
			<div class="col-12 col-lg-5">
				<div class="card mb-3">
					<div class="card-header d-flex align-items-center justify-content-between">
						<strong>新增日记</strong>
						<div class="btn-group">
							<button class="btn btn-sm btn-outline-primary" @click="useMyLocation">使用当前位置</button>
							<button class="btn btn-sm btn-outline-secondary" @click="clearForm">清空</button>
						</div>
					</div>
					<div class="card-body">
						<div class="mb-2">
							<label class="form-label">标题</label>
							<input v-model.trim="form.title" type="text" class="form-control" placeholder="请输入标题" />
						</div>
						<div class="mb-2">
							<label class="form-label">内容</label>
							<textarea v-model.trim="form.content" class="form-control" rows="5" placeholder="记录你的旅途…"></textarea>
						</div>
						<div class="row g-2">
							<div class="col-6">
								<label class="form-label">纬度</label>
								<input v-model.number="form.latitude" type="number" step="0.000001" class="form-control" />
							</div>
							<div class="col-6">
								<label class="form-label">经度</label>
								<input v-model.number="form.longitude" type="number" step="0.000001" class="form-control" />
							</div>
						</div>
					</div>
					<div class="card-footer d-flex justify-content-end gap-2">
						<button class="btn btn-primary" :disabled="submitting" @click="submitDiary">
							<span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>提交
						</button>
					</div>
				</div>

				<div class="card">
					<div class="card-header">我的日记 ({{ diaries.length }})</div>
					<ul class="list-group list-group-flush list-scroll">
						<li v-for="d in diaries" :key="d.id" class="list-group-item list-group-item-action"
								:class="{ active: selectedId === d.id }" @click="selectDiary(d)">
							<div class="d-flex justify-content-between align-items-center">
								<strong>{{ d.title }}</strong>
								<small class="text-muted">{{ d.date || '-' }}</small>
							</div>
							<div class="text-muted small ellipsis-2">
								{{ d.snippet || d.content || '（无内容）' }}
							</div>
						</li>
						<li v-if="diaries.length === 0" class="list-group-item text-muted">暂无日记</li>
					</ul>
					<div v-if="selectedDiary" class="card-body border-top">
						<h6 class="mb-2">{{ selectedDiary.title }}</h6>
						<div class="text-muted small mb-2">{{ selectedDiary.date || '-' }}</div>
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
				/>
			</div>
		</div>
	</div>
</template>

<script>
import BaseMap from '@/components/map/BaseMap.vue'
import { fetchDiaries, fetchDiaryDetail, createDiary } from '@/api/diary'

export default {
	name: 'TravelDiary',
	components: { BaseMap },
	data() {
		return {
			diaries: [],
			selectedId: null,
			selectedDiary: null,
			submitting: false,
			form: {
				title: '',
				content: '',
				latitude: null,
				longitude: null
			},
			mapCenter: [39.9042, 116.4074]
		}
	},
	computed: {
		markers() {
			return (this.diaries || [])
				.filter(d => typeof d.latitude === 'number' && typeof d.longitude === 'number')
				.map(d => ({
					id: d.id,
					name: d.title,
					latitude: d.latitude,
					longitude: d.longitude,
					popup: `${d.title}${d.date ? ' · ' + d.date : ''}`
				}))
		}
	},
	async mounted() {
		await this.loadDiaries()
	},
	methods: {
		async loadDiaries() {
			try {
				const list = await fetchDiaries({ user_id: 1 })
				this.diaries = Array.isArray(list) ? list : []
				if (this.diaries.length) {
					this.selectedId = this.diaries[0].id
					this.selectedDiary = this.diaries[0]
					const firstWithCoord = this.diaries.find(d => typeof d.latitude === 'number' && typeof d.longitude === 'number')
					if (firstWithCoord) this.mapCenter = [firstWithCoord.latitude, firstWithCoord.longitude]
				}
			} catch (e) {
				console.error('加载日记失败', e)
			}
		},
		async submitDiary() {
			if (!this.form.title || !this.form.content) return
			this.submitting = true
			try {
				const created = await createDiary({
					user_id: 1,
					title: this.form.title,
					content: this.form.content,
					latitude: this.form.latitude,
					longitude: this.form.longitude
				})
				if (created) {
					this.diaries = [created, ...this.diaries]
					this.selectedId = created.id
					this.selectedDiary = created
					if (typeof created.latitude === 'number' && typeof created.longitude === 'number') {
						this.mapCenter = [created.latitude, created.longitude]
					}
					this.clearForm()
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
			this.form.latitude = null
			this.form.longitude = null
		},
		async selectDiary(d) {
			this.selectedId = d.id
			// 若需要获取更详细信息
			try {
				const detail = await fetchDiaryDetail(d.id)
				this.selectedDiary = detail || d
			} catch {
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
		}
	}
}
</script>

<style scoped>
.list-scroll { max-height: calc(100vh - 280px); overflow: auto; }
.ellipsis-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.white-prewrap { white-space: pre-wrap; }
</style>
