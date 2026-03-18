<script setup lang="ts">
import axios from 'axios'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { api, MAX_FLASHCARDS_LIMIT } from '../services/api'

const router = useRouter()

const title = ref('')
const rawContent = ref('')
const maxFlashcards = ref(8)
const isSubmitting = ref(false)
const errorMessage = ref('')

const wordCount = computed(() => {
  const content = rawContent.value.trim()
  return content ? content.split(/\s+/).length : 0
})

const canSubmit = computed(() => {
  return title.value.trim().length > 0 && rawContent.value.trim().length >= 20 && !isSubmitting.value
})

const helperText = computed(() => {
  if (!wordCount.value) {
    return 'Paste your notes or lesson summary to start.'
  }

  return `${wordCount.value} words ready for generation.`
})

async function createDeck() {
  if (!canSubmit.value) {
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const learningUnitResponse = await api.post('/learning-units/', {
      title: title.value.trim(),
      raw_content: rawContent.value.trim(),
      max_flashcards: maxFlashcards.value,
    })

    const learningUnitId = learningUnitResponse.data.id as number

    await api.post(`/learning-units/${learningUnitId}/generate-cards/`)

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
  }
}
</script>

<template>
  <main class="create-page">
    <RouterLink class="text-link top-link" to="/">Back to dashboard</RouterLink>

    <section class="editor-shell">
      <form class="editor-panel" @submit.prevent="createDeck">
        <div class="section-head">
          <h2>New flashcard set</h2>
          <p>The deck title, source content, and generated cards will be stored in the backend database.</p>
        </div>

        <label class="field">
          <span>Deck title</span>
          <input
            v-model="title"
            type="text"
            maxlength="255"
            placeholder="Example: Human digestive system"
          />
        </label>

        <label class="field">
          <span>Content to turn into flashcards</span>
          <textarea
            v-model="rawContent"
            rows="14"
            placeholder="Paste textbook notes, a chapter summary, or lecture content here..."
          />
        </label>

        <label class="field">
          <span>How many flashcards do you need?</span>
          <input v-model.number="maxFlashcards" type="range" min="1" :max="MAX_FLASHCARDS_LIMIT" />
          <div class="range-meta">
            <strong>{{ maxFlashcards }} cards</strong>
            <span>Maximum allowed: {{ MAX_FLASHCARDS_LIMIT }}</span>
          </div>
        </label>

        <div class="form-actions">
          <button class="primary-button" type="submit" :disabled="!canSubmit">
            {{ isSubmitting ? 'Creating deck...' : 'Generate and open deck' }}
          </button>
        </div>

        <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>
      </form>

      <aside class="side-panel">
        <div class="metric-card">
          <span class="metric-label">Word count</span>
          <strong>{{ wordCount }}</strong>
          <p>{{ helperText }}</p>
        </div>
        <div class="metric-card accent">
          <span class="metric-label">Stored data</span>
          <strong>Title + source + cards</strong>
          <p>Each generated deck is saved, so you can return from the dashboard later.</p>
        </div>
      </aside>
    </section>
  </main>
</template>

<style scoped>
.create-page {
  display: grid;
  gap: 1.5rem;
}

.editor-panel,
.side-panel {
  border-radius: 28px;
  border: 1px solid var(--color-border);
  box-shadow: 0 18px 50px rgba(120, 98, 77, 0.08);
}

.text-link {
  color: var(--color-heading);
}

.top-link {
  justify-self: start;
  font-weight: 600;
}

.editor-shell {
  display: grid;
  gap: 1.5rem;
}

.editor-panel,
.side-panel {
  background: rgba(255, 250, 243, 0.78);
}

.editor-panel {
  padding: 1.4rem;
}

.section-head {
  margin-bottom: 1.2rem;
}

.section-head h2 {
  margin-bottom: 0.35rem;
  color: var(--color-heading);
}

.section-head p {
  color: var(--color-text-muted);
}

.field {
  display: grid;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.field span {
  font-weight: 600;
  color: var(--color-heading);
}

.field input,
.field textarea {
  width: 100%;
  border: 1px solid rgba(63, 63, 70, 0.12);
  border-radius: 18px;
  padding: 1rem 1.05rem;
  background: rgba(255, 255, 255, 0.9);
  font: inherit;
  color: var(--color-text);
}

.field textarea {
  min-height: 280px;
  resize: vertical;
}

.field input:focus,
.field textarea:focus {
  outline: none;
  border-color: rgba(79, 70, 229, 0.45);
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.12);
}

.field input[type='range'] {
  padding: 0;
}

.range-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  color: var(--color-text-muted);
}

.range-meta strong {
  color: var(--color-heading);
}

.form-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.side-panel {
  display: grid;
  gap: 1rem;
  padding: 1.25rem;
}

.metric-card {
  padding: 1rem;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(17, 24, 39, 0.08);
}

.metric-card.accent {
  background: linear-gradient(135deg, rgba(236, 243, 255, 0.98), rgba(216, 239, 247, 0.82));
}

.metric-label {
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.78rem;
}

.metric-card strong {
  display: block;
  margin: 0.3rem 0 0.35rem;
  color: var(--color-heading);
  font-size: 1.3rem;
}

.primary-button {
  border: 0;
  border-radius: 999px;
  padding: 0.9rem 1.25rem;
  cursor: pointer;
  font: inherit;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    background 0.2s ease;
}

.primary-button {
  background: linear-gradient(135deg, #7dd3fc, #4f46e5);
  color: #eef2ff;
  box-shadow: 0 16px 34px rgba(79, 70, 229, 0.24);
}

.primary-button:hover {
  transform: translateY(-1px);
}

.primary-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none;
}

.error-banner {
  margin-top: 1rem;
  border-radius: 18px;
  padding: 0.95rem 1rem;
  background: rgba(220, 38, 38, 0.08);
  color: #991b1b;
}

@media (min-width: 920px) {
  .editor-shell {
    grid-template-columns: minmax(0, 1.3fr) minmax(290px, 0.7fr);
    align-items: start;
  }
}

@media (max-width: 640px) {
  .range-meta,
  .form-actions {
    align-items: start;
    flex-direction: column;
  }
}
</style>
