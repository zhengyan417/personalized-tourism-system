<template>
  <div class="vl-container" :style="{ height: height + 'px' }" ref="container" @scroll="onScroll">
    <div :style="{ height: totalHeight + 'px', position: 'relative' }">
      <div
        v-for="(item, i) in visibleItems"
        :key="getKey(item, start + i)"
        class="vl-item"
        :style="{ position: 'absolute', top: (itemHeight * (start + i)) + 'px', left: 0, right: 0 }"
      >
        <slot :item="item" :index="start + i"></slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VirtualList',
  props: {
    items: { type: Array, required: true },
    itemHeight: { type: Number, required: true },
    height: { type: Number, default: 600 },
    buffer: { type: Number, default: 5 },
    itemKey: { type: [String, Function], default: 'id' }
  },
  data() {
    return { start: 0 }
  },
  computed: {
    totalHeight() { return (this.items?.length || 0) * this.itemHeight },
    visibleCount() { return Math.ceil(this.height / this.itemHeight) + this.buffer },
    visibleItems() { return (this.items || []).slice(this.start, Math.min(this.start + this.visibleCount, this.items.length)) }
  },
  methods: {
    onScroll(e) {
      const scrollTop = e.target.scrollTop
      const start = Math.floor(scrollTop / this.itemHeight)
      if (start !== this.start) this.start = start
    },
    getKey(item, index) {
      if (typeof this.itemKey === 'function') return this.itemKey(item, index)
      return item?.[this.itemKey] ?? index
    }
  }
}
</script>

<style scoped>
.vl-container { overflow: auto; }
</style>
