import { createStore } from 'vuex'

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

export default createStore({ modules: { routePlanning } })
