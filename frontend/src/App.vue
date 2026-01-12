<template>
	<div id="app" class="min-h-screen bg-gray-50 font-sans text-gray-900 flex flex-col">
		<nav class="bg-white border-b border-brand-100 shadow-sm sticky top-0 z-50">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="flex justify-between h-16">
					<div class="flex items-center">
						<router-link to="/" class="flex-shrink-0 flex items-center gap-2 cursor-pointer no-underline">
							<div class="bg-brand-500 p-1.5 rounded-lg">
								<i class="bi bi-compass text-white text-xl"></i>
							</div>
							<span class="font-bold text-xl text-gray-800 tracking-tight">简途 <span class="text-brand-500 text-sm font-normal">Jiantu</span></span>
						</router-link>
						<div class="hidden sm:ml-8 sm:flex sm:space-x-8">
							<router-link to="/" class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium h-full transition-colors no-underline" :class="$route.path === '/' ? 'border-brand-500 text-gray-900' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'">
								<i class="bi bi-map mr-2"></i> 行程规划
							</router-link>
							<router-link to="/community" class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium h-full transition-colors no-underline" :class="$route.path.startsWith('/community') || $route.path.startsWith('/diary') ? 'border-brand-500 text-gray-900' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'">
								<i class="bi bi-people mr-2"></i> 旅行社区
							</router-link>
							<router-link v-if="isLoggedIn" to="/profile" class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium h-full transition-colors no-underline" :class="$route.path === '/profile' ? 'border-brand-500 text-gray-900' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'">
								<i class="bi bi-person mr-2"></i> 个人中心
							</router-link>
						</div>
					</div>
					<div class="flex items-center gap-4">
						<ThemeToggle />
						<div v-if="!isLoggedIn" class="flex items-center gap-2">
							<router-link to="/login" class="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium no-underline">登录</router-link>
							<router-link to="/login" class="bg-brand-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-brand-700 transition-colors shadow-sm no-underline">注册</router-link>
						</div>
						<div v-else class="relative ml-3">
							<div class="dropdown">
								<button class="flex items-center max-w-xs bg-white rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500" type="button" data-bs-toggle="dropdown" aria-expanded="false">
									<span class="sr-only">Open user menu</span>
									<img class="h-8 w-8 rounded-full object-cover border border-gray-200" :src="user?.avatar || `https://ui-avatars.com/api/?name=${username}&background=0ea5e9&color=fff`" alt="">
									<span class="ml-2 text-sm font-medium text-gray-700 hidden md:block">{{ username }}</span>
									<i class="bi bi-chevron-down ml-1 text-xs text-gray-400 hidden md:block"></i>
								</button>
								<ul class="dropdown-menu dropdown-menu-end shadow-lg border-0 rounded-xl mt-2">
									<li><router-link class="dropdown-item px-4 py-2 text-sm text-gray-700 hover:bg-gray-50" to="/profile"><i class="bi bi-person me-2"></i>个人资料</router-link></li>
									<li><hr class="dropdown-divider my-1"></li>
									<li><a class="dropdown-item px-4 py-2 text-sm text-red-600 hover:bg-red-50" href="#" @click.prevent="handleLogout"><i class="bi bi-box-arrow-right me-2"></i>退出登录</a></li>
								</ul>
							</div>
						</div>
					</div>
				</div>
			</div>
		</nav>

		<main class="flex-1 relative">
			<router-view @user-logged-in="checkLoginStatus" @user-logged-out="checkLoginStatus" />
		</main>
		
		<!-- AI 助手组件 -->
		<AiAssistant v-if="isLoggedIn" :userProfile="user" :userId="user ? user.user_id : ''" />
	</div>
</template>

<script>
import ThemeToggle from './components/ui/ThemeToggle.vue'
import AiAssistant from './components/AiAssistant.vue'
import { me, logout } from './api/auth'

export default {
	name: 'App',
	components: { ThemeToggle, AiAssistant },
	data() {
		return {
			isLoggedIn: false,
			username: '',
			user: null
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
					this.user = data.data
					this.username = data.data.username || '用户'
				} else {
					this.isLoggedIn = false
					this.user = null
					this.username = ''
				}
			} catch {
				this.isLoggedIn = false
				this.user = null
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
			this.user = null
			this.username = ''
			// 退出登录后跳转到登录页
			this.$router.push('/login')
		}
	}
}
</script>

<style>
/* Global styles handled by Tailwind */
</style>
