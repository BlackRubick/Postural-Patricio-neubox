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
          <span class="af-step-num">{{ step + 1 }}</span>
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

      <!-- Miofascial: 3 image uploads for frontal and posterior (sagital is handled below) -->
      <div v-if="step === 5" class="mio-extra-images">
        <p class="mio-extra-label">Imagen anterior / frontal</p>
        <div class="upload-zone" :class="{ uploaded: !!form.miofascialFrontalImg }" style="margin-bottom:0.75rem">
          <input type="file" accept="image/*" capture="environment" @change="e => { const f = e.target.files?.[0]; if(f){ form.miofascialFrontalImg = f; const r = new FileReader(); r.onload = ev => { analisisState.miofascial.imagen_frontal = ev.target.result }; r.readAsDataURL(f) } }" />
          <div class="upload-icon">
            <svg v-if="!form.miofascialFrontalImg" width="20" height="20" fill="none" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <svg v-else width="20" height="20" fill="none" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <p class="upload-title" style="font-size:.8rem">{{ form.miofascialFrontalImg ? 'Anterior / frontal lista' : 'Subir imagen anterior / frontal' }}</p>
        </div>
        <p class="mio-extra-label">Imagen posterior / espalda</p>
        <div class="upload-zone" :class="{ uploaded: !!form.miofascialPosteriorImg }" style="margin-bottom:0.75rem">
          <input type="file" accept="image/*" capture="environment" @change="e => { const f = e.target.files?.[0]; if(f){ form.miofascialPosteriorImg = f; const r = new FileReader(); r.onload = ev => { analisisState.miofascial.imagen_posterior = ev.target.result }; r.readAsDataURL(f) } }" />
          <div class="upload-icon">
            <svg v-if="!form.miofascialPosteriorImg" width="20" height="20" fill="none" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <svg v-else width="20" height="20" fill="none" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <p class="upload-title" style="font-size:.8rem">{{ form.miofascialPosteriorImg ? 'Posterior / espalda lista' : 'Subir imagen posterior / espalda' }}</p>
        </div>
        <p class="mio-extra-label">Imagen lateral / sagital</p>
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

        <!-- Podometría (paso 0) — un resultado por pie -->
        <template v-if="step === 0 && analisisState.podometria.result">
          <div class="result-row" v-for="(r, i) in analisisState.podometria.result" :key="i">
            <div class="result-chip" v-if="r.lado"><strong>Pie {{ r.lado }}</strong></div>
            <div class="result-chip">Tipo: <strong>{{ r.tipo }}</strong></div>
            <div class="result-chip">Índice: <strong>{{ r.porcentajeX }}</strong></div>
            <div class="result-chip" v-if="r.X">Ancho X: <strong>{{ r.X }}</strong></div>
            <div class="result-chip" v-if="r.Y">Ancho Y: <strong>{{ r.Y }}</strong></div>
          </div>
        </template>

        <!-- Frontal (paso 1) -->
        <template v-if="step === 1 && analisisState.frontal.result">
          <div class="result-row">
            <div class="result-chip">Clasificación: <strong>{{ analisisState.frontal.result.tipo }}</strong></div>
            <div class="result-chip">Ángulo: <strong>{{ analisisState.frontal.result.angulo }}</strong></div>
          </div>
        </template>

        <!-- Sagital (paso 2) -->
        <template v-if="step === 2 && analisisState.sagital.result">
          <div class="result-row">
            <div class="result-chip">Clasificación: <strong>{{ analisisState.sagital.result.tipo }}</strong></div>
            <div class="result-chip">Ángulo: <strong>{{ analisisState.sagital.result.angulo }}</strong></div>
          </div>
        </template>

        <!-- Alineación sagital (paso 3) -->
        <template v-if="step === 3 && analisisState.alineacionSagital.result">
          <div class="result-row">
            <div class="result-chip">Clasificación: <strong>{{ analisisState.alineacionSagital.result.tipo }}</strong></div>
            <div class="result-chip">Hombro: <strong>{{ analisisState.alineacionSagital.result.hombro }}%</strong></div>
            <div class="result-chip">Oreja: <strong>{{ analisisState.alineacionSagital.result.oreja }}%</strong></div>
          </div>
        </template>

        <!-- Vertical de Barré (paso 4) -->
        <template v-if="step === 4 && analisisState.alineacionFrontal.result">
          <div class="result-row">
            <div class="result-chip">Tipo Barré: <strong>{{ analisisState.alineacionFrontal.result.tipo }}</strong></div>
            <div class="result-chip" v-if="analisisState.alineacionFrontal.result.clasificacion">Clasificación: <strong>{{ analisisState.alineacionFrontal.result.clasificacion }}</strong></div>
            <div class="result-chip" v-if="analisisState.alineacionFrontal.result.nariz != null">Desviación: <strong>{{ analisisState.alineacionFrontal.result.nariz }}%</strong></div>
          </div>
          <p v-if="analisisState.alineacionFrontal.result.descripcion" class="result-explanation">{{ analisisState.alineacionFrontal.result.descripcion }}</p>
        </template>

        <!-- Miofascial (paso 5) — rasgos con palomitas + porcentaje -->
        <template v-if="step === 5 && analisisState.miofascial.result">
          <div v-for="(r, i) in analisisState.miofascial.result" :key="i">
            <div class="result-row">
              <div class="result-chip">Cadena: <strong>{{ r.tipo }}</strong></div>
              <div class="result-chip result-chip-pct">{{ r.porcentaje?.toFixed(0) }}% de rasgos</div>
            </div>
            <p class="result-explanation">{{ r.explicacion }}</p>
            <ul v-if="r.rasgos_detallados?.length" class="result-rasgos-detallados">
              <li v-for="(rasgo, idx) in r.rasgos_detallados" :key="idx" class="rasgo-item">
                <span class="rasgo-icon" :style="{ color: rasgoColor(rasgo.cumple, rasgo.auto) }">
                  {{ rasgoIcon(rasgo.cumple, rasgo.auto) }}
                </span>
                <span class="rasgo-nombre" :class="{ 'rasgo-cumple': rasgo.cumple && rasgo.auto, 'rasgo-no': !rasgo.cumple && rasgo.auto }">
                  {{ rasgo.nombre }}
                </span>
              </li>
            </ul>
            <!-- Barra de porcentaje -->
            <div class="rasgo-pct-bar-wrap">
              <div class="rasgo-pct-bar">
                <div class="rasgo-pct-fill"
                  :style="{ width: (r.porcentaje || 0) + '%', background: (r.porcentaje||0) >= 50 ? '#16a34a' : (r.porcentaje||0) >= 25 ? '#d97706' : '#dc2626' }"
                ></div>
              </div>
              <span class="rasgo-pct-label">{{ r.porcentaje?.toFixed(0) }}%</span>
            </div>
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

      <!-- Notas del análisis (último paso) -->
      <div v-if="step === LAST_STEP" class="notas-section">
        <label class="notas-label">Observaciones / notas clínicas <span style="font-weight:400;color:var(--text-subtle)">(opcional)</span></label>
        <textarea
          v-model="form.notas"
          rows="3"
          placeholder="Escribe aquí las observaciones del análisis..."
          class="notas-input"
        ></textarea>
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
          {{ step < LAST_STEP ? 'Continuar' : 'Guardar análisis' }}
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
import { nextTick } from 'vue'
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

