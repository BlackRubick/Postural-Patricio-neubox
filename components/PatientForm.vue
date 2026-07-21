<template>
  <div class="w-full min-h-[calc(100vh-120px)] flex items-start justify-center px-4 py-10">
    <div class="w-full max-w-lg animate-fade-in">

      <!-- Card -->
      <div class="pf-card rounded-2xl shadow-sm overflow-hidden">
        <!-- Top accent -->
        <div class="h-1 w-full" style="background:linear-gradient(90deg,#2563eb,#7c3aed)"></div>

        <div class="p-8">
          <!-- Title -->
          <div class="flex items-center gap-3 mb-8">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" style="background:linear-gradient(135deg,#2563eb,#1d4ed8)">
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v1h16v-1c0-2.66-5.33-4-8-4z" fill="#fff"/>
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-bold text-gray-900 leading-tight">
                {{ initial ? 'Editar Paciente' : 'Registrar Paciente' }}
              </h2>
              <p class="text-xs text-gray-400 mt-0.5">Completa los datos del paciente</p>
            </div>
          </div>

          <form @submit.prevent="handleSubmit" class="flex flex-col gap-5">
            <!-- Nombre -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">Nombre completo</label>
              <input
                v-model="form.nombre"
                required
                autofocus
                placeholder="Ej. Juan García López"
                class="form-input"
              />
            </div>

            <!-- Edad + Sexo inline -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1.5">Edad</label>
                <input
                  v-model="form.edad"
                  type="number"
                  min="0"
                  max="120"
                  required
                  placeholder="Años"
                  class="form-input"
                />
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1.5">Sexo</label>
                <select v-model="form.sexo" required class="form-input">
                  <option value="">Seleccionar</option>
                  <option value="Masculino">Masculino</option>
                  <option value="Femenino">Femenino</option>
                  <option value="Otro">Otro</option>
                </select>
              </div>
            </div>

            <!-- Estatura -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">Estatura (cm) <span class="font-normal text-gray-400">— opcional</span></label>
              <input
                v-model="form.altura"
                type="number"
                min="50"
                max="250"
                step="0.5"
                placeholder="Ej. 170"
                class="form-input"
              />
            </div>

            <!-- Consentimiento -->
            <div class="consent-box rounded-xl p-4 mt-1">
              <label class="flex items-start gap-3 cursor-pointer select-none">
                <input
                  v-model="consent"
                  type="checkbox"
                  required
                  class="mt-0.5 w-4 h-4 rounded accent-blue-600 flex-shrink-0"
                />
                <span class="text-sm leading-snug" style="color:var(--text-muted)">
                  El paciente ha leído y acepta los
                  <button
                    type="button"
                    class="text-blue-600 font-semibold underline underline-offset-2 hover:text-blue-700 transition"
                    @click="modalOpen = true"
                  >
                    términos y condiciones
                  </button>
                  del aviso de privacidad.
                </span>
              </label>
            </div>

            <!-- Buttons -->
            <div class="flex justify-end gap-2.5 pt-2">
              <button type="button" class="btn-secondary text-sm" @click="handleCancel">
                Cancelar
              </button>
              <button
                type="submit"
                class="btn-primary text-sm"
                :disabled="!consent || !form.nombre.trim() || !form.edad || !form.sexo"
              >
                {{ initial ? 'Guardar cambios' : 'Registrar' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>

  <AppModal
    :open="modalOpen"
    title="Carta de Consentimiento Informado y Aviso de Privacidad"
    @close="modalOpen = false"
  >
    <div class="text-center mb-5">
      <span class="inline-flex items-center gap-1.5 bg-blue-50 text-blue-700 text-xs font-bold px-3 py-1.5 rounded-full">
        Proyecto: NEXO-POSTURAL: Kyene'is Pøndyam
      </span>
    </div>
    <div class="text-sm text-gray-700 space-y-4">
      <section>
        <h3 class="font-bold text-gray-900 mb-1">I. IDENTIDAD Y DOMICILIO DEL RESPONSABLE</h3>
        <p>El proyecto NEXO-POSTURAL, bajo la responsabilidad de Liliana Ruiz Alvarado y Ángel Enrique Patricio López, con domicilio en la Universidad Politécnica de Chiapas, es responsable del uso, tratamiento y protección de sus datos personales.</p>
      </section>
      <section>
        <h3 class="font-bold text-gray-900 mb-1">II. DATOS PERSONALES Y SENSIBLES</h3>
        <p>Se recabarán: nombre completo, fecha de nacimiento, sexo, estatura y peso. También datos sensibles:</p>
        <ul class="list-disc ml-5 mt-1 space-y-1">
          <li><span class="font-semibold">Imágenes Biométricas:</span> Registro fotográfico para detección de puntos anatómicos corporales.</li>
          <li><span class="font-semibold">Información de Salud:</span> Antecedentes médicos y diagnósticos derivados del estudio.</li>
        </ul>
      </section>
      <section>
        <h3 class="font-bold text-gray-900 mb-1">III. FINALIDAD</h3>
        <p>Los datos serán usados exclusivamente para análisis postural y generación de diagnósticos médicos relacionados con NEXO-POSTURAL.</p>
      </section>
      <section>
        <h3 class="font-bold text-gray-900 mb-1">IV. DERECHOS ARCO Y CONFIDENCIALIDAD</h3>
        <p>Tiene derecho a conocer, corregir o cancelar sus datos. Por NOM-004-SSA3-2012, los expedientes se conservan mínimo 5 años. Sus datos no serán divulgados y en investigación no podrá ser identificado.</p>
      </section>
      <section>
        <h3 class="font-bold text-gray-900 mb-1">V. DECLARACIÓN DE CONSENTIMIENTO</h3>
        <p>Al aceptar, autoriza al personal de NEXO-POSTURAL para la realización de diagnósticos biomecánicos y el tratamiento de sus datos personales conforme a este aviso.</p>
      </section>
    </div>
    <div class="flex justify-end mt-6">
      <button class="btn-primary text-sm" @click="modalOpen = false">Entendido</button>
    </div>
  </AppModal>
</template>

<script setup>
import Swal from 'sweetalert2'

const props = defineProps({
  initial: { type: Object, default: null },
})
const emit = defineEmits(['save', 'cancel'])

const form = ref(
  props.initial
    ? { nombre: props.initial.nombre, edad: props.initial.edad, sexo: props.initial.sexo, altura: props.initial.altura ?? '' }
    : { nombre: '', edad: '', sexo: '', altura: '' }
)
const consent = ref(false)
const modalOpen = ref(false)

function handleSubmit() {
  if (!consent.value) return
  emit('save', { ...form.value })
  Swal.fire({
    icon: 'success',
    title: props.initial ? 'Paciente editado' : 'Paciente registrado',
    timer: 1600,
    showConfirmButton: false,
  })
}

function handleCancel() {
  Swal.fire({
    icon: 'warning',
    title: '¿Cancelar?',
    text: 'Los cambios no se guardarán.',
    showCancelButton: true,
    confirmButtonText: 'Sí, cancelar',
    cancelButtonText: 'No',
    reverseButtons: true,
  }).then(result => {
    if (result.isConfirmed) emit('cancel')
  })
}
</script>

<style scoped>
.pf-card {
  background: var(--surface);
  border: 1px solid var(--border);
}
.consent-box {
  background: var(--surface-3);
  border: 1px solid var(--border);
}
.form-input {
  width: 100%;
  padding: 0.65rem 0.9rem;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 0.875rem;
  color: var(--text-base);
  background: var(--surface-3);
  transition: border-color 0.15s, box-shadow 0.15s, background 0.15s;
  outline: none;
}
.form-input:focus {
  border-color: var(--primary);
  background: var(--surface);
  box-shadow: 0 0 0 3px var(--primary-ring);
}
</style>
