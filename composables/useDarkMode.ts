const isDark = ref(false)

export function useDarkMode() {
  function apply(dark: boolean) {
    isDark.value = dark
    if (dark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('dark-mode', dark ? '1' : '0')
  }

  function init() {
    const stored = localStorage.getItem('dark-mode')
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    apply(stored !== null ? stored === '1' : prefersDark)
  }

  function toggle() {
    apply(!isDark.value)
  }

  return { isDark, init, toggle }
}
