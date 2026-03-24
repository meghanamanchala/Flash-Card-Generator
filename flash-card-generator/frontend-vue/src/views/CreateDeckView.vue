<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import {
  api,
  MAX_FLASHCARDS_LIMIT,
  type Flashcard,
  type GenerateResponse,
  type LearningUnit,
  type ReviewFlashcardInput,
} from '../services/api'

const router = useRouter()
const route = useRoute()
const DRAFT_STORAGE_KEY = 'flash-card-generator-create-draft'

const SAMPLE_TITLE = 'Cell Biology Fundamentals'
const SAMPLE_CONTENT = `Cells rely on specialized organelles to stay alive and perform complex work. The nucleus stores genetic information and coordinates many cell activities. Mitochondria are often called the powerhouses of the cell because they generate ATP, which provides usable energy. Ribosomes build proteins by translating genetic instructions. The endoplasmic reticulum helps process proteins and lipids, while the Golgi apparatus modifies, packages, and ships materials where they are needed.`

const title = ref('')
const rawContent = ref('')
const maxFlashcards = ref(8)
const isSubmitting = ref(false)
const errorMessage = ref('')
const submitStage = ref<'idle' | 'saving' | 'generating'>('idle')
const currentStep = ref<'editing' | 'review'>('editing')
const reviewDeckId = ref<number | null>(null)
const isFinishingReview = ref(false)
const isLoadingExistingDeck = ref(false)

type ReviewCard = Flashcard & {
  keep: boolean
  score: number
}

const wordCount = computed(() => {
  const content = rawContent.value.trim()
  return content ? content.split(/\s+/).length : 0
})

const canSubmit = computed(() => {
  return (
    title.value.trim().length > 0 &&
    rawContent.value.trim().length >= 20 &&
    !isSubmitting.value &&
    !isLoadingExistingDeck.value
  )
})

const editingDeckId = computed(() => {
  const rawDeckId = route.query.deckId
  const parsed = Number(Array.isArray(rawDeckId) ? rawDeckId[0] : rawDeckId)

  if (!Number.isFinite(parsed) || parsed <= 0) {
    return null
  }

  return parsed
})

const isEditingExistingDeck = computed(() => editingDeckId.value !== null)

const submitLabel = computed(() => {
  if (!isSubmitting.value) {
    return isEditingExistingDeck.value ? 'Regenerate Deck' : 'Generate Deck'
  }

  return submitStage.value === 'saving' ? 'Saving...' : 'Generating...'
})

const helperCopy = computed(() => {
  if (!rawContent.value.trim()) {
    return 'Paste your learning content here.'
  }

  return `${wordCount.value} words ready, up to ${maxFlashcards.value} cards.`
})

const reviewCards = ref<ReviewCard[]>([])

const keptCards = computed(() => {
  return reviewCards.value.filter((card) => {
    return card.keep && card.question.trim().length > 0 && card.answer.trim().length > 0
  })
})

const canFinishReview = computed(() => {
  return reviewDeckId.value !== null && keptCards.value.length > 0 && !isFinishingReview.value
})

const reviewSummary = computed(() => {
  const keptCount = keptCards.value.length
  const totalCount = reviewCards.value.length
  return `Draft cards — ${keptCount} kept${totalCount ? ` of ${totalCount}` : ''}`
})

const pageTitle = computed(() => {
  if (currentStep.value === 'review') {
    return 'Review Cards'
  }

  return isEditingExistingDeck.value ? 'Edit Deck' : 'New Deck'
})

function buildReviewCards(flashcards: Flashcard[]) {
  return flashcards.map((flashcard, index) => ({
    ...flashcard,
    keep: true,
    score: 88 + ((flashcard.question.length + flashcard.answer.length + index * 5) % 10),
  }))
}

function persistDraft() {
  if (isEditingExistingDeck.value) {
    return
  }

  localStorage.setItem(
    DRAFT_STORAGE_KEY,
    JSON.stringify({
      title: title.value,
      rawContent: rawContent.value,
      maxFlashcards: maxFlashcards.value,
    }),
  )
}

function fillSampleText() {
  title.value = SAMPLE_TITLE
  rawContent.value = SAMPLE_CONTENT
}

function returnToEditing() {
  currentStep.value = 'editing'
  errorMessage.value = ''
}

function toggleKeep(cardId: number) {
  reviewCards.value = reviewCards.value.map((card) =>
    card.id === cardId
      ? {
          ...card,
          keep: !card.keep,
        }
      : card,
  )
}

function buildReviewPayload(): ReviewFlashcardInput[] {
  return keptCards.value.map((card) => ({
    question: card.question.trim(),
    answer: card.answer.trim(),
    content: card.content.trim() || `${card.question.trim()} ${card.answer.trim()}`,
  }))
}