onMounted(async () => {
  if (props.patientId && !store.patients.length) {
    try { await store.loadPatients() } catch {}
  }
})

const STEPS = [
  { short: 'Podometría',    color: '#eff6ff', endpoint: 'http://127.0.0.1:8000/analyze-foot/' },
  { short: 'Frontal',       color: '#f0fdf4', endpoint: 'http://127.0.0.1:8000/analyze-knee/frontal/' },
  { short: 'Sagital',       color: '#fdf4ff', endpoint: 'http://127.0.0.1:8000/analyze-knee/sagittal/' },
  { short: 'Alin. Sagital', color: '#f0f9ff', endpoint: 'http://127.0.0.1:8000/analyze-alignment/sagittal/' },
  { short: 'V. de Barré',   color: '#f0fdf9', endpoint: 'http://127.0.0.1:8000/analyze-alignment/frontal/' },
  { short: 'Miofascial',    color: '#fff7ed', endpoint: 'http://127.0.0.1:8000/analyze-muscle-chain/' },
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
  alineacionSagitalImg: null,
  alineacionFrontalImg: null,
  miofascialFrontalImg: null,
  miofascialPosteriorImg: null,
  miofascialSagitalImg: null,
  tomarFoto: false,
  notas: '',
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
  podometria:        { result: null, debugImg: null, binImg: null, huella: null },
  frontal:           { result: null, debugImg: null },
  sagital:           { result: null, debugImg: null },
  alineacionSagital: { result: null, debugImg: null },
  alineacionFrontal: { result: null, debugImg: null },
  miofascial:        { result: null, debugImg: null, imagen_original: null, imagen_frontal: null, imagen_posterior: null },
})

