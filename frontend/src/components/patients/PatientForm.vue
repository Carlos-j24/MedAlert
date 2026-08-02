<template>

  <div class="bg-white dark:bg-slate-900 p-8 rounded-2xl shadow mb-10">

    <h2 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">

      {{ editingId ? '✏️ Editar paciente' : '➕ Agregar paciente' }}

    </h2>

    <form
      @submit.prevent="guardar"
      class="grid md:grid-cols-2 gap-5"
    >

      <input
        v-model="localNombres"
        type="text"
        placeholder="Nombres"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white dark:placeholder-gray-400"
      />

      <input
        v-model="localApellidos"
        type="text"
        placeholder="Apellidos"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white dark:placeholder-gray-400"
      />

      <input
        v-model="localIdentificacion"
        type="text"
        placeholder="Identificación (cédula)"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white dark:placeholder-gray-400"
      />

      <select
        v-model="localGenero"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      >

        <option disabled value="">
          Selecciona género
        </option>

        <option value="femenino">Femenino</option>
        <option value="masculino">Masculino</option>
        <option value="prefiero_no_decir">Prefiero no decir</option>

      </select>

      <button
        type="submit"
        class="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-xl md:col-span-2"
      >

        {{ editingId ? 'Actualizar paciente' : 'Guardar paciente' }}

      </button>

    </form>

  </div>

</template>

<script setup lang="ts">

import {
  ref,
  watch
} from 'vue'

const props = defineProps({

  nombres: String,
  apellidos: String,
  identificacion: String,
  genero: String,
  editingId: Number,

})

const emit = defineEmits([
  'guardar'
])

const localNombres = ref('')
const localApellidos = ref('')
const localIdentificacion = ref('')
const localGenero = ref('')

watch(
  () => props.nombres,
  (newValue) => { localNombres.value = newValue || '' },
  { immediate: true }
)

watch(
  () => props.apellidos,
  (newValue) => { localApellidos.value = newValue || '' },
  { immediate: true }
)

watch(
  () => props.identificacion,
  (newValue) => { localIdentificacion.value = newValue || '' },
  { immediate: true }
)

watch(
  () => props.genero,
  (newValue) => { localGenero.value = newValue || '' },
  { immediate: true }
)

const guardar = () => {

  emit(
    'guardar',
    {
      nombres: localNombres.value,
      apellidos: localApellidos.value,
      identificacion: localIdentificacion.value,
      genero: localGenero.value,
    }
  )

}

</script>
