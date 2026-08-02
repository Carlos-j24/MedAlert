<template>

  <div>

    <!-- HEADER -->
    <div class="mb-10">

      <h1 class="text-4xl font-bold text-gray-800 dark:text-white">
        Citas médicas
      </h1>

      <p class="text-gray-500 dark:text-gray-400 mt-2">
        Agenda y controla tus citas médicas
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

      Cargando citas médicas...

    </div>

    <!-- SIN PACIENTE -->
    <div
      v-else-if="!activePatientId"
      class="bg-white dark:bg-slate-900 p-10 rounded-3xl shadow mb-10 text-center"
    >

      <p class="text-gray-500 dark:text-gray-400 mb-4">
        Selecciona o agrega un paciente para ver sus citas médicas.
      </p>

      <RouterLink
        to="/pacientes"
        class="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl"
      >
        Ir a Pacientes
      </RouterLink>

    </div>

    <template v-else>

    <!-- ================================= -->
    <!-- CITAS -->
    <!-- ================================= -->

    <AppointmentForm
      v-model:fecha="appointmentDate"
      v-model:hora="appointmentTime"
      v-model:tipo="tipo"
      v-model:doctor="doctor"
      v-model:especialidad="especialidad"
      v-model:lugar="lugar"
      v-model:direccion="direccion"
      v-model:barrio="barrio"
      v-model:piso="piso"
      v-model:consultorio="consultorio"
      v-model:recordatorio="recordatorio"
      v-model:recordatorioAntesCantidad="recordatorioAntesCantidad"
      v-model:recordatorioAntesUnidad="recordatorioAntesUnidad"
      @guardar="crearCita"
    />

    <div class="mb-6 flex flex-col md:flex-row gap-4">

      <input
        v-model="busqueda"
        @input="onBuscar"
        type="text"
        placeholder="🔎 Buscar por doctor, especialidad o lugar..."
        class="flex-1 p-3 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      />

      <select
        v-model="filtroTipo"
        @change="cargarCitas()"
        class="p-3 border rounded-xl bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white"
      >
        <option value="">Todos los tipos</option>
        <option value="consulta">Consulta con especialista</option>
        <option value="examen">Examen médico</option>
        <option value="terapia">Terapia física</option>
        <option value="cirugia">Cirugía programada</option>
      </select>

    </div>

    <AppointmentList
      :appointments="appointments"
      @cumplida="cita => cambiarEstadoCita(cita, 'cumplida')"
      @cancelada="cita => cambiarEstadoCita(cita, 'cancelada')"
    />

    <div
      v-if="appointmentsNext || appointmentsPrevious"
      class="flex justify-center gap-4 mb-10"
    >

      <button
        :disabled="!appointmentsPrevious"
        @click="cargarCitas(appointmentsPrevious)"
        class="px-5 py-2 rounded-xl bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-300"
      >
        ← Anterior
      </button>

      <span class="self-center text-gray-500 dark:text-gray-400 text-sm">
        {{ appointmentsCount }} citas en total
      </span>

      <button
        :disabled="!appointmentsNext"
        @click="cargarCitas(appointmentsNext)"
        class="px-5 py-2 rounded-xl bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-300"
      >
        Siguiente →
      </button>

    </div>

    </template>

  </div>

</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { toast } from 'vue-sonner'

import api from '@/api/axios'
import { usePatient } from '@/composables/usePatient'

import AppointmentForm from '@/components/appointments/AppointmentForm.vue'
import AppointmentList from '@/components/appointments/AppointmentList.vue'

const { activePatientId } = usePatient()

// ======================================
// CITAS
// ======================================

const appointments = ref([])
const appointmentsCount = ref(0)
const appointmentsNext = ref<string | null>(null)
const appointmentsPrevious = ref<string | null>(null)

const appointmentDate = ref('')
const appointmentTime = ref('')

const lugar = ref('')
const direccion = ref('')
const barrio = ref('')

const piso = ref('')
const consultorio = ref('')

const doctor = ref('')
const especialidad = ref('')

const tipo = ref('consulta')

const recordatorio = ref(true)
const recordatorioAntesCantidad = ref(1)
const recordatorioAntesUnidad = ref('dias')

const busqueda = ref('')
const filtroTipo = ref('')

let temporizadorBusqueda: ReturnType<typeof setTimeout> | null = null

const onBuscar = () => {

  if (temporizadorBusqueda) clearTimeout(temporizadorBusqueda)

  temporizadorBusqueda = setTimeout(() => {

    cargarCitas()

  }, 400)

}

const cargarCitas = async (
  url: string | null = null
) => {

  if (!activePatientId.value) return

  try {

    const parametroBusqueda = busqueda.value
      ? `&search=${encodeURIComponent(busqueda.value)}`
      : ''

    const parametroTipo = filtroTipo.value
      ? `&tipo=${filtroTipo.value}`
      : ''

    const response = await api.get(
      url || `appointments/?patient=${activePatientId.value}${parametroBusqueda}${parametroTipo}`
    )

    appointments.value = response.data.results
    appointmentsCount.value = response.data.count
    appointmentsNext.value = response.data.next
    appointmentsPrevious.value = response.data.previous

  } catch (error) {

    console.error(error)

  }

}

const crearCita = async () => {

  if (!activePatientId.value) return

  try {

    await api.post(

      'appointments/',

      {
        patient: activePatientId.value,

        tipo: tipo.value,

        fecha: appointmentDate.value,
        hora: appointmentTime.value,

        lugar: lugar.value,
        direccion: direccion.value,
        barrio: barrio.value,

        piso: piso.value,
        consultorio: consultorio.value,

        doctor: doctor.value,
        especialidad: especialidad.value,

        estado: 'pendiente',
        recordatorio: recordatorio.value,
        recordatorio_antes_cantidad: recordatorioAntesCantidad.value,
        recordatorio_antes_unidad: recordatorioAntesUnidad.value,
      }

    )

    cargarCitas()

    toast.success(
      recordatorio.value
        ? 'Cita creada con recordatorios automáticos'
        : 'Cita creada'
    )

  } catch (error) {

    console.error(error)

    toast.error(
      'Error creando cita'
    )

  }

}

// CAMBIAR ESTADO
const cambiarEstadoCita = async (
  cita: any,
  nuevoEstado: string
) => {

  try {

    await api.put(

      `appointments/${cita.id}/`,

      {
        ...cita,
        estado: nuevoEstado,
      }

    )

    cargarCitas()

    toast.success(
      'Estado de la cita actualizado'
    )

  } catch (error: any) {

    console.error(
      'Error cambiando estado de la cita:',
      error?.response?.data || error
    )

    toast.error(
      'Error actualizando la cita'
    )

  }

}

// ======================================
// INIT
// ======================================

const cargandoInicial = ref(true)

onMounted(async () => {

  await cargarCitas()

  cargandoInicial.value = false

})

watch(activePatientId, () => {

  cargarCitas()

})
</script>
