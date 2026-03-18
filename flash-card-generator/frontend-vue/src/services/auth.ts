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

export const currentUser = computed(() => user.value)
export const isAuthenticated = computed(() => Boolean(user.value))

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
    setApiToken(null)
    user.value = null
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
    setApiToken(null)
    user.value = null
    initializationAttempted.value = true
  }
}
