<template>

  <div>

    <!-- HEADER -->
    <div class="mb-10">

      <h1 class="text-4xl font-bold text-gray-800 dark:text-white">
        Pacientes
      </h1>

      <p class="text-gray-500 dark:text-gray-400 mt-2">
        Administra a las personas que cuidas
      </p>

    </div>

    <!-- ESTADO DE CARGA -->
    <div
      v-if="cargandoInicial"
      class="bg-white dark:bg-slate-900 p-10 rounded-3xl shadow mb-10 flex items-center justify-center gap-3 text-gray-500 dark:text-gray-400"
    >

      <span
        class="w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"
      ></span>

      Cargando pacientes...

    </div>

    <template v-else>

    <PatientForm
      v-model:nombres="nombres"
      v-model:apellidos="apellidos"
      v-model:identificacion="identificacion"
      v-model:genero="genero"
      :editingId="editingId"
      @guardar="crearPaciente"
    />

    <div class="mb-6">

      <input
        v-model="busqueda"
        type="text"
        placeholder="🔎 Buscar paciente por nombre o identificación..."
        class="w-full md:w-96 p-3 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      />

    </div>

    <PatientList
      :patients="pacientesFiltrados"
      :activePatientId="activePatientId"
      :descargandoId="descargandoId"
      @eliminar="eliminarPaciente"
      @editar="editarPaciente"
      @seleccionar="seleccionarPaciente"
      @descargarPdf="descargarPdf"
    />

    </template>

  </div>

</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { toast } from 'vue-sonner'
import Swal from 'sweetalert2'

import api from '@/api/axios'
import { usePatient } from '@/composables/usePatient'

import PatientForm from '@/components/patients/PatientForm.vue'
import PatientList from '@/components/patients/PatientList.vue'

const {
  patients,
  activePatientId,
  cargarPacientes,
  seleccionarPaciente,
} = usePatient()

const busqueda = ref('')

const pacientesFiltrados = computed(() => {

  const termino = busqueda.value.trim().toLowerCase()

  if (!termino) return patients.value

  return patients.value.filter((p: any) => {

    return (
      p.nombres.toLowerCase().includes(termino) ||
      p.apellidos.toLowerCase().includes(termino) ||
      p.identificacion.toLowerCase().includes(termino)
    )

  })

})

const nombres = ref('')
const apellidos = ref('')
const identificacion = ref('')
const genero = ref('')

const editingId = ref<number | null>(null)

// CREAR / EDITAR
const crearPaciente = async (data: any) => {

  try {

    if (editingId.value) {

      await api.put(

        `patients/${editingId.value}/`,

        data

      )

      toast.success(
        'Paciente actualizado'
      )

      editingId.value = null

    } else {

      await api.post(

        'patients/',

        data

      )

      toast.success(
        'Paciente creado'
      )

    }

    nombres.value = ''
    apellidos.value = ''
    identificacion.value = ''
    genero.value = ''

    await cargarPacientes()

  } catch (error) {

    console.error(error)

    toast.error(
      'Error guardando el paciente'
    )

  }

}

// EDITAR
const editarPaciente = (patient: any) => {

  nombres.value = patient.nombres
  apellidos.value = patient.apellidos
  identificacion.value = patient.identificacion
  genero.value = patient.genero

  editingId.value = patient.id

}

// ELIMINAR
const eliminarPaciente = async (
  id: number
) => {

  const patient = patients.value.find(
    (p: any) => p.id === id
  )

  const nombreCompleto = patient
    ? `${patient.nombres} ${patient.apellidos}`
    : 'este paciente'

  const confirmacion = await Swal.fire({

    icon: 'warning',
    title: '¿Eliminar paciente?',

    html: `Se eliminará a <b>${nombreCompleto}</b> junto con todos sus medicamentos, recordatorios, citas e historial. Esta acción no se puede deshacer.`,

    showCancelButton: true,
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#dc2626',

  })

  if (!confirmacion.isConfirmed) return

  try {

    await api.delete(
      `patients/${id}/`
    )

    toast.success(
      'Paciente eliminado'
    )

    await cargarPacientes()

  } catch (error) {

    console.error(error)

    toast.error(
      'Error eliminando el paciente'
    )

  }

}

// DESCARGAR PDF
const descargandoId = ref<number | string | null>(null)

const descargarPdf = async (patient: any) => {

  descargandoId.value = patient.id

  try {

    const response = await api.get(

      `patients/${patient.id}/pdf/`,

      {
        responseType: 'blob',
      }

    )

    const url = window.URL.createObjectURL(
      new Blob([response.data], { type: 'application/pdf' })
    )

    const link = document.createElement('a')

    link.href = url

    link.download = `reporte_${patient.nombres}_${patient.apellidos}.pdf`.replace(/\s+/g, '_')

    link.click()

    window.URL.revokeObjectURL(url)

    toast.success(
      'PDF descargado'
    )

  } catch (error) {

    console.error(error)

    toast.error(
      'Error generando el PDF'
    )

  } finally {

    descargandoId.value = null

  }

}

// ======================================
// INIT
// ======================================

const cargandoInicial = ref(true)

onMounted(async () => {

  await cargarPacientes()

  cargandoInicial.value = false

})
</script>
