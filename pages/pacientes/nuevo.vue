<template>
  <PatientForm
    :initial="null"
    @save="handleSave"
    @cancel="navigateTo('/')"
  />
</template>

<script setup>
import Swal from 'sweetalert2'
import { usePatientsStore } from '~/stores/patients'

const store = usePatientsStore()

async function handleSave(data) {
  try {
    await store.addPatient(data)
    await Swal.fire({ icon: 'success', title: 'Paciente registrado', timer: 1400, showConfirmButton: false })
    navigateTo('/')
  } catch (e) {
    Swal.fire({ icon: 'error', title: 'Error', text: e?.data?.message || 'No se pudo registrar el paciente.' })
  }
}
</script>
