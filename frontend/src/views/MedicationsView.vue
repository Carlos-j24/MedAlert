<template>

  <div>

    <!-- HEADER -->
    <div class="mb-10">

      <h1 class="text-4xl font-bold text-gray-800 dark:text-white">
        Medicamentos
      </h1>

      <p class="text-gray-500 dark:text-gray-400 mt-2">
        Registra y administra tus medicamentos
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

      Cargando medicamentos...

    </div>

    <!-- SIN PACIENTE -->
    <div
      v-else-if="!activePatientId"
      class="bg-white dark:bg-slate-900 p-10 rounded-3xl shadow mb-10 text-center"
    >

      <p class="text-gray-500 dark:text-gray-400 mb-4">
        Selecciona o agrega un paciente para ver sus medicamentos.
      </p>

      <RouterLink
        to="/pacientes"
        class="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl"
      >
        Ir a Pacientes
      </RouterLink>

    </div>

    <template v-else>

    <!-- ================================= -->
    <!-- MEDICAMENTOS -->
    <!-- ================================= -->

    <MedicationForm
      v-model:name="name"
      v-model:dose="dose"
      :editingId="editingId"
      @guardar="crearMedicamento"
    />

    <div class="mb-6">

      <input
        v-model="busqueda"
        @input="onBuscar"
        type="text"
        placeholder="🔎 Buscar medicamento por nombre..."
        class="w-full md:w-96 p-3 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      />

    </div>

    <MedicationList
      :medications="medications"
      @eliminar="eliminarMedicamento"
      @editar="editarMedicamento"
    />

    <div
      v-if="medicationsNext || medicationsPrevious"
      class="flex justify-center gap-4 -mt-6 mb-10"
    >

      <button
        :disabled="!medicationsPrevious"
        @click="cargarMedicamentos(medicationsPrevious)"
        class="px-5 py-2 rounded-xl bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-300"
      >
        ← Anterior
      </button>

      <span class="self-center text-gray-500 dark:text-gray-400 text-sm">
        {{ medicationsCount }} medicamentos en total
      </span>

      <button
        :disabled="!medicationsNext"
        @click="cargarMedicamentos(medicationsNext)"
        class="px-5 py-2 rounded-xl bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-300"
      >
        Siguiente →
      </button>

    </div>

    <!-- ================================= -->
    <!-- HISTORIAL -->
    <!-- ================================= -->

    <div class="bg-white dark:bg-slate-900 p-8 rounded-3xl shadow mb-4">

      <h2 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">
        📋 Historial de Medicamentos
      </h2>

      <div
        v-if="history.length === 0"
        class="text-gray-500 dark:text-gray-400"
      >
        No hay registros todavía.
      </div>

      <div
        v-for="item in history"
        :key="item.id"
        class="border border-gray-100 dark:border-slate-700 p-5 rounded-2xl mb-4"
      >

        <h3 class="font-bold text-lg text-gray-800 dark:text-white">

          💊 {{ item.medication_nombre }}

        </h3>

        <p class="text-gray-500 dark:text-gray-400">

          Tomado el:

          {{ new Date(item.tomado_en).toLocaleString() }}

        </p>

      </div>

    </div>

    <div
      v-if="historyNext || historyPrevious"
      class="flex justify-center gap-4 mb-10"
    >

      <button
        :disabled="!historyPrevious"
        @click="cargarHistorial(historyPrevious)"
        class="px-5 py-2 rounded-xl bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-300"
      >
        ← Anterior
      </button>

      <span class="self-center text-gray-500 dark:text-gray-400 text-sm">
        {{ historyCount }} registros en total
      </span>

      <button
        :disabled="!historyNext"
        @click="cargarHistorial(historyNext)"
        class="px-5 py-2 rounded-xl bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-300"
      >
        Siguiente →
      </button>

    </div>

    </template>

  </div>

</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { toast } from 'vue-sonner'
import Swal from 'sweetalert2'

import api from '@/api/axios'
import { usePatient } from '@/composables/usePatient'

import MedicationForm from '@/components/medications/MedicationForm.vue'
import MedicationList from '@/components/medications/MedicationList.vue'

const { activePatientId } = usePatient()

// ======================================
// MEDICAMENTOS
// ======================================

const medications = ref([])
const medicationsCount = ref(0)
const medicationsNext = ref<string | null>(null)
const medicationsPrevious = ref<string | null>(null)

