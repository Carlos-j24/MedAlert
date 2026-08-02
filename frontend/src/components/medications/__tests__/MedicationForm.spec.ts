import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

import MedicationForm from '@/components/medications/MedicationForm.vue'

describe('MedicationForm', () => {

  it('emite guardar con nombre, dosis y los datos de frecuencia al crear', async () => {

    const wrapper = mount(MedicationForm, {

      props: {
        name: '',
        dose: '',
        editingId: null,
      },

    })

    await wrapper
      .find('input[placeholder="Nombre medicamento"]')
      .setValue('Paracetamol')

    await wrapper
      .find('input[placeholder="Dosis (ej. 500mg)"]')
      .setValue('500mg')

    await wrapper.find('form').trigger('submit')

    const emitido = wrapper.emitted('guardar')

    expect(emitido).toBeTruthy()

    expect(emitido![0][0]).toMatchObject({
      nombre: 'Paracetamol',
      dosis: '500mg',
    })

  })

  it('incluye frecuencia_horas, hora_inicio y duración por defecto', async () => {

    const wrapper = mount(MedicationForm, {

      props: {
        name: 'Ibuprofeno',
        dose: '400mg',
        editingId: null,
      },

    })

    await wrapper.find('form').trigger('submit')

    const datos = wrapper.emitted('guardar')![0][0] as any

    expect(datos.frecuencia_horas).toBe(8)
    expect(datos.hora_inicio).toBe('08:00')
    expect(datos.duracion_cantidad).toBe(7)
    expect(datos.duracion_unidad).toBe('dias')

  })

  it('oculta los campos de frecuencia/duración cuando se está editando', () => {

    const wrapper = mount(MedicationForm, {

      props: {
        name: 'Ibuprofeno',
        dose: '400mg',
        editingId: 5,
      },

    })

    expect(wrapper.text()).not.toContain('¿Cada cuánto se toma?')
    expect(wrapper.text()).toContain('Actualizar medicamento')

  })

  it('muestra el título de crear cuando no hay editingId', () => {

    const wrapper = mount(MedicationForm, {

      props: {
        name: '',
        dose: '',
        editingId: null,
      },

    })

    expect(wrapper.text()).toContain('Agregar medicamento')

  })

})
