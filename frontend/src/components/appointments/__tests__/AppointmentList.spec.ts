import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

import AppointmentList from '@/components/appointments/AppointmentList.vue'

const citaEjemplo = {
  id: 1,
  tipo: 'examen',
  doctor: 'Dr. Ruiz',
  especialidad: 'Laboratorio',
  fecha: '2026-08-15',
  hora: '09:00:00',
  lugar: 'Lab Nacional',
  estado: 'pendiente',
}

describe('AppointmentList', () => {

  it('muestra un mensaje cuando no hay citas', () => {

    const wrapper = mount(AppointmentList, {

      props: { appointments: [] },

    })

    expect(wrapper.text()).toContain('No hay citas registradas.')

  })

  it('muestra la etiqueta legible del tipo de cita', () => {

    const wrapper = mount(AppointmentList, {

      props: { appointments: [citaEjemplo] },

    })

    expect(wrapper.text()).toContain('Examen médico')
    expect(wrapper.text()).toContain('Dr. Ruiz')
    expect(wrapper.text()).toContain('Laboratorio')

  })

  it('usa el valor crudo como respaldo si el tipo no está mapeado', () => {

    const wrapper = mount(AppointmentList, {

      props: {
        appointments: [{ ...citaEjemplo, tipo: 'otro-tipo' }],
      },

    })

    expect(wrapper.text()).toContain('otro-tipo')

  })

  it('emite cumplida con la cita al hacer clic en el botón', async () => {

    const wrapper = mount(AppointmentList, {

      props: { appointments: [citaEjemplo] },

    })

    const botones = wrapper.findAll('button')

    const botonCumplida = botones.find((b) =>
      b.text().includes('Cumplida')
    )

    await botonCumplida!.trigger('click')

    const emitido = wrapper.emitted('cumplida')

    expect(emitido).toBeTruthy()
    expect(emitido![0][0]).toEqual(citaEjemplo)

  })

  it('emite cancelada con la cita al hacer clic en el botón', async () => {

    const wrapper = mount(AppointmentList, {

      props: { appointments: [citaEjemplo] },

    })

    const botones = wrapper.findAll('button')

    const botonCancelada = botones.find((b) =>
      b.text().includes('Cancelada')
    )

    await botonCancelada!.trigger('click')

    const emitido = wrapper.emitted('cancelada')

    expect(emitido).toBeTruthy()
    expect(emitido![0][0]).toEqual(citaEjemplo)

  })

})
