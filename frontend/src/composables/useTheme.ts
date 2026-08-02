import { ref, onMounted } from 'vue'

const darkMode = ref(false)

export function useTheme() {

  const toggleTheme = () => {

    darkMode.value = !darkMode.value

    if (darkMode.value) {

      document.documentElement.classList.add('dark')

      localStorage.setItem(
        'theme',
        'dark'
      )

    } else {

      document.documentElement.classList.remove('dark')

      localStorage.setItem(
        'theme',
        'light'
      )

    }

  }

  onMounted(() => {

    const savedTheme =
      localStorage.getItem('theme')

    if (savedTheme === 'dark') {

      darkMode.value = true

      document.documentElement.classList.add(
        'dark'
      )

    }

  })

  return {

    darkMode,
    toggleTheme,

  }

}