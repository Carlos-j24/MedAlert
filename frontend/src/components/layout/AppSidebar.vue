<template>

  <!-- FONDO OSCURO (solo en móvil, cuando el menú está abierto) -->
  <div
    v-if="abierto"
    @click="cerrar"
    class="md:hidden fixed inset-0 bg-black/50 z-40"
  ></div>

  <aside
    class="flex flex-col w-72 bg-gradient-to-b from-blue-700 to-blue-900 text-white min-h-screen p-6 shadow-2xl fixed md:static inset-y-0 left-0 z-50 overflow-y-auto transform transition-transform duration-300 md:translate-x-0"
    :class="abierto ? 'translate-x-0' : '-translate-x-full'"
  >

    <!-- CERRAR (solo en móvil) -->
    <button
      @click="cerrar"
      class="md:hidden self-end mb-4 bg-white/10 hover:bg-white/20 rounded-xl p-2"
      aria-label="Cerrar menú"
    >
      <X class="w-5 h-5" />
    </button>

    <!-- LOGO -->
    <div class="flex items-center gap-3 mb-12">

      <div
        class="bg-white/90 p-2 rounded-2xl w-14 h-14 flex items-center justify-center"
      >
        <AppLogo class="w-9 h-9" />
      </div>

      <div>

        <h1 class="text-3xl font-bold">
          MedAlert
        </h1>

        <p class="text-blue-200 text-sm">
          Gestión médica inteligente
        </p>

      </div>

    </div>

    <!-- PACIENTE ACTIVO -->
    <div class="mb-8">

      <label class="text-xs uppercase tracking-wide text-blue-200 mb-2 block">
        Paciente activo
      </label>

      <select
        v-if="patients.length > 0"
        :value="activePatientId"
        @change="seleccionarPaciente(($event.target as HTMLSelectElement).value)"
        class="w-full p-3 rounded-xl bg-white/10 border border-white/20 text-white"
      >

        <option
          v-for="patient in patients"
          :key="patient.id"
          :value="patient.id"
          class="text-gray-800"
        >
          {{ patient.nombres }} {{ patient.apellidos }}
        </option>

      </select>

      <RouterLink
        v-else
        to="/pacientes"
        @click="cerrar"
        class="block text-sm bg-white/10 hover:bg-white/20 transition p-3 rounded-xl text-center"
      >
        + Agregar tu primer paciente
      </RouterLink>

    </div>

    <!-- MENU -->
    <nav class="flex flex-col gap-3">

      <RouterLink
        to="/home"
        @click="cerrar"
        class="flex items-center gap-3 transition p-4 rounded-2xl cursor-pointer"
        :class="esRutaActiva('/home') ? 'bg-white/20' : 'hover:bg-white/20'"
      >
        <Home class="w-5 h-5" />

        <span>
          Home
        </span>
      </RouterLink>

      <RouterLink
        to="/pacientes"
        @click="cerrar"
        class="flex items-center gap-3 transition p-4 rounded-2xl cursor-pointer"
        :class="esRutaActiva('/pacientes') ? 'bg-white/20' : 'hover:bg-white/20'"
      >
        <Users class="w-5 h-5" />

        <span>
          Pacientes
        </span>
      </RouterLink>

      <RouterLink
        to="/medicamentos"
        @click="cerrar"
        class="flex items-center gap-3 transition p-4 rounded-2xl cursor-pointer"
        :class="esRutaActiva('/medicamentos') ? 'bg-white/20' : 'hover:bg-white/20'"
      >
        <Pill class="w-5 h-5" />

        <span>
          Medicamentos
        </span>
      </RouterLink>

      <RouterLink
        to="/recordatorios"
        @click="cerrar"
        class="flex items-center gap-3 transition p-4 rounded-2xl cursor-pointer"
        :class="esRutaActiva('/recordatorios') ? 'bg-white/20' : 'hover:bg-white/20'"
      >
        <Bell class="w-5 h-5" />

        <span>
          Recordatorios
        </span>
      </RouterLink>

      <RouterLink
        to="/citas"
        @click="cerrar"
        class="flex items-center gap-3 transition p-4 rounded-2xl cursor-pointer"
        :class="esRutaActiva('/citas') ? 'bg-white/20' : 'hover:bg-white/20'"
      >
        <CalendarDays class="w-5 h-5" />

        <span>
          Citas médicas
        </span>
      </RouterLink>

      <RouterLink
        to="/configuracion"
        @click="cerrar"
        class="flex items-center gap-3 transition p-4 rounded-2xl cursor-pointer"
        :class="esRutaActiva('/configuracion') ? 'bg-white/20' : 'hover:bg-white/20'"
      >
        <Settings class="w-5 h-5" />

        <span>
          Configuración
        </span>
      </RouterLink>

    </nav>

    <!-- FOOTER -->
    <div class="mt-auto pt-10 flex flex-col gap-4">

      <div
        class="bg-white/10 rounded-2xl p-4"
      >

        <p class="text-sm text-blue-100">
          Sistema médico inteligente para control de tratamientos y citas.
        </p>

      </div>

      <button
        @click="toggleTheme"
        class="flex items-center justify-center gap-2 bg-white/10 hover:bg-white/20 transition p-4 rounded-2xl font-bold"
      >
        <component
          :is="darkMode ? Sun : Moon"
          class="w-5 h-5"
        />
        {{ darkMode ? 'Modo claro' : 'Modo oscuro' }}
      </button>

      <button
        @click="logout"
        class="flex items-center justify-center gap-2 bg-red-500 hover:bg-red-600 transition p-4 rounded-2xl font-bold"
      >
        <LogOut class="w-5 h-5" />
        Cerrar sesión
      </button>

    </div>

  </aside>

</template>

<script setup lang="ts">
import {

  Home,
  Users,
  Pill,
  Bell,
  CalendarDays,
  Settings,
  LogOut,
  Sun,
  Moon,
  X,

} from 'lucide-vue-next'

import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import { usePatient } from '@/composables/usePatient'
import { useMobileMenu } from '@/composables/useMobileMenu'

import AppLogo from './AppLogo.vue'

const route = useRoute()
const router = useRouter()

const { darkMode, toggleTheme } = useTheme()

const { abierto, cerrar } = useMobileMenu()

const {
  patients,
  activePatientId,
  cargarPacientes,
  seleccionarPaciente,
} = usePatient()

onMounted(() => {

  cargarPacientes()

})

const esRutaActiva = (path: string) => {

  return route.path === path

}

const logout = () => {

  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  localStorage.removeItem('activePatientId')

  cerrar()

  router.push('/login')

}
</script>
