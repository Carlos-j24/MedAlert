<template>

  <div class="bg-white dark:bg-slate-900 p-8 rounded-2xl shadow mb-10">

    <h2 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">
      🔔 Recordatorios
    </h2>

    <div
      v-if="reminders.length === 0"
      class="text-gray-500 dark:text-gray-400"
    >
      No hay recordatorios.
    </div>

    <div
      v-for="reminder in reminders"
      :key="reminder.id"
      class="border dark:border-slate-700 p-5 rounded-xl mb-4 flex justify-between items-center"
    >

      <div>

        <h3 class="text-xl font-bold text-gray-800 dark:text-white">
          {{ reminder.medication_nombre ? reminder.medication_nombre : `🏥 ${reminder.appointment_info}` }}
        </h3>

        <p
          v-if="reminder.appointment_info"
          class="text-gray-500 dark:text-gray-400"
        >
          {{ reminder.frecuencia }} — {{ formatearFecha(reminder.fecha) }} ⏰ {{ reminder.hora }}
        </p>

        <p
          v-else
          class="text-gray-500 dark:text-gray-400"
        >
          ⏰ {{ reminder.hora }}
        </p>

        <p
          v-if="reminder.fecha_fin"
          class="text-xs mt-1"
          :class="estaVencido(reminder.fecha_fin) ? 'text-red-500' : 'text-gray-400 dark:text-gray-500'"
        >
          {{ estaVencido(reminder.fecha_fin) ? '⚠️ Tratamiento finalizado' : `Hasta el ${formatearFecha(reminder.fecha_fin)}` }}
        </p>

      </div>

      <div class="flex gap-3">

        <button
          @click="$emit('toggleActivo', reminder)"
          :class="reminder.activo ? 'bg-green-500' : 'bg-gray-400'"
          class="text-white px-4 py-2 rounded-xl"
        >
          {{ reminder.activo ? 'Activo' : 'Inactivo' }}
        </button>

        <button
          @click="$emit('toggleTomado', reminder)"
          :class="reminder.tomado ? 'bg-blue-500' : 'bg-yellow-500'"
          class="text-white px-4 py-2 rounded-xl"
        >
          {{ reminder.tomado ? 'Tomado' : 'Pendiente' }}
        </button>

      </div>

    </div>

  </div>

</template>

<script setup lang="ts">

defineProps({

  reminders: {

    type: Array,
    required: true,

  },

})

defineEmits([
  'toggleActivo',
  'toggleTomado'
])

const estaVencido = (fechaFin: string) => {

  return new Date(fechaFin) < new Date(new Date().toDateString())

}

const formatearFecha = (fechaFin: string) => {

  return new Date(fechaFin + 'T00:00:00').toLocaleDateString()

}

</script>