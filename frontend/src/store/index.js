import { createStore } from 'vuex'

// 用户认证模块
const auth = {
	namespaced: true,
	state: () => ({
		user: null, // { id, username, email, ... }
		isLoggedIn: false
	}),
	mutations: {
		setUser(state, user) {
			state.user = user
			state.isLoggedIn = !!user
		},
		logout(state) {
			state.user = null
			state.isLoggedIn = false
		}
	},
	actions: {
		login({ commit }, user) {
			commit('setUser', user)
		},
		logout({ commit }) {
			commit('logout')
		}
	},
	getters: {
		isLoggedIn: state => state.isLoggedIn,
		currentUser: state => state.user,
		userId: state => state.user?.id
	}
}

// 路径规划模块
const routePlanning = {
	namespaced: true,
	state: () => ({
		startPoint: null, // { id,name,latitude,longitude }
		endPoint: null,
		waypoints: [], // array of points
		calculatedRoute: null, // { path: [[lat,lng],...], total_distance }
		currentMode: null, // 'setStart' | 'setEnd' | 'addWaypoint' | null
		loading: false,
		error: ''
	}),
	mutations: {
		setMode(state, mode) { state.currentMode = mode },
		setStart(state, p) { state.startPoint = p },
		setEnd(state, p) { state.endPoint = p },
		addWaypoint(state, p) { state.waypoints.push(p) },
		removeWaypoint(state, index) { state.waypoints.splice(index, 1) },
		clearWaypoints(state) { state.waypoints = [] },
		setCalculatedRoute(state, r) { state.calculatedRoute = r },
		clearRoute(state) { state.calculatedRoute = null },
		clearAll(state) {
			state.startPoint = null
			state.endPoint = null
			state.waypoints = []
			state.calculatedRoute = null
			state.currentMode = null
			state.error = ''
		},
		setLoading(state, v) { state.loading = v },
		setError(state, msg) { state.error = msg }
	},
	actions: {
		addToWaypoints({ commit }, p) { commit('addWaypoint', p) }
	}
}

export default createStore({ 
	modules: { 
		auth,
		routePlanning 
	} 
})
