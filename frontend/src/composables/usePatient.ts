import { ref, computed } from 'vue'
import api from '@/api/axios'

const patients = ref<any[]>([])

const activePatientId = ref<string | null>(
  localStorage.getItem('activePatientId')
)

const cargandoPacientes = ref(false)

export function usePatient() {

  const seleccionarPaciente = (id: number | string) => {

    activePatientId.value = String(id)

    localStorage.setItem(
      'activePatientId',
      String(id)
    )

  }

  const cargarPacientes = async () => {

    cargandoPacientes.value = true

    try {

      const response = await api.get(
        'patients/?page_size=100'
      )

      patients.value = response.data.results

      const sigueValido = patients.value.some(
        p => String(p.id) === activePatientId.value
      )

      if (!sigueValido && patients.value.length > 0) {

        seleccionarPaciente(patients.value[0].id)

      }

      if (patients.value.length === 0) {

        activePatientId.value = null

        localStorage.removeItem('activePatientId')

      }

    } catch (error) {

      console.error(error)

    } finally {

      cargandoPacientes.value = false

    }

  }

  const pacienteActivo = computed(() => {

    return patients.value.find(
      p => String(p.id) === activePatientId.value
    ) || null

  })

  return {

    patients,
    activePatientId,
    pacienteActivo,
    cargandoPacientes,

    cargarPacientes,
    seleccionarPaciente,

  }

}
