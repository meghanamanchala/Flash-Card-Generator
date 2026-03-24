<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { api, MAX_FLASHCARDS_LIMIT } from '../services/api'

const router = useRouter()
const DRAFT_STORAGE_KEY = 'flash-card-generator-create-draft'

const SAMPLE_TITLE = 'Cell Biology Fundamentals'
const SAMPLE_CONTENT = `Cells rely on specialized organelles to stay alive and perform complex work. The nucleus stores genetic information and coordinates many cell activities. Mitochondria are often called the powerhouses of the cell because they generate ATP, which provides usable energy. Ribosomes build proteins by translating genetic instructions. The endoplasmic reticulum helps process proteins and lipids, while the Golgi apparatus modifies, packages, and ships materials where they are needed.`

const title = ref('')
const rawContent = ref('')
const maxFlashcards = ref(8)
const isSubmitting = ref(false)
const errorMessage = ref('')
const submitStage = ref<'idle' | 'saving' | 'generating'>('idle')

const wordCount = computed(() => {
  const content = rawContent.value.trim()
  return content ? content.split(/\s+/).length : 0
})

const canSubmit = computed(() => {
  return title.value.trim().length > 0 && rawContent.value.trim().length >= 20 && !isSubmitting.value
})

const submitLabel = computed(() => {
  if (!isSubmitting.value) {
    return 'Generate Deck'
  }

  return submitStage.value === 'saving' ? 'Saving...' : 'Generating...'
})

const helperCopy = computed(() => {
  if (!rawContent.value.trim()) {
    return 'Paste your learning content here.'
  }

  return `${wordCount.value} words ready, up to ${maxFlashcards.value} cards.`
})

function persistDraft() {
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

async function createDeck() {
  if (!canSubmit.value) {
    return
  }

  isSubmitting.value = true
  submitStage.value = 'saving'
  errorMessage.value = ''

  try {
    const learningUnitResponse = await api.post('/learning-units/', {
      title: title.value.trim(),
      raw_content: rawContent.value.trim(),
      max_flashcards: Math.min(MAX_FLASHCARDS_LIMIT, Math.max(1, maxFlashcards.value)),
    })

    const learningUnitId = learningUnitResponse.data.id as number

    submitStage.value = 'generating'
    await api.post(`/learning-units/${learningUnitId}/generate-cards/`)
    localStorage.removeItem(DRAFT_STORAGE_KEY)

    await router.push({
      name: 'deck',
      params: { id: learningUnitId.toString() },
    })
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

onMounted(() => {
  const savedDraft = localStorage.getItem(DRAFT_STORAGE_KEY)

  if (!savedDraft) {
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
})

watch([title, rawContent, maxFlashcards], () => {
  persistDraft()
})
</script>

<template>
  <main class="create-page">
    <section class="create-frame">
      <header class="page-bar">
        <RouterLink class="back-link" to="/">
          <span aria-hidden="true">←</span>
          <span>New Deck</span>
        </RouterLink>
      </header>

      <form class="editor-shell" @submit.prevent="createDeck">
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

          <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>
        </div>
      </form>
    </section>
  </main>
</template>

<style scoped>
.create-page {
  display: grid;
}

.create-frame {
  min-height: calc(100vh - 120px);
  border: 1px solid var(--color-border);
  border-radius: 28px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(245, 247, 252, 0.98)),
    var(--color-surface);
  box-shadow: var(--color-shadow);
}

.page-bar {
  padding: 0.95rem 1.4rem;
  border-bottom: 1px solid var(--color-border);
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--color-heading);
  font-size: 1.05rem;
  font-weight: 600;
}

.editor-shell {
  display: grid;
  place-items: center;
  padding: 2.5rem 1.25rem 3rem;
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

@media (max-width: 720px) {
  .editor-shell {
    padding: 1.6rem 1rem 2rem;
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
}
</style>
