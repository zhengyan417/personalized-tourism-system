<template>
  <div :class="['map-container', { 'map-fullscreen': fullScreen }]" :style="containerStyle" ref="mapContainer"></div>
  </template>

<script>
import { nextTick } from 'vue'
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
    },
    // 路径规划模式：开启后点击地图会触发 route-point-add 事件
    // 已移除自由路径点功能（routeMode/routeMarkers）
    // 道路折线：真实导航路径 [[lat, lon], ...]
    roadPath: {
      type: Array,
      default: () => []
    }
    ,
    // 选定起终点高亮（景点ID）
    startAttractionId: {
      type: [Number, String, null],
      default: null
    },
    endAttractionId: {
      type: [Number, String, null],
      default: null
    }
  },
  data() {
    return {
      map: null,
      _resizeHandler: null,
      _markerLayer: null,
      _markerMap: new Map(),
      _initTimer: null,
      _mapReady: false,
      _routeLayer: null,
      _roadPolyline: null,
      _zooming: false,
      _pendingRoadRender: false,
      _pendingRoadLatLngs: null,
      _pendingRoadClear: false,
      _fallbackAdded: false,
      _tileErrorLogged: false,
      _isDestroying: false  // 新增：标记组件正在销毁
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
      this._initTimer = setTimeout(() => this.invalidateSizeSafe(), 0)
    })
    // 监听窗口尺寸变化
    this._resizeHandler = () => this.invalidateSizeSafe()
    window.addEventListener('resize', this._resizeHandler)

    // 监听外部变更（使用 this.$watch 保证在组件销毁时自动移除）
    this.$watch(
      () => this.center,
      (val) => {
        if (this._isDestroying || !this.map || !this._mapReady || !Array.isArray(val) || val.length !== 2) return
        try {
          this.map.setView(val, this.map.getZoom(), { animate: this.canAnimate() })
        } catch (e) {
          console.warn('[BaseMap] setView 失败', e)
        }
      },
      { deep: true }
    )

    this.$watch(
      () => this.zoom,
      (z) => {
        if (this._isDestroying || !this.map || !this._mapReady || typeof z !== 'number') return
        try {
          this.map.setZoom(z, { animate: this.canAnimate() })
        } catch (e) {
          console.warn('[BaseMap] setZoom 失败', e)
        }
      }
    )

    this.$watch(
      () => this.markers,
      () => {
        if (this._isDestroying || !this.map || !this._mapReady) return
        this.renderMarkers()
      },
      { deep: true, immediate: false }
    )

    this.$watch(
      () => this.selectedId,
      (id) => {
        if (this._isDestroying || !id || !this.map || !this._mapReady) return
        const m = this._markerMap.get(String(id))
        if (m) {
          try {
            m.openPopup()
            const latlng = m.getLatLng()
            this.map.panTo(latlng, { animate: this.canAnimate() })
          } catch (e) {
            console.warn('[BaseMap] 标记交互失败', e)
          }
        }
      }
    )

    // 监听路径点变化，重绘路径（独立 watcher）
    // 监听道路导航路径变化
    this.$watch(
      () => this.roadPath,
      () => {
        if (this._isDestroying || !this.map || !this._mapReady) return
        this.renderRoadPath && this.renderRoadPath()
      },
      { deep: true, immediate: true }
    )
  },
  beforeUnmount() {
    // 立即标记为销毁中和未就绪，阻止所有后续操作
    this._isDestroying = true
    this._mapReady = false
    this._zooming = false
    
    window.removeEventListener('resize', this._resizeHandler)
    if (this._initTimer) {
      clearTimeout(this._initTimer)
      this._initTimer = null
    }
    if (this._geoWatchId) {
      try { navigator.geolocation.clearWatch(this._geoWatchId) } catch (e) {}
      this._geoWatchId = null
    }
    if (this.map) {
      // 移除所有事件监听器（必须在清理图层之前）
      try { 
        this.map.off()
        // 禁用所有动画选项
        if (this.map.options) {
          this.map.options.zoomAnimation = false
          this.map.options.fadeAnimation = false
          this.map.options.markerZoomAnimation = false
        }
      } catch (e) {}
      
      // 停止任何正在进行的动画和缩放转换
      try { 
        if (typeof this.map.stop === 'function') {
          this.map.stop()
        }
        // 清除所有动画帧
        if (this.map._animatingZoom) {
          this.map._animatingZoom = false
        }
        if (this.map._zooming) {
          this.map._zooming = false
        }
      } catch (e) {}
      
      // 清理图层
      try {
        if (this._roadPolyline) {
          this._roadPolyline.remove()
          this._roadPolyline = null
        }
        if (this._routeLayer) {
          this._routeLayer.clearLayers()
          this._routeLayer.remove()
          this._routeLayer = null
        }
        if (this._markerLayer) {
          this._markerLayer.clearLayers()
          this._markerLayer.remove()
          this._markerLayer = null
        }
        if (this._userLayer) {
          this._userLayer.clearLayers()
          this._userLayer.remove()
          this._userLayer = null
        }
      } catch (e) {
        console.warn('[BaseMap] 清理图层时出错', e)
      }
      
      // 最后销毁地图
      try { 
        this.map.remove() 
      } catch (e) {
        console.warn('[BaseMap] 移除地图时出错', e)
      }
      
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
  // 完全禁用所有动画，避免销毁时的异步动画错误
  this.map = L.map(el, { 
    zoomAnimation: false,
    fadeAnimation: false,
    markerZoomAnimation: false,
    preferCanvas: true,
    zoomControl: true
  }).setView(this.center, this.zoom)
      
      // 使用 OpenStreetMap 作为默认底图（与 OSRM 路由生态一致）
      const layer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        minZoom: 3,
        attribution: '© OpenStreetMap contributors',
        errorTileUrl: 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7' // 透明1x1 gif
      })
      
      // 添加瓦片错误处理，静默失败
      layer.on('tileerror', (e) => {
        // 避免瓦片加载错误导致红色界面
        if (!this._tileErrorLogged) {
          this._tileErrorLogged = true
          console.warn('[BaseMap] 部分地图瓦片加载失败（网络问题或缩放过快），不影响使用')
        }
      })
      
      layer.addTo(this.map)

  // 初始化标记图层
  this._markerLayer = L.layerGroup().addTo(this.map)
  // 路径图层（路径点与折线）
  this._routeLayer = L.layerGroup().addTo(this.map)
  this.renderMarkers()
  this.renderRoadPath && this.renderRoadPath()
      // 标记地图已就绪（用于判断是否可安全执行动画）
      try {
        if (this.map && typeof this.map.whenReady === 'function') {
          this.map.whenReady(() => {
            this._mapReady = true
            // 地图真正 ready 后再次强制渲染路径，避免初始化阶段 _routeLayer 为空导致未绘制
            try { this.renderRoadPath && this.renderRoadPath() } catch {}
          })
        } else {
          this._mapReady = true
          try { this.renderRoadPath && this.renderRoadPath() } catch {}
        }
      } catch (e) { this._mapReady = true }
      // 添加定位控件与用户定位图层
      this._userLayer = L.layerGroup().addTo(this.map)
      this._locateControl = this._createLocateControl()
      this._locateControl.addTo(this.map)
      // 点击地图以添加路径点（仅在 routeMode 开启时）
      // 已移除自由绘制路径点点击逻辑
      // 缩放动画期间避免立即重绘路径（清空图层会触发 _animateZoom 访问已移除对象导致报错）
      this.map.on('zoomstart', () => {
        this._zooming = true
      })
      this.map.on('zoomend', () => {
        this._zooming = false
        try {
          this._flushPendingRoadPath && this._flushPendingRoadPath()
        } catch (e) {
          console.warn('[BaseMap] 缩放后刷新路径失败', e)
        }
      })
      // 添加额外的缩放动画保护
      this.map.on('zoomanim', () => {
        this._zooming = true
      })
      // 通用地图点击事件：向父组件发送点击位置（经纬度）
      this.map.on('click', (e) => {
        try {
          const lat = e.latlng.lat
          const lon = e.latlng.lng
          this.$emit && this.$emit('map-click', { latitude: lat, longitude: lon })
        } catch (err) {
          console.warn('[BaseMap] 处理地图点击失败', err)
        }
      })
    },
    invalidateSizeSafe() {
      if (this._isDestroying || !this.map) return
      // 根据当前可动画能力选择是否平滑（平滑时体验更好）
      try { this.map.invalidateSize({ animate: this.canAnimate() }) } catch (e) { 
        try { this.map.invalidateSize() } catch (e2) {}
      }
    },
    renderMarkers() {
      if (this._isDestroying || !this.map || !this._markerLayer || !this._mapReady) return
      // 避免在缩放动画期间清空图层（防止红色错误界面）
      if (this._zooming) {
        return
      }
      try {
        this._markerLayer.clearLayers()
      } catch (e) {
        console.warn('[BaseMap] 清理标记图层时出错，已忽略', e)
        return
      }
      this._markerMap.clear()
      if (!Array.isArray(this.markers)) return
      const bounds = []
      this.markers.forEach((mk) => {
        const { id, name, latitude, longitude, popup } = mk
        if (typeof latitude !== 'number' || typeof longitude !== 'number') return
        let marker
        const isStart = this.startAttractionId != null && String(id) === String(this.startAttractionId)
        const isEnd = this.endAttractionId != null && String(id) === String(this.endAttractionId)
        try {
          if (isStart || isEnd) {
            const color = isStart ? '#27ae60' : '#c0392b'
            marker = L.circleMarker([latitude, longitude], {
              radius: 10,
              color,
              weight: 3,
              fillColor: color,
              fillOpacity: 0.85
            })
            marker.addTo(this._markerLayer)
            L.marker([latitude, longitude], {
              icon: L.divIcon({
                className: 'attraction-label',
                html: `<div>${id}</div>`,
                iconSize: [24,24],
                iconAnchor: [12,30]
              }),
              interactive: false
            }).addTo(this._markerLayer)
          } else {
            marker = L.marker([latitude, longitude])
            marker.addTo(this._markerLayer)
          }
          const content = popup || name || `#${id}`
          if (content && marker && marker.bindPopup) marker.bindPopup(content)
          marker.on('click', () => this.$emit && this.$emit('marker-click', mk))
          if (id !== undefined && id !== null) this._markerMap.set(String(id), marker)
          bounds.push([latitude, longitude])
        } catch (e) {
          console.warn('[BaseMap] 添加标记失败', e)
        }
      })
      if (bounds.length > 0 && !this.fullScreen && this.map) {
        try { 
          this.map.fitBounds(bounds, { padding: [24, 24], animate: this.canAnimate() }) 
        } catch (e) {
          console.warn('[BaseMap] fitBounds 失败', e)
        }
      }
    },
    // 计算两点间大圆距离（千米）
    _haversineKm(lat1, lon1, lat2, lon2) {
      const toRad = (d) => d * Math.PI / 180
      const R = 6371
      const dLat = toRad(lat2 - lat1)
      const dLon = toRad(lon2 - lon1)
      const a = Math.sin(dLat/2) * Math.sin(dLat/2) + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon/2) * Math.sin(dLon/2)
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
      return R * c
    },
    // 绘制路径点与折线（带序号与分段距离）
    // 绘制真实道路导航路径
    renderRoadPath() {
      // 增强地图存在性检查
      if (this._isDestroying || !this.map || !this._routeLayer || !this._mapReady) return
      
      // 如果正在缩放动画，延迟处理
      if (this._zooming) {
        const latlngs = Array.isArray(this.roadPath)
          ? this.roadPath.filter(p => Array.isArray(p) && p.length === 2)
          : null
        const valid = latlngs && latlngs.length >= 2
        this._pendingRoadRender = true
        this._pendingRoadLatLngs = valid ? latlngs : null
        this._pendingRoadClear = !valid
        return
      }
      this._pendingRoadRender = false
      this._pendingRoadLatLngs = null
      this._pendingRoadClear = false
      if (!Array.isArray(this.roadPath)) {
        this._clearRoadPolyline()
        return
      }
      const latlngs = this.roadPath.filter(p => Array.isArray(p) && p.length === 2)
      if (latlngs.length < 2) {
        this._clearRoadPolyline()
        return
      }
      this._updateRoadPolyline(latlngs)
    },
    _flushPendingRoadPath() {
      if (this._isDestroying || !this._pendingRoadRender || !this.map || !this._routeLayer) return
      this._pendingRoadRender = false
      if (this._pendingRoadClear) {
        this._pendingRoadClear = false
        this._pendingRoadLatLngs = null
        this._clearRoadPolyline()
        return
      }
      const latlngs = this._pendingRoadLatLngs
      this._pendingRoadLatLngs = null
      if (Array.isArray(latlngs) && latlngs.length >= 2) {
        this._updateRoadPolyline(latlngs)
      }
    },
    _updateRoadPolyline(latlngs) {
      if (this._isDestroying || !this.map || !this._routeLayer || !Array.isArray(latlngs) || latlngs.length < 2) {
        this._clearRoadPolyline()
        return
      }
      if (!this._roadPolyline) {
        try {
          this._roadPolyline = L.polyline(latlngs, { color: '#2980b9', weight: 5, opacity: 0.85, dashArray: '8 6', className: 'road-polyline' })
          this._roadPolyline.addTo(this._routeLayer)
        } catch (e) {
          console.warn('[BaseMap] 创建路径线失败', e)
        }
      } else {
        try {
          this._roadPolyline.setLatLngs(latlngs)
        } catch (e) {
          try { 
            if (this._routeLayer && this._routeLayer.hasLayer && this._routeLayer.hasLayer(this._roadPolyline)) {
              this._routeLayer.removeLayer(this._roadPolyline) 
            }
          } catch (err) {}
          try {
            this._roadPolyline = L.polyline(latlngs, { color: '#2980b9', weight: 5, opacity: 0.85, dashArray: '8 6', className: 'road-polyline' })
            this._roadPolyline.addTo(this._routeLayer)
          } catch (err) {
            console.warn('[BaseMap] 重建路径线失败', err)
          }
        }
      }
    },
    _clearRoadPolyline() {
      if (this._roadPolyline) {
        try { 
          if (this._routeLayer && this._routeLayer.hasLayer && this._routeLayer.hasLayer(this._roadPolyline)) {
            this._routeLayer.removeLayer(this._roadPolyline)
          }
        } catch (e) {
          console.warn('[BaseMap] 清理路径线时出错，已忽略', e)
        }
        this._roadPolyline = null
      }
    },
    // ------- 定位相关 -------
    _createLocateControl() {
      const self = this
      const LocateControl = L.Control.extend({
        options: { position: 'topleft' },
        onAdd: function () {
          const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control')
          const a = L.DomUtil.create('a', '', container)
          a.href = '#'
          a.title = '定位到我的位置'
          a.innerHTML = '\u25CF' // simple dot
          a.style.fontSize = '18px'
          a.style.lineHeight = '26px'
          a.style.textAlign = 'center'
          a.style.width = '30px'
          a.style.height = '30px'
          a.style.color = '#007bff'
          L.DomEvent.on(a, 'click', L.DomEvent.stopPropagation)
          L.DomEvent.on(a, 'click', L.DomEvent.preventDefault)
          L.DomEvent.on(a, 'click', () => { self.locateUser(true) })
          return container
        }
      })
      return new LocateControl()
    },

    locateUser(watch = false) {
      if (!navigator || !navigator.geolocation) {
        console.warn('[BaseMap] 浏览器不支持定位')
        return
      }
      // 如果希望持续监听，则使用 watchPosition
      if (watch && navigator.geolocation.watchPosition) {
        if (this._geoWatchId) return // 已在监听
        this._geoWatchId = navigator.geolocation.watchPosition(
          (pos) => this._handleGeoSuccess(pos),
          (err) => this._handleGeoError(err),
          { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 }
        )
      } else {
        navigator.geolocation.getCurrentPosition(
          (pos) => this._handleGeoSuccess(pos),
          (err) => this._handleGeoError(err),
          { enableHighAccuracy: true, maximumAge: 0, timeout: 10000 }
        )
      }
    },

    _handleGeoSuccess(pos) {
      try {
        const lat = pos.coords.latitude
        const lon = pos.coords.longitude
        const acc = pos.coords.accuracy
        this._setUserLocation(lat, lon, acc)
        // 向父组件/页面广播位置更新
        this.$emit && this.$emit('location-update', { latitude: lat, longitude: lon, accuracy: acc })
      } catch (e) {
        console.error('[BaseMap] 处理定位成功时出错', e)
      }
    },

    _handleGeoError(err) {
      console.warn('[BaseMap] 定位失败', err && err.message)
    },

    _setUserLocation(lat, lon, accuracy) {
      if (!this.map) return
      // 清理旧图层
      if (this._userLayer) this._userLayer.clearLayers()
      // 精度圆
      if (typeof accuracy === 'number') {
        L.circle([lat, lon], { radius: Math.max(5, accuracy), color: '#007bff', weight: 1, fillOpacity: 0.15 }).addTo(this._userLayer)
      }
      // 圆点标记
      const marker = L.circleMarker([lat, lon], { radius: 8, color: '#fff', weight: 2, fillColor: '#007bff', fillOpacity: 0.9 })
      marker.bindPopup('我的位置').openPopup()
      marker.addTo(this._userLayer)
      // 视图跟随（平滑或瞬移由 canAnimate 决定）
      try { this.map.panTo([lat, lon], { animate: this.canAnimate() }) } catch (e) {}
    }
    ,
    // 完全禁用动画，避免销毁时的异步错误
    canAnimate() {
      return false  // 始终禁用动画
    }
  }
}
</script>

<style scoped>
.map-container {
  width: 100%;
  /* 高度由 props.height 控制，默认 400px */
  border: 1px solid var(--bs-border-color, #ddd);
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

/* 路径点序号标签样式 */
.route-pt-label div {
  background: rgba(0,0,0,0.75);
  color: #fff;
  font-size: 12px;
  width: 22px;
  height: 22px;
  line-height: 22px;
  border-radius: 50%;
  text-align: center;
  box-shadow: 0 0 2px rgba(0,0,0,0.4);
  user-select: none;
}
.route-pt-label.route-pt-start div { background: #2ecc71; }
.route-pt-label.route-pt-end div { background: #e74c3c; }

/* 分段距离标签 */
.route-seg-label span {
  background: rgba(255,255,255,0.9);
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 11px;
  color: #333;
  border: 1px solid #ddd;
  box-shadow: 0 1px 2px rgba(0,0,0,0.2);
  white-space: nowrap;
}
</style>
