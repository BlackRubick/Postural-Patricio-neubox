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
            <span class="font-bold text-gray-900 text-sm block truncate">{{ patient?.nombre || a.tipoTest }}</span>
            <span class="text-xs text-gray-500 block truncate">{{ a.tipoTest }}</span>
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

        <!-- PDF Button -->
        <button
          class="pdf-btn"
          :class="{ 'pdf-btn-loading': pdfLoading === a.id }"
          :disabled="pdfLoading === a.id"
          @click="generatePdf(a)"
        >
          <svg v-if="pdfLoading !== a.id" width="13" height="13" fill="none" viewBox="0 0 24 24">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
            <path d="M14 2v6h6M9 13h6M9 17h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <div v-else class="spinner" style="width:13px;height:13px;border-width:2px;border-color:#fff transparent transparent transparent"></div>
          {{ pdfLoading === a.id ? 'Generando PDF...' : 'Descargar PDF' }}
        </button>
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

const props = defineProps({
  analyses: { type: Array, default: () => [] },
  patient: { type: Object, default: null },
})
defineEmits(['add', 'edit', 'delete'])

const modalOpen = ref(false)
const selectedAnalysis = ref(null)
const comment = ref('')
const pdfLoading = ref(null)

async function generatePdf(a) {
  pdfLoading.value = a.id
  try {
    const analisis = []

    if (a.podometriaResult) {
      const imgs = []
      if (a.podometriaHuella)   imgs.push({ titulo: 'Huella plantar', base64: a.podometriaHuella.replace(/^data:image\/\w+;base64,/, '') })
      if (a.podometriaDebugImg) imgs.push({ titulo: 'Podometría', base64: a.podometriaDebugImg.replace(/^data:image\/\w+;base64,/, '') })
      const arr = Array.isArray(a.podometriaResult) ? a.podometriaResult : [a.podometriaResult]
      const metricas = arr.flatMap(r => [
        r.lado ? `Pie ${r.lado} — Tipo: ${r.tipo}` : `Tipo de pie: ${r.tipo}`,
        `Índice plantar: ${r.porcentajeX || ''}`,
        r.X ? `Ancho X: ${r.X}` : null,
        r.Y ? `Ancho Y: ${r.Y}` : null,
      ].filter(Boolean))
      const exp = arr.map(r => `${r.lado ? 'Pie ' + r.lado + ': ' : ''}${r.tipo}`).join(' | ')
      analisis.push({ titulo: 'Podometría digital', explicacion: exp, metricas, imagenes: imgs })
    }

    if (a.frontalResult) {
      const imgs = a.frontalDebugImg ? [{ titulo: 'Vista frontal', base64: a.frontalDebugImg.replace(/^data:image\/\w+;base64,/, '') }] : []
      analisis.push({ titulo: 'Ángulo Tibiofemoral (Anterior o Frontal)', explicacion: a.frontalResult.tipo || '', metricas: [`Ángulo: ${a.frontalResult.angulo}`], imagenes: imgs })
    }

    if (a.sagitalResult) {
      const imgs = a.sagitalDebugImg ? [{ titulo: 'Vista lateral / sagital', base64: a.sagitalDebugImg.replace(/^data:image\/\w+;base64,/, '') }] : []
      analisis.push({ titulo: 'Ángulo Tibiofemoral (Lateral o Sagital)', explicacion: a.sagitalResult.tipo || '', metricas: [`Ángulo: ${a.sagitalResult.angulo}`], imagenes: imgs })
    }

    if (a.alineacionSagitalResult) {
      const r = a.alineacionSagitalResult
      const imgs = a.alineacionSagitalDebugImg ? [{ titulo: 'Alineación — Línea Plomada de Kendall', base64: a.alineacionSagitalDebugImg.replace(/^data:image\/\w+;base64,/, '') }] : []
      analisis.push({
        titulo: 'Alineación Postural — Línea Plomada de Kendall',
        explicacion: r.tipo || '',
        metricas: [
          `Desviación hombro: ${r.hombro != null ? r.hombro + '%' : 'N/A'}`,
          `Desviación oreja: ${r.oreja != null ? r.oreja + '%' : 'N/A'}`,
          `Lado evaluado: ${r.lado || ''}`,
        ],
        imagenes: imgs,
      })
    }

    if (a.alineacionFrontalResult) {
      const r = a.alineacionFrontalResult
      const imgs = a.alineacionFrontalDebugImg ? [{ titulo: 'Vertical de Barré', base64: a.alineacionFrontalDebugImg.replace(/^data:image\/\w+;base64,/, '') }] : []
      const metricas = [`Desviación: ${r.nariz != null ? r.nariz + '%' : 'N/A'}`]
      if (r.inferior_dev != null) metricas.push(`Tren inferior: ${r.inferior_dev}%`)
      if (r.superior_dev != null) metricas.push(`Tren superior: ${r.superior_dev}%`)
      analisis.push({
        titulo: 'Vertical de Barré',
        explicacion: r.descripcion || r.tipo || '',
        metricas,
        imagenes: imgs,
        barre_class: r.clasificacion || null,
      })
    }

    if (a.miofascialResult) {
      const arr = Array.isArray(a.miofascialResult) ? a.miofascialResult : [a.miofascialResult]
      const m = arr[0]
      const imgs = []
      if (a.miofascialDebugImg) imgs.push({ titulo: 'Cadena miofascial (lateral / sagital)', base64: a.miofascialDebugImg.replace(/^data:image\/\w+;base64,/, '') })
      analisis.push({
        titulo: 'Evaluación de Cadenas Miofasiales',
        tipo: m?.tipo || '',
        explicacion: m?.explicacion || '',
        metricas: m?.rasgos || [],
        rasgos_detallados: m?.rasgos_detallados || [],
        porcentaje: m?.porcentaje ?? 0,
        imagenes: imgs,
      })
    }

    const reportData = {
      paciente: {
        nombre: props.patient?.nombre || 'Paciente',
        edad: props.patient?.edad ?? null,
        sexo: props.patient?.sexo ?? null,
        altura: props.patient?.altura ?? null,
      },
      fecha: a.fecha,
      notas: a.notas || null,
      analisis,
    }
    if (a.miofascialImagenOriginal) reportData.imagen_original = a.miofascialImagenOriginal
    if (a.miofascialFrontalImg)     reportData.imagen_frontal   = a.miofascialFrontalImg
    if (a.miofascialPosteriorImg)   reportData.imagen_posterior = a.miofascialPosteriorImg

    const res = await fetch('http://127.0.0.1:8000/generate-report/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reportData),
    })
    if (!res.ok) throw new Error('Error al generar el PDF')
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `Reporte_${props.patient?.nombre || 'Paciente'}_${a.fecha}.pdf`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch {
    Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudo generar el PDF. Asegúrate de que la API Python esté corriendo.' })
  } finally {
    pdfLoading.value = null
  }
}

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

function openModal(analysis) {
  selectedAnalysis.value = analysis
  comment.value = analysis.notas || ''
  modalOpen.value = true
}

async function saveComment() {
  if (!selectedAnalysis.value) return
  try {
    await $fetch(`/api/analyses/${selectedAnalysis.value.id}`, {
      method: 'PUT',
      body: { notas: comment.value },
    })
    selectedAnalysis.value.notas = comment.value
    modalOpen.value = false
    Swal.fire({ icon: 'success', title: 'Nota guardada', timer: 1200, showConfirmButton: false })
  } catch {
    Swal.fire({ icon: 'error', title: 'Error', text: 'No se pudo guardar la nota.' })
  }
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

.pdf-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  margin-top: 8px;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1.5px solid #dc2626;
  background: #fff5f5;
  color: #dc2626;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
  letter-spacing: 0.01em;
}
.pdf-btn:hover:not(:disabled) {
  background: #dc2626;
  color: #fff;
}
.pdf-btn:disabled,
.pdf-btn-loading {
  opacity: 0.7;
  cursor: not-allowed;
  background: #dc2626;
  color: #fff;
}
.spinner {
  border-radius: 50%;
  border-style: solid;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
