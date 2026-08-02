<template>

  <div>

    <!-- HEADER -->
    <div class="mb-10">

      <h1 class="text-4xl font-bold text-gray-800 dark:text-white">
        Configuración
      </h1>

      <p class="text-gray-500 dark:text-gray-400 mt-2">
        Notificaciones de WhatsApp para tus recordatorios
      </p>

    </div>

    <!-- ESTADO DE CARGA -->
    <div
      v-if="cargandoInicial"
      class="bg-white dark:bg-slate-900 p-10 rounded-3xl shadow mb-10 flex items-center justify-center gap-3 text-gray-500 dark:text-gray-400"
    >

      <span
        class="w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"
      ></span>

      Cargando configuración...

    </div>

    <template v-else>

    <!-- INSTRUCCIONES -->
    <div class="bg-white dark:bg-slate-900 p-8 rounded-2xl shadow mb-8">

      <h2 class="text-2xl font-bold mb-4 text-gray-800 dark:text-white">
        📱 Cómo activar WhatsApp (gratis, con CallMeBot)
      </h2>

      <ol class="list-decimal list-inside space-y-2 text-gray-700 dark:text-gray-300 text-sm">

        <li>
          Agrega este número a tus contactos de WhatsApp:
          <b>+34 644 51 95 23</b>
        </li>

        <li>
          Envíale un mensaje con el texto exacto:
          <code class="bg-gray-100 dark:bg-slate-800 px-2 py-1 rounded">
            I allow callmebot to send me messages
          </code>
        </li>

        <li>
          Te va a responder con tu <b>API Key</b> (un número). Cópialo.
        </li>

        <li>
          Pega tu número de WhatsApp (con código de país, sin espacios ni "+")
          y tu API Key abajo, guarda, y envía un mensaje de prueba.
        </li>

      </ol>

    </div>

    <!-- FORMULARIO -->
    <div class="bg-white dark:bg-slate-900 p-8 rounded-2xl shadow mb-10">

      <h2 class="text-2xl font-bold mb-6 text-gray-800 dark:text-white">
        WhatsApp
      </h2>

      <form
        @submit.prevent="guardar"
        class="grid md:grid-cols-2 gap-5"
      >

        <div>

          <label class="text-sm text-gray-500 dark:text-gray-400 block mb-1">
            Número de WhatsApp (código de país + número)
          </label>

          <input
            v-model="whatsappNumero"
            type="text"
            placeholder="Ej: 573001234567"
            class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white w-full"
          />

        </div>

        <div>

          <label class="text-sm text-gray-500 dark:text-gray-400 block mb-1">
            API Key de CallMeBot
          </label>

          <input
            v-model="whatsappApikey"
            type="text"
            placeholder="La clave que te envió CallMeBot"
            class="p-4 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white w-full"
          />

        </div>

        <div class="md:col-span-2 flex flex-col md:flex-row gap-4">

          <button
            type="submit"
            :disabled="guardando"
            class="bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white p-4 rounded-xl flex-1"
          >
            {{ guardando ? 'Guardando...' : 'Guardar' }}
          </button>

          <button
            type="button"
            @click="probar"
            :disabled="probando || !whatsappNumero || !whatsappApikey"
            class="bg-green-600 hover:bg-green-700 disabled:opacity-40 disabled:cursor-not-allowed text-white p-4 rounded-xl flex-1"
          >
            {{ probando ? 'Enviando...' : '📤 Enviar mensaje de prueba' }}
          </button>

        </div>

      </form>

    </div>

    </template>

  </div>

</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { toast } from 'vue-sonner'

import api from '@/api/axios'

const whatsappNumero = ref('')
const whatsappApikey = ref('')

const cargandoInicial = ref(true)
const guardando = ref(false)
const probando = ref(false)

const cargarPerfil = async () => {

  try {

    const response = await api.get('perfil/')

    whatsappNumero.value = response.data.whatsapp_numero || ''
    whatsappApikey.value = response.data.whatsapp_apikey || ''

  } catch (error) {

    console.error(error)

  } finally {

    cargandoInicial.value = false

  }

}

const guardar = async () => {

  guardando.value = true

  try {

    await api.patch('perfil/', {
      whatsapp_numero: whatsappNumero.value,
      whatsapp_apikey: whatsappApikey.value,
    })

    toast.success(
      'Configuración guardada'
    )

  } catch (error) {

    console.error(error)

    toast.error(
      'Error guardando la configuración'
    )

  } finally {

    guardando.value = false

  }

}

const probar = async () => {

  probando.value = true

  try {

    await api.post('perfil/probar-whatsapp/', {
      whatsapp_numero: whatsappNumero.value,
      whatsapp_apikey: whatsappApikey.value,
    })

    toast.success(
      'Mensaje de prueba enviado — revisa tu WhatsApp'
    )

  } catch (error: any) {

    console.error(error)

    toast.error(
      error?.response?.data?.detail || 'Error enviando el mensaje de prueba'
    )

  } finally {

    probando.value = false

  }

}

onMounted(() => {

  cargarPerfil()

})
</script>