import { createRouter, createWebHashHistory } from 'vue-router'

import Home from '../views/Home.vue'
import PlaceQuery from '../views/PlaceQuery.vue'
import Recommendation from '../views/Recommendation.vue'
import RoutePlanning from '../views/RoutePlanning.vue'
import TravelDiary from '../views/TravelDiary.vue'

const routes = [
	{ path: '/', name: 'Home', component: Home },
	{ path: '/place', name: 'PlaceQuery', component: PlaceQuery },
	{ path: '/recommendation', name: 'Recommendation', component: Recommendation },
	{ path: '/route', name: 'RoutePlanning', component: RoutePlanning },
	{ path: '/diary', name: 'TravelDiary', component: TravelDiary }
]

const router = createRouter({
	history: createWebHashHistory(),
	routes
})

export default router
