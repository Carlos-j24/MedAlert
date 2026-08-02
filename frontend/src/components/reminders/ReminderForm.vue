<template>

  <div class="bg-white dark:bg-slate-900 p-8 rounded-2xl shadow mb-10">

    <h2 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">
      ⏰ Agregar recordatorio
    </h2>

    <form
      @submit.prevent="emit('guardar')"
      class="grid grid-cols-1 md:grid-cols-3 gap-5"
    >

      <select
        :value="selectedMedication"
        @input="emit('update:selectedMedication', $event.target.value)"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      >

        <option disabled value="">
          Selecciona medicamento
        </option>

        <option
          v-for="med in medications"
          :key="med.id"
          :value="med.id"
        >
          {{ med.nombre }}
        </option>

      </select>

      <input
        :value="hora"
        @input="emit('update:hora', $event.target.value)"
        type="time"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      />

      <button
        type="submit"
        class="bg-green-600 hover:bg-green-700 text-white p-4 rounded-xl"
      >
        Guardar
      </button>

    </form>

  </div>

</template>

<script setup lang="ts">

defineProps({

  medications: Array,
  selectedMedication: String,
  hora: String,

})

const emit = defineEmits([
  'guardar',
  'update:selectedMedication',
  'update:hora'
])

</script>