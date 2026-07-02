<template>
  <div class="px-6 py-8 max-w-4xl mx-auto w-full">

    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h2 class="text-2xl font-extrabold text-gray-900 tracking-tight">Pacientes</h2>
        <p class="text-sm text-gray-400 mt-0.5">{{ filtered.length }} paciente{{ filtered.length !== 1 ? 's' : '' }} registrado{{ filtered.length !== 1 ? 's' : '' }}</p>
      </div>
      <button class="btn-primary flex items-center gap-2 text-sm self-start sm:self-auto" @click="$emit('add')">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
          <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        Nuevo Paciente
      </button>
    </div>

    <!-- Search -->
    <div class="relative mb-6">
      <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
          <path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </span>
      <input
        v-model="search"
        type="text"
        placeholder="Buscar paciente por nombre..."
        class="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent text-gray-700 shadow-sm transition"
      />
    </div>

    <!-- Empty state -->
    <div v-if="patients.length === 0" class="flex flex-col items-center justify-center py-20 text-center">
      <div class="w-16 h-16 rounded-2xl bg-blue-50 flex items-center justify-center mb-4">
        <svg width="32" height="32" fill="none" viewBox="0 0 24 24" class="text-blue-300">
          <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </div>
      <p class="font-semibold text-gray-500 text-sm">No hay pacientes registrados</p>
      <p class="text-gray-400 text-xs mt-1">Comienza registrando tu primer paciente</p>
      <button class="btn-primary mt-5 text-sm flex items-center gap-2" @click="$emit('add')">
        <svg width="15" height="15" fill="none" viewBox="0 0 24 24">
          <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        Registrar Paciente
      </button>
    </div>

    <!-- No results -->
    <div v-else-if="filtered.length === 0" class="flex flex-col items-center justify-center py-16 text-center">
      <div class="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center mb-3">
        <svg width="22" height="22" fill="none" viewBox="0 0 24 24" class="text-gray-400">
          <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="1.5"/>
          <path d="M21 21l-4.35-4.35M11 8v3M11 14h.01" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </div>
      <p class="text-gray-500 text-sm font-medium">Sin resultados para "{{ search }}"</p>
    </div>

    <!-- Grid -->
    <div v-else class="grid gap-4 md:grid-cols-2">
      <div
        v-for="p in filtered"
        :key="p.id"
        class="patient-card group"
        @click="$emit('select', p)"
      >
        <div class="flex items-start gap-3">
          <!-- Avatar -->
          <div class="avatar-circle flex-shrink-0" :style="{ background: avatarColor(p.nombre) }">
            {{ initials(p.nombre) }}
          </div>

          <!-- Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="font-bold text-gray-900 text-sm truncate group-hover:text-blue-600 transition">{{ p.nombre }}</span>
              <span class="badge-gender" :class="p.sexo === 'Masculino' ? 'badge-male' : p.sexo === 'Femenino' ? 'badge-female' : 'badge-other'">
                {{ p.sexo }}
              </span>
            </div>
            <p class="text-xs text-gray-400 mt-0.5">{{ p.edad }} años</p>
          </div>

          <!-- Arrow -->
          <svg width="16" height="16" fill="none" viewBox="0 0 24 24" class="text-gray-300 group-hover:text-blue-400 transition mt-1 flex-shrink-0">
            <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>

        <!-- Actions -->
        <div class="flex gap-2 mt-4 pt-4 border-t border-gray-100">
          <button
            class="action-btn flex-1 hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200"
            @click.stop="$emit('edit', p)"
          >
            <svg width="13" height="13" fill="none" viewBox="0 0 24 24">
              <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            Editar
          </button>
          <button
            class="action-btn flex-1 hover:bg-red-50 hover:text-red-500 hover:border-red-200"
            @click.stop="$emit('delete', p)"
          >
            <svg width="13" height="13" fill="none" viewBox="0 0 24 24">
              <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  patients: { type: Array, default: () => [] },
})
defineEmits(['select', 'add', 'edit', 'delete'])

const search = ref('')

const filtered = computed(() => {
  if (!search.value.trim()) return props.patients
  const q = search.value.toLowerCase()
  return props.patients.filter(p => p.nombre.toLowerCase().includes(q))
})

const PALETTE = ['#2563eb','#7c3aed','#db2777','#059669','#d97706','#dc2626','#0891b2','#65a30d']

function avatarColor(name) {
  let h = 0
  for (let i = 0; i < name.length; i++) h = name.charCodeAt(i) + ((h << 5) - h)
  return PALETTE[Math.abs(h) % PALETTE.length]
}

function initials(name) {
  return name.trim().split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
}
</script>

<style scoped>
.patient-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.1rem;
  cursor: pointer;
  transition: all 0.18s ease;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.patient-card:hover {
  border-color: #bfdbfe;
  box-shadow: 0 4px 20px rgba(37,99,235,0.1);
  transform: translateY(-1px);
}
.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  color: #fff;
  font-size: 0.8rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: 0.03em;
}
.badge-gender {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 99px;
  letter-spacing: 0.04em;
}
.badge-male   { background: rgba(37,99,235,0.12);  color: #2563eb; }
.badge-female { background: rgba(219,39,119,0.12); color: #db2777; }
.badge-other  { background: rgba(124,58,237,0.12); color: #7c3aed; }
.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  padding: 0.45rem 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  transition: all 0.15s;
}
</style>
