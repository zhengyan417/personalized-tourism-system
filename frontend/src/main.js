import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Global styles: Bootstrap and Leaflet CSS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import 'leaflet/dist/leaflet.css'

const app = createApp(App)
app.use(router)
app.mount('#app')
