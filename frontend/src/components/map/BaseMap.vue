<template>
  <div :class="['map-container', { 'map-fullscreen': fullScreen }]" :style="containerStyle" ref="mapContainer"></div>
  </template>

<script>
import { nextTick, onBeforeUnmount } from 'vue'
import L from 'leaflet'

export default {
  name: 'BaseMap',
  props: {
    center: {
      type: Array,
      default: () => [39.9042, 116.4074] // 北京经纬度
    },
    zoom: {
      type: Number,
      default: 11
    },
    height: {
      type: [String, Number],
      default: 400
    },
    fullScreen: {
      type: Boolean,
      default: false
    },
    offsetTop: {
      // 全屏模式下距离顶部的偏移（避免遮挡导航）
      type: [Number, String],
      default: 0
    }
  },
  data() {
    return {
      map: null,
      _resizeHandler: null
    }
  },
  computed: {
    containerStyle() {
      // 在全屏模式下应用顶部偏移
      if (this.fullScreen) {
        const top = typeof this.offsetTop === 'number' ? `${this.offsetTop}px` : this.offsetTop
        return { top }
      }
      return {}
    }
  },
  mounted() {
    // 等待下一次 DOM 刷新，确保容器尺寸稳定
    nextTick(() => {
      this.initMap()
      // 初次渲染后稍作延迟，确保计算尺寸准确
      setTimeout(() => this.invalidateSizeSafe(), 0)
    })
    // 监听窗口尺寸变化
    this._resizeHandler = () => this.invalidateSizeSafe()
    window.addEventListener('resize', this._resizeHandler)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this._resizeHandler)
    if (this.map) {
      this.map.remove()
      this.map = null
    }
  },
  methods: {
    initMap() {
      const el = this.$refs.mapContainer
      if (!el) {
        console.error('[BaseMap] 容器未找到')
        return
      }
      // 如果非全屏，则由 height prop 控制容器高度
      if (!this.fullScreen) {
        el.style.height = typeof this.height === 'number' ? `${this.height}px` : this.height
      }
      this.map = L.map(el).setView(this.center, this.zoom)
      const layer = L.tileLayer('http://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}', {
        maxZoom: 19,
        subdomains: ['1','2','3','4'],
        attribution: '© 高德地图'
      })
      layer.on('tileerror', (e) => {
        console.error('[BaseMap] 瓦片加载失败', e)
      })
      layer.addTo(this.map)
    },
    invalidateSizeSafe() {
      if (this.map) {
        this.map.invalidateSize()
      }
    }
  }
}
</script>

<style scoped>
.map-container {
  width: 100%;
  /* 高度由 props.height 控制，默认 400px */
  border: 1px solid #ddd;
  border-radius: 6px;
  overflow: hidden;
}

.map-fullscreen {
  position: fixed;
  top: 0; /* 会被内联样式的 offsetTop 覆盖 */
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 900; /* 低于导航栏（Bootstrap sticky-top ~1020） */
}
</style>
