<template>
  <div class="af-shell">
    <div class="af-card animate-fade-in">

      <!-- Step progress -->
      <div class="step-bar">
        <div v-for="(s, i) in STEPS" :key="i" class="step-item">
          <div class="step-connector" v-if="i > 0" :class="{ done: step > i - 1 }"></div>
          <div class="step-dot" :class="{ active: step === i, done: step > i }">
            <svg v-if="step > i" width="12" height="12" fill="none" viewBox="0 0 24 24">
              <path d="M5 13l4 4L19 7" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span v-else>{{ i + 1 }}</span>
          </div>
          <div class="step-label" :class="{ active: step === i, done: step > i }">{{ s.short }}</div>
        </div>
      </div>

      <!-- Header -->
      <div class="af-header">
        <div class="af-icon" :style="{ background: STEPS[step].color }">
          <span style="font-size:1.3rem">{{ STEPS[step].emoji }}</span>
        </div>
        <div>
          <h2 class="af-title">{{ stepTitle }}</h2>
          <p class="af-subtitle">{{ stepSubtitle }}</p>
        </div>
      </div>

      <!-- Binarization controls (step 0 only) -->
      <div v-if="step === 0" class="bin-controls">
        <div class="bin-row">
          <label class="bin-label">
            Binarización
            <select v-model="binarizationType" class="bin-select">
              <option value="adaptive">Adaptativo</option>
              <option value="fixed">Fijo</option>
              <option value="otsu">Otsu (auto)</option>
            </select>
          </label>
          <label v-if="binarizationType === 'adaptive'" class="bin-label">
            Sensibilidad (C): <strong>{{ adaptiveC }}</strong>
            <input type="range" min="-20" max="30" v-model.number="adaptiveC" class="bin-range" />
          </label>
          <label v-if="binarizationType === 'fixed'" class="bin-label">
            Umbral fijo: <strong>{{ fixedThreshold }}</strong>
            <input type="range" min="0" max="255" v-model.number="fixedThreshold" class="bin-range" />
          </label>
          <label class="bin-label" style="flex-direction:row;align-items:center;gap:8px">
            <input v-model="invertThreshold" type="checkbox" class="bin-check" />
            Invertir umbral
          </label>
          <label class="bin-label">
            Longitud del pie (cm, opcional):
            <input
              v-model.number="footLengthCm"
              type="number"
              min="10" max="40" step="0.5"
              placeholder="ej. 26"
              class="bin-select"
              style="width:80px"
            />
          </label>
        </div>
        <div v-if="pieBinImg" class="bin-preview">
          <span class="bin-preview-label">Vista binarizada</span>
          <img :src="pieBinImg" alt="Binarizado" class="bin-preview-img" />
        </div>
      </div>

      <!-- Capture method tabs -->
      <div class="capture-tabs">
        <button
          :class="['capture-tab', !form.tomarFoto ? 'active' : '']"
          @click="form.tomarFoto = false; form[uploadKey] = null"
        >
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
            <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M16 8l-4-4-4 4M12 4v12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Subir imagen
        </button>
        <button
          :class="['capture-tab', form.tomarFoto ? 'active' : '']"
          @click="form.tomarFoto = true; form[uploadKey] = null"
        >
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
            <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
            <circle cx="12" cy="13" r="4" stroke="currentColor" stroke-width="2"/>
          </svg>
          Tomar foto
        </button>
      </div>

      <!-- Upload zone -->
      <div v-if="!form.tomarFoto" class="upload-zone" :class="{ uploaded: !!form[uploadKey] }">
        <input type="file" accept="image/*" :key="uploadKey" @change="handleFileChange" />
        <div class="upload-icon">
          <svg v-if="!form[uploadKey]" width="24" height="24" fill="none" viewBox="0 0 24 24">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else width="24" height="24" fill="none" viewBox="0 0 24 24">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <p class="upload-title">{{ form[uploadKey] ? 'Imagen lista para analizar' : 'Arrastra o haz clic para subir' }}</p>
        <p class="upload-hint">PNG, JPG, WEBP · máx. 10 MB</p>

        <!-- Loading -->
        <div v-if="pieLoading" class="upload-loading">
          <div class="spinner" style="width:20px;height:20px;border-width:2px"></div>
          <span>Analizando imagen…</span>
        </div>
      </div>

      <!-- Results panel -->
      <div v-if="currentResult" class="result-panel">
        <div class="result-header">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="#16a34a" stroke-width="2" stroke-linecap="round"/>
          </svg>
          Resultado del análisis
        </div>

        <!-- Podometría -->
        <template v-if="step === 0 && analisisState.podometria.result">
          <div class="result-row" v-for="(r, i) in analisisState.podometria.result" :key="i">
            <div class="result-chip">Tipo de pie: <strong>{{ r.tipo }}</strong></div>
            <div class="result-chip">Índice plantar: <strong>{{ r.porcentajeX }}</strong></div>
            <div class="result-chip" v-if="r.X">Ancho X: <strong>{{ r.X }}</strong></div>
            <div class="result-chip" v-if="r.Y">Ancho Y: <strong>{{ r.Y }}</strong></div>
          </div>
        </template>

        <!-- Frontal -->
        <template v-if="step === 1 && analisisState.frontal.result">
          <div class="result-row">
            <div class="result-chip">Clasificación: <strong>{{ analisisState.frontal.result.tipo }}</strong></div>
            <div class="result-chip">Ángulo: <strong>{{ analisisState.frontal.result.angulo }}</strong></div>
          </div>
        </template>

        <!-- Sagital -->
        <template v-if="step === 2 && analisisState.sagital.result">
          <div class="result-row">
            <div class="result-chip">Clasificación: <strong>{{ analisisState.sagital.result.tipo }}</strong></div>
            <div class="result-chip">Ángulo: <strong>{{ analisisState.sagital.result.angulo }}</strong></div>
          </div>
        </template>

        <!-- Miofascial -->
        <template v-if="step === 3 && analisisState.miofascial.result">
          <div class="result-row" v-for="(r, i) in analisisState.miofascial.result" :key="i">
            <div class="result-chip">Cadena: <strong>{{ r.tipo }}</strong></div>
            <p class="result-explanation">{{ r.explicacion }}</p>
            <ul v-if="r.rasgos?.length" class="result-rasgos">
              <li v-for="(rasgo, idx) in r.rasgos" :key="idx">{{ rasgo }}</li>
            </ul>
          </div>
        </template>

        <!-- Debug image -->
        <div v-if="pieDebugImg" class="result-debug">
          <span class="result-debug-label">Debug visual</span>
          <img :src="pieDebugImg" alt="Debug" class="result-debug-img" />
        </div>
      </div>

      <!-- Camera section -->
      <div v-if="form.tomarFoto" class="camera-section">
        <select v-model="form.cameraDevice" class="form-field">
          <option value="">— Selecciona una cámara —</option>
          <option v-for="cam in availableCameras" :key="cam.deviceId" :value="cam.deviceId">
            {{ cam.label || `Cámara ${cam.deviceId}` }}
          </option>
        </select>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <button type="button" class="btn-secondary" style="font-size:.8rem;padding:.5rem .9rem" @click="refreshCameras">
            <svg width="13" height="13" fill="none" viewBox="0 0 24 24">
              <path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            Actualizar cámaras
          </button>
          <button type="button" class="btn-primary" style="font-size:.8rem;padding:.5rem .9rem" @click="handleOpenCamera">
            <svg width="13" height="13" fill="none" viewBox="0 0 24 24">
              <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z" stroke="currentColor" stroke-width="2"/>
              <circle cx="12" cy="13" r="4" stroke="currentColor" stroke-width="2"/>
            </svg>
            Abrir cámara
          </button>
        </div>
        <div v-if="form[uploadKey]" class="camera-ok">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7" stroke="#16a34a" stroke-width="2.5" stroke-linecap="round"/></svg>
          Foto capturada correctamente
        </div>
      </div>

      <!-- Action row -->
      <div class="af-actions">
        <div style="display:flex;gap:8px">
          <button type="button" class="btn-secondary" :disabled="step === 0" @click="goBack" style="font-size:.8rem;padding:.5rem .9rem">
            ← Atrás
          </button>
          <button type="button" class="btn-secondary" @click="handleCancel" style="font-size:.8rem;padding:.5rem .9rem">
            Cancelar
          </button>
        </div>
        <button
          type="button"
          class="btn-primary"
          :disabled="isNextDisabled"
          @click="handleSubmit"
          style="font-size:.875rem;padding:.6rem 1.4rem"
        >
          {{ step < 3 ? 'Continuar' : 'Guardar análisis' }}
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
            <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
    </div>
  </div>

  <!-- Camera modal -->
  <Teleport to="body">
    <div v-if="showCamera" class="cam-overlay" @click.self="showCamera = false; stopStream()">
      <div class="cam-box animate-fade-in-up">
        <div class="cam-header">
          <h3>Vista de cámara</h3>
          <button class="cam-close" @click="showCamera = false; stopStream()">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>
          </button>
        </div>
        <video ref="videoRef" autoplay playsinline class="cam-video" />
        <canvas ref="canvasRef" style="display:none" />
        <button class="btn-primary" style="width:100%;justify-content:center" @click="handleCapture">
          <svg width="15" height="15" fill="none" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <circle cx="12" cy="12" r="4" fill="currentColor"/>
          </svg>
          Capturar foto
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import Swal from 'sweetalert2'
import { usePatientsStore } from '~/stores/patients'

