import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CreateDeckView from '../views/CreateDeckView.vue'
import DeckView from '../views/DeckView.vue'
import AuthView from '../views/AuthView.vue'
import { initializeAuth, isAuthenticated } from '../services/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path: '/create',
      name: 'create',
      component: CreateDeckView,
      meta: { requiresAuth: true },
    },
    {
      path: '/decks/:id',
      name: 'deck',
      component: DeckView,
      meta: { requiresAuth: true },
    },
    {
      path: '/auth',
      name: 'auth',
      component: AuthView,
      meta: { guestOnly: true },
    },
  ],
})

router.beforeEach(async (to) => {
  await initializeAuth()

  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return {
      name: 'auth',
      query: { redirect: to.fullPath },
    }
  }

  if (to.meta.guestOnly && isAuthenticated.value) {
    return { name: 'home' }
  }
})

export default router
