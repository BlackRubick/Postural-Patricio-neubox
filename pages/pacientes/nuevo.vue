<template>
  <PatientForm
    :initial="null"
    @save="handleSave"
    @cancel="navigateTo('/')"
  />
</template>

<script setup>
import { usePatientsStore } from '~/stores/patients'

const store = usePatientsStore()

async function handleSave(data) {
  try {
    await store.addPatient(data)
    navigateTo('/')
  } catch (e) {
    console.error('Error registrando paciente:', e)
  }
}
</script>
