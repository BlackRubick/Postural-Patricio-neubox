<template>
  <PatientForm
    v-if="patient"
    :initial="patient"
    @save="handleSave"
    @cancel="navigateTo('/')"
  />
  <div v-else class="p-8 text-center text-secondary card max-w-lg mx-auto mt-16">
    Paciente no encontrado.
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

async function handleSave(data) {
  try {
    await store.updatePatient(Number(route.params.id), data)
    navigateTo('/')
  } catch (e) {
    console.error('Error actualizando paciente:', e)
  }
}
</script>
