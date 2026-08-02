import { describe, it, expect, beforeEach } from 'vitest'
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'

import { useTheme } from '@/composables/useTheme'

describe('useTheme', () => {

  beforeEach(() => {

    localStorage.clear()

    document.documentElement.classList.remove('dark')

    const { darkMode } = useTheme()

    darkMode.value = false

  })

  it('toggleTheme activa el modo oscuro y lo guarda en localStorage', () => {

    const { toggleTheme, darkMode } = useTheme()

    toggleTheme()

    expect(darkMode.value).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(localStorage.getItem('theme')).toBe('dark')

  })

  it('toggleTheme vuelve a modo claro si se llama dos veces', () => {

    const { toggleTheme, darkMode } = useTheme()

    toggleTheme()
    toggleTheme()

    expect(darkMode.value).toBe(false)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
    expect(localStorage.getItem('theme')).toBe('light')

  })

  it('restaura el modo oscuro guardado al montar un componente', () => {

    localStorage.setItem('theme', 'dark')

    const Componente = defineComponent({

      setup() {

        const { darkMode } = useTheme()

        return { darkMode }

      },

      template: '<div>{{ darkMode }}</div>',

    })

    mount(Componente)

    expect(document.documentElement.classList.contains('dark')).toBe(true)

  })

})
