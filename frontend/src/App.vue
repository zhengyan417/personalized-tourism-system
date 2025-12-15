<template>
	<div id="app">
		<nav class="navbar navbar-expand-lg sticky-top bg-body-tertiary shadow-sm">
			<div class="container-fluid">
				<a class="navbar-brand fw-bold" href="#/">简途</a>
				<button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
					<span class="navbar-toggler-icon"></span>
				</button>
				<div class="collapse navbar-collapse" id="navbarNav">
					<ul class="navbar-nav me-auto">
						<li class="nav-item"><router-link class="nav-link" to="/">首页</router-link></li>
						<li class="nav-item"><router-link class="nav-link" to="/place">地点查询</router-link></li>
						<li class="nav-item"><router-link class="nav-link" to="/recommendation">推荐</router-link></li>
						<li class="nav-item"><router-link class="nav-link" to="/route">路径规划</router-link></li>
						<li class="nav-item"><router-link class="nav-link" to="/diary">旅行日记</router-link></li>
						<li class="nav-item" v-if="isLoggedIn"><router-link class="nav-link" to="/profile">个人资料</router-link></li>
					</ul>
					<ul class="navbar-nav ms-auto">
						<li class="nav-item" v-if="!isLoggedIn">
							<router-link class="nav-link" to="/login">登录</router-link>
						</li>
						<li class="nav-item dropdown" v-if="isLoggedIn">
							<a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
								{{ username }}
							</a>
							<ul class="dropdown-menu dropdown-menu-end">
								<li><router-link class="dropdown-item" to="/profile">个人资料</router-link></li>
								<li><hr class="dropdown-divider"></li>
								<li><a class="dropdown-item" href="#" @click.prevent="handleLogout">退出登录</a></li>
							</ul>
						</li>
					</ul>
					<ThemeToggle class="ms-2" />
				</div>
			</div>
		</nav>
		<main class="container py-3">
			<router-view @user-logged-in="checkLoginStatus" @user-logged-out="checkLoginStatus" />
		</main>
	</div>
</template>

<script>
import ThemeToggle from './components/ui/ThemeToggle.vue'
import { me, logout } from './api/auth'

export default {
	name: 'App',
	components: { ThemeToggle },
	data() {
		return {
			isLoggedIn: false,
			username: ''
		}
	},
	async mounted() {
		await this.checkLoginStatus()
	},
	methods: {
		async checkLoginStatus() {
			try {
				const { data } = await me()
				if (data && data.status === 'success' && data.data) {
					this.isLoggedIn = true
					this.username = data.data.username || '用户'
				} else {
					this.isLoggedIn = false
					this.username = ''
				}
			} catch {
				this.isLoggedIn = false
				this.username = ''
			}
		},
		async handleLogout() {
			try {
				await logout()
			} catch (e) {
				console.error('退出登录失败', e)
			}
			this.isLoggedIn = false
			this.username = ''
			// 退出登录后跳转到登录页
			this.$router.push('/login')
		}
	}
}
</script>

<style>
html, body, #app {
	height: 100%;
}
</style>
