<template>
  <div class="min-h-[calc(100vh-64px)] flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white p-8 rounded-2xl shadow-lg border border-gray-100">
      <div>
        <div class="mx-auto h-12 w-12 bg-brand-100 rounded-full flex items-center justify-center text-brand-600 text-2xl">
          <i class="bi bi-person-fill"></i>
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          {{ user ? '已登录' : '登录 / 注册' }}
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600" v-if="!user">
          欢迎回到简途旅行
        </p>
      </div>

      <div v-if="!user" class="mt-8 space-y-6">
        <div class="rounded-md shadow-sm -space-y-px">
          <div class="mb-4">
            <label for="username" class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
            <input id="username" v-model="form.username" type="text" required class="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-brand-500 focus:border-brand-500 focus:z-10 sm:text-sm" placeholder="输入用户名">
          </div>
          <div class="mb-4">
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input id="password" v-model="form.password" type="password" required class="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-brand-500 focus:border-brand-500 focus:z-10 sm:text-sm" placeholder="输入密码">
          </div>
          <div class="mb-4">
            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">邮箱 <span class="text-gray-400 font-normal">(注册可选)</span></label>
            <input id="email" v-model="form.email" type="email" class="appearance-none rounded-lg relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-brand-500 focus:border-brand-500 focus:z-10 sm:text-sm" placeholder="example@domain.com">
          </div>
        </div>

        <div class="flex gap-4">
          <button @click="onLogin" :disabled="loading" class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-brand-600 hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500 disabled:opacity-50 transition-colors">
            <span class="absolute left-0 inset-y-0 flex items-center pl-3" v-if="loading">
              <span class="spinner-border spinner-border-sm w-4 h-4 text-brand-200"></span>
            </span>
            登录
          </button>
          <button @click="onRegister" :disabled="loading" class="group relative w-full flex justify-center py-2 px-4 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500 disabled:opacity-50 transition-colors">
            注册
          </button>
        </div>

        <div v-if="message" class="rounded-md p-4" :class="messageType === 'error' ? 'bg-red-50 text-red-700' : 'bg-blue-50 text-blue-700'">
          <div class="flex">
            <div class="flex-shrink-0">
              <i class="bi" :class="messageType === 'error' ? 'bi-x-circle-fill' : 'bi-check-circle-fill'"></i>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium">{{ message }}</p>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center space-y-4">
        <div class="bg-green-50 text-green-800 p-4 rounded-lg">
          <p class="font-medium">当前登录用户：{{ user.username }}</p>
        </div>
        <div class="flex flex-col gap-3">
          <router-link to="/profile" class="w-full flex justify-center items-center gap-2 py-2 px-4 border border-brand-600 text-sm font-medium rounded-lg text-brand-600 bg-white hover:bg-brand-50 transition-colors">
            <i class="bi bi-person-circle"></i> 个人资料
          </router-link>
          <button @click="onLogout" class="w-full flex justify-center items-center gap-2 py-2 px-4 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 transition-colors">
            <i class="bi bi-box-arrow-right"></i> 退出登录
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { login, register, logout, me } from '@/api/auth'

export default {
  name: 'Login',
  data() {
    return {
      form: { username: '', password: '', email: '' },
      loading: false,
      message: '',
      messageType: 'info',
      user: null
    }
  },
  mounted() {
    this.fetchMe()
  },
  methods: {
    async fetchMe() {
      try {
        const { data } = await me()
        if (data && data.status === 'success') {
          this.user = data.data
        }
      } catch {}
    },
    async onLogin() {
      this.loading = true
      this.message = ''
      try {
        const { data } = await login({ username: this.form.username, password: this.form.password })
        if (data.status === 'success') {
          this.message = '登录成功'
          this.messageType = 'info'
          this.user = data.data
          this.$emit('user-logged-in')
          // 登录成功后跳转到首页
          setTimeout(() => {
            this.$router.push('/')
          }, 500)
        } else {
          this.message = data.message || '登录失败'
          this.messageType = 'error'
        }
      } catch (e) {
        this.message = (e && e.response && e.response.data && e.response.data.message) || '请求失败'
        this.messageType = 'error'
      } finally {
        this.loading = false
      }
    },
    async onRegister() {
      this.loading = true
      this.message = ''
      try {
        const { data } = await register({ username: this.form.username, password: this.form.password, email: this.form.email })
        if (data.status === 'success') {
          this.message = '注册成功，请登录'
          this.messageType = 'info'
        } else {
          this.message = data.message || '注册失败'
          this.messageType = 'error'
        }
      } catch (e) {
        this.message = (e && e.response && e.response.data && e.response.data.message) || '请求失败'
        this.messageType = 'error'
      } finally {
        this.loading = false
      }
    },
    async onLogout() {
      try { await logout() } catch {}
      this.user = null
      this.message = '已退出登录'
      this.messageType = 'info'
      this.$emit('user-logged-out')
      // 退出登录后清空表单，停留在登录页让用户重新登录
      this.form.username = ''
      this.form.password = ''
      this.form.email = ''
    }
  }
}
</script>
