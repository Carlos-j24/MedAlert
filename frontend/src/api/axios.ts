import axios from 'axios'
import router from '@/router'

const API_URL = import.meta.env.VITE_API_URL

const api = axios.create({

  baseURL: API_URL,

})

// ======================================
// REQUEST INTERCEPTOR
// ======================================

api.interceptors.request.use(

  (config) => {

    const token = localStorage.getItem('access')

    if (token) {

      config.headers.Authorization =
        `Bearer ${token}`

    }

    return config

  },

  (error) => Promise.reject(error)

)

// ======================================
// RESPONSE INTERCEPTOR
// ======================================

api.interceptors.response.use(

  (response) => response,

  async (error) => {

    const originalRequest = error.config

    // TOKEN EXPIRADO
    if (

      error.response?.status === 401 &&
      !originalRequest._retry

    ) {

      originalRequest._retry = true

      try {

        const refresh =
          localStorage.getItem('refresh')

        // PEDIR NUEVO ACCESS
        const response = await axios.post(

          `${API_URL}token/refresh/`,

          {
            refresh,
          }

        )

        const newAccess =
          response.data.access

        // GUARDAR NUEVO TOKEN
        localStorage.setItem(
          'access',
          newAccess
        )

        // ACTUALIZAR HEADER
        originalRequest.headers.Authorization =
          `Bearer ${newAccess}`

        // REPETIR REQUEST ORIGINAL
        return api(originalRequest)

      } catch (refreshError) {

        // SI EL REFRESH FALLA
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')

        router.push('/login')

        return Promise.reject(refreshError)

      }

    }

    return Promise.reject(error)

  }

)

export default api