<template>

  <div class="bg-white dark:bg-slate-900 p-8 rounded-2xl shadow mb-10">

    <h2 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">
      🏥 Agendar cita médica
    </h2>

    <form
      @submit.prevent="emit('guardar')"
      class="grid grid-cols-1 md:grid-cols-2 gap-5"
    >

      <select
        :value="tipo"
        @change="emit('update:tipo', ($event.target as HTMLSelectElement).value)"
        class="p-4 border rounded-xl md:col-span-2 bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      >
        <option value="consulta">Consulta con especialista</option>
        <option value="examen">Examen médico</option>
        <option value="terapia">Terapia física</option>
        <option value="cirugia">Cirugía programada</option>
      </select>

      <input
        :value="fecha"
        @input="emit('update:fecha', $event.target.value)"
        type="date"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      />

      <input
        :value="hora"
        @input="emit('update:hora', $event.target.value)"
        type="time"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      />

      <input
        :value="doctor"
        @input="emit('update:doctor', $event.target.value)"
        type="text"
        placeholder="Doctor"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      />

      <input
        :value="especialidad"
        @input="emit('update:especialidad', $event.target.value)"
        type="text"
        placeholder="Especialidad"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      />

      <input
        :value="lugar"
        @input="emit('update:lugar', $event.target.value)"
        type="text"
        placeholder="Lugar"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      />

      <input
        :value="direccion"
        @input="emit('update:direccion', $event.target.value)"
        type="text"
        placeholder="Dirección"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      />

      <input
        :value="barrio"
        @input="emit('update:barrio', $event.target.value)"
        type="text"
        placeholder="Barrio"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      />

      <input
        :value="piso"
        @input="emit('update:piso', $event.target.value)"
        type="text"
        placeholder="Piso"
        class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      />

      <input
        :value="consultorio"
        @input="emit('update:consultorio', $event.target.value)"
        type="text"
        placeholder="Consultorio"
        class="p-4 border rounded-xl md:col-span-2 bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      />

      <div class="md:col-span-2 border-t dark:border-slate-700 pt-5">

        <label class="flex items-center gap-2 text-gray-800 dark:text-white mb-4">

          <input
            :checked="recordatorio"
            @change="emit('update:recordatorio', ($event.target as HTMLInputElement).checked)"
            type="checkbox"
            class="w-5 h-5"
          />

          Generar recordatorios automáticos para esta cita

        </label>

        <div
          v-if="recordatorio"
          class="grid grid-cols-2 gap-5"
        >

          <div>

            <label class="text-sm text-gray-500 dark:text-gray-400 block mb-1">
              Avisar con anticipación de
            </label>

            <input
              :value="recordatorioAntesCantidad"
              @input="emit('update:recordatorioAntesCantidad', Number(($event.target as HTMLInputElement).value))"
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
              :value="recordatorioAntesUnidad"
              @change="emit('update:recordatorioAntesUnidad', ($event.target as HTMLSelectElement).value)"
              class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white w-full"
            >
              <option value="horas">Horas antes</option>
              <option value="dias">Días antes</option>
            </select>

          </div>

        </div>

        <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
          Se creará un recordatorio con esa anticipación y otro el mismo día de la cita.
        </p>

      </div>

      <button
        type="submit"
        class="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-xl md:col-span-2"
      >
        Guardar cita
      </button>

    </form>

  </div>

</template>

<script setup lang="ts">

defineProps({

  fecha: String,
  hora: String,
  tipo: String,
  doctor: String,
  especialidad: String,
  lugar: String,
  direccion: String,
  barrio: String,
  piso: String,
  consultorio: String,
  recordatorio: {
    type: Boolean,
    default: true,
  },
  recordatorioAntesCantidad: Number,
  recordatorioAntesUnidad: String,

})

const emit = defineEmits([

  'guardar',

  'update:fecha',
  'update:hora',
  'update:tipo',
  'update:doctor',
  'update:especialidad',
  'update:lugar',
  'update:direccion',
  'update:barrio',
  'update:piso',
  'update:consultorio',
  'update:recordatorio',
  'update:recordatorioAntesCantidad',
  'update:recordatorioAntesUnidad',

])

</script>