<template>
  <div>
    <div v-if="store.loading" class="loading-shell">
      <div class="loading-grid">
        <div v-for="i in 6" :key="i" class="skeleton-card">
          <div class="skeleton" style="width:40px;height:40px;border-radius:12px;margin-bottom:12px"></div>
          <div class="skeleton" style="width:60%;height:12px;border-radius:6px;margin-bottom:8px"></div>
          <div class="skeleton" style="width:40%;height:10px;border-radius:6px"></div>
        </div>
      </div>
    </div>

    <PatientList
      v-else
      :patients="store.patients"
      @select="handleSelect"
      @add="navigateTo('/pacientes/nuevo')"
      @edit="p => navigateTo(`/pacientes/${p.id}/editar`)"
      @delete="handleDelete"
    />
  </div>
</template>

<script setup>
import Swal from 'sweetalert2'
import { usePatientsStore } from '~/stores/patients'

const store = usePatientsStore()

onMounted(async () => {
  try { await store.loadPatients() } catch (e) { console.error('Error cargando pacientes:', e) }
})

function handleSelect(patient) { navigateTo(`/pacientes/${patient.id}/analisis`) }

function handleDelete(patient) {
  Swal.fire({
    icon: 'warning',
    title: '¿Eliminar paciente?',
    text: 'Esta acción eliminará también todos sus análisis.',
    showCancelButton: true,
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar',
    reverseButtons: true,
  }).then(async result => {
    if (result.isConfirmed) {
      try {
        await store.deletePatient(patient.id)
        Swal.fire({ icon: 'success', title: 'Paciente eliminado', showConfirmButton: false, timer: 1200 })
      } catch (e) {
        Swal.fire({ icon: 'error', title: 'Error al eliminar', text: e.message })
      }
    }
  })
}
</script>

<style scoped>
.loading-shell {
  padding: 2rem 1.5rem;
}
.loading-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  max-width: 900px;
  margin: 2rem auto 0;
}
.skeleton-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1.25rem;
}
</style>