function hydrateEditorState(deck: LearningUnit) {
  title.value = deck.title
  rawContent.value = deck.raw_content
  maxFlashcards.value = Math.min(
    MAX_FLASHCARDS_LIMIT,
    Math.max(1, deck.max_flashcards ?? maxFlashcards.value),
  )
  reviewDeckId.value = deck.id
  reviewCards.value = deck.flashcards.length ? buildReviewCards(deck.flashcards) : []
  currentStep.value = 'editing'
}

async function loadExistingDeck(deckId: number) {
  isLoadingExistingDeck.value = true
  errorMessage.value = ''

  try {
    const { data } = await api.get<LearningUnit>(`/learning-units/${deckId}/`)
    hydrateEditorState(data)
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errorMessage.value = error.response?.data?.detail || 'This deck could not be opened for editing.'
    } else {
      errorMessage.value = 'Something went wrong while loading the deck editor.'
    }
  } finally {
    isLoadingExistingDeck.value = false
  }
}

function restoreDraft() {
  reviewDeckId.value = null
  currentStep.value = 'editing'
  reviewCards.value = []

  const savedDraft = localStorage.getItem(DRAFT_STORAGE_KEY)

  if (!savedDraft) {
    title.value = ''
    rawContent.value = ''
    maxFlashcards.value = 8
    return
  }

  try {
    const parsedDraft = JSON.parse(savedDraft) as {
      title?: string
      rawContent?: string
      maxFlashcards?: number
    }

    title.value = parsedDraft.title ?? ''
    rawContent.value = parsedDraft.rawContent ?? ''
    maxFlashcards.value = Math.min(
      MAX_FLASHCARDS_LIMIT,
      Math.max(1, parsedDraft.maxFlashcards ?? maxFlashcards.value),
    )
  } catch {
    localStorage.removeItem(DRAFT_STORAGE_KEY)
  }
}

async function createDeck() {
  if (!canSubmit.value) {
    return
  }

  isSubmitting.value = true
  submitStage.value = 'saving'
  errorMessage.value = ''

  try {
    const payload = {
      title: title.value.trim(),
      raw_content: rawContent.value.trim(),
      max_flashcards: Math.min(MAX_FLASHCARDS_LIMIT, Math.max(1, maxFlashcards.value)),
    }

    let learningUnitId = reviewDeckId.value

    if (learningUnitId === null) {
      const learningUnitResponse = await api.post('/learning-units/', payload)
      learningUnitId = learningUnitResponse.data.id as number
    } else {
      await api.patch(`/learning-units/${learningUnitId}/`, payload)
    }

    submitStage.value = 'generating'
    const { data } = await api.post<GenerateResponse>(`/learning-units/${learningUnitId}/generate-cards/`)
    reviewDeckId.value = learningUnitId
    reviewCards.value = buildReviewCards(data.flashcards)
    currentStep.value = 'review'
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errorMessage.value =
        error.response?.data?.detail ||
        'The deck could not be created right now. Please try again with more complete content.'
    } else {
      errorMessage.value = 'Something went wrong while saving the deck.'
    }
  } finally {
    isSubmitting.value = false
    submitStage.value = 'idle'
  }
}

async function finishDeck() {
  if (!canFinishReview.value || reviewDeckId.value === null) {
    return
  }

  isFinishingReview.value = true
  errorMessage.value = ''

  try {
    await api.post(`/learning-units/${reviewDeckId.value}/review-cards/`, {
      flashcards: buildReviewPayload(),
    })
    localStorage.removeItem(DRAFT_STORAGE_KEY)

    await router.push({
      name: 'deck',
      params: { id: reviewDeckId.value.toString() },
    })
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errorMessage.value =
        error.response?.data?.detail ||
        'The reviewed cards could not be saved right now. Please try again.'
    } else {
      errorMessage.value = 'Something went wrong while finishing the deck.'
    }
  } finally {
    isFinishingReview.value = false
  }
}

onMounted(() => {
  if (editingDeckId.value !== null) {
    void loadExistingDeck(editingDeckId.value)
    return
  }

  restoreDraft()
})

watch([title, rawContent, maxFlashcards], () => {
  persistDraft()
})

watch(
  () => editingDeckId.value,
  (deckId) => {
    if (deckId !== null) {
      void loadExistingDeck(deckId)
      return
    }

    restoreDraft()
  },
)
</script>

