import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import ForgotPasswordView from '@/views/ForgotPasswordView.vue'
import ResetPasswordView from '@/views/ResetPasswordView.vue'
import DashboardView from '@/views/DashboardView.vue'
import MedicationsView from '@/views/MedicationsView.vue'
import RemindersView from '@/views/RemindersView.vue'
import AppointmentsView from '@/views/AppointmentsView.vue'
import PatientsView from '@/views/PatientsView.vue'
import ConfiguracionView from '@/views/ConfiguracionView.vue'

import AppLayout from '@/layouts/AppLayout.vue'

// Guard reutilizable para todas las secciones autenticadas
const requireAuth = (to, from, next) => {

  const token = localStorage.getItem('access')

  if (token) {

    next()

  } else {

    next('/login')

  }

}

const routes = [

  {
    path: '/',
    redirect: '/login',
  },

  {
    path: '/login',
    component: LoginView,
  },

  {
    path: '/register',
    component: RegisterView,
  },

  {
    path: '/olvide-password',
    component: ForgotPasswordView,
  },

  {
    path: '/restablecer-password',
    component: ResetPasswordView,
  },

  {
    path: '/',
    component: AppLayout,

    beforeEnter: requireAuth,

    children: [

      {
        path: 'home',
        component: DashboardView,
      },

      {
        path: 'pacientes',
        component: PatientsView,
      },

      {
        path: 'medicamentos',
        component: MedicationsView,
      },

      {
        path: 'recordatorios',
        component: RemindersView,
      },

      {
        path: 'citas',
        component: AppointmentsView,
      },

      {
        path: 'configuracion',
        component: ConfiguracionView,
      },

    ],

  },

]

const router = createRouter({

  history: createWebHistory(),

  routes,

})

export default router
