import axios from 'axios'
import { computed, ref } from 'vue'

import { api, getApiToken, setApiToken, type AuthUser } from './api'

type AuthResponse = {
  token: string
  user: AuthUser
}

const user = ref<AuthUser | null>(null)
const isInitializing = ref(false)
const initializationAttempted = ref(false)
const AUTH_FEEDBACK_STORAGE_KEY = 'flash-card-generator-auth-feedback'

export const currentUser = computed(() => user.value)
export const isAuthenticated = computed(() => Boolean(user.value))
export const authIsInitializing = computed(() => isInitializing.value)

function setAuthFeedback(message: string) {
  sessionStorage.setItem(AUTH_FEEDBACK_STORAGE_KEY, message)
}

export function consumeAuthFeedback() {
  const message = sessionStorage.getItem(AUTH_FEEDBACK_STORAGE_KEY)

  if (message) {
    sessionStorage.removeItem(AUTH_FEEDBACK_STORAGE_KEY)
  }

  return message
}

export function clearAuthState() {
  setApiToken(null)
  user.value = null
  initializationAttempted.value = true
}

export async function initializeAuth() {
  if (initializationAttempted.value || !getApiToken()) {
    initializationAttempted.value = true
    return
  }

  isInitializing.value = true

  try {
    const { data } = await api.get<{ user: AuthUser }>('/auth/me/')
    user.value = data.user
  } catch {
    clearAuthState()
  } finally {
    initializationAttempted.value = true
    isInitializing.value = false
  }
}

export async function register(username: string, password: string) {
  const { data } = await api.post<AuthResponse>('/auth/register/', { username, password })
  setApiToken(data.token)
  user.value = data.user
  initializationAttempted.value = true
}

export async function login(username: string, password: string) {
  const { data } = await api.post<AuthResponse>('/auth/login/', { username, password })
  setApiToken(data.token)
  user.value = data.user
  initializationAttempted.value = true
}

export async function logout() {
  try {
    await api.post('/auth/logout/')
  } catch (error) {
    if (!axios.isAxiosError(error) || error.response?.status !== 401) {
      throw error
    }
  } finally {
    clearAuthState()
  }
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      axios.isAxiosError(error) &&
      error.response?.status === 401 &&
      getApiToken() &&
      !error.config?.url?.includes('/auth/login/') &&
      !error.config?.url?.includes('/auth/register/') &&
      !error.config?.url?.includes('/auth/logout/')
    ) {
      clearAuthState()
      setAuthFeedback('Your session expired. Please sign in again.')

      if (!window.location.pathname.includes('/auth')) {
        const redirectTarget = `${window.location.pathname}${window.location.search}${window.location.hash}`
        window.location.assign(`/auth?redirect=${encodeURIComponent(redirectTarget)}`)
      }
    }

    return Promise.reject(error)
  },
)
