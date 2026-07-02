<template>
  <div class="min-h-screen flex font-sans">
    <!-- Panel izquierdo: branding -->
    <div class="hidden lg:flex lg:w-[45%] flex-col justify-between p-12 relative overflow-hidden"
      style="background: linear-gradient(145deg, #1d4ed8 0%, #2563eb 40%, #1e40af 100%)">
      <!-- Círculos decorativos -->
      <div class="absolute -top-24 -right-24 w-80 h-80 rounded-full opacity-10" style="background:rgba(255,255,255,0.3)"></div>
      <div class="absolute -bottom-16 -left-16 w-64 h-64 rounded-full opacity-10" style="background:rgba(255,255,255,0.3)"></div>
      <div class="absolute top-1/3 right-8 w-32 h-32 rounded-full opacity-5" style="background:rgba(255,255,255,0.5)"></div>

      <!-- Logo -->
      <div class="flex items-center gap-3 relative z-10">
        <div class="w-11 h-11 rounded-xl overflow-hidden shadow-lg border-2 border-white/20">
          <img src="/images/logonegro.jpeg" alt="Logo" class="w-full h-full object-cover" />
        </div>
        <span class="text-white font-bold text-lg tracking-tight">Nexo Postural</span>
      </div>

      <!-- Contenido central -->
      <div class="relative z-10">
        <div class="inline-flex items-center gap-2 bg-white/10 text-blue-100 text-xs font-semibold px-3 py-1.5 rounded-full mb-6 border border-white/20">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          Sistema activo
        </div>
        <h1 class="text-4xl font-extrabold text-white leading-tight mb-4 tracking-tight">
          Análisis Postural<br/>
          <span class="text-blue-200">Inteligente</span>
        </h1>
        <p class="text-blue-200 text-base leading-relaxed mb-10 max-w-xs">
          Kyene'is Pondyam — Diagnóstico biomecánico de precisión para profesionales de la salud.
        </p>

        <div class="flex flex-col gap-4">
          <div v-for="feat in features" :key="feat" class="flex items-center gap-3 text-blue-100">
            <div class="w-7 h-7 rounded-lg bg-white/10 border border-white/15 flex items-center justify-center flex-shrink-0">
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
                <path d="M5 13l4 4L19 7" stroke="#86efac" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <span class="text-sm font-medium">{{ feat }}</span>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="relative z-10 text-blue-300 text-xs">
        Universidad Politécnica de Chiapas &copy; 2026
      </div>
    </div>

    <!-- Panel derecho: formulario -->
    <div class="login-panel flex-1 flex items-center justify-center px-6 py-12">
      <div class="w-full max-w-sm">
        <!-- Logo mobile -->
        <div class="flex items-center gap-3 mb-10 lg:hidden">
          <img src="/images/logonegro.jpeg" alt="Logo" class="h-9 w-9 rounded-xl object-cover" />
          <span class="font-extrabold text-xl text-blue-700 tracking-tight">Nexo Postural</span>
        </div>

        <div class="mb-8">
          <h2 class="text-2xl font-extrabold text-gray-900 tracking-tight">Bienvenido</h2>
          <p class="text-gray-500 text-sm mt-1">Ingresa tus credenciales para continuar</p>
        </div>

        <form @submit.prevent="handleLogin" class="flex flex-col gap-5">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Correo electrónico</label>
            <div class="relative">
              <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
                  <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </span>
              <input
                v-model="email"
                type="email"
                required
                autocomplete="email"
                placeholder="doctor@gmail.com"
                class="login-input w-full pl-10 pr-4 py-3 rounded-xl focus:outline-none text-sm transition shadow-sm"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">Contraseña</label>
            <div class="relative">
              <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
                <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
                  <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" stroke-width="2"/>
                  <path d="M7 11V7a5 5 0 0110 0v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </span>
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="current-password"
                placeholder="••••••••••"
                class="login-input w-full pl-10 pr-12 py-3 rounded-xl focus:outline-none text-sm transition shadow-sm"
              />
              <button
                type="button"
                class="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-600 transition"
                @click="showPassword = !showPassword"
              >
                <svg v-if="!showPassword" width="16" height="16" fill="none" viewBox="0 0 24 24">
                  <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" stroke="currentColor" stroke-width="2"/>
                  <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                </svg>
                <svg v-else width="16" height="16" fill="none" viewBox="0 0 24 24">
                  <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24M1 1l22 22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
          </div>

          <transition name="slide-down">
            <div v-if="errorMsg" class="flex items-center gap-2.5 bg-red-50 border border-red-200 text-red-600 rounded-xl px-4 py-3 text-sm font-medium">
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" class="flex-shrink-0">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              {{ errorMsg }}
            </div>
          </transition>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 rounded-xl font-bold text-sm text-white transition shadow-md disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-1"
            style="background: linear-gradient(135deg, #2563eb, #1d4ed8);"
          >
            <svg v-if="loading" class="animate-spin" width="16" height="16" fill="none" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-opacity=".25" stroke-width="3"/>
              <path d="M12 2a10 10 0 0110 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
            </svg>
            {{ loading ? 'Ingresando...' : 'Iniciar sesión' }}
          </button>
        </form>

        <p class="mt-8 text-center text-xs text-gray-400">
          Acceso restringido a personal autorizado
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({ layout: false })

const { login } = useAuth()

const features = [
  'Podometría digital avanzada',
  'Análisis frontal y sagital',
  'Evaluación miofascial',
  'Generación de reportes PDF',
]

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  errorMsg.value = ''
  loading.value = true
  try {
    await login(email.value, password.value)
    await navigateTo('/')
  } catch (e) {
    errorMsg.value = e?.data?.message || 'Credenciales incorrectas'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-panel {
  background: var(--surface-2);
}
.login-input {
  border: 1.5px solid var(--border);
  background: var(--surface);
  color: var(--text-base);
}
.login-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-ring);
}
.login-input::placeholder {
  color: var(--text-subtle);
}
.slide-down-enter-active, .slide-down-leave-active {
  transition: all 0.25s ease;
}
.slide-down-enter-from, .slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