const props = defineProps({
  initial: { type: Object, default: null },
  patientId: { type: Number, default: null },
})
const emit = defineEmits(['save', 'cancel'])

const store = usePatientsStore()
const currentPatient = computed(() =>
  props.patientId ? store.patients.find(p => p.id === props.patientId) || null : null
)

const STEPS = [
  { short: 'Podometría',  emoji: '🦶', color: '#eff6ff', endpoint: 'http://127.0.0.1:8000/analyze-foot/' },
  { short: 'Frontal',     emoji: '🧍', color: '#f0fdf4', endpoint: 'http://127.0.0.1:8000/analyze-knee/frontal/' },
  { short: 'Sagital',     emoji: '📐', color: '#fdf4ff', endpoint: 'http://127.0.0.1:8000/analyze-knee/sagittal/' },
  { short: 'Miofascial',  emoji: '💪', color: '#fff7ed', endpoint: 'http://127.0.0.1:8000/analyze-muscle-chain/' },
]

const today = new Date().toISOString().slice(0, 10)
const step = ref(0)

const form = ref({
  tipoTest: 'Podometría digital',
  fecha: props.initial?.fecha || today,
  completado: false,
  cameraDevice: '',
  podometriaImg: null,
  tibiofemoralFrontal: null,
  tibiofemoralSagital: null,
  miofascialFrontal: null,
  miofascialSagital: null,
  tomarFoto: false,
})