const LAST_STEP = STEPS.length - 1

const uploadKey = computed(() => {
  if (step.value === 0) return 'podometriaImg'
  if (step.value === 1) return 'tibiofemoralFrontal'
  if (step.value === 2) return 'tibiofemoralSagital'
  if (step.value === 3) return 'alineacionSagitalImg'
  if (step.value === 4) return 'alineacionFrontalImg'
  return 'miofascialSagitalImg'
})

const stepTitle = computed(() => {
  const t = [
    'Podometría digital',
    'Ángulo Tibiofemoral (Anterior o Frontal)',
    'Ángulo Tibiofemoral (Lateral o Sagital)',
    'Alineación Postural — Línea Plomada de Kendall',
    'Vertical de Barré',
    'Evaluación de Cadenas Miofasiales',
  ]
  return props.initial ? 'Editar Test' : t[step.value]
})

const stepSubtitle = computed(() => {
  const s = [
    'Captura la huella plantar del paciente',
    'Sube o toma la imagen anterior / frontal (rodilla)',
    'Sube o toma la imagen lateral / sagital (rodilla)',
    'Vista lateral — evaluación con línea plomada de Kendall',
    'Vista posterior / espalda — línea vertical de Barré',
    'Sube 3 imágenes posturales para el análisis de cadenas miofasiales',
  ]
  return s[step.value]
})

const currentResult = computed(() => {
  if (step.value === 0) return analisisState.value.podometria.result
  if (step.value === 1) return analisisState.value.frontal.result
  if (step.value === 2) return analisisState.value.sagital.result
  if (step.value === 3) return analisisState.value.alineacionSagital.result
  if (step.value === 4) return analisisState.value.alineacionFrontal.result
  if (step.value === 5) return analisisState.value.miofascial.result
  return null
})

const isNextDisabled = computed(() => {
  if (step.value === 0) return !form.value.podometriaImg
  if (step.value === 1) return !form.value.tibiofemoralFrontal
  if (step.value === 2) return !form.value.tibiofemoralSagital
  if (step.value === 3) return !form.value.alineacionSagitalImg
  if (step.value === 4) return !form.value.alineacionFrontalImg
  if (step.value === 5) return !form.value.miofascialSagitalImg
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
  if (s === 5 && form.value.miofascialFrontalImg) fd.append('file_frontal', form.value.miofascialFrontalImg)
  if (s === 5 && form.value.miofascialPosteriorImg) fd.append('file_posterior', form.value.miofascialPosteriorImg)
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
      // metrics ahora es array (un entry por pie)
      const metricsArr = Array.isArray(data.metrics) ? data.metrics : [data.metrics]
      analisisState.value.podometria.result = metricsArr.map(m => ({
        lado: m.side || '',
        tipo: m.classification,
        porcentajeX: m.plantar_index?.toFixed(2),
        X: m.calibrated
          ? m.x_width_cm?.toFixed(1) + ' cm'
          : m.x_width_px?.toFixed(0) + ' px',
        Y: m.calibrated
          ? m.y_width_cm?.toFixed(1) + ' cm'
          : m.y_width_px?.toFixed(0) + ' px',
      }))
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
    } else if (s === 3 && data?.metrics) {
      ok = true
      analisisState.value.alineacionSagital.result = {
        tipo: data.metrics.classification,
        hombro: data.metrics.shoulder_deviation_pct,
        oreja: data.metrics.ear_deviation_pct,
        lado: data.metrics.side,
      }
      if (data.images?.annotated) { analisisState.value.alineacionSagital.debugImg = data.images.annotated; pieDebugImg.value = data.images.annotated }
    } else if (s === 4 && data?.metrics) {
      ok = true
      analisisState.value.alineacionFrontal.result = {
        tipo: data.metrics.classification,
        clasificacion: data.metrics.barre_class ?? null,
        descripcion: data.metrics.barre_description ?? null,
        nariz: data.metrics.nose_deviation_pct,
        inferior_dev: data.metrics.inferior_deviation_pct ?? null,
        superior_dev: data.metrics.superior_deviation_pct ?? null,
      }
      if (data.images?.annotated) { analisisState.value.alineacionFrontal.debugImg = data.images.annotated; pieDebugImg.value = data.images.annotated }
    } else if (s === 5 && (data?.chain || data?.explanation || data?.rasgos)) {
      ok = true
      analisisState.value.miofascial.result = [{
        tipo: data.chain,
        explicacion: data.explanation,
        rasgos: data.rasgos,
        rasgos_detallados: data.rasgos_detallados || [],
        porcentaje: data.porcentaje ?? 0,
      }]
      if (data.imagen_original) analisisState.value.miofascial.imagen_original = data.imagen_original
      if (data.imagen_frontal) analisisState.value.miofascial.imagen_frontal = data.imagen_frontal
      if (data.imagen_posterior) analisisState.value.miofascial.imagen_posterior = data.imagen_posterior
      if (data.images?.annotated) { analisisState.value.miofascial.debugImg = data.images.annotated; pieDebugImg.value = data.images.annotated }
    }
    if (!ok) Swal.fire({ icon: 'error', title: 'Sin datos válidos', text: `El servidor no devolvió datos reconocibles para ${label}.` })
  } catch (err) {
    Swal.fire({ icon: 'error', title: 'Error de conexión', text: err?.message || `No se pudo conectar con el servidor (${label}).` })
  } finally {
    pieLoading.value = false
  }
}

