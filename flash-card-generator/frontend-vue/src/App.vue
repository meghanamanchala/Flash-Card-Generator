<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

import { currentUser, isAuthenticated, logout } from './services/auth'

const route = useRoute()
const router = useRouter()

const showDashboardHeader = computed(() => isAuthenticated.value && route.name === 'home')
const username = computed(() => currentUser.value?.username ?? '')

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

        <button class="logout-button" type="button" @click="signOut">
          <svg viewBox="0 0 24 24" aria-hidden="true" role="presentation">
            <path
              d="M14 7.5V6.75A2.75 2.75 0 0 0 11.25 4h-4.5A2.75 2.75 0 0 0 4 6.75v10.5A2.75 2.75 0 0 0 6.75 20h4.5A2.75 2.75 0 0 0 14 17.25v-.75M10 12h10m0 0-2.75-2.75M20 12l-2.75 2.75"
              fill="none"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.7"
            />
          </svg>
          <span>Logout</span>
        </button>
      </div>
    </header>

    <RouterView />
  </div>
</template>

<style scoped>
.app-shell {
  display: grid;
  gap: 0;
}

.app-navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 0 1.15rem;
  border-bottom: 1px solid rgba(15, 23, 42, 0.1);
}

.brand-mark {
  color: var(--color-heading);
}

.brand-mark strong {
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.03em;
}

.primary-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.72rem 1.1rem;
  border-radius: 14px;
  background: linear-gradient(180deg, #3b6cff, #2f5de6);
  color: #ffffff;
  font-weight: 700;
  box-shadow: 0 14px 28px rgba(47, 93, 230, 0.18);
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.user-chip,
.logout-button {
  font: inherit;
}

.user-chip {
  padding: 0.42rem 0.1rem;
  color: var(--color-text-muted);
  font-size: 0.95rem;
  font-weight: 600;
}

.logout-button {
  border: 0;
  display: inline-flex;
  align-items: center;
  gap: 0.38rem;
  padding: 0.42rem 0.1rem;
  background: transparent;
  color: var(--color-text-muted);
  font-weight: 600;
  cursor: pointer;
}

.logout-button svg {
  width: 1rem;
  height: 1rem;
}

.logout-button:hover,
.logout-button:focus-visible {
  outline: none;
  color: var(--color-heading);
}

@media (max-width: 720px) {
  .app-navbar {
    padding-bottom: 1rem;
    align-items: flex-start;
    flex-direction: column;
  }

  .navbar-actions {
    width: 100%;
  }
}
</style>
