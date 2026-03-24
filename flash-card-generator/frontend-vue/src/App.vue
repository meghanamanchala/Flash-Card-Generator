<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

import { currentUser, isAuthenticated, logout } from './services/auth'

const route = useRoute()
const router = useRouter()

const username = computed(() => currentUser.value?.username ?? '')
const showDashboardHeader = computed(() => isAuthenticated.value && route.name === 'home')

async function signOut() {
  await logout()
  await router.push({ name: 'auth' })
}
</script>

<template>
  <div class="app-shell">
    <header v-if="showDashboardHeader" class="app-navbar">
      <RouterLink class="brand-mark" to="/">
        <strong>Flash Card Generator</strong>
      </RouterLink>

      <div class="navbar-actions">
        <span class="user-chip">{{ username }}</span>
        <RouterLink class="primary-link" to="/create">
          <span aria-hidden="true">+</span>
          <span>New Deck</span>
        </RouterLink>
        <button class="logout-button" type="button" @click="signOut">Logout</button>
      </div>
    </header>

    <RouterView />
  </div>
</template>

<style scoped>
.app-shell {
  display: grid;
  gap: 1.25rem;
}

.app-navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.15rem 1.5rem;
  border: 1px solid var(--color-border);
  border-radius: 24px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(244, 247, 252, 0.98)),
    var(--color-surface);
  box-shadow: var(--color-shadow);
}

.brand-mark {
  color: var(--color-heading);
}

.brand-mark strong {
  font-size: 1.95rem;
  font-weight: 700;
  letter-spacing: -0.04em;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.user-chip,
.logout-button,
.primary-link {
  border-radius: 14px;
  font: inherit;
}

.user-chip {
  padding: 0.7rem 0.95rem;
  background: var(--color-panel);
  color: var(--color-text);
  font-size: 0.95rem;
  font-weight: 600;
  border: 1px solid var(--color-border);
}

.primary-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.8rem 1.1rem;
  background: linear-gradient(180deg, #3b6cff, #2f5de6);
  color: #ffffff;
  font-weight: 700;
  box-shadow: 0 14px 28px rgba(47, 93, 230, 0.18);
}

.logout-button {
  border: 1px solid var(--color-border);
  padding: 0.8rem 1rem;
  cursor: pointer;
  background: var(--color-panel);
  color: var(--color-heading);
  font-weight: 600;
}

@media (max-width: 720px) {
  .app-navbar {
    align-items: start;
    flex-direction: column;
  }

  .navbar-actions {
    width: 100%;
  }
}
</style>
