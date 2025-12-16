import { createRouter, createWebHashHistory } from 'vue-router'

import Home from '../views/Home.vue'
import PlaceQuery from '../views/PlaceQuery.vue'
import Recommendation from '../views/Recommendation.vue'
import RoutePlanning from '../views/RoutePlanning.vue'
import TravelDiary from '../views/TravelDiary.vue'
import Login from '../views/Login.vue'
import UserProfile from '../views/UserProfile.vue'

const routes = [
	{ path: '/', name: 'Home', component: Home },
	{ path: '/place', name: 'PlaceQuery', component: PlaceQuery },
	{ path: '/recommendation', name: 'Recommendation', component: Recommendation },
	{ path: '/route', name: 'RoutePlanning', component: RoutePlanning },
	{ path: '/diary', name: 'TravelDiary', component: TravelDiary },
	{ path: '/login', name: 'Login', component: Login },
	{ path: '/profile', name: 'UserProfile', component: UserProfile }
]

const router = createRouter({
	history: createWebHashHistory(),
	routes
})

// 添加路由守卫，在导航前确保地图动画完成
router.beforeEach((to, from, next) => {
	// 给当前页面的地图组件一点时间停止动画
	if (from.name) {
		// 使用 setTimeout 0 确保当前事件循环完成
		setTimeout(() => next(), 0)
	} else {
		next()
	}
})

export default router
