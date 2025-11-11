<template>
  <div class="dropdown">
    <button class="btn btn-outline-secondary btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
      {{ label }}
    </button>
    <ul class="dropdown-menu dropdown-menu-end">
      <li><a class="dropdown-item" href="#" @click.prevent="setTheme('light')">白天模式</a></li>
      <li><a class="dropdown-item" href="#" @click.prevent="setTheme('dark')">夜间模式</a></li>
      <li><hr class="dropdown-divider" /></li>
      <li><a class="dropdown-item" href="#" @click.prevent="setTheme('auto')">跟随系统</a></li>
    </ul>
  </div>
</template>

<script>
const THEME_KEY = 'PTS_THEME'

export default {
  name: 'ThemeToggle',
  data() {
    return { theme: 'auto' }
  },
  computed: {
    label() {
      return this.theme === 'dark' ? '夜间模式' : this.theme === 'light' ? '白天模式' : '跟随系统'
    }
  },
  mounted() {
    // 读取持久化主题
    const saved = window.localStorage.getItem(THEME_KEY)
    if (saved) this.theme = saved
    this.applyTheme()
    // 当系统主题变更时，若为 auto 则自动切换
    try {
      this._mq = window.matchMedia('(prefers-color-scheme: dark)')
      this._mq.addEventListener?.('change', this.onSystemThemeChange)
      this._mq.addListener?.(this.onSystemThemeChange) // 兼容旧浏览器
    } catch {}
  },
  beforeUnmount() {
    try {
      this._mq?.removeEventListener?.('change', this.onSystemThemeChange)
      this._mq?.removeListener?.(this.onSystemThemeChange)
    } catch {}
  },
  methods: {
    onSystemThemeChange() { if (this.theme === 'auto') this.applyTheme() },
    setTheme(t) {
      this.theme = t
      window.localStorage.setItem(THEME_KEY, t)
      this.applyTheme()
    },
    applyTheme() {
      const doc = document.documentElement
      if (this.theme === 'auto') {
        const dark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
        doc.setAttribute('data-bs-theme', dark ? 'dark' : 'light')
      } else {
        doc.setAttribute('data-bs-theme', this.theme)
      }
    }
  }
}
</script>

<style scoped>
</style>