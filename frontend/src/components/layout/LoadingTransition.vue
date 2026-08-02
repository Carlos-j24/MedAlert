<template>

  <div
    class="fixed inset-0 z-50 flex flex-col items-center justify-center gap-6 bg-white dark:bg-slate-950"
  >

    <div
      class="relative w-24 h-24 rounded-full bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center"
    >

      <span
        class="absolute inset-[-6px] rounded-full border-2 border-blue-500 border-t-transparent animate-spin"
      ></span>

      <component
        :is="iconoActual"
        class="w-9 h-9 text-blue-600 dark:text-blue-400 transition-all duration-300"
        :class="desvanecido ? 'opacity-0 scale-75' : 'opacity-100 scale-100'"
      />

    </div>

    <p class="text-gray-500 dark:text-gray-400 text-sm">
      Cargando tu dashboard...
    </p>

  </div>

</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Pill, Bell, CalendarDays, HeartPulse } from 'lucide-vue-next'

const iconos = [Pill, Bell, CalendarDays, HeartPulse]

const indice = ref(0)
const desvanecido = ref(false)

const iconoActual = ref(iconos[0])

let intervalo: ReturnType<typeof setInterval> | null = null

onMounted(() => {

  intervalo = setInterval(() => {

    desvanecido.value = true

    setTimeout(() => {

      indice.value = (indice.value + 1) % iconos.length
      iconoActual.value = iconos[indice.value]

      desvanecido.value = false

    }, 300)

  }, 700)

})

onUnmounted(() => {

  if (intervalo) {

    clearInterval(intervalo)

  }

})
</script>
