<template>
  <div>
    <!-- Patient header band -->
    <div v-if="patient" class="patient-band animate-slide-in">
      <div class="patient-band-inner">
        <button class="back-btn" @click="navigateTo('/')">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
            <path d="M19 12H5M12 5l-7 7 7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          Pacientes
        </button>

        <div class="patient-band-divider">/</div>

        <div class="patient-chip">
          <div class="patient-chip-avatar" :style="{ background: avatarColor(patient.nombre) }">
            {{ initials(patient.nombre) }}
          </div>
          <div>
            <span class="patient-chip-name">{{ patient.nombre }}</span>
            <span class="patient-chip-meta">{{ patient.edad }} años · {{ patient.sexo }}</span>
          </div>
        </div>

        <div class="patient-band-divider">/</div>
        <span class="patient-band-section">Análisis</span>
      </div>
    </div>

    <AnalysisList
      :analyses="analyses"
      @add="navigateTo(`/pacientes/${route.params.id}/analisis/nuevo`)"
      @edit="a => navigateTo(`/pacientes/${route.params.id}/analisis/${a.id}/editar`)"
      @delete="handleDelete"
    />
  </div>
</template>

<script setup>
import Swal from 'sweetalert2'
import { usePatientsStore } from '~/stores/patients'

const route = useRoute()
const store = usePatientsStore()

onMounted(async () => {
  if (!store.patients.length) {
    try { await store.loadPatients() } catch (e) { console.error(e) }
  }
})

const patient  = computed(() => store.patients.find(p => p.id === Number(route.params.id)) || null)
const analyses = computed(() => patient.value?.analyses || [])

const PALETTE = ['#2563eb','#7c3aed','#db2777','#059669','#d97706','#0891b2','#65a30d']
function avatarColor(name) {
  let h = 0
  for (let i = 0; i < name.length; i++) h = name.charCodeAt(i) + ((h << 5) - h)
  return PALETTE[Math.abs(h) % PALETTE.length]
}
function initials(name) {
  return name.trim().split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
}

function handleDelete(analysis) {
  Swal.fire({
    icon: 'warning',
    title: '¿Eliminar análisis?',
    text: 'Esta acción no se puede deshacer.',
    showCancelButton: true,
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'No',
    reverseButtons: true,
  }).then(async result => {
    if (result.isConfirmed) {
      try {
        await store.deleteAnalysis(Number(route.params.id), analysis.id)
        Swal.fire({ icon: 'success', title: '¡Análisis eliminado!', showConfirmButton: false, timer: 1200 })
      } catch (e) {
        Swal.fire({ icon: 'error', title: 'Error al eliminar', text: e.message })
      }
    }
  })
}
</script>

<style scoped>
.patient-band {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  box-shadow: var(--shadow-xs);
}
.patient-band-inner {
  max-width: 1024px;
  margin: 0 auto;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.back-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.3rem 0.6rem;
  border-radius: var(--radius-xs);
  transition: background 0.15s, color 0.15s;
}
.back-btn:hover { background: var(--surface-3); color: var(--text-base); }
.patient-band-divider { color: var(--text-subtle); font-size: 0.875rem; }
.patient-chip {
  display: flex;
  align-items: center;
  gap: 8px;
}
.patient-chip-avatar {
  width: 28px; height: 28px;
  border-radius: 8px;
  color: #fff;
  font-size: 0.65rem;
  font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.patient-chip-name {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-base);
  display: block;
  line-height: 1;
}
.patient-chip-meta {
  font-size: 0.7rem;
  color: var(--text-subtle);
  display: block;
  margin-top: 2px;
}
.patient-band-section {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--primary);
}
</style>
