import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

import PatientForm from '@/components/patients/PatientForm.vue'

describe('PatientForm', () => {

  it('emite guardar con los datos ingresados', async () => {

    const wrapper = mount(PatientForm, {

      props: {
        nombres: '',
        apellidos: '',
        identificacion: '',
        genero: '',
        editingId: null,
      },

    })

    await wrapper
      .find('input[placeholder="Nombres"]')
      .setValue('Ana')

    await wrapper
      .find('input[placeholder="Apellidos"]')
      .setValue('Gómez')

    await wrapper
      .find('input[placeholder="Identificación (cédula)"]')
      .setValue('123456')

    await wrapper
      .find('select')
      .setValue('femenino')

    await wrapper.find('form').trigger('submit')

    const emitido = wrapper.emitted('guardar')

    expect(emitido).toBeTruthy()

    expect(emitido![0][0]).toEqual({
      nombres: 'Ana',
      apellidos: 'Gómez',
      identificacion: '123456',
      genero: 'femenino',
    })

  })

  it('precarga los datos existentes cuando se está editando', () => {

    const wrapper = mount(PatientForm, {

      props: {
        nombres: 'Luis',
        apellidos: 'Ramírez',
        identificacion: '999999',
        genero: 'masculino',
        editingId: 3,
      },

    })

    expect(wrapper.text()).toContain('Editar paciente')

    const inputNombres = wrapper.find(
      'input[placeholder="Nombres"]'
    ).element as HTMLInputElement

    expect(inputNombres.value).toBe('Luis')

  })

})
