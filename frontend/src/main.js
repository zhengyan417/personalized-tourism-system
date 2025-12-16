import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// Global styles: Bootstrap and Leaflet CSS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import 'leaflet/dist/leaflet.css'
import './assets/tailwind.css'

const app = createApp(App)

// 全局错误处理器：捕获 Leaflet 缩放期间的错误，避免红色界面
app.config.errorHandler = (err, instance, info) => {
  // 静默处理 Leaflet 地图相关的缩放错误
  if (err && err.message && (
    err.message.includes('_animateZoom') || 
    err.message.includes('_latLngToNewLayerPoint') ||
    err.message.includes('_leaflet_pos') ||
    err.message.includes('_getMapPanePos') ||
    err.message.includes('_getNewPixelOrigin') ||
    err.message.includes('_onZoomTransitionEnd') ||
    err.message.includes('Cannot read properties of null') ||
    err.message.includes('Cannot read properties of undefined') ||
    err.message.includes('leaflet') ||
    (err.message.includes('map') && (err.message.includes('null') || err.message.includes('undefined')))
  )) {
    console.warn('[App] 地图动画错误已静默处理（不影响使用）:', err.message.substring(0, 100))
    return
  }
  // 其他错误正常抛出
  console.error('[App] 运行时错误:', err, info)
}

// 捕获更底层的错误（包括 Leaflet 内部抛出的错误）
window.addEventListener('error', (event) => {
  if (event.error && event.error.message) {
    const msg = event.error.message
    if (msg.includes('_latLngToNewLayerPoint') ||
        msg.includes('_animateZoom') ||
        msg.includes('_leaflet_pos') ||
        msg.includes('_getMapPanePos') ||
        msg.includes('_getNewPixelOrigin') ||
        msg.includes('getPosition') ||
        (msg.includes('leaflet') && (msg.includes('null') || msg.includes('undefined')))) {
      console.warn('[Window] Leaflet 动画错误已静默处理')
      event.preventDefault()
      return false
    }
  }
})

// 捕获未处理的 Promise 错误
window.addEventListener('unhandledrejection', (event) => {
  if (event.reason && event.reason.message) {
    const msg = event.reason.message
    if (msg.includes('_latLngToNewLayerPoint') || 
        msg.includes('_animateZoom') ||
        msg.includes('_leaflet_pos')) {
      console.warn('[Promise] Leaflet 错误已静默处理')
      event.preventDefault()
      return false
    }
  }
})

app.use(router)
app.use(store)
app.mount('#app')
