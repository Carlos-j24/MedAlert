<template>

  <div class="bg-white dark:bg-slate-900 p-8 rounded-2xl shadow">

    <h2 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">
      👥 Mis pacientes
    </h2>

    <div
      v-if="patients.length === 0"
      class="text-gray-500 dark:text-gray-400"
    >
      Todavía no has agregado ningún paciente.
    </div>

    <div
      v-for="patient in patients"
      :key="patient.id"
      class="border dark:border-slate-700 p-5 rounded-xl mb-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4"
      :class="String(patient.id) === String(activePatientId) ? 'border-blue-500 dark:border-blue-500' : ''"
    >

      <div>

        <h3 class="text-xl font-bold text-gray-800 dark:text-white flex items-center gap-2">

          {{ patient.nombres }} {{ patient.apellidos }}

          <span
            v-if="String(patient.id) === String(activePatientId)"
            class="text-xs bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 px-3 py-1 rounded-full font-normal"
          >
            Activo
          </span>

        </h3>

        <p class="text-gray-500 dark:text-gray-400">
          🪪 {{ patient.identificacion }}
        </p>

      </div>

      <div class="flex gap-3 flex-wrap">

        <button
          v-if="String(patient.id) !== String(activePatientId)"
          @click="$emit('seleccionar', patient.id)"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl"
        >
          Usar este paciente
        </button>

        <button
          @click="$emit('descargarPdf', patient)"
          :disabled="String(descargandoId) === String(patient.id)"
          class="bg-blue-100 dark:bg-blue-900/40 hover:bg-blue-200 dark:hover:bg-blue-900/60 disabled:opacity-60 disabled:cursor-not-allowed text-blue-700 dark:text-blue-400 px-4 py-2 rounded-xl flex items-center gap-2"
        >

          <span
            v-if="String(descargandoId) === String(patient.id)"
            class="w-4 h-4 border-2 border-blue-700 dark:border-blue-400 border-t-transparent rounded-full animate-spin"
          ></span>

          {{ String(descargandoId) === String(patient.id) ? 'Generando...' : '📄 Descargar PDF' }}

        </button>

        <button
          @click="$emit('editar', patient)"
          class="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded-xl"
        >
          Editar
        </button>

        <button
          @click="$emit('eliminar', patient.id)"
          class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-xl"
        >
          Eliminar
        </button>

      </div>

    </div>

  </div>

</template>

<script setup lang="ts">

defineProps({

  patients: {
    type: Array,
    required: true,
  },

  activePatientId: {
    type: [String, Number, null],
    default: null,
  },

  descargandoId: {
    type: [String, Number, null],
    default: null,
  },

})

defineEmits([
  'editar',
  'eliminar',
  'seleccionar',
  'descargarPdf',
])

</script>
