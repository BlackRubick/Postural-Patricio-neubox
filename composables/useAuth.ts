export const useAuth = () => {
  const user = useState<{ id: number; email: string; name?: string | null; role: string } | null>('auth_user', () => null)

  const fetchUser = async () => {
    try {
      user.value = await $fetch('/api/auth/me')
    } catch {
      user.value = null
    }
  }

  const login = async (email: string, password: string) => {
    const data = await $fetch<{ user: typeof user.value }>('/api/auth/login', {
      method: 'POST',
      body: { email, password },
    })
    user.value = data.user
    return data
  }

  const logout = async () => {
    await $fetch('/api/auth/logout', { method: 'POST' })
    user.value = null
    await navigateTo('/login')
  }

  return { user, fetchUser, login, logout }
}