<template>
  <main class="create-page">
    <section class="create-frame">
      <header class="page-bar">
        <button v-if="currentStep === 'review'" class="back-link button-reset" type="button" @click="returnToEditing">
          <span aria-hidden="true">←</span>
          <span>{{ pageTitle }}</span>
        </button>
        <RouterLink v-else class="back-link" to="/">
          <span aria-hidden="true">←</span>
          <span>{{ pageTitle }}</span>
        </RouterLink>
      </header>

      <form v-if="currentStep === 'editing'" class="editor-shell" @submit.prevent="createDeck">
        <div class="editor-stack">
          <label class="title-field">
            <span class="sr-only">Deck title</span>
            <input v-model="title" type="text" maxlength="255" placeholder="Deck title" />
          </label>

          <label class="content-field">
            <span class="sr-only">Learning content</span>
            <textarea
              v-model="rawContent"
              rows="14"
              placeholder="Paste your learning content here — articles, notes, textbook excerpts..."
            />
          </label>

          <div class="controls-row">
            <div class="slider-panel">
              <div class="slider-copy">
                <strong>{{ maxFlashcards }} cards</strong>
                <span>{{ helperCopy }}</span>
              </div>
              <input
                v-model.number="maxFlashcards"
                class="slider-input"
                type="range"
                min="1"
                :max="MAX_FLASHCARDS_LIMIT"
              />
            </div>

            <div class="action-row">
              <button class="sample-button" type="button" @click="fillSampleText">
                Try Sample Text
                <span aria-hidden="true">→</span>
              </button>
              <button class="primary-button" type="submit" :disabled="!canSubmit">
                {{ submitLabel }}
              </button>
            </div>
          </div>

          <p v-if="isLoadingExistingDeck" class="editor-note">Loading deck details...</p>
          <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>
        </div>
      </form>

      <section v-else class="review-shell">
        <div class="review-grid">
          <aside class="source-panel">
            <p class="review-label">Source</p>
            <div class="source-copy">
              {{ rawContent }}
            </div>
          </aside>

          <div class="review-column">
            <div class="review-header">
              <div class="review-header-copy">
                <p class="review-label">{{ reviewSummary }}</p>
                <p class="review-help">Check the generated cards, edit anything unclear, then finish the deck.</p>
              </div>

              <button class="primary-button finish-button" type="button" :disabled="!canFinishReview" @click="finishDeck">
                {{ isFinishingReview ? 'Finishing...' : 'Finish Deck →' }}
              </button>
            </div>

            <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>

            <div class="review-list">
              <article
                v-for="(card, index) in reviewCards"
                :key="card.id"
                class="review-card"
                :class="{ discarded: !card.keep }"
              >
                <div class="review-card-header">
                  <span class="score-pill">{{ card.score }}%</span>
                  <button
                    class="keep-toggle"
                    :class="{ active: card.keep }"
                    type="button"
                    @click="toggleKeep(card.id)"
                  >
                    {{ card.keep ? 'Kept' : 'Discard' }}
                  </button>
                </div>

                <label class="review-field">
                  <span>Question {{ index + 1 }}</span>
                  <textarea v-model="card.question" rows="2" :disabled="!card.keep" />
                </label>

                <label class="review-field">
                  <span>Answer</span>
                  <textarea v-model="card.answer" rows="3" :disabled="!card.keep" />
                </label>

                <p v-if="card.content" class="review-source-note">{{ card.content }}</p>
              </article>
            </div>
          </div>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.create-page {
  display: grid;
}

.create-frame {
  min-height: calc(100vh - 120px);
}

.page-bar {
  padding: 0.95rem 0 1rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--color-heading);
  font-size: 1.05rem;
  font-weight: 600;
}

.button-reset {
  padding: 0;
  border: 0;
  background: transparent;
}

.editor-shell {
  display: grid;
  place-items: center;
  padding: 2.5rem 0 3rem;
}

.editor-stack {
  width: min(100%, 900px);
  display: grid;
  gap: 1.5rem;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

.title-field input,
.content-field textarea {
  width: 100%;
  border: 1px solid transparent;
  border-radius: 22px;
  color: var(--color-heading);
  background: var(--color-panel);
}

.title-field input {
  padding: 0.2rem 0;
  background: transparent;
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 700;
  letter-spacing: -0.05em;
}

.content-field textarea {
  min-height: 350px;
  padding: 1.35rem 1.2rem;
  resize: vertical;
  font-size: 1.05rem;
  line-height: 1.7;
  border-color: rgba(15, 23, 42, 0.08);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.75);
}

.title-field input:focus,
.content-field textarea:focus,
.slider-input:focus {
  outline: none;
}

.content-field textarea:focus {
  border-color: rgba(47, 93, 230, 0.24);
  box-shadow: 0 0 0 3px rgba(47, 93, 230, 0.1);
}