const availableCameras = ref([])
const showCamera = ref(false)
const videoRef = ref(null)
const canvasRef = ref(null)
const stream = ref(null)
const pieLoading = ref(false)
const adaptiveC = ref(10)
const invertThreshold = ref(true)
const binarizationType = ref('adaptive')
const fixedThreshold = ref(120)
const footLengthCm = ref('')
const pieBinImg = ref(null)
const pieDebugImg = ref(null)

const analisisState = ref({
  podometria: { result: null, debugImg: null, binImg: null, huella: null },
  frontal:    { result: null, debugImg: null },
  sagital:    { result: null, debugImg: null },
  miofascial: { result: null, debugImg: null, imagen_original: null },
})

const uploadKey = computed(() => {
  if (step.value === 0) return 'podometriaImg'
  if (step.value === 1) return 'tibiofemoralFrontal'
  if (step.value === 2) return 'tibiofemoralSagital'
  return form.value.miofascialFrontal === null ? 'miofascialFrontal' : 'miofascialSagital'
})

const stepTitle = computed(() => {
  const t = ['Podometría digital', 'Ángulo tibiofemoral (Frontal)', 'Ángulo tibiofemoral (Sagital)', 'Cadena miofascial causal']
  return props.initial ? 'Editar Test' : t[step.value]
})

