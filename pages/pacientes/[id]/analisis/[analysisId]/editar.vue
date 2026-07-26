<template>
  <AnalysisForm
    v-if="analysis"
    :initial="analysis"
    :patient-id="Number(route.params.id)"
    @save="handleSave"
    @cancel="navigateTo(`/pacientes/${route.params.id}/analisis`)"
  />
  <div v-else class="p-8 text-center text-secondary card max-w-lg mx-auto mt-16">
    Análisis no encontrado.
  </div>
</template>

<script setup>
import { usePatientsStore } from '~/stores/patients'

const route = useRoute()
const store = usePatientsStore()

onMounted(async () => {
  if (!store.patients.length) {
    try {
      await store.loadPatients()
    } catch (e) {
      console.error('Error cargando pacientes:', e)
    }
  }
})

const patient = computed(() =>
  store.patients.find(p => p.id === Number(route.params.id)) || null
)

const analysis = computed(() =>
  patient.value?.analyses.find(a => a.id === Number(route.params.analysisId)) || null
)

function handleSave(savedAnalysis) {
  store.replaceAnalysis(Number(route.params.id), Number(route.params.analysisId), savedAnalysis)
  navigateTo(`/pacientes/${route.params.id}/analisis`)
}
</script>
