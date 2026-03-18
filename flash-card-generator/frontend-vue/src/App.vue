<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'

import { currentUser, isAuthenticated, logout } from './services/auth'

const router = useRouter()

const username = computed(() => currentUser.value?.username ?? '')

async function signOut() {
  await logout()
  await router.push({ name: 'auth' })
}
</script>

<template>
  <div class="app-shell">
    <header class="app-navbar">
      <RouterLink class="brand-mark" to="/">
        <span class="brand-badge">FC</span>
        <div>
          <strong>Flash Card Generator</strong>
          <small>Study deck workspace</small>
        </div>
      </RouterLink>

      <nav class="nav-links" aria-label="Main navigation">
        <RouterLink v-if="isAuthenticated" class="nav-link" to="/">Dashboard</RouterLink>
        <RouterLink v-if="isAuthenticated" class="nav-link" to="/create">Create Deck</RouterLink>
        <RouterLink v-if="!isAuthenticated" class="nav-link" to="/auth">Login</RouterLink>
      </nav>

      <div v-if="isAuthenticated" class="nav-account">
        <span class="user-chip">{{ username }}</span>
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
  padding: 1rem 1.2rem;
  border-radius: 24px;
  border: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.74);
  box-shadow: 0 14px 40px rgba(44, 28, 84, 0.08);
  backdrop-filter: blur(14px);
}

.brand-mark {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  color: var(--color-heading);
}

.brand-badge {
  display: inline-grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 16px;
  background: linear-gradient(135deg, #93c5fd, #4f46e5);
  color: #eff6ff;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.brand-mark strong,
.brand-mark small {
  display: block;
}

.brand-mark strong {
  font-size: 0.98rem;
}

.brand-mark small {
  color: var(--color-text-muted);
  font-size: 0.84rem;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  flex-wrap: wrap;
}

.nav-account {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  flex-wrap: wrap;
}

.nav-link {
  padding: 0.72rem 1rem;
  border-radius: 999px;
  color: var(--color-heading);
  font-weight: 600;
  background: rgba(79, 70, 229, 0.06);
}

.nav-link.router-link-exact-active {
  background: linear-gradient(135deg, #dbeafe, #c7d2fe);
  color: #312e81;
}

.user-chip,
.logout-button {
  border-radius: 999px;
  font: inherit;
}

.user-chip {
  padding: 0.72rem 1rem;
  background: rgba(79, 70, 229, 0.08);
  color: var(--color-heading);
  font-weight: 600;
}

.logout-button {
  border: 0;
  padding: 0.72rem 1rem;
  cursor: pointer;
  background: rgba(17, 24, 39, 0.06);
  color: var(--color-heading);
}

@media (max-width: 640px) {
  .app-navbar {
    align-items: start;
    flex-direction: column;
  }

  .nav-links {
    width: 100%;
  }

  .nav-account {
    width: 100%;
  }
}
</style>