async function handleSubmit() {
  if (!props.initial) {
    const checks = [
      analisisState.value.podometria.result,
      analisisState.value.frontal.result,
      analisisState.value.sagital.result,
      analisisState.value.alineacionSagital.result,
      analisisState.value.alineacionFrontal.result,
      analisisState.value.miofascial.result,
    ]
    if (!checks[step.value]) {
      Swal.fire({ icon: 'error', title: 'Imagen no procesada', text: 'Sube y procesa la imagen antes de continuar.' })
      return
    }
  }
  if (step.value < LAST_STEP) {
    step.value++
    pieDebugImg.value = null
    pieBinImg.value = null
    return
  }
  if (!form.value.miofascialSagitalImg) {
    Swal.fire({ icon: 'warning', title: 'Falta imagen', text: 'Sube al menos la imagen sagital para la cadena miofascial.' })
    return
  }
  const st = analisisState.value

  Swal.fire({ title: 'Guardando análisis...', allowOutsideClick: false, didOpen: () => Swal.showLoading() })

  try {
    const compressed = await compressAnalisisState(st)

    const body = {
      tipoTest: form.value.tipoTest,
      fecha: form.value.fecha,
      completado: form.value.completado,
      pdfUrl: null,
      notas: form.value.notas || null,
      podometriaResult: st.podometria.result ?? null,
      podometriaDebugImg: compressed.podometriaDebugImg ?? null,
      podometriaHuella: compressed.podometriaHuella ?? null,
      frontalResult: st.frontal.result ?? null,
      frontalDebugImg: compressed.frontalDebugImg ?? null,
      sagitalResult: st.sagital.result ?? null,
      sagitalDebugImg: compressed.sagitalDebugImg ?? null,
      alineacionSagitalResult: st.alineacionSagital.result ?? null,
      alineacionSagitalDebugImg: compressed.alineacionSagitalDebugImg ?? null,
      alineacionFrontalResult: st.alineacionFrontal.result ?? null,
      alineacionFrontalDebugImg: compressed.alineacionFrontalDebugImg ?? null,
      miofascialResult: st.miofascial.result ?? null,
      miofascialDebugImg: compressed.miofascialDebugImg ?? null,
      miofascialImagenOriginal: compressed.miofascialImagenOriginal ?? null,
      miofascialFrontalImg: compressed.miofascialFrontalImg ?? null,
      miofascialPosteriorImg: compressed.miofascialPosteriorImg ?? null,
    }

    const saved = props.initial
      ? await $fetch(`/api/analyses/${props.initial.id}`, { method: 'PUT', body })
      : await $fetch(`/api/patients/${props.patientId}/analyses`, { method: 'POST', body })

    emit('save', saved)
    Swal.fire({ icon: 'success', title: props.initial ? 'Análisis actualizado' : 'Análisis guardado', timer: 1600, showConfirmButton: false })
    generateAndDownloadPdf(saved.id)
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Error al guardar', text: e?.data?.message || e?.message || 'No se pudo guardar el análisis.' })
  }
}

