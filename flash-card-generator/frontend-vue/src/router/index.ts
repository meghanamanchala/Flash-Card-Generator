import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CreateDeckView from '../views/CreateDeckView.vue'
import DeckView from '../views/DeckView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/create',
      name: 'create',
      component: CreateDeckView,
    },
    {
      path: '/decks/:id',
      name: 'deck',
      component: DeckView,
    },
  ],
})

export default router
