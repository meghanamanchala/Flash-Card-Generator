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
        <div class="brand-copy">
          <strong>Flash Card Generator</strong>
          <small>Build and review decks</small>
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
  gap: 1.5rem;
}

.app-navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-radius: 28px;
  border: 1px solid var(--color-border);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.94)),
    var(--color-surface);
  box-shadow: var(--color-shadow);
  backdrop-filter: blur(14px);
}

.brand-mark {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: var(--color-heading);
}

.brand-badge {
  display: inline-grid;
  place-items: center;
  width: 3rem;
  height: 3rem;
  border-radius: 18px;
  background: linear-gradient(135deg, #1d4ed8, #335cff);
  color: #eff6ff;
  font-weight: 800;
  letter-spacing: 0.06em;
  box-shadow: 0 14px 30px rgba(51, 92, 255, 0.28);
}

.brand-copy {
  display: grid;
  gap: 0.1rem;
}

.brand-label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--color-primary-dark);
}

.brand-mark strong,
.brand-mark small {
  display: block;
}

.brand-mark strong {
  font-size: 1rem;
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
  padding: 0.78rem 1.05rem;
  border-radius: 999px;
  color: var(--color-text-muted);
  font-weight: 700;
  background: rgba(15, 23, 42, 0.04);
  border: 1px solid transparent;
}

.nav-link.router-link-exact-active {
  background: linear-gradient(135deg, #dbe7ff, #c7d8ff);
  color: #193cb8;
  border-color: rgba(51, 92, 255, 0.14);
  box-shadow: 0 10px 24px rgba(51, 92, 255, 0.14);
}

.user-chip,
.logout-button {
  border-radius: 999px;
  font: inherit;
}

.user-chip {
  padding: 0.72rem 1rem;
  background: rgba(15, 23, 42, 0.05);
  color: var(--color-heading);
  font-weight: 700;
  border: 1px solid rgba(15, 23, 42, 0.05);
}

.logout-button {
  border: 1px solid rgba(15, 23, 42, 0.08);
  padding: 0.72rem 1rem;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.78);
  color: var(--color-heading);
  font-weight: 600;
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
