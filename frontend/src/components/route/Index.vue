<template>
  <div class="route-box p-3">
    <h3 class="mb-3">路径规划模块（最短路径示例）</h3>
    <form class="row g-2" @submit.prevent="onSubmit">
      <div class="col-4">
        <label class="form-label">起点ID</label>
        <input v-model.number="startId" type="number" min="1" class="form-control" placeholder="例如 1" />
      </div>
      <div class="col-4">
        <label class="form-label">终点ID</label>
        <input v-model.number="endId" type="number" min="1" class="form-control" placeholder="例如 5" />
      </div>
      <div class="col-4">
        <label class="form-label">构边阈值(km)</label>
        <input v-model.number="maxDistance" type="number" min="1" class="form-control" />
      </div>
      <div class="col-12 d-flex gap-2 mt-2">
        <button class="btn btn-primary" :disabled="loading">{{ loading ? '计算中…' : '计算最短路径' }}</button>
        <button type="button" class="btn btn-outline-secondary" @click="reset" :disabled="loading">重置</button>
      </div>
    </form>

    <div class="mt-3">
      <div v-if="error" class="alert alert-danger py-2 px-3">{{ error }}</div>
      <div v-else-if="result && result.status==='success'" class="alert alert-success py-2 px-3">
        <div><strong>路径:</strong> {{ result.data.path.join(' -> ') }}</div>
        <div><strong>距离(km):</strong> {{ result.data.distance_km }}</div>
        <div><strong>节点数:</strong> {{ result.data.nodes }}</div>
        <div class="small text-muted">构边阈值: {{ result.data.edge_threshold_km }} km</div>
      </div>
      <div v-else-if="result && result.status==='error'" class="alert alert-warning py-2 px-3">
        {{ result.message || '未找到路径' }}
      </div>
      <div v-else class="text-muted small">输入起点/终点 ID 进行最短路径计算。</div>
    </div>
  </div>
</template>

<script>
import { fetchShortestRoute } from '@/api/route'
export default {
  name: 'RouteIndex',
  data() {
    return {
      startId: 1,
      endId: 5,
      maxDistance: 50,
      loading: false,
      result: null,
      error: ''
    }
  },
  methods: {
    async onSubmit() {
      this.error = ''
      this.result = null
      if (!this.startId || !this.endId) {
        this.error = '起点与终点ID不能为空'
        return
      }
      this.loading = true
      try {
        const data = await fetchShortestRoute(this.startId, this.endId, this.maxDistance)
        if (data.error) {
          this.error = data.error
        } else {
          this.result = data
        }
      } catch (e) {
        this.error = e.message || '请求失败'
      } finally {
        this.loading = false
      }
    },
    reset() {
      this.startId = 1
      this.endId = 5
      this.maxDistance = 50
      this.result = null
      this.error = ''
    }
  }
}
</script>

<style scoped>
.route-box { background:#fff; border:1px solid #ddd; border-radius:8px; }
input.form-control { font-size: 0.9rem; }
</style>