.controls-row {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.slider-panel {
  min-width: 280px;
  display: grid;
  gap: 0.55rem;
}

.slider-copy {
  display: grid;
  gap: 0.15rem;
}

.slider-copy strong {
  color: var(--color-heading);
  font-size: 1rem;
  font-weight: 700;
}

.slider-copy span {
  color: var(--color-text-muted);
  font-size: 0.95rem;
}

.slider-input {
  accent-color: var(--color-primary);
}

.action-row {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-wrap: wrap;
}

.sample-button,
.primary-button {
  border: 0;
  border-radius: 16px;
  padding: 0.95rem 1.25rem;
  cursor: pointer;
  font-weight: 700;
}

.sample-button {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  background: var(--color-panel-strong);
  color: var(--color-primary-dark);
  border: 1px solid rgba(47, 93, 230, 0.12);
}

.primary-button {
  background: linear-gradient(180deg, #3b6cff, #2f5de6);
  color: #ffffff;
  box-shadow: 0 14px 28px rgba(47, 93, 230, 0.18);
}

.primary-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  box-shadow: none;
}

.error-banner {
  padding: 0.95rem 1rem;
  border-radius: 16px;
  background: #fff1f0;
  color: #c24144;
}

.editor-note {
  color: var(--color-text-muted);
  font-size: 0.95rem;
}

.review-shell {
  padding: 1.75rem 0 2rem;
}

.review-grid {
  display: grid;
  gap: 1.5rem;
}

.source-panel,
.review-card {
  border: 1px solid var(--color-border);
  border-radius: 22px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(242, 246, 252, 0.94)),
    var(--color-surface);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
}

.source-panel {
  padding: 1.25rem;
}

.review-label {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.source-copy {
  max-height: 720px;
  margin-top: 1rem;
  overflow: auto;
  color: var(--color-heading);
  font-size: 1.05rem;
  line-height: 1.95;
  white-space: pre-wrap;
}

.review-column {
  display: grid;
  gap: 1rem;
}

.review-header {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.review-header-copy {
  display: grid;
  gap: 0.4rem;
}

.review-help {
  margin: 0;
  color: var(--color-text-muted);
}

.finish-button {
  min-width: 180px;
}

.review-list {
  display: grid;
  gap: 1rem;
}

.review-card {
  display: grid;
  gap: 0.9rem;
  padding: 1.2rem;
}

.review-card.discarded {
  opacity: 0.56;
}

.review-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.score-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 3.25rem;
  padding: 0.35rem 0.55rem;
  border-radius: 10px;
  background: rgba(34, 197, 94, 0.12);
  color: #15803d;
  font-size: 0.9rem;
  font-weight: 700;
}

.keep-toggle {
  border: 1px solid var(--color-border);
  border-radius: 999px;
  padding: 0.5rem 0.85rem;
  background: rgba(15, 23, 42, 0.03);
  color: var(--color-text-muted);
  font-weight: 700;
  cursor: pointer;
}

.keep-toggle.active {
  background: rgba(34, 197, 94, 0.12);
  color: #15803d;
  border-color: rgba(34, 197, 94, 0.18);
}

.review-field {
  display: grid;
  gap: 0.45rem;
}

.review-field span {
  color: var(--color-heading);
  font-size: 0.9rem;
  font-weight: 700;
}

.review-field textarea {
  width: 100%;
  resize: vertical;
  border: 1px solid rgba(15, 23, 42, 0.1);
  border-radius: 16px;
  padding: 0.95rem 1rem;
  background: var(--color-panel);
  color: var(--color-heading);
  font-size: 1rem;
  line-height: 1.65;
}

.review-field textarea:focus {
  outline: none;
  border-color: rgba(47, 93, 230, 0.24);
  box-shadow: 0 0 0 3px rgba(47, 93, 230, 0.1);
}

.review-field textarea:disabled {
  cursor: not-allowed;
}

.review-source-note {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.92rem;
  line-height: 1.7;
}

@media (min-width: 980px) {
  .review-grid {
    grid-template-columns: minmax(280px, 0.42fr) minmax(0, 0.58fr);
    align-items: start;
  }

  .source-panel {
    position: sticky;
    top: 1rem;
  }
}

@media (max-width: 720px) {
  .editor-shell {
    padding: 1.6rem 0 2rem;
  }

  .content-field textarea {
    min-height: 280px;
  }

  .controls-row,
  .action-row {
    align-items: stretch;
    flex-direction: column;
  }

  .slider-panel {
    min-width: 100%;
  }

  .sample-button,
  .primary-button {
    width: 100%;
    justify-content: center;
  }

  .review-shell {
    padding: 1rem 0;
  }

  .review-header {
    align-items: stretch;
  }

  .finish-button {
    width: 100%;
  }
}
</style>
