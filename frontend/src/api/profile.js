import axios from './index'

// 获取用户资料
export function getProfile() {
  return axios.get('/api/auth/profile')
}

// 更新用户资料
export function updateProfile(data) {
  return axios.put('/api/auth/profile', data)
}

// 获取当前用户信息
export function getCurrentUser() {
  return axios.get('/api/auth/me')
}
