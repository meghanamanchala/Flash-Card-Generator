<script setup lang="ts">
import axios from 'axios'
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { login, register } from '../services/auth'

const route = useRoute()
const router = useRouter()

const mode = ref<'login' | 'register'>('login')
const username = ref('')
const password = ref('')
const isSubmitting = ref(false)
const errorMessage = ref('')

const heading = computed(() => {
  return mode.value === 'login' ? 'Sign in to your decks' : 'Create your account'
})

const submitLabel = computed(() => {
  return isSubmitting.value
    ? mode.value === 'login'
      ? 'Signing in...'
      : 'Creating account...'
    : mode.value === 'login'
      ? 'Sign in'
      : 'Create account'
})

async function submitForm() {
  isSubmitting.value = true
  errorMessage.value = ''

  try {
    if (mode.value === 'login') {
      await login(username.value.trim(), password.value)
    } else {
      await register(username.value.trim(), password.value)
    }

    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    await router.push(redirect)
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const responseData = error.response?.data
      if (typeof responseData?.detail === 'string') {
        errorMessage.value = responseData.detail
      } else if (typeof responseData?.non_field_errors?.[0] === 'string') {
        errorMessage.value = responseData.non_field_errors[0]
      } else if (typeof responseData?.username?.[0] === 'string') {
        errorMessage.value = responseData.username[0]
      } else if (typeof responseData?.password?.[0] === 'string') {
        errorMessage.value = responseData.password[0]
      } else {
        errorMessage.value = 'Authentication failed. Please check your details and try again.'
      }
    } else {
      errorMessage.value = 'Something went wrong during authentication.'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-card">
      <div class="auth-copy">
        <p class="eyebrow">Account Access</p>
        <h1>{{ heading }}</h1>
        <p>Sign in to view your saved flashcard decks, or create an account to start building them.</p>
      </div>

      <div class="mode-toggle">
        <button
          class="mode-button"
          :class="{ active: mode === 'login' }"
          type="button"
          @click="mode = 'login'"
        >
          Login
        </button>
        <button
          class="mode-button"
          :class="{ active: mode === 'register' }"
          type="button"
          @click="mode = 'register'"
        >
          Register
        </button>
      </div>

      <form class="auth-form" @submit.prevent="submitForm">
        <label class="field">
          <span>Username</span>
          <input v-model="username" type="text" autocomplete="username" placeholder="Enter your username" />
        </label>

        <label class="field">
          <span>Password</span>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="Enter your password"
          />
        </label>

        <button class="primary-button" type="submit" :disabled="isSubmitting">
          {{ submitLabel }}
        </button>

        <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>
      </form>
    </section>
  </main>
</template>

<style scoped>
.auth-page {
  display: grid;
  place-items: center;
  min-height: calc(100vh - 180px);
}

.auth-card {
  width: min(100%, 560px);
  display: grid;
  gap: 1.25rem;
  padding: 1.5rem;
  border-radius: 30px;
  border: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 18px 50px rgba(44, 28, 84, 0.1);
}

.eyebrow {
  font-size: 0.78rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.auth-copy h1 {
  margin: 0.45rem 0 0.35rem;
  color: var(--color-heading);
}

.auth-copy p:last-child {
  color: var(--color-text-muted);
}

.mode-toggle {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.mode-button,
.primary-button {
  border: 0;
  border-radius: 999px;
  font: inherit;
}

.mode-button {
  padding: 0.8rem 1rem;
  cursor: pointer;
  background: rgba(79, 70, 229, 0.08);
  color: var(--color-heading);
}

.mode-button.active {
  background: linear-gradient(135deg, #dbeafe, #c7d2fe);
  color: #312e81;
}

.auth-form {
  display: grid;
  gap: 1rem;
}

.field {
  display: grid;
  gap: 0.45rem;
}

.field span {
  font-weight: 600;
  color: var(--color-heading);
}

.field input {
  width: 100%;
  border: 1px solid rgba(63, 63, 70, 0.12);
  border-radius: 18px;
  padding: 1rem 1.05rem;
  background: rgba(255, 255, 255, 0.9);
  font: inherit;
  color: var(--color-text);
}

.field input:focus {
  outline: none;
  border-color: rgba(79, 70, 229, 0.45);
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.12);
}

.primary-button {
  padding: 0.95rem 1.25rem;
  cursor: pointer;
  background: linear-gradient(135deg, #7dd3fc, #4f46e5);
  color: #eef2ff;
  box-shadow: 0 16px 34px rgba(79, 70, 229, 0.24);
}

.primary-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.error-banner {
  border-radius: 18px;
  padding: 0.95rem 1rem;
  background: rgba(220, 38, 38, 0.08);
  color: #991b1b;
}
</style>
