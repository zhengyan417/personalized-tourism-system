<template>
  <div class="container py-4" style="max-width: 480px;">
    <h3 class="mb-3">登录 / 注册</h3>
    <div class="card mb-3">
      <div class="card-body">
        <div class="mb-3">
          <label class="form-label">用户名</label>
          <input v-model="form.username" type="text" class="form-control" placeholder="输入用户名">
        </div>
        <div class="mb-3">
          <label class="form-label">密码</label>
          <input v-model="form.password" type="password" class="form-control" placeholder="输入密码">
        </div>
        <div class="mb-3">
          <label class="form-label">邮箱（注册可选）</label>
          <input v-model="form.email" type="email" class="form-control" placeholder="example@domain.com">
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-primary" @click="onLogin" :disabled="loading">登录</button>
          <button class="btn btn-outline-secondary" @click="onRegister" :disabled="loading">注册</button>
        </div>
        <div v-if="message" class="mt-3 alert" :class="messageTypeClass">{{ message }}</div>
      </div>
    </div>
    <div v-if="user" class="alert alert-success">
      已登录：{{ user.username }}
      <div class="mt-2 d-flex gap-2">
        <router-link to="/profile" class="btn btn-sm btn-outline-primary">
          <i class="bi bi-person-circle"></i> 个人资料
        </router-link>
        <button class="btn btn-sm btn-outline-secondary" @click="onLogout">
          <i class="bi bi-box-arrow-right"></i> 退出
        </button>
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
  computed: {
    messageTypeClass() {
      return this.messageType === 'error' ? 'alert-danger' : 'alert-info'
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

<style scoped>
</style>
