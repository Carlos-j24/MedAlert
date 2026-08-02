<template>

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
        @submit.prevent="register"
        class="space-y-5"
      >

        <div class="grid grid-cols-2 gap-4">

          <div>
            <input
              v-model="firstName"
              type="text"
              placeholder="Nombres"
              class="w-full p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
              :class="{ 'border-red-500': errors.first_name }"
            />
            <p
              v-if="errors.first_name"
              class="text-red-600 text-sm mt-1"
            >
              {{ errors.first_name }}
            </p>
          </div>

          <div>
            <input
              v-model="lastName"
              type="text"
              placeholder="Apellidos"
              class="w-full p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
              :class="{ 'border-red-500': errors.last_name }"
            />
            <p
              v-if="errors.last_name"
              class="text-red-600 text-sm mt-1"
            >
              {{ errors.last_name }}
            </p>
          </div>

        </div>

        <div>
          <input
            v-model="identificacion"
            type="text"
            placeholder="Identificación (cédula)"
            class="w-full p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
            :class="{ 'border-red-500': errors.identificacion }"
          />
          <p
            v-if="errors.identificacion"
            class="text-red-600 text-sm mt-1"
          >
            {{ errors.identificacion }}
          </p>
        </div>

        <div>
          <select
            v-model="genero"
            class="w-full p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
            :class="{ 'border-red-500': errors.genero }"
          >
            <option disabled value="">
              Selecciona género
            </option>
            <option value="femenino">Femenino</option>
            <option value="masculino">Masculino</option>
            <option value="prefiero_no_decir">Prefiero no decir</option>
          </select>
          <p
            v-if="errors.genero"
            class="text-red-600 text-sm mt-1"
          >
            {{ errors.genero }}
          </p>
        </div>

        <div>
          <input
            v-model="username"
            type="text"
            placeholder="Usuario"
            class="w-full p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
            :class="{ 'border-red-500': errors.username }"
          />
          <p
            v-if="errors.username"
            class="text-red-600 text-sm mt-1"
          >
            {{ errors.username }}
          </p>
        </div>

        <div>
          <input
            v-model="email"
            type="email"
            placeholder="Correo electrónico"
            class="w-full p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
            :class="{ 'border-red-500': errors.email }"
          />
          <p
            v-if="errors.email"
            class="text-red-600 text-sm mt-1"
          >
            {{ errors.email }}
          </p>
        </div>

        <div>
          <input
            v-model="password"
            type="password"
            placeholder="Contraseña"
            class="w-full p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
            :class="{ 'border-red-500': errors.password.length }"
          />
          <ul
            v-if="errors.password.length"
            class="text-red-600 text-sm mt-1 list-disc list-inside space-y-0.5"
          >
            <li
              v-for="(msg, i) in errors.password"
              :key="i"
            >
              {{ msg }}
            </li>
          </ul>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed text-white p-4 rounded-xl transition"
        >
          {{ loading ? 'Creando cuenta...' : 'Crear cuenta' }}
        </button>

      </form>

      <p class="text-center mt-6 text-gray-500 dark:text-gray-400">

        ¿Ya tienes cuenta?

        <router-link
          to="/login"
          class="text-blue-600 font-bold"
        >
          Inicia sesión
        </router-link>

      </p>

    </div>

  </div>

</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import Swal from 'sweetalert2'

import api from '@/api/axios'
import AppLogo from '@/components/layout/AppLogo.vue'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const firstName = ref('')
const lastName = ref('')
const identificacion = ref('')
const genero = ref('')
const loading = ref(false)

const errors = reactive({
  username: '',
  email: '',
  password: [] as string[],
  first_name: '',
  last_name: '',
  identificacion: '',
  genero: '',
})

const resetErrors = () => {
  errors.username = ''
  errors.email = ''
  errors.password = []
  errors.first_name = ''
  errors.last_name = ''
  errors.identificacion = ''
  errors.genero = ''
}

const register = async () => {

  resetErrors()
  loading.value = true

  try {

    await api.post(
      'register/',
      {
        username: username.value,
        email: email.value,
        password: password.value,
        first_name: firstName.value,
        last_name: lastName.value,
        identificacion: identificacion.value,
        genero: genero.value,
      }
    )

    Swal.fire({
      icon: 'success',
      title: 'Cuenta creada',
      text: 'Ahora puedes iniciar sesión',
    })

    router.push('/login')

  } catch (error: any) {

    const data = error?.response?.data

    if (data) {

      // DRF devuelve { campo: [mensajes] } cuando falla la validación
      if (data.username) errors.username = data.username[0]
      if (data.email) errors.email = data.email[0]
      if (data.password) errors.password = data.password
      if (data.first_name) errors.first_name = data.first_name[0]
      if (data.last_name) errors.last_name = data.last_name[0]
      if (data.identificacion) errors.identificacion = data.identificacion[0]
      if (data.genero) errors.genero = data.genero[0]

    }

    const sinErroresDeCampo =
      !data ||
      (!data.username && !data.email && !data.password &&
       !data.first_name && !data.last_name &&
       !data.identificacion && !data.genero)

    if (sinErroresDeCampo) {

      Swal.fire({
        icon: 'error',
        title: 'No se pudo crear la cuenta',
        text: 'Intenta de nuevo en unos momentos',
      })

    }

    console.error(error)

  } finally {

    loading.value = false

  }

}
</script>
