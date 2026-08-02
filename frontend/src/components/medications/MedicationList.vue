<template>

  <div class="bg-white dark:bg-slate-900 p-8 rounded-2xl shadow">

    <h2 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">
      📋 Lista medicamentos
    </h2>

    <div
      v-if="medications.length === 0"
      class="text-gray-500 dark:text-gray-400"
    >
      No hay medicamentos.
    </div>

    <div
      v-for="med in medications"
      :key="med.id"
      class="border dark:border-slate-700 p-5 rounded-xl mb-4 flex justify-between items-center"
    >

      <div>

        <h3 class="text-xl font-bold text-gray-800 dark:text-white">
          {{ med.nombre }}
        </h3>

        <p class="text-gray-500 dark:text-gray-400">
          💊 {{ med.dosis }}
        </p>

      </div>

      <!-- BOTONES -->

      <div class="flex gap-3">

        <!-- EDITAR -->

        <button
          @click="$emit('editar', med)"
          class="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded-xl"
        >
          Editar
        </button>

        <!-- ELIMINAR -->

        <button
          @click="$emit('eliminar', med.id)"
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

  medications: {

    type: Array,
    required: true,

  },

})

defineEmits([
  'editar',
  'eliminar'
])

</script>