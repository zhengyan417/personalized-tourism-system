<template>
  <div :class="['map-container', { 'map-fullscreen': fullScreen }]" :style="containerStyle" ref="mapContainer"></div>
  </template>

<script>
import { nextTick, onBeforeUnmount, watch } from 'vue'
import L from 'leaflet'
import iconUrl from 'leaflet/dist/images/marker-icon.png'
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png'
import shadowUrl from 'leaflet/dist/images/marker-shadow.png'

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
    },
    markers: {
      // [{ id, name, latitude, longitude, popup }]
      type: Array,
      default: () => []
    },
    selectedId: {
      type: [String, Number, null],
      default: null
    }
  },
  data() {
    return {
      map: null,
      _resizeHandler: null,
      _markerLayer: null,
      _markerMap: new Map()
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

    // 监听外部变更
    watch(() => this.center, (val) => {
      if (this.map && Array.isArray(val) && val.length === 2) {
        this.map.setView(val, this.map.getZoom())
      }
    }, { deep: true })

    watch(() => this.zoom, (z) => {
      if (this.map && typeof z === 'number') this.map.setZoom(z)
    })

    watch(() => this.markers, () => {
      this.renderMarkers()
    }, { deep: true, immediate: false })

    watch(() => this.selectedId, (id) => {
      if (!id) return
      const m = this._markerMap.get(String(id))
      if (m) {
        m.openPopup()
        const latlng = m.getLatLng()
        this.map && this.map.panTo(latlng)
      }
    })
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
      // 修复默认图标路径
      L.Icon.Default.mergeOptions({
        iconUrl,
        iconRetinaUrl,
        shadowUrl
      })
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

      // 初始化标记图层
      this._markerLayer = L.layerGroup().addTo(this.map)
      this.renderMarkers()
    },
    invalidateSizeSafe() {
      if (this.map) {
        this.map.invalidateSize()
      }
    },
    renderMarkers() {
      if (!this.map || !this._markerLayer) return
      this._markerLayer.clearLayers()
      this._markerMap.clear()
      if (!Array.isArray(this.markers)) return
      const bounds = []
      this.markers.forEach((mk) => {
        const { id, name, latitude, longitude, popup } = mk
        if (typeof latitude !== 'number' || typeof longitude !== 'number') return
        const marker = L.marker([latitude, longitude])
        const content = popup || name || String(id || '')
        if (content) marker.bindPopup(content)
        marker.on('click', () => this.$emit && this.$emit('marker-click', mk))
        marker.addTo(this._markerLayer)
        if (id !== undefined && id !== null) this._markerMap.set(String(id), marker)
        bounds.push([latitude, longitude])
      })
      if (bounds.length > 0 && !this.fullScreen) {
        try { this.map.fitBounds(bounds, { padding: [24, 24] }) } catch {}
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
