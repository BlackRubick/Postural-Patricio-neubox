<template>
  <AnalysisForm
    :initial="null"
    :patient-id="Number(route.params.id)"
    @save="handleSave"
    @cancel="navigateTo(`/pacientes/${route.params.id}/analisis`)"
  />
</template>

<script setup>
import { usePatientsStore } from '~/stores/patients'

const route = useRoute()
const store = usePatientsStore()

async function handleSave(data) {
  try {
    await store.addAnalysis(Number(route.params.id), data)
    navigateTo(`/pacientes/${route.params.id}/analisis`)
  } catch (e) {
    console.error('Error guardando análisis:', e)
  }
}
</script>
