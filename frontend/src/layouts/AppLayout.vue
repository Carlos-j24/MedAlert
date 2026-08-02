<template>

  <div
    class="
      min-h-screen
      bg-gray-100
      dark:bg-slate-950
      flex
      transition-all
      duration-300
    "
  >

    <!-- SIDEBAR -->
    <AppSidebar />

    <div class="flex-1 flex flex-col min-w-0">

      <!-- BARRA SUPERIOR (solo en móvil) -->
      <header
        class="md:hidden flex items-center justify-between bg-gradient-to-r from-blue-700 to-blue-900 text-white p-4 sticky top-0 z-30 shadow-lg"
      >

        <button
          @click="alternar"
          aria-label="Abrir menú"
        >
          <Menu class="w-6 h-6" />
        </button>

        <span class="font-bold text-lg">
          MedAlert
        </span>

        <div class="w-6"></div>

      </header>

      <!-- CONTENIDO DE LA SECCIÓN ACTIVA -->
      <main class="flex-1 p-4 md:p-10">

        <RouterView />

      </main>

    </div>

  </div>

</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { Menu } from 'lucide-vue-next'

import AppSidebar from '@/components/layout/AppSidebar.vue'
import { useMobileMenu } from '@/composables/useMobileMenu'

const { alternar } = useMobileMenu()
</script>
