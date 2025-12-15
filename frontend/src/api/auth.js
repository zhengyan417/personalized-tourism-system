import api from './index'

export function register({ username, password, email }) {
  return api.post('/api/auth/register', { username, password, email })
}

export function login({ username, password }) {
  return api.post('/api/auth/login', { username, password })
}

export function logout() {
  return api.post('/api/auth/logout')
}

export function me() {
  return api.get('/api/auth/me')
}
