import { ref } from 'vue'

const abierto = ref(false)

export function useMobileMenu() {

  const abrir = () => {

    abierto.value = true

  }

  const cerrar = () => {

    abierto.value = false

  }

  const alternar = () => {

    abierto.value = !abierto.value

  }

  return {

    abierto,
    abrir,
    cerrar,
    alternar,

  }

}
