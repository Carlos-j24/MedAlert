<template>

  <LoadingTransition v-if="mostrarTransicion" />

  <div class="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-slate-950">

    <div class="bg-white dark:bg-slate-900 p-10 rounded-2xl shadow w-full max-w-md">

      <div class="flex items-center justify-center gap-3 mb-8">

        <div class="w-14 h-14">
          <AppLogo animated />
        </div>

        <h1 class="text-4xl font-bold text-blue-700 dark:text-blue-400">
          MedAlert
        </h1>

      </div>

      <form
        @submit.prevent="login"
        class="space-y-5"
      >

        <input
          v-model="username"
          type="text"
          placeholder="Usuario"
          class="w-full p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
        />

        <input
          v-model="password"
          type="password"
          placeholder="Contraseña"
          class="w-full p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
        />

        <button
          type="submit"
          class="w-full bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-xl transition"
        >
          Iniciar sesión
        </button>

      </form>

      <p class="text-center mt-4">

        <router-link
          to="/olvide-password"
          class="text-sm text-gray-500 dark:text-gray-400 hover:text-blue-600"
        >
          ¿Olvidaste tu contraseña?
        </router-link>

      </p>

      <p class="text-center mt-6 text-gray-500 dark:text-gray-400">

        ¿No tienes cuenta?

        <router-link
          to="/register"
          class="text-blue-600 font-bold"
        >
          Regístrate
        </router-link>

      </p>

    </div>

  </div>

</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import Swal from 'sweetalert2'

import api from '@/api/axios'

import LoadingTransition from '@/components/layout/LoadingTransition.vue'
import AppLogo from '@/components/layout/AppLogo.vue'

const router = useRouter()

const username = ref('')
const password = ref('')

const mostrarTransicion = ref(false)

const login = async () => {

  try {

    const response = await api.post(

      'token/',

      {
        username: username.value,
        password: password.value,
      }

    )

    localStorage.setItem(
      'access',
      response.data.access
    )

    localStorage.setItem(
      'refresh',
      response.data.refresh
    )

    mostrarTransicion.value = true

    setTimeout(() => {

      router.push('/home')

    }, 1800)

  } catch (error) {

    Swal.fire({

      icon: 'error',
      title: 'Credenciales incorrectas',

    })

    console.error(error)

  }

}
</script>