function compressBase64Image(src, maxWidth = 800, quality = 0.72) {
  if (!src) return Promise.resolve(src)
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      const scale = Math.min(1, maxWidth / img.width)
      const canvas = document.createElement('canvas')
      canvas.width  = Math.round(img.width  * scale)
      canvas.height = Math.round(img.height * scale)
      canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height)
      resolve(canvas.toDataURL('image/jpeg', quality))
    }
    img.onerror = () => resolve(src)
    img.src = src.startsWith('data:') ? src : `data:image/jpeg;base64,${src}`
  })
}

async function compressAnalisisState(st) {
  const [
    podDebug, podHuella,
    frontalDebug, sagitalDebug,
    alinSagDebug, alinFronDebug,
    miofDebug, miofOrig, miofFrontal, miofPosterior,
  ] = await Promise.all([
    compressBase64Image(st.podometria.debugImg),
    compressBase64Image(st.podometria.huella),
    compressBase64Image(st.frontal.debugImg),
    compressBase64Image(st.sagital.debugImg),
    compressBase64Image(st.alineacionSagital.debugImg),
    compressBase64Image(st.alineacionFrontal.debugImg),
    compressBase64Image(st.miofascial.debugImg),
    compressBase64Image(st.miofascial.imagen_original),
    compressBase64Image(st.miofascial.imagen_frontal),
    compressBase64Image(st.miofascial.imagen_posterior),
  ])
  return {
    podometriaDebugImg: podDebug,
    podometriaHuella: podHuella,
    frontalDebugImg: frontalDebug,
    sagitalDebugImg: sagitalDebug,
    alineacionSagitalDebugImg: alinSagDebug,
    alineacionFrontalDebugImg: alinFronDebug,
    miofascialDebugImg: miofDebug,
    miofascialImagenOriginal: miofOrig,
    miofascialFrontalImg: miofFrontal,
    miofascialPosteriorImg: miofPosterior,
  }
}

