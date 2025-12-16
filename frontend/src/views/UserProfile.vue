<template>
  <div class="min-h-[calc(100vh-64px)] bg-slate-50 py-10 px-4 sm:px-6 lg:px-10">
    <div class="max-w-5xl mx-auto space-y-8">
      <!-- Hero -->
      <div class="bg-gradient-to-br from-brand-600 via-brand-500 to-brand-400 text-white rounded-[32px] shadow-xl overflow-hidden">
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 p-8">
          <div class="flex items-center gap-4">
            <div class="relative">
              <img v-if="avatarPreview" :src="avatarPreview" alt="头像" class="w-20 h-20 rounded-[24px] object-cover border-4 border-white/30 shadow-lg" />
              <div v-else class="w-20 h-20 rounded-[24px] bg-white/20 backdrop-blur flex items-center justify-center text-3xl font-semibold">
                {{ avatarInitial }}
              </div>
              <span class="absolute -bottom-2 -right-2 bg-white text-brand-600 text-xs font-bold px-3 py-1 rounded-full shadow">旅人</span>
            </div>
            <div>
              <p class="text-xs uppercase tracking-[0.4em] text-white/60">Profile</p>
              <h1 class="text-3xl font-semibold">{{ profile.username || '旅行者' }}</h1>
              <p class="text-sm text-white/80 max-w-md mt-1">{{ form.travel_persona || form.bio || '记录每一次风景，让旅程更有温度。' }}</p>
            </div>
          </div>
          <div class="flex flex-col items-start md:items-end gap-3 w-full md:w-auto">
            <router-link to="/" class="inline-flex items-center gap-2 px-4 py-2 bg-white/10 text-white rounded-full text-sm font-semibold hover:bg-white/20 transition">
              <i class="bi bi-arrow-left"></i> 返回首页
            </router-link>
            <p class="text-xs text-white/70">最后更新：{{ profile.updated_at ? formatDate(profile.updated_at) : '从未更新' }}</p>
          </div>
        </div>
      </div>

      <!-- Profile Highlights -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div v-for="item in profileHighlights" :key="item.label" class="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-4">
          <p class="text-[11px] uppercase tracking-[0.3em] text-slate-400">{{ item.label }}</p>
          <p class="text-3xl font-semibold text-slate-900 mt-2">{{ item.value }}</p>
          <p class="text-xs text-slate-500 mt-1">{{ item.desc }}</p>
        </div>
      </div>

      <!-- Form card -->
      <div class="bg-white shadow-xl rounded-[32px] border border-slate-100 overflow-hidden">
        <div class="px-6 sm:px-10 py-6 border-b border-slate-100">
          <h4 class="text-2xl font-semibold text-slate-900">基本资料</h4>
          <p class="text-sm text-slate-500 mt-1">完善你的旅程档案，个性化推荐将更加精准。</p>
        </div>
        <div class="p-6 sm:p-10">
          <div v-if="loading" class="flex justify-center py-12">
            <span class="w-10 h-10 border-4 border-brand-200 border-t-transparent rounded-full animate-spin"></span>
          </div>
          <div v-else>
            <form @submit.prevent="handleSubmit" class="space-y-6">
              <div class="grid grid-cols-1 gap-y-6 gap-x-6 sm:grid-cols-6">
                <div class="sm:col-span-3">
                  <label class="block text-sm font-medium text-slate-600 mb-1">用户名</label>
                  <input type="text" :value="profile.username" disabled class="block w-full rounded-2xl border border-slate-200 bg-slate-50 text-slate-500 px-4 py-2.5 text-sm">
                  <p class="mt-1 text-xs text-slate-400">用户名不可修改</p>
                </div>
                <div class="sm:col-span-3">
                  <label for="email" class="block text-sm font-medium text-slate-600 mb-1">邮箱</label>
                  <input id="email" type="email" v-model="form.email" placeholder="请输入邮箱" class="block w-full rounded-2xl border border-slate-200 px-4 py-2.5 text-sm focus:border-brand-500 focus:ring-2 focus:ring-brand-100">
                </div>
                <div class="sm:col-span-2">
                  <label for="age" class="block text-sm font-medium text-slate-600 mb-1">年龄</label>
                  <input id="age" type="number" min="0" max="150" v-model.number="form.age" placeholder="年龄" class="block w-full rounded-2xl border border-slate-200 px-4 py-2.5 text-sm focus:border-brand-500 focus:ring-2 focus:ring-brand-100">
                </div>
                <div class="sm:col-span-4">
                  <label for="occupation" class="block text-sm font-medium text-slate-600 mb-1">职业</label>
                  <input id="occupation" type="text" v-model="form.occupation" placeholder="请输入职业，如：学生、程序员、教师等" class="block w-full rounded-2xl border border-slate-200 px-4 py-2.5 text-sm focus:border-brand-500 focus:ring-2 focus:ring-brand-100">
                </div>
                <div class="sm:col-span-6">
                  <label for="bio" class="block text-sm font-medium text-slate-600 mb-1">个人简介</label>
                  <textarea id="bio" v-model="form.bio" rows="4" placeholder="介绍一下自己吧..." class="block w-full rounded-2xl border border-slate-200 px-4 py-2.5 text-sm focus:border-brand-500 focus:ring-2 focus:ring-brand-100"></textarea>
                </div>
                <div class="sm:col-span-6">
                  <label for="travelPersona" class="block text-sm font-medium text-slate-600 mb-1">旅行画像 / 风格</label>
                  <textarea id="travelPersona" v-model="form.travel_persona" rows="3" placeholder="例如：慢旅行爱好者，偏爱在海边住两晚、在城市里住一晚" class="block w-full rounded-2xl border border-slate-200 px-4 py-2.5 text-sm focus:border-brand-500 focus:ring-2 focus:ring-brand-100"></textarea>
                  <p class="mt-1 text-xs text-slate-400">这段描述会被行程推荐与 AI 助手引用。</p>
                </div>
                <div class="sm:col-span-6">
                  <label for="favoriteCities" class="block text-sm font-medium text-slate-600 mb-1">常去 / 向往的城市</label>
                  <textarea id="favoriteCities" v-model="form.favorite_cities" rows="2" placeholder="使用逗号或换行分隔，如：成都，青岛，札幌" class="block w-full rounded-2xl border border-slate-200 px-4 py-2.5 text-sm focus:border-brand-500 focus:ring-2 focus:ring-brand-100"></textarea>
                  <p class="mt-1 text-xs text-slate-400">后续将用于城市推荐与酒店/餐厅筛选。</p>
                  <div v-if="favoriteCitiesChips.length" class="flex flex-wrap gap-2 mt-2">
                    <span v-for="city in favoriteCitiesChips" :key="city" class="px-3 py-1 rounded-full bg-brand-50 text-brand-700 text-xs font-semibold">{{ city }}</span>
                  </div>
                </div>
                <div class="sm:col-span-6">
                  <label for="avatar" class="block text-sm font-medium text-slate-600 mb-1">头像 URL</label>
                  <div class="flex flex-col sm:flex-row gap-4 items-start">
                    <div class="flex-1 w-full">
                      <input id="avatar" type="url" v-model="form.avatar" placeholder="请输入头像图片链接" class="block w-full rounded-2xl border border-slate-200 px-4 py-2.5 text-sm focus:border-brand-500 focus:ring-2 focus:ring-brand-100">
                      <p class="mt-1 text-xs text-slate-400">可选，输入头像图片的网址</p>
                    </div>
                    <div class="flex-shrink-0">
                      <img v-if="avatarPreview" :src="avatarPreview" alt="头像预览" class="h-16 w-16 rounded-2xl object-cover border border-slate-100 shadow" />
                      <div v-else class="h-16 w-16 rounded-2xl bg-slate-100 flex items-center justify-center text-lg font-semibold text-slate-500">{{ avatarInitial }}</div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="pt-4 border-t border-slate-100 flex justify-end">
                <button type="submit" class="inline-flex justify-center items-center gap-2 py-3 px-8 rounded-2xl text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500 disabled:opacity-50" :disabled="submitting">
                  <span v-if="submitting" class="inline-flex items-center gap-2">
                    <span class="w-4 h-4 border-2 border-white/40 border-t-transparent rounded-full animate-spin"></span>
                    保存中...
                  </span>
                  <span v-else>保存修改</span>
                </button>
              </div>
            </form>

            <div v-if="message" class="mt-6 rounded-2xl p-4 border" :class="messageType === 'success' ? 'bg-green-50 text-green-700 border-green-100' : 'bg-rose-50 text-rose-700 border-rose-100'">
              <div class="flex items-start gap-3">
                <i class="bi" :class="messageType === 'success' ? 'bi-check-circle-fill' : 'bi-x-circle-fill'"></i>
                <p class="text-sm font-medium">{{ message }}</p>
              </div>
            </div>

            <div class="mt-10 pt-6 border-t border-slate-100">
              <h6 class="text-xs font-bold text-slate-400 uppercase tracking-[0.4em] mb-3">账户信息</h6>
              <div class="flex flex-col sm:flex-row gap-3 text-xs text-slate-500">
                <p>注册时间: {{ profile.created_at ? formatDate(profile.created_at) : '未知' }}</p>
                <p>最后更新: {{ profile.updated_at ? formatDate(profile.updated_at) : '从未更新' }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getProfile, updateProfile } from '../api/profile'

