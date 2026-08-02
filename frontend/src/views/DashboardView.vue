<template>

  <div>

    <!-- HEADER -->
    <div class="mb-10">

      <h1 class="text-4xl font-bold text-gray-800 dark:text-white">
        Home
      </h1>

      <p class="text-gray-500 dark:text-gray-400 mt-2">
        Gestión inteligente de medicamentos
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

      Cargando resumen...

    </div>

    <!-- SIN PACIENTE -->
    <div
      v-if="!cargandoInicial && !activePatientId"
      class="bg-white dark:bg-slate-900 p-10 rounded-3xl shadow mb-10 text-center"
    >

      <p class="text-gray-500 dark:text-gray-400 mb-4">
        Todavía no tienes un paciente seleccionado.
      </p>

      <RouterLink
        to="/pacientes"
        class="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl"
      >
        Agregar paciente
      </RouterLink>

    </div>

    <!-- STATS -->
    <div
      v-else-if="!cargandoInicial"
      class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-10"
    >

      <!-- MEDICAMENTOS -->
      <RouterLink
        to="/medicamentos"
        class="bg-white dark:bg-slate-900 p-6 rounded-3xl shadow-sm hover:shadow-xl transition border border-gray-100 dark:border-slate-700 block"
      >

        <div class="flex justify-between items-center mb-4">

          <div
            class="bg-blue-100 dark:bg-blue-900/40 p-4 rounded-2xl"
          >
            <Pill class="w-7 h-7 text-blue-600 dark:text-blue-400" />
          </div>

          <span class="text-sm text-gray-400 dark:text-gray-500">
            Medicamentos
          </span>

        </div>

        <h3 class="text-4xl font-bold text-gray-800 dark:text-white">
          {{ medications.length }}
        </h3>

        <p class="text-gray-500 dark:text-gray-400 mt-2">
          Medicamentos registrados
        </p>

      </RouterLink>

      <!-- RECORDATORIOS -->
      <RouterLink
        to="/recordatorios"
        class="bg-white dark:bg-slate-900 p-6 rounded-3xl shadow-sm hover:shadow-xl transition border border-gray-100 dark:border-slate-700 block"
      >

        <div class="flex justify-between items-center mb-4">

          <div
            class="bg-green-100 dark:bg-green-900/40 p-4 rounded-2xl"
          >
            <Bell class="w-7 h-7 text-green-600 dark:text-green-400" />
          </div>

          <span class="text-sm text-gray-400 dark:text-gray-500">
            Activos
          </span>

        </div>

        <h3 class="text-4xl font-bold text-gray-800 dark:text-white">
          {{ reminders.filter(r => r.activo).length }}
        </h3>

        <p class="text-gray-500 dark:text-gray-400 mt-2">
          Recordatorios activos
        </p>

      </RouterLink>

      <!-- PRÓXIMA TOMA -->
      <RouterLink
        to="/recordatorios"
        class="bg-white dark:bg-slate-900 p-6 rounded-3xl shadow-sm hover:shadow-xl transition border border-gray-100 dark:border-slate-700 block"
      >

        <div class="flex justify-between items-center mb-4">

          <div
            class="bg-purple-100 dark:bg-purple-900/40 p-4 rounded-2xl"
          >
            <Clock3 class="w-7 h-7 text-purple-600 dark:text-purple-400" />
          </div>

          <span class="text-sm text-gray-400 dark:text-gray-500">
            Próxima
          </span>

        </div>

        <h3 class="text-2xl font-bold text-gray-800 dark:text-white">
          {{ nextReminder ? nextReminder.hora : '--:--' }}
        </h3>

        <p class="text-gray-500 dark:text-gray-400 mt-2">
          Próxima toma programada
        </p>

      </RouterLink>

      <!-- CITAS -->
      <RouterLink
        to="/citas"
        class="bg-white dark:bg-slate-900 p-6 rounded-3xl shadow-sm hover:shadow-xl transition border border-gray-100 dark:border-slate-700 block"
      >

        <div class="flex justify-between items-center mb-4">

          <div
            class="bg-orange-100 dark:bg-orange-900/40 p-4 rounded-2xl"
          >
            <CalendarDays class="w-7 h-7 text-orange-600 dark:text-orange-400" />
          </div>

          <span class="text-sm text-gray-400 dark:text-gray-500">
            Médicas
          </span>

        </div>

        <h3 class="text-4xl font-bold text-gray-800 dark:text-white">
          {{ appointments.length }}
        </h3>

        <p class="text-gray-500 dark:text-gray-400 mt-2">
          Citas registradas
        </p>

      </RouterLink>

    </div>

  </div>

</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import {
  Pill,
  Bell,
  Clock3,
  CalendarDays
} from 'lucide-vue-next'

import api from '@/api/axios'
import { usePatient } from '@/composables/usePatient'

const { activePatientId } = usePatient()

// ======================================
// DATOS PARA LAS TARJETAS DE RESUMEN
// ======================================

const medications = ref([])
const reminders = ref([])
const appointments = ref([])

const nextReminder = computed(() => {

  return reminders.value.find(
    reminder => reminder.activo
  )

})

const cargarMedicamentos = async () => {

  if (!activePatientId.value) return

  try {

    // page_size=100: acá solo necesitamos el conteo total,
    // no una página paginada.
    const response = await api.get(
      `medications/?page_size=100&patient=${activePatientId.value}`
    )

    medications.value = response.data.results

  } catch (error) {

    console.error(error)

  }

}

const cargarRecordatorios = async () => {

  if (!activePatientId.value) return

  try {

    const response = await api.get(
      `reminders/?page_size=100&patient=${activePatientId.value}`
    )

    reminders.value = response.data.results

  } catch (error) {

    console.error(error)

  }

}

const cargarCitas = async () => {

  if (!activePatientId.value) return

  try {

    const response = await api.get(
      `appointments/?page_size=100&patient=${activePatientId.value}`
    )

    appointments.value = response.data.results

  } catch (error) {

    console.error(error)

  }

}

const cargarTodo = async () => {

  await Promise.all([

    cargarMedicamentos(),
    cargarRecordatorios(),
    cargarCitas(),

  ])

}

// ======================================
// INIT
// ======================================

const cargandoInicial = ref(true)

onMounted(async () => {

  await cargarTodo()

  cargandoInicial.value = false

})

watch(activePatientId, () => {

  cargarTodo()

})
</script>
