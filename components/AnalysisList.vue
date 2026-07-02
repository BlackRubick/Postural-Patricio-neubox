<template>
  <div class="px-6 py-8 max-w-4xl mx-auto w-full">

    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h2 class="text-2xl font-extrabold text-gray-900 tracking-tight">Historial de Análisis</h2>
        <p class="text-sm text-gray-400 mt-0.5">{{ analyses.length }} análisis registrado{{ analyses.length !== 1 ? 's' : '' }}</p>
      </div>
      <button class="btn-primary flex items-center gap-2 text-sm self-start sm:self-auto" @click="$emit('add')">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
          <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        Nuevo Test
      </button>
    </div>

    <!-- Empty state -->
    <div v-if="analyses.length === 0" class="flex flex-col items-center justify-center py-20 text-center">
      <div class="w-16 h-16 rounded-2xl bg-blue-50 flex items-center justify-center mb-4">
        <svg width="30" height="30" fill="none" viewBox="0 0 24 24" class="text-blue-300">
          <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </div>
      <p class="font-semibold text-gray-500 text-sm">No hay análisis registrados</p>
      <p class="text-gray-400 text-xs mt-1">Crea un nuevo test para comenzar</p>
      <button class="btn-primary mt-5 text-sm flex items-center gap-2" @click="$emit('add')">
        <svg width="15" height="15" fill="none" viewBox="0 0 24 24">
          <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        Nuevo Test
      </button>
    </div>

    <!-- Grid -->
    <div v-else class="grid gap-4 md:grid-cols-2">
      <div v-for="a in analyses" :key="a.id" class="analysis-card">

        <!-- Top row -->
        <div class="flex items-start gap-3">
          <div class="type-icon flex-shrink-0" :style="{ background: typeColor(a.tipoTest).bg }">
            <span :style="{ color: typeColor(a.tipoTest).fg }">{{ typeEmoji(a.tipoTest) }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <span class="font-bold text-gray-900 text-sm block truncate">{{ a.tipoTest }}</span>
            <span class="text-xs text-gray-400 mt-0.5 block">{{ a.fecha }}</span>
          </div>
          <span
            class="status-badge flex-shrink-0"
            :class="a.completado ? 'status-done' : 'status-pending'"
          >
            {{ a.completado ? 'Completado' : 'Pendiente' }}
          </span>
        </div>

        <!-- Actions -->
        <div class="grid grid-cols-3 gap-2 mt-4 pt-4 border-t border-gray-100">
          <button class="action-btn hover:bg-blue-50 hover:text-blue-600 hover:border-blue-200" @click="$emit('edit', a)">
            <svg width="12" height="12" fill="none" viewBox="0 0 24 24">
              <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            Editar
          </button>
          <button class="action-btn hover:bg-red-50 hover:text-red-500 hover:border-red-200" @click="$emit('delete', a)">
            <svg width="12" height="12" fill="none" viewBox="0 0 24 24">
              <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Eliminar
          </button>
          <button class="action-btn hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-200" @click="openModal(a)">
            <svg width="12" height="12" fill="none" viewBox="0 0 24 24">
              <path d="M8 10h8M8 14h5M20 6H4a2 2 0 00-2 2v9a2 2 0 002 2h1l3 3v-3h12a2 2 0 002-2V8a2 2 0 00-2-2z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            Notas
          </button>
        </div>
      </div>
    </div>

    <!-- Modal observaciones -->
    <AppModal :open="modalOpen" title="Notas del análisis" @close="modalOpen = false">
      <div v-if="selectedAnalysis" class="flex flex-col gap-4">
        <div class="modal-info rounded-xl p-4 text-sm">
          <div class="flex items-center gap-2 mb-1">
            <span class="font-bold" style="color:var(--text-base)">{{ selectedAnalysis.tipoTest }}</span>
            <span class="status-badge" :class="selectedAnalysis.completado ? 'status-done' : 'status-pending'">
              {{ selectedAnalysis.completado ? 'Completado' : 'Pendiente' }}
            </span>
          </div>
          <span class="text-xs" style="color:var(--text-subtle)">{{ selectedAnalysis.fecha }}</span>
        </div>
        <div>
          <label class="block text-sm font-semibold mb-1.5" style="color:var(--text-muted)">Observaciones</label>
          <textarea
            v-model="comment"
            class="modal-textarea w-full rounded-xl p-3 text-sm min-h-[100px] focus:outline-none resize-none"
            placeholder="Agrega tus observaciones o comentarios sobre este análisis..."
          />
        </div>
        <div class="flex gap-2 justify-end">
          <button class="btn-secondary text-sm" @click="modalOpen = false">Cancelar</button>
          <button class="btn-primary text-sm" @click="saveComment">Guardar</button>
        </div>
      </div>
    </AppModal>
  </div>
</template>

<script setup>
import Swal from 'sweetalert2'

defineProps({
  analyses: { type: Array, default: () => [] },
})
defineEmits(['add', 'edit', 'delete'])

const modalOpen = ref(false)
const selectedAnalysis = ref(null)
const comment = ref('')

const TYPE_MAP = {
  'Podometría digital': { bg: '#eff6ff', fg: '#2563eb', emoji: '🦶' },
  'Análisis frontal':   { bg: '#f0fdf4', fg: '#16a34a', emoji: '🧍' },
  'Análisis sagital':   { bg: '#fdf4ff', fg: '#9333ea', emoji: '📐' },
  'Miofascial':         { bg: '#fff7ed', fg: '#ea580c', emoji: '💪' },
}

function typeColor(tipo) {
  return TYPE_MAP[tipo] || { bg: '#f8fafc', fg: '#475569' }
}
function typeEmoji(tipo) {
  return (TYPE_MAP[tipo] || { emoji: '🔬' }).emoji
}

function getStoredComment(id) {
  if (!import.meta.client) return ''
  const comments = JSON.parse(localStorage.getItem('analysisComments') || '{}')
  return comments[id] || ''
}

function openModal(analysis) {
  selectedAnalysis.value = analysis
  comment.value = getStoredComment(analysis.id)
  modalOpen.value = true
}

function saveComment() {
  if (!selectedAnalysis.value) return
  const comments = JSON.parse(localStorage.getItem('analysisComments') || '{}')
  comments[selectedAnalysis.value.id] = comment.value
  localStorage.setItem('analysisComments', JSON.stringify(comments))
  modalOpen.value = false
  Swal.fire({ icon: 'success', title: 'Nota guardada', timer: 1200, showConfirmButton: false })
}
</script>

<style scoped>
.analysis-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.1rem;
  transition: all 0.18s ease;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.analysis-card:hover {
  border-color: #e0e7ff;
  box-shadow: 0 4px 20px rgba(99,102,241,0.09);
}
.type-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}
.status-badge {
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.2rem 0.55rem;
  border-radius: 99px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.status-done    { background: rgba(22,163,74,0.12);  color: #16a34a; }
.status-pending { background: rgba(202,138,4,0.12);  color: #ca8a04; }
.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  padding: 0.45rem 0.5rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-muted);
  transition: all 0.15s;
  white-space: nowrap;
}
.modal-info {
  background: var(--surface-3);
  border: 1px solid var(--border);
}
.modal-textarea {
  background: var(--surface-3);
  border: 1.5px solid var(--border);
  color: var(--text-base);
  font-size: 0.875rem;
  transition: border-color 0.15s, box-shadow 0.15s;
  outline: none;
}
.modal-textarea:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-ring);
}
.modal-textarea::placeholder { color: var(--text-subtle); }
</style>
