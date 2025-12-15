<template>
  <div class="profile-container">
    <div class="container py-4">
      <div class="row">
        <div class="col-md-8 mx-auto">
          <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
              <h4 class="mb-0">
                <i class="bi bi-person-circle"></i> 个人资料
              </h4>
            </div>
            <div class="card-body">
              <!-- 加载状态 -->
              <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">加载中...</span>
                </div>
              </div>

              <!-- 资料表单 -->
              <form v-else @submit.prevent="handleSubmit">
                <!-- 用户名（只读） -->
                <div class="mb-3">
                  <label class="form-label">用户名</label>
                  <input type="text" class="form-control" :value="profile.username" disabled>
                  <small class="text-muted">用户名不可修改</small>
                </div>

                <!-- 邮箱 -->
                <div class="mb-3">
                  <label for="email" class="form-label">邮箱</label>
                  <input 
                    type="email" 
                    class="form-control" 
                    id="email" 
                    v-model="form.email"
                    placeholder="请输入邮箱"
                  >
                </div>

                <!-- 年龄 -->
                <div class="mb-3">
                  <label for="age" class="form-label">年龄</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    id="age" 
                    v-model.number="form.age"
                    min="0" 
                    max="150"
                    placeholder="请输入年龄"
                  >
                </div>

                <!-- 职业 -->
                <div class="mb-3">
                  <label for="occupation" class="form-label">职业</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="occupation" 
                    v-model="form.occupation"
                    placeholder="请输入职业，如：学生、程序员、教师等"
                  >
                </div>

                <!-- 个人简介 -->
                <div class="mb-3">
                  <label for="bio" class="form-label">个人简介</label>
                  <textarea 
                    class="form-control" 
                    id="bio" 
                    v-model="form.bio"
                    rows="4"
                    placeholder="介绍一下自己吧..."
                  ></textarea>
                </div>

                <!-- 头像URL -->
                <div class="mb-3">
                  <label for="avatar" class="form-label">头像URL</label>
                  <input 
                    type="url" 
                    class="form-control" 
                    id="avatar" 
                    v-model="form.avatar"
                    placeholder="请输入头像图片链接"
                  >
                  <small class="text-muted">可选，输入头像图片的网址</small>
                  <div v-if="form.avatar" class="mt-2">
                    <img :src="form.avatar" alt="头像预览" class="avatar-preview">
                  </div>
                </div>

                <!-- 提交按钮 -->
                <div class="d-grid gap-2">
                  <button type="submit" class="btn btn-primary" :disabled="submitting">
                    <span v-if="submitting">
                      <span class="spinner-border spinner-border-sm me-2"></span>
                      保存中...
                    </span>
                    <span v-else>
                      <i class="bi bi-check-circle"></i> 保存资料
                    </span>
                  </button>
                  <button type="button" class="btn btn-outline-secondary" @click="$router.back()">
                    <i class="bi bi-arrow-left"></i> 返回
                  </button>
                </div>
              </form>

              <!-- 提示信息 -->
              <div v-if="message" class="alert mt-3" :class="messageType === 'success' ? 'alert-success' : 'alert-danger'">
                {{ message }}
              </div>
            </div>
          </div>

          <!-- 账户信息 -->
          <div class="card shadow-sm mt-3">
            <div class="card-body">
              <h6 class="text-muted">账户信息</h6>
              <p class="mb-1"><small>注册时间: {{ profile.created_at ? formatDate(profile.created_at) : '未知' }}</small></p>
              <p class="mb-0"><small>最后更新: {{ profile.updated_at ? formatDate(profile.updated_at) : '从未更新' }}</small></p>
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
        avatar: ''
      }
    }
  },
  mounted() {
    this.loadProfile()
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
          }, 1000)
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

<style scoped>
.profile-container {
  min-height: 80vh;
  background-color: #f8f9fa;
}

.avatar-preview {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 50%;
  border: 2px solid #dee2e6;
}

.card {
  border-radius: 8px;
}

.card-header {
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

label {
  font-weight: 500;
}

.bi {
  margin-right: 0.25rem;
}
</style>
