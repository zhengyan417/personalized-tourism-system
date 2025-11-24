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
    routeMode: {
      type: Boolean,
      default: false
    },
    // 路径点数组：[{ latitude, longitude }]
    routeMarkers: {
      type: Array,
      default: () => []
    },
    // 规划完成后的路径坐标数组 [[lat,lng],...]
    plannedPath: {
      type: Array,
      default: () => []
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
      _zooming: false,
      _pendingRouteRender: false
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
        if (this.map && Array.isArray(val) && val.length === 2) {
          this.map.setView(val, this.map.getZoom(), { animate: this.canAnimate() })
        }
      },
      { deep: true }
    )

    this.$watch(
      () => this.zoom,
      (z) => {
        if (this.map && typeof z === 'number') this.map.setZoom(z, { animate: this.canAnimate() })
      }
    )

    this.$watch(
      () => this.markers,
      () => {
        this.renderMarkers()
      },
      { deep: true, immediate: false }
    )

    this.$watch(
      () => this.selectedId,
      (id) => {
        if (!id) return
        const m = this._markerMap.get(String(id))
        if (m) {
          m.openPopup()
          const latlng = m.getLatLng()
          this.map && this.map.panTo(latlng, { animate: this.canAnimate() })
        }
      }
    )

    // 监听路径点变化，重绘路径（独立 watcher）
    this.$watch(
      () => this.routeMarkers,
      () => {
        // 如果正在缩放，先标记，等动画结束再重绘
        if (this._zooming) {
          this._pendingRouteRender = true
        } else {
          this.renderRoute && this.renderRoute()
        }
      },
      { deep: true, immediate: true }
    )

    // 监听规划路线
    this.$watch(
      () => this.plannedPath,
      () => {
        if (this._zooming) {
          this._pendingPlannedRender = true
        } else {
          this.renderPlannedRoute && this.renderPlannedRoute()
        }
      },
      { deep: true, immediate: true }
    )
  },
  beforeUnmount() {
    window.removeEventListener('resize', this._resizeHandler)
    if (this._initTimer) {
      clearTimeout(this._initTimer)
      this._initTimer = null
    }
    if (this.map) {
      try { this.map.off() } catch {}
      try { this.map.remove() } catch (e) {}
      this.map = null
      this._mapReady = false
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
  // 启用动画（平滑体验），但后续方法会根据 canAnimate 动态决定是否播放动画
  this.map = L.map(el, { zoomAnimation: true, zoomAnimationThreshold: 4, fadeAnimation: true, preferCanvas: true }).setView(this.center, this.zoom)
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
  // 路径图层（路径点与折线）
  this._routeLayer = L.layerGroup().addTo(this.map)
  this._plannedLayer = L.layerGroup().addTo(this.map)
  this.renderMarkers()
  this.renderRoute && this.renderRoute()
      // 标记地图已就绪（用于判断是否可安全执行动画）
      try {
        if (this.map && typeof this.map.whenReady === 'function') {
          this.map.whenReady(() => {
            this._mapReady = true
            // 地图真正 ready 后再次强制渲染路径，避免初始化阶段 _routeLayer 为空导致未绘制
            try { this.renderRoute && this.renderRoute() } catch {}
            try { this.renderPlannedRoute && this.renderPlannedRoute() } catch {}
          })
        } else {
          this._mapReady = true
          try { this.renderRoute && this.renderRoute() } catch {}
          try { this.renderPlannedRoute && this.renderPlannedRoute() } catch {}
        }
      } catch (e) { this._mapReady = true }
      // 添加定位控件与用户定位图层
      this._userLayer = L.layerGroup().addTo(this.map)
      this._locateControl = this._createLocateControl()
      this._locateControl.addTo(this.map)
      // 点击地图以添加路径点（仅在 routeMode 开启时）
      this.map.on('click', (e) => {
        if (!this.routeMode) return
        const { lat, lng } = e.latlng || {}
        if (typeof lat === 'number' && typeof lng === 'number') {
          const point = { latitude: +lat.toFixed(6), longitude: +lng.toFixed(6) }
          this.$emit && this.$emit('route-point-add', point)
        }
      })
      // 缩放动画期间避免立即重绘路径（清空图层会触发 _animateZoom 访问已移除对象导致报错）
      this.map.on('zoomstart', () => {
        this._zooming = true
      })
      this.map.on('zoomend', () => {
        this._zooming = false
        if (this._pendingRouteRender) {
          this._pendingRouteRender = false
          try { this.renderRoute && this.renderRoute() } catch {}
        }
      })
    },
    invalidateSizeSafe() {
      if (this.map) {
        // 根据当前可动画能力选择是否平滑（平滑时体验更好）
        try { this.map.invalidateSize({ animate: this.canAnimate() }) } catch (e) { this.map.invalidateSize() }
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
        let marker
        if (mk.color) {
          marker = L.circleMarker([latitude, longitude], {
            radius: 8,
            color: mk.color,
            weight: 2,
            fillColor: mk.color,
            fillOpacity: 0.85
          })
        } else {
          marker = L.marker([latitude, longitude])
        }
        const content = popup || name || String(id || '')
        if (content) marker.bindPopup(content)
        marker.on('click', () => this.$emit && this.$emit('marker-click', mk))
        marker.addTo(this._markerLayer)
        if (id !== undefined && id !== null) this._markerMap.set(String(id), marker)
        bounds.push([latitude, longitude])
      })
      if (bounds.length > 0 && !this.fullScreen) {
        try { this.map.fitBounds(bounds, { padding: [24, 24], animate: this.canAnimate() }) } catch {}
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
    renderRoute() {
      if (!this.map || !this._routeLayer) return
      // 若处于缩放动画中，延后重绘以避免 Leaflet 对已移除图层执行 _animateZoom 报错
      if (this._zooming) {
        this._pendingRouteRender = true
        return
      }
      this._routeLayer.clearLayers()
      if (!Array.isArray(this.routeMarkers) || this.routeMarkers.length === 0) return
      const latlngs = []
      const n = this.routeMarkers.length
      this.routeMarkers.forEach((p, idx) => {
        const { latitude, longitude } = p || {}
        if (typeof latitude !== 'number' || typeof longitude !== 'number') return
        latlngs.push([latitude, longitude])
        // 起终点/中间点不同样式
        const isStart = idx === 0
        const isEnd = idx === n - 1
        const color = isStart ? '#2ecc71' : (isEnd ? '#e74c3c' : '#f39c12')
        const cm = L.circleMarker([latitude, longitude], {
          radius: 8,
          color,
          weight: 3,
          fillColor: color,
          fillOpacity: 0.95
        }).addTo(this._routeLayer)
        // 悬停高亮
        cm.on('mouseover', () => cm.setStyle({ radius: 10 }))
        cm.on('mouseout', () => cm.setStyle({ radius: 8 }))
        // 序号标签（divIcon）
        L.marker([latitude, longitude], {
          icon: L.divIcon({
            className: `route-pt-label${isStart ? ' route-pt-start' : (isEnd ? ' route-pt-end' : '')}`,
            html: `<div>${idx + 1}</div>`,
            iconSize: [24, 24],
            iconAnchor: [12, 12]
          }),
          interactive: false
        }).addTo(this._routeLayer)
      })
      if (latlngs.length >= 2) {
  L.polyline(latlngs, { color: '#e74c3c', weight: 4, opacity: 0.9 }).addTo(this._routeLayer)
        // 分段距离标签
        for (let i = 0; i < latlngs.length - 1; i++) {
          const [lat1, lon1] = latlngs[i]
          const [lat2, lon2] = latlngs[i + 1]
          const mid = [ (lat1 + lat2) / 2, (lon1 + lon2) / 2 ]
          const d = this._haversineKm(lat1, lon1, lat2, lon2)
          L.marker(mid, {
            icon: L.divIcon({
              className: 'route-seg-label',
              html: `<span>${d.toFixed(2)} km</span>`,
              iconSize: [0, 0],
              iconAnchor: [0, 0]
            }),
            interactive: false
          }).addTo(this._routeLayer)
        }
      }
    },
    // 绘制规划完成的最终路线（蓝色），支持悬停高亮与方向箭头（简易）
    renderPlannedRoute() {
      if (!this.map || !this._plannedLayer) return
      if (this._zooming) { this._pendingPlannedRender = true; return }
      this._plannedLayer.clearLayers()
      if (!Array.isArray(this.plannedPath) || this.plannedPath.length < 2) return
      const latlngs = this.plannedPath.filter(p => Array.isArray(p) && p.length === 2)
      if (latlngs.length < 2) return
      const poly = L.polyline(latlngs, { color: '#1e6bd6', weight: 5, opacity: 0.9, smoothFactor: 1.2 })
      poly.on('mouseover', () => poly.setStyle({ color: '#ff9800', weight: 8 }))
      poly.on('mouseout', () => poly.setStyle({ color: '#1e6bd6', weight: 5 }))
      poly.addTo(this._plannedLayer)
      // 简易方向箭头：在每段中点放置一个箭头图标（指向下一点）
      for (let i = 0; i < latlngs.length - 1; i++) {
        const [lat1, lon1] = latlngs[i]
        const [lat2, lon2] = latlngs[i + 1]
        const mid = [ (lat1 + lat2) / 2, (lon1 + lon2) / 2 ]
        const angle = Math.atan2(lat2 - lat1, lon2 - lon1) * 180 / Math.PI
        L.marker(mid, {
          icon: L.divIcon({
            className: 'planned-arrow',
            html: `<div style="transform: rotate(${angle}deg)">➤</div>`,
            iconSize: [20,20],
            iconAnchor: [10,10]
          }),
          interactive: false
        }).addTo(this._plannedLayer)
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
    // 在动画前先判断地图是否就绪并且容器可见
    canAnimate() {
      try {
        const el = this.$refs.mapContainer
        const visible = el && el.offsetParent !== null
        return !!(this.map && this._mapReady && visible)
      } catch (e) {
        return false
      }
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
.planned-arrow div {
  color: #1e6bd6;
  font-size: 16px;
  text-shadow: 0 0 2px rgba(0,0,0,0.4);
}
</style>
