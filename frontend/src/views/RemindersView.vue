<template>

  <div>

    <!-- HEADER -->
    <div class="mb-10">

      <h1 class="text-4xl font-bold text-gray-800 dark:text-white">
        Recordatorios
      </h1>

      <p class="text-gray-500 dark:text-gray-400 mt-2">
        Programa y controla tus recordatorios de medicamentos
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

      Cargando recordatorios...

    </div>

    <!-- SIN PACIENTE -->
    <div
      v-else-if="!activePatientId"
      class="bg-white dark:bg-slate-900 p-10 rounded-3xl shadow mb-10 text-center"
    >

      <p class="text-gray-500 dark:text-gray-400 mb-4">
        Selecciona o agrega un paciente para ver sus recordatorios.
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
    <!-- RECORDATORIOS -->
    <!-- ================================= -->

    <ReminderForm
      :medications="medications"
      v-model:selectedMedication="selectedMedication"
      v-model:hora="hora"
      @guardar="crearRecordatorio"
    />

    <div class="mb-6">

      <input
        v-model="busqueda"
        @input="onBuscar"
        type="text"
        placeholder="🔎 Buscar por medicamento o doctor..."
        class="w-full md:w-96 p-3 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      />

    </div>

    <ReminderList
      :reminders="reminders"
      @toggleActivo="toggleReminder"
      @toggleTomado="toggleTomado"
    />

    <div
      v-if="remindersNext || remindersPrevious"
      class="flex justify-center gap-4 mb-10"
    >

      <button
        :disabled="!remindersPrevious"
        @click="cargarRecordatorios(remindersPrevious)"
        class="px-5 py-2 rounded-xl bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-300"
      >
        ← Anterior
      </button>

      <span class="self-center text-gray-500 dark:text-gray-400 text-sm">
        {{ remindersCount }} recordatorios en total
      </span>

      <button
        :disabled="!remindersNext"
        @click="cargarRecordatorios(remindersNext)"
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

import api from '@/api/axios'
import { usePatient } from '@/composables/usePatient'

import ReminderForm from '@/components/reminders/ReminderForm.vue'
import ReminderList from '@/components/reminders/ReminderList.vue'

const { activePatientId } = usePatient()

// ======================================
// MEDICAMENTOS (para el selector del formulario)
// ======================================

const medications = ref([])

const cargarMedicamentos = async () => {

  if (!activePatientId.value) return

  try {

    // page_size=100: acá necesitamos todos los medicamentos
    // disponibles para el <select>, no una página paginada.
    const response = await api.get(
      `medications/?page_size=100&patient=${activePatientId.value}`
    )

    medications.value = response.data.results

  } catch (error) {

    console.error(error)

    toast.error(
      'Error cargando medicamentos'
    )

  }

}

// ======================================
// RECORDATORIOS
// ======================================

const reminders = ref([])
const remindersCount = ref(0)
const remindersNext = ref<string | null>(null)
const remindersPrevious = ref<string | null>(null)

const selectedMedication = ref('')
const hora = ref('')

const busqueda = ref('')

let temporizadorBusqueda: ReturnType<typeof setTimeout> | null = null

const onBuscar = () => {

  if (temporizadorBusqueda) clearTimeout(temporizadorBusqueda)

  temporizadorBusqueda = setTimeout(() => {

    cargarRecordatorios()

  }, 400)

}

const cargarRecordatorios = async (
  url: string | null = null
) => {

  if (!activePatientId.value) return

  try {

    const parametroBusqueda = busqueda.value
      ? `&search=${encodeURIComponent(busqueda.value)}`
      : ''

    const response = await api.get(
      url || `reminders/?patient=${activePatientId.value}${parametroBusqueda}`
    )

    reminders.value = response.data.results
    remindersCount.value = response.data.count
    remindersNext.value = response.data.next
    remindersPrevious.value = response.data.previous

  } catch (error) {

    console.error(error)

  }

}

const crearRecordatorio = async () => {

  if (!activePatientId.value) return

  try {

    await api.post(

      'reminders/',

      {
        patient: activePatientId.value,
        medication: selectedMedication.value,
        hora: hora.value,
        frecuencia: 'Diaria',
      }

    )

    selectedMedication.value = ''
    hora.value = ''

    cargarRecordatorios()

    toast.success(
      'Recordatorio creado'
    )

  } catch (error) {

    console.error(error)

    toast.error(
      'Error creando recordatorio'
    )

  }

}

// TOGGLE ACTIVO
const toggleReminder = async (
  reminder: any
) => {

  try {

    await api.put(

      `reminders/${reminder.id}/`,

      {
        ...reminder,
        activo: !reminder.activo,
      }

    )

    cargarRecordatorios()

    toast.success(
      reminder.activo
        ? 'Recordatorio desactivado'
        : 'Recordatorio activado'
    )

  } catch (error) {

    console.error(error)

    toast.error(
      'Error actualizando el recordatorio'
    )

  }

}

// TOGGLE TOMADO
const toggleTomado = async (
  reminder: any
) => {

  try {

    await api.put(

      `reminders/${reminder.id}/`,

      {
        ...reminder,
        tomado: !reminder.tomado,
      }

    )

    if (!reminder.tomado && reminder.medication) {

      await api.post(
        'history/',
        {
          patient: activePatientId.value,
          medication: reminder.medication,
          reminder: reminder.id
        }
      )

    }

    cargarRecordatorios()

    toast.success(
      reminder.tomado
        ? 'Marcado como pendiente'
        : 'Marcado como tomado'
    )

  } catch (error) {

    console.error(error)

    toast.error(
      'Error actualizando el recordatorio'
    )

  }

}

// ======================================
// INIT
// ======================================

const cargandoInicial = ref(true)

const cargarTodo = async () => {

  await Promise.all([

    cargarMedicamentos(),
    cargarRecordatorios(),

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