export default {
  name: 'UserProfile',
  data() {
    return {
      loading: true,
      submitting: false,
      message: '',
      messageType: 'success',
      profile: {},
      form: {
        email: '',
        age: null,
        occupation: '',
        bio: '',
        avatar: '',
        travel_persona: '',
        favorite_cities: ''
      }
    }
  },
  mounted() {
    this.loadProfile()
  },
  computed: {
    avatarPreview() {
      return (this.form.avatar && this.form.avatar.trim()) || this.profile.avatar || ''
    },
    avatarInitial() {
      const source = this.profile.username || '旅'
      return source.slice(0, 1).toUpperCase()
    },
    favoriteCitiesChips() {
      const source = (this.form.favorite_cities || this.profile.favorite_cities || '')
      return source
        .split(/[,，\n]/)
        .map(item => item.trim())
        .filter(Boolean)
        .slice(0, 6)
    },
    profileHighlights() {
      const diaryValue = this.profile.diary_count ?? '--'
      const personaRaw = this.form.travel_persona || this.profile.travel_persona || '待补充画像'
      const personaValue = personaRaw.length > 18 ? `${personaRaw.slice(0, 18)}…` : personaRaw
      const citiesValue = this.favoriteCitiesChips.length ? this.favoriteCitiesChips.join(' · ') : '尚未填写'
      return [
        { label: '已保存日记', value: diaryValue, desc: '实时同步 Travel Diary' },
        { label: '旅行画像', value: personaValue, desc: '用于推荐与 AI 助手' },
        { label: '偏好城市', value: citiesValue, desc: '逗号分隔可填写多个城市' }
      ]
    }
  },
  methods: {
    async loadProfile() {
      try {
        const res = await getProfile()
        if (res.data.status === 'success') {
          this.profile = res.data.data
          // 填充表单
          this.form.email = this.profile.email || ''
          this.form.age = this.profile.age
          this.form.occupation = this.profile.occupation || ''
          this.form.bio = this.profile.bio || ''
          this.form.avatar = this.profile.avatar || ''
          this.form.travel_persona = this.profile.travel_persona || ''
          this.form.favorite_cities = this.profile.favorite_cities || ''
        }
      } catch (error) {
        console.error('加载资料失败:', error)
        if (error.response?.status === 401) {
          this.$router.push('/login')
        } else {
          this.showMessage('加载资料失败，请刷新重试', 'error')
        }
      } finally {
        this.loading = false
      }
    },
    async handleSubmit() {
      this.submitting = true
      this.message = ''
      
      try {
        const res = await updateProfile(this.form)
        if (res.data.status === 'success') {
          this.showMessage('资料保存成功！', 'success')
          // 重新加载资料
          setTimeout(() => {
            this.loadProfile()
          }, 800)
        }
      } catch (error) {
        console.error('保存失败:', error)
        const msg = error.response?.data?.message || '保存失败，请重试'
        this.showMessage(msg, 'error')
      } finally {
        this.submitting = false
      }
    },
    showMessage(text, type) {
      this.message = text
      this.messageType = type
      setTimeout(() => {
        this.message = ''
      }, 3000)
    },
    formatDate(dateStr) {
      if (!dateStr) return '未知'
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN')
    }
  }
}
</script>
