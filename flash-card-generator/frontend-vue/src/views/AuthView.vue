<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { authIsInitializing, consumeAuthFeedback, login, register } from '../services/auth'

const route = useRoute()
const router = useRouter()

const mode = ref<'login' | 'register'>('login')
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const isSubmitting = ref(false)
const errorMessage = ref('')
const infoMessage = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const isRegisterMode = computed(() => mode.value === 'register')

const heading = computed(() => {
  return isRegisterMode.value ? 'Create your account' : 'Sign in to your decks'
})

const subtitle = computed(() => {
  return isRegisterMode.value
    ? 'Create an account to save decks, reopen study sessions, and keep everything attached to your library.'
    : 'Sign in to view your saved decks and continue studying where you left off.'
})

const submitLabel = computed(() => {
  if (isSubmitting.value) {
    return isRegisterMode.value ? 'Creating account...' : 'Signing in...'
  }

  return isRegisterMode.value ? 'Create account' : 'Sign in'
})

const redirectNotice = computed(() => {
  return typeof route.query.redirect === 'string'
    ? 'Sign in to continue to the page you were trying to open.'
    : ''
})

const usernameError = computed(() => {
  const value = username.value.trim()

  if (!value) {
    return 'Enter your username.'
  }

  if (value.length < 3) {
    return 'Username must be at least 3 characters.'
  }

  return ''
})

const passwordError = computed(() => {
  if (!password.value) {
    return 'Enter your password.'
  }

  if (isRegisterMode.value && password.value.length < 8) {
    return 'Password must be at least 8 characters.'
  }

  return ''
})

const confirmPasswordError = computed(() => {
  if (!isRegisterMode.value) {
    return ''
  }

  if (!confirmPassword.value) {
    return 'Confirm your password.'
  }

  if (confirmPassword.value !== password.value) {
    return 'Passwords do not match.'
  }

  return ''
})

const canSubmit = computed(() => {
  return (
    !isSubmitting.value &&
    !authIsInitializing.value &&
    !usernameError.value &&
    !passwordError.value &&
    !confirmPasswordError.value
  )
})

function applyMode(nextMode: 'login' | 'register') {
  mode.value = nextMode
  errorMessage.value = ''
  infoMessage.value = redirectNotice.value
  showPassword.value = false
  showConfirmPassword.value = false

  if (nextMode === 'login') {
    confirmPassword.value = ''
  }
}

