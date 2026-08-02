import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

import ReminderList from '@/components/reminders/ReminderList.vue'

describe('ReminderList', () => {

  it('muestra un mensaje cuando no hay recordatorios', () => {

    const wrapper = mount(ReminderList, {

      props: { reminders: [] },

    })

    expect(wrapper.text()).toContain('No hay recordatorios.')

  })

  it('muestra "Tratamiento finalizado" cuando fecha_fin ya pasó', () => {

    const recordatorio = {
      id: 1,
      medication_nombre: 'Paracetamol',
      appointment_info: null,
      hora: '08:00:00',
      fecha_fin: '2020-01-01',
      activo: true,
      tomado: false,
    }

    const wrapper = mount(ReminderList, {

      props: { reminders: [recordatorio] },

    })

    expect(wrapper.text()).toContain('Tratamiento finalizado')

  })

  it('muestra la fecha de fin cuando el tratamiento sigue vigente', () => {

    const fechaFutura = new Date()

    fechaFutura.setDate(fechaFutura.getDate() + 10)

    const fechaFinStr = fechaFutura.toISOString().split('T')[0]

    const recordatorio = {
      id: 2,
      medication_nombre: 'Ibuprofeno',
      appointment_info: null,
      hora: '08:00:00',
      fecha_fin: fechaFinStr,
      activo: true,
      tomado: false,
    }

    const wrapper = mount(ReminderList, {

      props: { reminders: [recordatorio] },

    })

    expect(wrapper.text()).toContain('Hasta el')
    expect(wrapper.text()).not.toContain('finalizado')

  })

  it('muestra la información de la cita cuando el recordatorio no es de un medicamento', () => {

    const recordatorio = {
      id: 3,
      medication_nombre: null,
      appointment_info: 'Dr. Pérez - Cardiología',
      frecuencia: 'Antes de la cita',
      fecha: '2026-08-01',
      hora: '10:00:00',
      fecha_fin: null,
      activo: true,
      tomado: false,
    }

    const wrapper = mount(ReminderList, {

      props: { reminders: [recordatorio] },

    })

    expect(wrapper.text()).toContain('Dr. Pérez - Cardiología')
    expect(wrapper.text()).toContain('Antes de la cita')

  })

  it('emite toggleActivo y toggleTomado con el recordatorio correspondiente', async () => {

    const recordatorio = {
      id: 4,
      medication_nombre: 'Losartán',
      appointment_info: null,
      hora: '09:00:00',
      fecha_fin: null,
      activo: false,
      tomado: false,
    }

    const wrapper = mount(ReminderList, {

      props: { reminders: [recordatorio] },

    })

    const botones = wrapper.findAll('button')

    const botonActivo = botones.find((b) =>
      b.text().includes('Inactivo')
    )

    const botonTomado = botones.find((b) =>
      b.text().includes('Pendiente')
    )

    await botonActivo!.trigger('click')
    await botonTomado!.trigger('click')

    expect(wrapper.emitted('toggleActivo')![0][0]).toEqual(recordatorio)
    expect(wrapper.emitted('toggleTomado')![0][0]).toEqual(recordatorio)

  })

})
