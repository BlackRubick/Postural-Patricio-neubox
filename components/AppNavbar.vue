<template>
  <header class="navbar">
    <div class="navbar-inner">

      <!-- Brand -->
      <button class="brand" @click="navigateTo('/')">
        <div class="brand-logo">
          <img src="/images/logonegro.jpeg" alt="Logo" />
        </div>
        <div class="brand-text">
          <span class="brand-name">Nexo Postural</span>
          <span class="brand-sub">Kyene'is Pondyam</span>
        </div>
      </button>

      <!-- Nav -->
      <nav class="nav-links">
        <NuxtLink to="/" class="nav-item" :class="{ active: route.path === '/' }">
          <svg width="15" height="15" fill="none" viewBox="0 0 24 24">
            <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span>Pacientes</span>
        </NuxtLink>

        <NuxtLink to="/pacientes/nuevo" class="nav-item" :class="{ active: route.path === '/pacientes/nuevo' }">
          <svg width="15" height="15" fill="none" viewBox="0 0 24 24">
            <path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2M12 7a4 4 0 110 8 4 4 0 010-8zM19 8v6M22 11h-6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span>Nuevo</span>
        </NuxtLink>

        <button
          class="nav-item"
          :class="{ active: route.path.includes('/analisis'), disabled: !patientId }"
          :disabled="!patientId"
          @click="patientId && navigateTo(`/pacientes/${patientId}/analisis`)"
        >
          <svg width="15" height="15" fill="none" viewBox="0 0 24 24">
            <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>Análisis</span>
        </button>

        <NuxtLink
          v-if="user?.role === 'admin'"
          to="/usuarios"
          class="nav-item"
          :class="{ active: route.path.startsWith('/usuarios') }"
        >
          <svg width="15" height="15" fill="none" viewBox="0 0 24 24">
            <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span>Usuarios</span>
        </NuxtLink>
      </nav>

      <!-- Dark mode toggle -->
      <button class="dark-toggle" :title="isDark ? 'Modo claro' : 'Modo oscuro'" @click="toggle">
        <!-- Sun icon (visible in dark mode) -->
        <svg v-if="isDark" width="16" height="16" fill="none" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="2"/>
          <path d="M12 2v2M12 20v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M2 12h2M20 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <!-- Moon icon (visible in light mode) -->
        <svg v-else width="16" height="16" fill="none" viewBox="0 0 24 24">
          <path d="M21 12.79A9 9 0 1111.21 3a7 7 0 009.79 9.79z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <!-- User -->
      <div v-if="user" class="user-area">
        <div class="user-info">
          <span class="user-name">{{ user.name || 'Doctor' }}</span>
          <span class="user-email">{{ user.email }}</span>
        </div>
        <div class="user-avatar">{{ initials }}</div>
        <button class="logout-btn" title="Cerrar sesión" @click="handleLogout">
          <svg width="15" height="15" fill="none" viewBox="0 0 24 24">
            <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Active route indicator bar -->
    <div class="nav-underline"></div>
  </header>
</template>

<script setup>
const route = useRoute()
const patientId = computed(() => route.params.id || null)
const { user, logout } = useAuth()
const initials = computed(() => {
  const name = user.value?.name || user.value?.email || '?'
  return name.split(/[\s@]/)[0].slice(0, 2).toUpperCase()
})
async function handleLogout() { await logout() }

const { isDark, init, toggle } = useDarkMode()
onMounted(init)
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 40;
  background: var(--navbar-bg);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border-bottom: 1px solid var(--border);
  box-shadow: 0 1px 0 0 var(--border), var(--shadow-xs);
  transition: background 0.2s, border-color 0.2s;
}
.navbar-inner {
  max-width: 1024px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Brand */
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  flex-shrink: 0;
  text-align: left;
}
.brand-logo {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  overflow: hidden;
  border: 1.5px solid var(--border);
  flex-shrink: 0;
}
.brand-logo img { width: 100%; height: 100%; object-fit: cover; }
.brand-text { display: flex; flex-direction: column; line-height: 1; }
.brand-name { font-size: 0.875rem; font-weight: 800; color: var(--text-base); letter-spacing: -0.02em; }
.brand-sub  { font-size: 0.65rem; color: var(--text-subtle); margin-top: 2px; }

/* Nav links */
.nav-links {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;
  padding-left: 0.5rem;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0.45rem 0.85rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  background: none;
  border: none;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.15s, background 0.15s;
  white-space: nowrap;
}
.nav-item:hover:not(.disabled) {
  background: var(--primary-light);
  color: var(--primary);
}
.nav-item.active {
  background: var(--primary-light);
  color: var(--primary);
}
.nav-item.disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.nav-underline { height: 2px; }

/* User */
.user-area {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
  flex-shrink: 0;
}
.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  line-height: 1;
}
.user-name  { font-size: 0.78rem; font-weight: 700; color: var(--text-base); }
.user-email { font-size: 0.67rem; color: var(--text-subtle); margin-top: 2px; }
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  letter-spacing: 0.02em;
}
.logout-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-xs);
  background: none;
  border: 1.5px solid var(--border);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.logout-btn:hover {
  background: rgba(220, 38, 38, 0.1);
  color: var(--error);
  border-color: rgba(220, 38, 38, 0.35);
}

/* Dark mode toggle */
.dark-toggle {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-xs);
  background: none;
  border: 1.5px solid var(--border);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  flex-shrink: 0;
}
.dark-toggle:hover {
  background: var(--primary-light);
  color: var(--primary);
  border-color: var(--primary);
}

@media (max-width: 600px) {
  .user-info { display: none; }
  .brand-sub  { display: none; }
  .nav-item span { display: none; }
  .nav-item { padding: 0.45rem 0.6rem; }
}
</style>