const stepSubtitle = computed(() => {
  const s = [
    'Captura la huella plantar del paciente',
    'Sube o toma la foto de la vista frontal',
    'Sube o toma la foto de la vista sagital',
    'Sube o toma la foto (frontal y/o sagital)',
  ]
  return s[step.value]
})

const currentResult = computed(() => {
  if (step.value === 0) return analisisState.value.podometria.result
  if (step.value === 1) return analisisState.value.frontal.result
  if (step.value === 2) return analisisState.value.sagital.result
  if (step.value === 3) return analisisState.value.miofascial.result
  return null
})

const isNextDisabled = computed(() => {
  if (step.value === 0) return !form.value.podometriaImg
  if (step.value === 1) return !form.value.tibiofemoralFrontal
  if (step.value === 2) return !form.value.tibiofemoralSagital
  if (step.value === 3) return !form.value.miofascialFrontal && !form.value.miofascialSagital
  return false
})

function errMsg(data, fallback) {
  if (!data) return fallback
  if (typeof data === 'string' && data.trim()) return data
  return data.detail || data.message || data.error || fallback
}

async function handleFileChange(e) {
  const files = e.target.files
  if (!files?.length) return
  const key = uploadKey.value
  form.value[key] = files[0]
  pieLoading.value = true
  const s = step.value
  const endpoint = STEPS[s]?.endpoint || ''
  const label = STEPS[s]?.short || 'imagen'
  const fd = new FormData()
  fd.append('file', files[0])
  if (s === 0) {
    fd.append('binarization_type', binarizationType.value)
    fd.append('adaptive_c', adaptiveC.value.toString())
    fd.append('fixed_threshold', fixedThreshold.value.toString())
    fd.append('invert', invertThreshold.value.toString())
    fd.append('foot_length_cm', (footLengthCm.value || 0).toString())
  }
  try {
    const res = await fetch(endpoint, { method: 'POST', body: fd })
    let data = null
    try { data = await res.json() } catch {}
    if (!res.ok) {
      Swal.fire({ icon: 'error', title: 'Error al procesar', text: errMsg(data, `El servidor respondió con estado ${res.status}.`) })
      return
    }
    let ok = false
    if (s === 0 && data?.metrics) {
      ok = true
      const calibrated = data.metrics.calibrated
      analisisState.value.podometria.result = [{
        tipo: data.metrics.classification,
        porcentajeX: data.metrics.plantar_index?.toFixed(2),
        X: calibrated
          ? data.metrics.x_width_cm?.toFixed(1) + ' cm'
          : data.metrics.x_width_px?.toFixed(0) + ' px (sin calibrar)',
        Y: calibrated
          ? data.metrics.y_width_cm?.toFixed(1) + ' cm'
          : data.metrics.y_width_px?.toFixed(0) + ' px (sin calibrar)',
      }]
      if (data.images?.annotated) { analisisState.value.podometria.debugImg = data.images.annotated; pieDebugImg.value = data.images.annotated }
      const reader = new FileReader()
      reader.onload = ev => { analisisState.value.podometria.huella = ev.target.result }
      reader.readAsDataURL(files[0])
    } else if (s === 1 && data?.metrics) {
      ok = true
      analisisState.value.frontal.result = { tipo: data.metrics.classification, angulo: data.metrics.knee_angle_deg?.toFixed(1) + '°' }
      if (data.images?.annotated) { analisisState.value.frontal.debugImg = data.images.annotated; pieDebugImg.value = data.images.annotated }
    } else if (s === 2 && data?.metrics) {
      ok = true
      analisisState.value.sagital.result = { tipo: data.metrics.classification, angulo: data.metrics.knee_angle_deg?.toFixed(1) + '°' }
      if (data.images?.annotated) { analisisState.value.sagital.debugImg = data.images.annotated; pieDebugImg.value = data.images.annotated }
    } else if (s === 3 && (data?.chain || data?.explanation || data?.rasgos)) {
      ok = true
      analisisState.value.miofascial.result = [{ tipo: data.chain, explicacion: data.explanation, rasgos: data.rasgos }]
      if (data.imagen_original) analisisState.value.miofascial.imagen_original = data.imagen_original
      if (data.images?.annotated) { analisisState.value.miofascial.debugImg = data.images.annotated; pieDebugImg.value = data.images.annotated }
    }
    if (!ok) Swal.fire({ icon: 'error', title: 'Sin datos válidos', text: `El servidor no devolvió datos reconocibles para ${label}.` })
  } catch (err) {
    Swal.fire({ icon: 'error', title: 'Error de conexión', text: err?.message || `No se pudo conectar con el servidor (${label}).` })
  } finally {
    pieLoading.value = false
  }
}

