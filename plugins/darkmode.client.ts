export default defineNuxtPlugin(() => {
  const { init } = useDarkMode()
  init()
})
