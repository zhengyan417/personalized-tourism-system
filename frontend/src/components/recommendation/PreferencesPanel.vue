<template>
  <div class="card">
    <div class="card-header">偏好设置</div>
    <div class="card-body">
      <div class="mb-3">
        <label class="form-label">推荐算法</label>
        <select class="form-select" v-model="local.algorithm">
          <option value="content_based">内容推荐</option>
          <option value="collaborative">协同过滤</option>
        </select>
      </div>
      <div class="mb-3">
        <label class="form-label">排序依据</label>
        <select class="form-select" v-model="local.sort_by">
          <option value="score">综合得分</option>
          <option value="popularity">热度</option>
          <option value="rating">评分</option>
        </select>
      </div>
      <div class="mb-3">
        <label class="form-label">Top N</label>
        <input type="number" class="form-control" v-model.number="local.top_n" min="1" max="1000" />
      </div>
      <div>
        <label class="form-label">类别（可多选）</label>
        <div class="d-flex flex-wrap gap-2">
          <label class="form-check-label" v-for="c in categories" :key="c">
            <input class="form-check-input me-1" type="checkbox" :value="c" v-model="local.categories" /> {{ c }}
          </label>
        </div>
      </div>
    </div>
    <div class="card-footer d-flex gap-2">
      <button class="btn btn-primary" @click="onApply">应用</button>
      <button class="btn btn-outline-secondary" @click="onReset">重置</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PreferencesPanel',
  props: {
    modelValue: { type: Object, default: () => ({ algorithm: 'content_based', sort_by: 'score', top_n: 50, categories: [] }) },
    categories: { type: Array, default: () => ['景点','美食','自然','历史'] }
  },
  emits: ['update:modelValue', 'apply', 'reset'],
  data() {
    return { local: JSON.parse(JSON.stringify(this.modelValue)) }
  },
  watch: {
    modelValue: {
      deep: true,
      handler(v) { this.local = JSON.parse(JSON.stringify(v)) }
    }
  },
  methods: {
    onApply() { this.$emit('update:modelValue', { ...this.local }); this.$emit('apply', { ...this.local }) },
    onReset() { const d = { algorithm: 'content_based', sort_by: 'score', top_n: 50, categories: [] }; this.$emit('update:modelValue', d); this.$emit('reset') }
  }
}
</script>

<style scoped>
</style>
