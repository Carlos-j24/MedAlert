import { describe, it, expect, beforeEach } from 'vitest'

import { useMobileMenu } from '@/composables/useMobileMenu'

describe('useMobileMenu', () => {

  beforeEach(() => {

    const { cerrar } = useMobileMenu()

    cerrar()

  })

  it('empieza cerrado', () => {

    const { abierto } = useMobileMenu()

    expect(abierto.value).toBe(false)

  })

  it('abrir() lo pone en true', () => {

    const { abierto, abrir } = useMobileMenu()

    abrir()

    expect(abierto.value).toBe(true)

  })

  it('cerrar() lo pone en false', () => {

    const { abierto, abrir, cerrar } = useMobileMenu()

    abrir()
    cerrar()

    expect(abierto.value).toBe(false)

  })

  it('alternar() invierte el estado actual', () => {

    const { abierto, alternar } = useMobileMenu()

    const valorInicial = abierto.value

    alternar()

    expect(abierto.value).toBe(!valorInicial)

  })

  it('el estado se comparte entre distintas llamadas (singleton)', () => {

    const primero = useMobileMenu()
    const segundo = useMobileMenu()

    primero.abrir()

    expect(segundo.abierto.value).toBe(true)

  })

})
