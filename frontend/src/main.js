import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Global styles: Bootstrap and Leaflet CSS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import 'leaflet/dist/leaflet.css'

const app = createApp(App)

// 全局错误处理器：捕获 Leaflet 缩放期间的错误，避免红色界面
app.config.errorHandler = (err, instance, info) => {
  // 静默处理 Leaflet 地图相关的缩放错误
  if (err && err.message && (
    err.message.includes('_animateZoom') || 
    err.message.includes('Cannot read properties of null') ||
    err.message.includes('leaflet') ||
    err.message.includes('map')
  )) {
    console.warn('[App] 地图缩放动画错误已自动处理:', err.message)
    return
  }
  // 其他错误正常抛出
  console.error('[App] 运行时错误:', err, info)
}

app.use(router)
app.mount('#app')
