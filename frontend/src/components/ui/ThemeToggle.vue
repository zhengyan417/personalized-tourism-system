<template>
  <div class="relative" ref="dropdown">
    <button 
      class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors" 
      @click="isOpen = !isOpen"
    >
      <i class="bi" :class="icon"></i>
      <span class="hidden sm:inline">{{ label }}</span>
    </button>
    
    <div v-if="isOpen" class="absolute right-0 mt-2 w-36 bg-white rounded-xl shadow-lg border border-gray-100 py-1 z-50">
      <button class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2" @click="setTheme('light')">
        <i class="bi bi-sun"></i> 白天模式
      </button>
      <button class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2" @click="setTheme('dark')">
        <i class="bi bi-moon"></i> 夜间模式
      </button>
      <div class="border-t border-gray-100 my-1"></div>
      <button class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2" @click="setTheme('auto')">
        <i class="bi bi-display"></i> 跟随系统
      </button>
    </div>
  </div>
</template>

<script>
const THEME_KEY = 'PTS_THEME'

export default {
  name: 'ThemeToggle',
  data() {
    return { theme: 'auto', isOpen: false }
  },
  computed: {
    label() {
      return this.theme === 'dark' ? '夜间' : this.theme === 'light' ? '白天' : '自动'
    },
    icon() {
      return this.theme === 'dark' ? 'bi-moon' : this.theme === 'light' ? 'bi-sun' : 'bi-display'
    }
  },
  mounted() {
    const saved = window.localStorage.getItem(THEME_KEY)
    if (saved) this.theme = saved
    this.applyTheme()
    try {
      this._mq = window.matchMedia('(prefers-color-scheme: dark)')
      this._mq.addEventListener?.('change', this.onSystemThemeChange)
      this._mq.addListener?.(this.onSystemThemeChange)
    } catch {}
    document.addEventListener('click', this.closeDropdown)
  },
  beforeUnmount() {
    try {
      this._mq?.removeEventListener?.('change', this.onSystemThemeChange)
      this._mq?.removeListener?.(this.onSystemThemeChange)
    } catch {}
    document.removeEventListener('click', this.closeDropdown)
  },
  methods: {
    closeDropdown(e) {
      if (this.$refs.dropdown && !this.$refs.dropdown.contains(e.target)) {
        this.isOpen = false
      }
    },
    onSystemThemeChange() { if (this.theme === 'auto') this.applyTheme() },
    setTheme(t) {
      this.theme = t
      window.localStorage.setItem(THEME_KEY, t)
      this.applyTheme()
      this.isOpen = false
    },
    applyTheme() {
      const doc = document.documentElement
      let isDark = false
      if (this.theme === 'auto') {
        isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      } else {
        isDark = this.theme === 'dark'
      }
      
      if (isDark) {
        doc.classList.add('dark')
      } else {
        doc.classList.remove('dark')
      }
    }
  }
}
</script>