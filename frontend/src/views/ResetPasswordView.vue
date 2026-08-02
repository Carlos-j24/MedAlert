<template>

  <div class="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-slate-950">

    <div class="bg-white dark:bg-slate-900 p-10 rounded-2xl shadow w-full max-w-md">

      <div class="flex items-center justify-center gap-3 mb-8">

        <div class="w-14 h-14">
          <AppLogo />
        </div>

        <h1 class="text-2xl font-bold text-blue-700 dark:text-blue-400">
          Nueva contraseña
        </h1>

      </div>

      <template v-if="!enlaceInvalido && !completado">

        <form
          @submit.prevent="restablecer"
          class="space-y-5"
        >

          <div>

            <input
              v-model="password"
              type="password"
              placeholder="Nueva contraseña"
              class="w-full p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
              :class="{ 'border-red-500': errores.length }"
            />

            <ul
              v-if="errores.length"
              class="text-red-600 text-sm mt-1 list-disc list-inside space-y-0.5"
            >
              <li
                v-for="(msg, i) in errores"
                :key="i"
              >
                {{ msg }}
              </li>
            </ul>

          </div>

          <button
            type="submit"
            :disabled="enviando"
            class="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white p-4 rounded-xl transition"
          >
            {{ enviando ? 'Guardando...' : 'Guardar nueva contraseña' }}
          </button>

        </form>

      </template>

      <template v-else-if="enlaceInvalido">

        <p class="text-gray-700 dark:text-gray-300 text-center mb-6">
          Este enlace no es válido o ya expiró. Pide uno nuevo desde
          la pantalla de inicio de sesión.
        </p>

      </template>

      <template v-else>

        <p class="text-gray-700 dark:text-gray-300 text-center mb-6">
          Tu contraseña se actualizó correctamente. Ya puedes
          iniciar sesión con ella.
        </p>

      </template>

      <p class="text-center mt-6 text-gray-500 dark:text-gray-400">

        <router-link
          to="/login"
          class="text-blue-600 font-bold"
        >
          Ir a iniciar sesión
        </router-link>

      </p>

    </div>

  </div>

</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import api from '@/api/axios'
import AppLogo from '@/components/layout/AppLogo.vue'

const route = useRoute()

const uid = ref('')
const token = ref('')

const password = ref('')
const errores = ref<string[]>([])

const enviando = ref(false)
const completado = ref(false)
const enlaceInvalido = ref(false)

onMounted(() => {

  uid.value = String(route.query.uid || '')
  token.value = String(route.query.token || '')

  if (!uid.value || !token.value) {

    enlaceInvalido.value = true

  }

})

const restablecer = async () => {

  errores.value = []
  enviando.value = true

  try {

    await api.post('password-reset-confirm/', {
      uid: uid.value,
      token: token.value,
      password: password.value,
    })

    completado.value = true

  } catch (error: any) {

    const data = error?.response?.data

    if (data?.password) {

      errores.value = data.password

    } else if (data?.detail) {

      enlaceInvalido.value = true

    } else {

      errores.value = ['Ocurrió un error, intenta de nuevo.']

    }

    console.error(error)

  } finally {

    enviando.value = false

  }

}
</script>