function handleSubmit() {
  if (!props.initial) {
    const checks = [
      analisisState.value.podometria.result,
      analisisState.value.frontal.result,
      analisisState.value.sagital.result,
      analisisState.value.miofascial.result,
    ]
    if (!checks[step.value]) {
      Swal.fire({ icon: 'error', title: 'Imagen no procesada', text: 'Sube y procesa la imagen antes de continuar.' })
      return
    }
  }
  if (step.value < 3) {
    step.value++
    pieDebugImg.value = null
    pieBinImg.value = null
    return
  }
  if (!form.value.miofascialFrontal && !form.value.miofascialSagital) {
    Swal.fire({ icon: 'warning', title: 'Falta imagen', text: 'Sube al menos una imagen para la cadena miofascial.' })
    return
  }
  const st = analisisState.value
  const id = form.value.id || Date.now()
  emit('save', {
    tipoTest: form.value.tipoTest,
    fecha: form.value.fecha,
    completado: form.value.completado,
    id,
    pdfUrl: null,
    podometriaResult: st.podometria.result ?? null,
    podometriaDebugImg: st.podometria.debugImg ?? null,
    podometriaHuella: st.podometria.huella ?? null,
    frontalResult: st.frontal.result ?? null,
    frontalDebugImg: st.frontal.debugImg ?? null,
    sagitalResult: st.sagital.result ?? null,
    sagitalDebugImg: st.sagital.debugImg ?? null,
    miofascialResult: st.miofascial.result ?? null,
    miofascialDebugImg: st.miofascial.debugImg ?? null,
    miofascialImagenOriginal: st.miofascial.imagen_original ?? null,
  })
  Swal.fire({ icon: 'success', title: props.initial ? 'Análisis actualizado' : 'Análisis guardado', timer: 1600, showConfirmButton: false })
  generateAndDownloadPdf(id)
}

function generateAndDownloadPdf(analysisId) {
  const st = analisisState.value
  const analisis = []
  if (st.podometria.result) {
    const imgs = []
    if (st.podometria.huella) imgs.push({ titulo: 'Huella plantar', base64: st.podometria.huella.replace(/^data:image\/\w+;base64,/, '') })
    if (st.podometria.debugImg) imgs.push({ titulo: 'Podometría', base64: st.podometria.debugImg.replace(/^data:image\/\w+;base64,/, '') })
    analisis.push({ titulo: 'Podometría digital', explicacion: `Tipo de pie: ${st.podometria.result[0]?.tipo || ''}`, metricas: [`Índice: ${st.podometria.result[0]?.porcentajeX || ''}`], imagenes: imgs })
  }
  if (st.frontal.result) {
    const imgs = st.frontal.debugImg ? [{ titulo: 'Frontal', base64: st.frontal.debugImg.replace(/^data:image\/\w+;base64,/, '') }] : []
    analisis.push({ titulo: 'Ángulo tibiofemoral (frontal)', explicacion: st.frontal.result.tipo || '', metricas: [`Ángulo: ${st.frontal.result.angulo}`], imagenes: imgs })
  }
  if (st.sagital.result) {
    const imgs = st.sagital.debugImg ? [{ titulo: 'Sagital', base64: st.sagital.debugImg.replace(/^data:image\/\w+;base64,/, '') }] : []
    analisis.push({ titulo: 'Ángulo tibiofemoral (sagital)', explicacion: st.sagital.result.tipo || '', metricas: [`Ángulo: ${st.sagital.result.angulo}`], imagenes: imgs })
  }
  if (st.miofascial.result) {
    const imgs = st.miofascial.debugImg ? [{ titulo: 'Miofascial', base64: st.miofascial.debugImg.replace(/^data:image\/\w+;base64,/, '') }] : []
    analisis.push({ titulo: 'Cadena miofascial', tipo: st.miofascial.result[0]?.tipo || '', explicacion: st.miofascial.result[0]?.explicacion || '', metricas: st.miofascial.result[0]?.rasgos || [], imagenes: imgs })
  }
  const patient = currentPatient.value
  const reportData = {
    paciente: {
      nombre: patient?.nombre || 'Paciente',
      edad: patient?.edad ?? null,
      sexo: patient?.sexo ?? null,
    },
    fecha: form.value.fecha,
    analisis,
  }
  if (st.miofascial.imagen_original) reportData.imagen_original = st.miofascial.imagen_original
  fetch('http://127.0.0.1:8000/generate-report/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(reportData),
  })
    .then(res => res.blob())
    .then(blob => {
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'ReportePaciente.pdf'
      document.body.appendChild(a)
      a.click()
      a.remove()
    })
    .catch(() => {})
}