async function submitForm() {
  if (!canSubmit.value) {
    errorMessage.value =
      usernameError.value || passwordError.value || confirmPasswordError.value || ''
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    if (isRegisterMode.value) {
      await register(username.value.trim(), password.value)
    } else {
      await login(username.value.trim(), password.value)
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

watch(mode, () => {
  errorMessage.value = ''
})

onMounted(() => {
  infoMessage.value = consumeAuthFeedback() || redirectNotice.value
})
</script>

<template>
  <main class="auth-page">
    <section class="auth-shell">
      <aside class="auth-panel copy-panel">
        <p class="eyebrow">Authentication</p>
        <h1>{{ heading }}</h1>
        <p class="hero-copy">{{ subtitle }}</p>

        <div class="benefit-list">
          <article class="benefit-card">
            <strong>Persistent study library</strong>
            <p>Your decks stay attached to your account and reopen on any session.</p>
          </article>
          <article class="benefit-card">
            <strong>Protected generation flow</strong>
            <p>Deck creation, browsing, and study mode stay private to your account.</p>
          </article>
        </div>
      </aside>

      <section class="auth-panel form-panel">
        <div class="mode-toggle">
          <button
            class="mode-button"
            :class="{ active: !isRegisterMode }"
            type="button"
            @click="applyMode('login')"
          >
            Login
          </button>
          <button
            class="mode-button"
            :class="{ active: isRegisterMode }"
            type="button"
            @click="applyMode('register')"
          >
            Register
          </button>
        </div>

        <p v-if="infoMessage" class="info-banner">{{ infoMessage }}</p>

        <form class="auth-form" @submit.prevent="submitForm">
          <label class="field">
            <span>Username</span>
            <input
              v-model="username"
              type="text"
              autocomplete="username"
              placeholder="Enter your username"
            />
            <small v-if="username && usernameError" class="field-error">{{ usernameError }}</small>
          </label>

          <label class="field">
            <span>Password</span>
            <div class="password-row">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                :autocomplete="isRegisterMode ? 'new-password' : 'current-password'"
                placeholder="Enter your password"
              />
              <button class="toggle-button" type="button" @click="showPassword = !showPassword">
                {{ showPassword ? 'Hide' : 'Show' }}
              </button>
            </div>
            <small v-if="password && passwordError" class="field-error">{{ passwordError }}</small>
          </label>

          <label v-if="isRegisterMode" class="field">
            <span>Confirm password</span>
            <div class="password-row">
              <input
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                autocomplete="new-password"
                placeholder="Re-enter your password"
              />
              <button
                class="toggle-button"
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
              >
                {{ showConfirmPassword ? 'Hide' : 'Show' }}
              </button>
            </div>
            <small
              v-if="confirmPassword && confirmPasswordError"
              class="field-error"
            >
              {{ confirmPasswordError }}
            </small>
          </label>

          <div class="helper-panel">
            <strong>{{ isRegisterMode ? 'Password guidance' : 'Quick note' }}</strong>
            <p>
              {{
                isRegisterMode
                  ? 'Use at least 8 characters. A mix of upper, lower, number, and symbol works best.'
                  : 'Your account uses the same credentials you registered with earlier.'
              }}
            </p>
          </div>

          <button class="primary-button" type="submit" :disabled="!canSubmit">
            {{ submitLabel }}
          </button>

          <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>
        </form>
      </section>
    </section>
  </main>
</template>

<style scoped>
.auth-page {
  min-height: calc(100vh - 120px);
  display: grid;
  place-items: center;
}

.auth-shell {
  width: min(100%, 1080px);
  display: grid;
  gap: 1.25rem;
}

.auth-panel {
  border: 1px solid var(--color-border);
  border-radius: 28px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(244, 247, 252, 0.98)),
    var(--color-surface);
  box-shadow: var(--color-shadow);
}

.copy-panel,
.form-panel {
  padding: 1.5rem;
}

.copy-panel {
  display: grid;
  gap: 1rem;
}

.eyebrow {
  color: var(--color-primary-dark);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.copy-panel h1 {
  font-size: clamp(2rem, 4vw, 3.3rem);
  font-weight: 800;
}

.hero-copy {
  max-width: 46ch;
  color: var(--color-text-muted);
}

.benefit-list {
  display: grid;
  gap: 0.9rem;
}

.benefit-card {
  padding: 1rem 1.05rem;
  border: 1px solid var(--color-border);
  border-radius: 20px;
  background: var(--color-panel);
}

.benefit-card strong {
  display: block;
  margin-bottom: 0.3rem;
  color: var(--color-heading);
  font-weight: 700;
}

.benefit-card p {
  color: var(--color-text-muted);
}

.form-panel {
  display: grid;
  gap: 1rem;
}

.mode-toggle {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.7rem;
  padding: 0.35rem;
  border-radius: 18px;
  background: var(--color-panel);
}

.mode-button {
  border: 0;
  border-radius: 14px;
  padding: 0.85rem 1rem;
  cursor: pointer;
  background: transparent;
  color: var(--color-text-muted);
  font-weight: 700;
}

.mode-button.active {
  background: #ffffff;
  color: var(--color-heading);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
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
  color: var(--color-heading);
  font-weight: 700;
}

.field input {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 1rem 1.05rem;
  background: var(--color-panel);
  color: var(--color-text);
}

.field input:focus {
  outline: none;
  border-color: rgba(47, 93, 230, 0.28);
  box-shadow: 0 0 0 3px rgba(47, 93, 230, 0.1);
}

.password-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.7rem;
}

.toggle-button {
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 0.9rem 1rem;
  cursor: pointer;
  background: #ffffff;
  color: var(--color-heading);
  font-weight: 600;
}

.helper-panel {
  padding: 1rem 1.05rem;
  border: 1px solid var(--color-border);
  border-radius: 18px;
  background: var(--color-panel);
}

.helper-panel strong {
  display: block;
  margin-bottom: 0.25rem;
  color: var(--color-heading);
  font-weight: 700;
}

.helper-panel p {
  color: var(--color-text-muted);
}

.primary-button {
  border: 0;
  border-radius: 16px;
  padding: 1rem 1.2rem;
  cursor: pointer;
  background: linear-gradient(180deg, var(--color-primary), var(--color-primary-dark));
  color: #ffffff;
  font-weight: 700;
  box-shadow: 0 14px 28px rgba(47, 93, 230, 0.2);
}

.primary-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  box-shadow: none;
}

.field-error {
  color: #c24144;
  font-size: 0.92rem;
}

.info-banner,
.error-banner {
  padding: 0.95rem 1rem;
  border-radius: 16px;
}

.info-banner {
  background: #e7eefc;
  color: #2643a3;
}

.error-banner {
  background: #fff1f0;
  color: #c24144;
}

@media (min-width: 900px) {
  .auth-shell {
    grid-template-columns: minmax(0, 1fr) minmax(420px, 0.88fr);
    align-items: stretch;
  }
}

@media (max-width: 640px) {
  .auth-panel {
    padding: 1rem;
  }

  .password-row {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
