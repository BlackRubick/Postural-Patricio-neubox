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

function handleSave(savedAnalysis) {
  store.insertAnalysis(Number(route.params.id), savedAnalysis)
  navigateTo(`/pacientes/${route.params.id}/analisis`)
}
</script>