function generateAndDownloadPdf(analysisId) {
  const st = analisisState.value
  const analisis = []

  if (st.podometria.result) {
    const imgs = []
    if (st.podometria.huella)   imgs.push({ titulo: 'Huella plantar', base64: st.podometria.huella.replace(/^data:image\/\w+;base64,/, '') })
    if (st.podometria.debugImg) imgs.push({ titulo: 'Podometría', base64: st.podometria.debugImg.replace(/^data:image\/\w+;base64,/, '') })
    const metricas = st.podometria.result.flatMap(r => [
      r.lado ? `Pie ${r.lado} — Tipo: ${r.tipo}` : `Tipo de pie: ${r.tipo}`,
      `Índice plantar: ${r.porcentajeX || ''}`,
      r.X ? `Ancho X: ${r.X}` : null,
      r.Y ? `Ancho Y: ${r.Y}` : null,
    ].filter(Boolean))
    const exp = st.podometria.result.map(r => `${r.lado ? 'Pie ' + r.lado + ': ' : ''}${r.tipo}`).join(' | ')
    analisis.push({ titulo: 'Podometría digital', explicacion: exp, metricas, imagenes: imgs })
  }

  if (st.frontal.result) {
    const imgs = st.frontal.debugImg ? [{ titulo: 'Vista frontal', base64: st.frontal.debugImg.replace(/^data:image\/\w+;base64,/, '') }] : []
    analisis.push({ titulo: 'Ángulo Tibiofemoral (Anterior o Frontal)', explicacion: st.frontal.result.tipo || '', metricas: [`Ángulo: ${st.frontal.result.angulo}`], imagenes: imgs })
  }

  if (st.sagital.result) {
    const imgs = st.sagital.debugImg ? [{ titulo: 'Vista lateral / sagital', base64: st.sagital.debugImg.replace(/^data:image\/\w+;base64,/, '') }] : []
    analisis.push({ titulo: 'Ángulo Tibiofemoral (Lateral o Sagital)', explicacion: st.sagital.result.tipo || '', metricas: [`Ángulo: ${st.sagital.result.angulo}`], imagenes: imgs })
  }

  if (st.alineacionSagital.result) {
    const r = st.alineacionSagital.result
    const imgs = st.alineacionSagital.debugImg ? [{ titulo: 'Alineación — Línea Plomada de Kendall', base64: st.alineacionSagital.debugImg.replace(/^data:image\/\w+;base64,/, '') }] : []
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

  if (st.alineacionFrontal.result) {
    const r = st.alineacionFrontal.result
    const imgs = st.alineacionFrontal.debugImg ? [{ titulo: 'Vertical de Barré', base64: st.alineacionFrontal.debugImg.replace(/^data:image\/\w+;base64,/, '') }] : []
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

  if (st.miofascial.result) {
    const m = st.miofascial.result[0]
    const imgs = []
    if (st.miofascial.debugImg)    imgs.push({ titulo: 'Cadena miofascial (lateral / sagital)', base64: st.miofascial.debugImg.replace(/^data:image\/\w+;base64,/, '') })
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

  const patient = currentPatient.value
  const reportData = {
    paciente: {
      nombre: patient?.nombre || 'Paciente',
      edad: patient?.edad ?? null,
      sexo: patient?.sexo ?? null,
      altura: patient?.altura ?? null,
    },
    fecha: form.value.fecha,
    notas: form.value.notas || null,
    analisis,
  }
  if (st.miofascial.imagen_original) reportData.imagen_original = st.miofascial.imagen_original
  if (st.miofascial.imagen_frontal)  reportData.imagen_frontal = st.miofascial.imagen_frontal
  if (st.miofascial.imagen_posterior) reportData.imagen_posterior = st.miofascial.imagen_posterior

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

function rasgoIcon(cumple, auto) {
  if (!auto) return '·'
  return cumple ? '✓' : '✗'
}
function rasgoColor(cumple, auto) {
  if (!auto) return '#94a3b8'
  return cumple ? '#16a34a' : '#dc2626'
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
  // getUserMedia is required first so the browser exposes device labels
  let tempStream = null
  try {
    tempStream = await navigator.mediaDevices.getUserMedia({ video: true })
  } catch {}
  availableCameras.value = (await navigator.mediaDevices.enumerateDevices()).filter(d => d.kind === 'videoinput')
  tempStream?.getTracks().forEach(t => t.stop())
  if (availableCameras.value.length && !form.value.cameraDevice) {
    form.value.cameraDevice = availableCameras.value[0].deviceId
  }
}

watch(() => form.value.tomarFoto, (val) => { if (val) refreshCameras() })

async function handleOpenCamera() {
  if (!form.value.cameraDevice) return alert('Selecciona una cámara')
  showCamera.value = true
  await nextTick()
  try {
    const ms = await navigator.mediaDevices.getUserMedia({ video: { deviceId: { exact: form.value.cameraDevice } } })
    stream.value = ms
    if (videoRef.value) videoRef.value.srcObject = ms
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
.af-step-num {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--primary);
  line-height: 1;
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
.result-chip-pct {
  background: #e0f2fe;
  border-color: #0ea5e9;
  color: #0369a1;
  font-weight: 700;
}
.result-rasgos-detallados {
  list-style: none;
  margin: 6px 0 0;
  padding: 0;
  width: 100%;
}
.rasgo-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 3px 0;
  font-size: 0.78rem;
  border-bottom: 1px solid rgba(0,0,0,0.04);
}
.rasgo-icon {
  font-size: 0.85rem;
  font-weight: 800;
  width: 16px;
  text-align: center;
  flex-shrink: 0;
}
.rasgo-nombre  { color: var(--text-muted); }
.rasgo-cumple  { color: #15803d; font-weight: 600; }
.rasgo-no      { color: #b91c1c; }
.rasgo-pct-bar-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  width: 100%;
}
.rasgo-pct-bar {
  flex: 1;
  height: 10px;
  background: #e2e8f0;
  border-radius: 99px;
  overflow: hidden;
}
.rasgo-pct-fill {
  height: 100%;
  border-radius: 99px;
  transition: width 0.4s ease;
}
.rasgo-pct-label {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-base);
  min-width: 32px;
  text-align: right;
}
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

/* Miofascial 3 images */
.mio-extra-images {
  background: var(--surface-3);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-bottom: 1rem;
}
.mio-extra-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 6px;
}

/* Notas */
.notas-section {
  margin-bottom: 1rem;
}
.notas-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-muted);
  margin-bottom: 6px;
}
.notas-input {
  width: 100%;
  padding: 0.6rem 0.8rem;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 0.85rem;
  color: var(--text-base);
  background: var(--surface-3);
  resize: vertical;
  outline: none;
  font-family: inherit;
  transition: border-color 0.15s, background 0.15s;
}
.notas-input:focus {
  border-color: var(--primary);
  background: var(--surface);
}
</style>