function goBack() {
  if (step.value > 0) { step.value--; pieDebugImg.value = null; pieBinImg.value = null }
}

function handleCancel() {
  Swal.fire({
    icon: 'question',
    title: '¿Cancelar análisis?',
    text: 'Los datos no guardados se perderán.',
    showCancelButton: true,
    confirmButtonText: 'Sí, cancelar',
    cancelButtonText: 'Volver',
    reverseButtons: true,
  }).then(r => { if (r.isConfirmed) emit('cancel') })
}

function stopStream() {
  stream.value?.getTracks().forEach(t => t.stop())
  stream.value = null
}

async function refreshCameras() {
  if (!navigator.mediaDevices?.enumerateDevices) return
  availableCameras.value = (await navigator.mediaDevices.enumerateDevices()).filter(d => d.kind === 'videoinput')
}

async function handleOpenCamera() {
  if (!form.value.cameraDevice) return alert('Selecciona una cámara')
  showCamera.value = true
  try {
    const ms = await navigator.mediaDevices.getUserMedia({ video: { deviceId: { exact: form.value.cameraDevice } } })
    stream.value = ms
    setTimeout(() => { if (videoRef.value) videoRef.value.srcObject = ms }, 100)
  } catch {
    alert('No se pudo acceder a la cámara')
    showCamera.value = false
  }
}

function handleCapture() {
  if (!videoRef.value || !canvasRef.value) return
  const v = videoRef.value, c = canvasRef.value
  c.width = v.videoWidth; c.height = v.videoHeight
  c.getContext('2d').drawImage(v, 0, 0)
  c.toBlob(blob => { form.value[uploadKey.value] = blob; showCamera.value = false; stopStream() })
}
</script>

<style scoped>
.af-shell {
  min-height: calc(100vh - 120px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 2rem 1rem;
}
.af-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  padding: 2.5rem 2rem;
  width: 100%;
  max-width: 660px;
}

/* Step bar */
.step-bar {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
}
.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
}
.step-connector {
  position: absolute;
  left: -50%;
  right: 50%;
  top: 14px;
  height: 2px;
  background: var(--border);
  z-index: 0;
  transition: background 0.3s;
}
.step-connector.done { background: var(--primary); }
.step-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid var(--border);
  background: var(--surface);
  color: var(--text-subtle);
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
  transition: all 0.25s;
}
.step-dot.active { border-color: var(--primary); color: var(--primary); background: var(--primary-light); box-shadow: 0 0 0 4px var(--primary-ring); }
.step-dot.done   { border-color: var(--primary); background: var(--primary); color: #fff; }
.step-label {
  font-size: 0.65rem;
  font-weight: 600;
  color: var(--text-subtle);
  margin-top: 6px;
  text-align: center;
  transition: color 0.25s;
  white-space: nowrap;
}
.step-label.active { color: var(--primary); }
.step-label.done   { color: var(--text-muted); }

/* Header */
.af-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 1.5rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border);
}
.af-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid var(--border);
}
.af-title    { font-size: 1.05rem; font-weight: 800; color: var(--text-base); letter-spacing: -0.02em; }
.af-subtitle { font-size: 0.78rem; color: var(--text-muted); margin-top: 2px; }

