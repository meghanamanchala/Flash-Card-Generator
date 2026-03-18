import axios from 'axios'

export type Flashcard = {
  id: number
  content: string
  order: number
  created_at: string
}

export type LearningUnit = {
  id: number
  title: string
  raw_content: string
  max_flashcards: number
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

export const MAX_FLASHCARDS_LIMIT = 20

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
})
