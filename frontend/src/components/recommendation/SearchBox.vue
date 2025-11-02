<template>
  <form @submit.prevent="onSubmit" class="d-flex gap-2">
    <input v-model="model" type="text" class="form-control" placeholder="搜索景点名称/类别/关键词..." />
    <button class="btn btn-primary" type="submit">搜索</button>
    <button class="btn btn-outline-secondary" type="button" @click="onReset">清空</button>
  </form>
</template>

<script>
export default {
  name: 'SearchBox',
  props: { modelValue: { type: String, default: '' } },
  emits: ['update:modelValue', 'search', 'reset'],
  computed: {
    model: {
      get() { return this.modelValue },
      set(v) { this.$emit('update:modelValue', v) }
    }
  },
  methods: {
    onSubmit() { this.$emit('search', this.model) },
    onReset() { this.$emit('update:modelValue', ''); this.$emit('reset') }
  }
}
</script>

<style scoped>
</style>