/* Binarization */
.bin-controls {
  background: var(--surface-3);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-bottom: 1.25rem;
}
.bin-row { display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; }
.bin-label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
}
.bin-select {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-xs);
  padding: 0.3rem 0.5rem;
  font-size: 0.8rem;
  color: var(--text-base);
  outline: none;
}
.bin-range { width: 120px; accent-color: var(--primary); }
.bin-check { accent-color: var(--primary); width: 15px; height: 15px; }
.bin-preview { margin-top: 10px; }
.bin-preview-label { font-size: 0.72rem; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; display: block; }
.bin-preview-img { max-width: 280px; border-radius: var(--radius-sm); border: 1.5px solid var(--border); }

/* Tabs */
.capture-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  background: var(--surface-3);
  border-radius: var(--radius-sm);
  padding: 3px;
  gap: 3px;
  margin-bottom: 1rem;
}
.capture-tab {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 0.55rem;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-muted);
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.18s;
}
.capture-tab.active {
  background: var(--surface);
  color: var(--primary);
  box-shadow: var(--shadow-xs);
}

/* Upload */
.upload-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius-md);
  padding: 2rem 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  position: relative;
  background: var(--surface-2);
  margin-bottom: 1rem;
}
.upload-zone:hover, .upload-zone:focus-within {
  border-color: var(--primary);
  background: var(--primary-light);
}
.upload-zone.uploaded {
  border-color: rgba(22,163,74,0.5);
  background: rgba(22,163,74,0.07);
  border-style: solid;
}
.upload-zone input[type="file"] {
  position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%;
}
.upload-icon {
  width: 44px; height: 44px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 10px;
  color: var(--text-muted);
}
.upload-title { font-size: 0.875rem; font-weight: 700; color: var(--text-base); margin-bottom: 3px; }
.upload-hint  { font-size: 0.75rem; color: var(--text-subtle); }
.upload-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--primary);
}

/* Results */
.result-panel {
  background: rgba(22,163,74,0.08);
  border: 1.5px solid rgba(22,163,74,0.25);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-bottom: 1rem;
}
.result-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--success);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 10px;
}
.result-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 6px; }
.result-chip {
  background: var(--surface);
  border: 1px solid rgba(22,163,74,0.2);
  border-radius: 6px;
  padding: 0.3rem 0.7rem;
  font-size: 0.78rem;
  color: var(--text-muted);
}
.result-chip strong { color: var(--text-base); font-weight: 700; }
.result-explanation { font-size: 0.8rem; color: var(--text-muted); margin: 4px 0; width: 100%; }
.result-rasgos {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 4px 0 0 1rem;
  padding: 0;
  list-style: disc;
}
.result-rasgos li { margin-bottom: 2px; }
.result-debug { margin-top: 10px; }
.result-debug-label { font-size: 0.72rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 6px; }
.result-debug-img { max-width: 280px; border-radius: var(--radius-sm); border: 1.5px solid #d1fae5; }

/* Camera */
.camera-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 1rem;
  padding: 1rem;
  background: var(--surface-3);
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
}
.camera-ok {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--success);
}

/* Actions */
.af-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border);
  gap: 8px;
}

/* Camera modal */
.cam-overlay {
  position: fixed; inset: 0;
  background: rgba(15,23,42,0.55);
  backdrop-filter: blur(6px);
  z-index: 50;
  display: flex; align-items: center; justify-content: center;
  padding: 1rem;
}
.cam-box {
  background: var(--surface);
  border-radius: var(--radius-xl);
  padding: 1.5rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.25);
}
.cam-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 1rem;
}
.cam-header h3 { font-size: 1rem; font-weight: 700; color: var(--text-base); }
.cam-close {
  width: 30px; height: 30px;
  border-radius: var(--radius-xs);
  background: var(--surface-3);
  border: 1px solid var(--border);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: var(--text-muted);
  transition: background 0.15s;
}
.cam-close:hover { background: #fee2e2; color: var(--error); }
.cam-video {
  width: 100%;
  border-radius: var(--radius-md);
  background: #0f172a;
  aspect-ratio: 4/3;
  object-fit: cover;
  display: block;
  margin-bottom: 1rem;
}
</style>
