<template>

  <div class="bg-white dark:bg-slate-900 p-8 rounded-2xl shadow mb-10">

    <h2 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">
      📅 Citas médicas
    </h2>

    <div
      v-if="appointments.length === 0"
      class="text-gray-500 dark:text-gray-400"
    >
      No hay citas registradas.
    </div>

    <div
      v-for="cita in appointments"
      :key="cita.id"
      class="border dark:border-slate-700 p-5 rounded-xl mb-4"
    >

      <div class="flex justify-between items-center">

        <div>

          <span class="text-xs uppercase tracking-wide text-blue-600 dark:text-blue-400 font-bold">
            {{ etiquetaTipo(cita.tipo) }}
          </span>

          <h3 class="text-xl font-bold text-gray-800 dark:text-white">
            👨‍⚕️ {{ cita.doctor }}
          </h3>

          <p class="text-gray-500 dark:text-gray-400">
            🩺 {{ cita.especialidad }}
          </p>

          <p class="text-gray-500 dark:text-gray-400">
            📅 {{ cita.fecha }}
          </p>

          <p class="text-gray-500 dark:text-gray-400">
            ⏰ {{ cita.hora }}
          </p>

          <p class="text-gray-500 dark:text-gray-400">
            📍 {{ cita.lugar }}
          </p>

          <span
            class="inline-block mt-2 px-3 py-1 rounded-full text-sm font-bold text-white"
            :class="{
              'bg-yellow-500': cita.estado === 'pendiente',
              'bg-green-600': cita.estado === 'cumplida',
              'bg-red-600': cita.estado === 'cancelada',
            }"
          >
            {{ cita.estado }}
          </span>

        </div>

        <div class="flex flex-col gap-3">

          <button
            @click="$emit('cumplida', cita)"
            class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-xl"
          >
            Cumplida
          </button>

          <button
            @click="$emit('cancelada', cita)"
            class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl"
          >
            Cancelada
          </button>

        </div>

      </div>

    </div>

  </div>

</template>

<script setup lang="ts">

defineProps({

  appointments: {

    type: Array,
    required: true,

  },

})

defineEmits([
  'cumplida',
  'cancelada'
])

const etiquetas: Record<string, string> = {
  consulta: 'Consulta con especialista',
  examen: 'Examen médico',
  terapia: 'Terapia física',
  cirugia: 'Cirugía programada',
}

const etiquetaTipo = (tipo: string) => {

  return etiquetas[tipo] || tipo

}

</script>