import axios from 'axios'

export type Flashcard = {
  id: number
  question: string
  answer: string
  content: string
  order: number
  created_at: string
}

export type LearningUnit = {
  id: number
  title: string
  raw_content: string
  max_flashcards: number
  last_studied_at: string | null
  generated_flashcards_count: number
  created_at: string
  updated_at: string
  flashcards: Flashcard[]
}

export type GenerateResponse = {
  learning_unit_id: number
  title: string
  max_flashcards: number
  flashcards: Flashcard[]
}

export type ReviewFlashcardInput = {
  question: string
  answer: string
  content: string
}

export type AuthUser = {
  id: number
  username: string
}

export const MAX_FLASHCARDS_LIMIT = 20
export const AUTH_TOKEN_STORAGE_KEY = 'flash-card-generator-token'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
})

let authToken = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY)

export function setApiToken(token: string | null) {
  authToken = token

  if (token) {
    localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, token)
  } else {
    localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY)
  }
}

export function getApiToken() {
  return authToken
}

api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`
  }

  return config
})