const name = ref('')
const dose = ref('')

const editingId = ref<number | null>(null)

const busqueda = ref('')

let temporizadorBusqueda: ReturnType<typeof setTimeout> | null = null

const onBuscar = () => {

  if (temporizadorBusqueda) clearTimeout(temporizadorBusqueda)

  temporizadorBusqueda = setTimeout(() => {

    cargarMedicamentos()

  }, 400)

}

// ======================================
// HISTORIAL
// ======================================

const history = ref([])
const historyCount = ref(0)
const historyNext = ref<string | null>(null)
const historyPrevious = ref<string | null>(null)

// ======================================
// MEDICAMENTOS
// ======================================

const cargarMedicamentos = async (
  url: string | null = null
) => {

  if (!activePatientId.value) return

  try {

    const parametroBusqueda = busqueda.value
      ? `&search=${encodeURIComponent(busqueda.value)}`
      : ''

    const response = await api.get(
      url || `medications/?patient=${activePatientId.value}${parametroBusqueda}`
    )

    medications.value = response.data.results
    medicationsCount.value = response.data.count
    medicationsNext.value = response.data.next
    medicationsPrevious.value = response.data.previous

  } catch (error) {

    console.error(error)

    toast.error(
      'Error cargando medicamentos'
    )

  }

}

// CREAR / EDITAR
const crearMedicamento = async (data: any) => {

  if (!activePatientId.value) return

  try {

    // EDITAR (PATCH: solo tocamos nombre/dosis, sin resetear
    // la frecuencia/duración ya generada)
    if (editingId.value) {

      await api.patch(

        `medications/${editingId.value}/`,

        {
          nombre: data.nombre,
          dosis: data.dosis,
        }

      )

      toast.success(
        'Medicamento actualizado'
      )

      editingId.value = null

    }

    // CREAR
    else {

      const response = await api.post(

        'medications/',

        {
          patient: activePatientId.value,
          nombre: data.nombre,
          dosis: data.dosis,
          descripcion: '',
          frecuencia_horas: data.frecuencia_horas,
          hora_inicio: data.hora_inicio,
          duracion_cantidad: data.duracion_cantidad,
          duracion_unidad: data.duracion_unidad,
        }

      )

      toast.success(
        `Medicamento creado con ${24 / data.frecuencia_horas} recordatorios diarios`
      )

    }

    cargarMedicamentos()

  } catch (error) {

    console.error(error)

    toast.error(
      'Error guardando medicamento'
    )

  }

}

// EDITAR
const editarMedicamento = (med: any) => {

  name.value = med.nombre
  dose.value = med.dosis

  editingId.value = med.id

}

// ELIMINAR
const eliminarMedicamento = async (
  id: number
) => {

  const medicamento = medications.value.find(
    (m: any) => m.id === id
  )

  const nombre = medicamento ? medicamento.nombre : 'este medicamento'

  const confirmacion = await Swal.fire({

    icon: 'warning',
    title: '¿Eliminar medicamento?',

    html: `Se eliminará <b>${nombre}</b> junto con sus recordatorios y el historial de tomas asociado. Esta acción no se puede deshacer.`,

    showCancelButton: true,
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: '#dc2626',

  })

  if (!confirmacion.isConfirmed) return

  try {

    await api.delete(
      `medications/${id}/`
    )

    cargarMedicamentos()

    toast.success(
      'Medicamento eliminado'
    )

  } catch (error) {

    console.error(error)

    toast.error(
      'Error eliminando medicamento'
    )

  }

}

// ======================================
// HISTORIAL
// ======================================

const cargarHistorial = async (
  url: string | null = null
) => {

  if (!activePatientId.value) return

  try {

    const response = await api.get(
      url || `history/?patient=${activePatientId.value}`
    )

    history.value = response.data.results
    historyCount.value = response.data.count
    historyNext.value = response.data.next
    historyPrevious.value = response.data.previous

  }

  catch (error) {

    console.error(error)

  }

}

// ======================================
// INIT
// ======================================

const cargandoInicial = ref(true)

const cargarTodo = async () => {

  await Promise.all([

    cargarMedicamentos(),
    cargarHistorial(),

  ])

}

onMounted(async () => {

  await cargarTodo()

  cargandoInicial.value = false

})

watch(activePatientId, () => {

  cargarTodo()

})
</script>
