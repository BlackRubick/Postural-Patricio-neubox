import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePatientsStore = defineStore('patients', () => {
  const patients = ref([])
  const loading = ref(false)

  async function loadPatients() {
    loading.value = true
    try {
      patients.value = await $fetch('/api/patients')
    } finally {
      loading.value = false
    }
  }

  async function addPatient(data) {
    const created = await $fetch('/api/patients', {
      method: 'POST',
      body: { nombre: data.nombre, edad: data.edad, sexo: data.sexo },
    })
    patients.value.unshift(created)
    return created
  }

  async function updatePatient(id, data) {
    const updated = await $fetch(`/api/patients/${id}`, {
      method: 'PUT',
      body: { nombre: data.nombre, edad: data.edad, sexo: data.sexo },
    })
    const idx = patients.value.findIndex(p => p.id === id)
    if (idx !== -1) patients.value[idx] = updated
  }

  async function deletePatient(id) {
    await $fetch(`/api/patients/${id}`, { method: 'DELETE' })
    patients.value = patients.value.filter(p => p.id !== id)
  }

  async function addAnalysis(patientId, data) {
    const created = await $fetch(`/api/patients/${patientId}/analyses`, {
      method: 'POST',
      body: {
        tipoTest: data.tipoTest,
        fecha: data.fecha,
        completado: data.completado ?? false,
        pdfUrl: null,
        podometriaResult: data.podometriaResult ?? null,
        podometriaDebugImg: data.podometriaDebugImg ?? null,
        podometriaHuella: data.podometriaHuella ?? null,
        frontalResult: data.frontalResult ?? null,
        frontalDebugImg: data.frontalDebugImg ?? null,
        sagitalResult: data.sagitalResult ?? null,
        sagitalDebugImg: data.sagitalDebugImg ?? null,
        miofascialResult: data.miofascialResult ?? null,
        miofascialDebugImg: data.miofascialDebugImg ?? null,
        miofascialImagenOriginal: data.miofascialImagenOriginal ?? null,
        alineacionSagitalResult: data.alineacionSagitalResult ?? null,
        alineacionSagitalDebugImg: data.alineacionSagitalDebugImg ?? null,
        alineacionFrontalResult: data.alineacionFrontalResult ?? null,
        alineacionFrontalDebugImg: data.alineacionFrontalDebugImg ?? null,
      },
    })
    const patient = patients.value.find(p => p.id === patientId)
    if (patient) {
      if (!patient.analyses) patient.analyses = []
      patient.analyses.unshift(created)
    }
    return created
  }

  async function updateAnalysis(patientId, analysisId, data) {
    const updated = await $fetch(`/api/analyses/${analysisId}`, {
      method: 'PUT',
      body: {
        tipoTest: data.tipoTest,
        fecha: data.fecha,
        completado: data.completado ?? false,
        pdfUrl: data.pdfUrl ?? null,
        podometriaResult: data.podometriaResult ?? null,
        podometriaDebugImg: data.podometriaDebugImg ?? null,
        podometriaHuella: data.podometriaHuella ?? null,
        frontalResult: data.frontalResult ?? null,
        frontalDebugImg: data.frontalDebugImg ?? null,
        sagitalResult: data.sagitalResult ?? null,
        sagitalDebugImg: data.sagitalDebugImg ?? null,
        miofascialResult: data.miofascialResult ?? null,
        miofascialDebugImg: data.miofascialDebugImg ?? null,
        miofascialImagenOriginal: data.miofascialImagenOriginal ?? null,
        alineacionSagitalResult: data.alineacionSagitalResult ?? null,
        alineacionSagitalDebugImg: data.alineacionSagitalDebugImg ?? null,
        alineacionFrontalResult: data.alineacionFrontalResult ?? null,
        alineacionFrontalDebugImg: data.alineacionFrontalDebugImg ?? null,
      },
    })
    const patient = patients.value.find(p => p.id === patientId)
    if (patient) {
      const idx = patient.analyses.findIndex(a => a.id === analysisId)
      if (idx !== -1) patient.analyses[idx] = updated
    }
  }

  async function deleteAnalysis(patientId, analysisId) {
    await $fetch(`/api/analyses/${analysisId}`, { method: 'DELETE' })
    const patient = patients.value.find(p => p.id === patientId)
    if (patient) {
      patient.analyses = patient.analyses.filter(a => a.id !== analysisId)
    }
  }

  return {
    patients,
    loading,
    loadPatients,
    addPatient,
    updatePatient,
    deletePatient,
    addAnalysis,
    updateAnalysis,
    deleteAnalysis,
  }
})
