<template>

  <div class="bg-white dark:bg-slate-900 p-8 rounded-2xl shadow mb-10">

    <h2 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">

      {{ editingId ? '✏️ Editar medicamento' : '💊 Agregar medicamento' }}

    </h2>

    <form
      @submit.prevent="guardar"
      class="grid md:grid-cols-2 gap-5"
    >

      <!-- NOMBRE -->

      <input
        v-model="localName"
        type="text"
        placeholder="Nombre medicamento"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white dark:placeholder-gray-400"
      />

      <!-- DOSIS -->

      <input
        v-model="localDose"
        type="text"
        placeholder="Dosis (ej. 500mg)"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white dark:placeholder-gray-400"
      />

      <template v-if="!editingId">

        <!-- FRECUENCIA -->

        <div>

          <label class="text-sm text-gray-500 dark:text-gray-400 block mb-1">
            ¿Cada cuánto se toma?
          </label>

          <select
            v-model.number="localFrecuenciaHoras"
            class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white w-full"
          >
            <option :value="8">Cada 8 horas</option>
            <option :value="12">Cada 12 horas</option>
            <option :value="24">Cada 24 horas</option>
          </select>

        </div>

        <!-- HORA DE LA PRIMERA TOMA -->

        <div>

          <label class="text-sm text-gray-500 dark:text-gray-400 block mb-1">
            Hora de la primera toma
          </label>

          <input
            v-model="localHoraInicio"
            type="time"
            class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white w-full"
          />

        </div>

        <!-- DURACIÓN -->

        <div class="md:col-span-2 grid grid-cols-2 gap-5">

          <div>

            <label class="text-sm text-gray-500 dark:text-gray-400 block mb-1">
              Duración del tratamiento
            </label>

            <input
              v-model.number="localDuracionCantidad"
              type="number"
              min="1"
              class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white w-full"
            />

          </div>

          <div>

            <label class="text-sm text-gray-500 dark:text-gray-400 block mb-1">
              &nbsp;
            </label>

            <select
              v-model="localDuracionUnidad"
              class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white w-full"
            >
              <option value="dias">Días</option>
              <option value="meses">Meses</option>
            </select>

          </div>

        </div>

        <p class="md:col-span-2 text-sm text-gray-500 dark:text-gray-400 -mt-2">
          Con estos datos generamos automáticamente los recordatorios
          de cada toma.
        </p>

      </template>

      <!-- BOTON -->

      <button
        type="submit"
        class="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-xl md:col-span-2"
      >

        {{ editingId ? 'Actualizar medicamento' : 'Guardar medicamento y generar recordatorios' }}

      </button>

    </form>

  </div>

</template>

<script setup lang="ts">

import {
  ref,
  watch
} from 'vue'

// PROPS

const props = defineProps({

  name: String,
  dose: String,
  editingId: Number,

})

// EMITS

const emit = defineEmits([
  'guardar'
])

// VARIABLES LOCALES

const localName = ref('')
const localDose = ref('')

const localFrecuenciaHoras = ref(8)
const localHoraInicio = ref('08:00')
const localDuracionCantidad = ref(7)
const localDuracionUnidad = ref('dias')

// WATCH

watch(

  () => props.name,

  (newValue) => {

    localName.value = newValue || ''

  },

  { immediate: true }

)

watch(

  () => props.dose,

  (newValue) => {

    localDose.value = newValue || ''

  },

  { immediate: true }

)

// GUARDAR

const guardar = () => {

  emit(
    'guardar',
    {
      nombre: localName.value,
      dosis: localDose.value,
      frecuencia_horas: localFrecuenciaHoras.value,
      hora_inicio: localHoraInicio.value,
      duracion_cantidad: localDuracionCantidad.value,
      duracion_unidad: localDuracionUnidad.value,
    }
  )

  // Reseteamos los campos de frecuencia/duración para el
  // próximo medicamento que se agregue.
  localFrecuenciaHoras.value = 8
  localHoraInicio.value = '08:00'
  localDuracionCantidad.value = 7
  localDuracionUnidad.value = 'dias'

}

</script>
