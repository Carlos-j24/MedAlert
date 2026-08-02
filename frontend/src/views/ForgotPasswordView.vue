<template>

  <div class="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-slate-950">

    <div class="bg-white dark:bg-slate-900 p-10 rounded-2xl shadow w-full max-w-md">

      <div class="flex items-center justify-center gap-3 mb-8">

        <div class="w-14 h-14">
          <AppLogo />
        </div>

        <h1 class="text-2xl font-bold text-blue-700 dark:text-blue-400">
          Recuperar contraseña
        </h1>

      </div>

      <template v-if="!enviado">

        <p class="text-gray-500 dark:text-gray-400 text-sm mb-5">
          Escribe el correo con el que te registraste. Si existe una
          cuenta asociada, te enviaremos un enlace para elegir una
          contraseña nueva.
        </p>

        <form
          @submit.prevent="enviar"
          class="space-y-5"
        >

          <input
            v-model="email"
            type="email"
            placeholder="Correo electrónico"
            class="w-full p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
          />

          <button
            type="submit"
            :disabled="enviando"
            class="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white p-4 rounded-xl transition"
          >
            {{ enviando ? 'Enviando...' : 'Enviar enlace' }}
          </button>

        </form>

      </template>

      <template v-else>

        <div class="text-center">

          <p class="text-gray-700 dark:text-gray-300 mb-6">
            Si ese correo está registrado, te enviamos un enlace
            para restablecer tu contraseña. Revisa tu bandeja de
            entrada (y la de spam, por si acaso).
          </p>

        </div>

      </template>

      <p class="text-center mt-6 text-gray-500 dark:text-gray-400">

        <router-link
          to="/login"
          class="text-blue-600 font-bold"
        >
          Volver a iniciar sesión
        </router-link>

      </p>

    </div>

  </div>

</template>

<script setup lang="ts">
import { ref } from 'vue'

import api from '@/api/axios'
import AppLogo from '@/components/layout/AppLogo.vue'

const email = ref('')
const enviando = ref(false)
const enviado = ref(false)

const enviar = async () => {

  enviando.value = true

  try {

    await api.post('password-reset/', {
      email: email.value,
    })

    enviado.value = true

  } catch (error) {

    // Aunque falle, mostramos el mismo mensaje genérico por
    // seguridad (no confirmamos ni negamos si el correo existe).
    enviado.value = true

    console.error(error)

  } finally {

    enviando.value = false

  }

}
</script>
