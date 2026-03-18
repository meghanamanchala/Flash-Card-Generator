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
          <h2>New deck</h2>
          <p>Save the title, source text, and generated cards together for later review.</p>
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
          <div class="metric-head">
            <span class="metric-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" role="presentation">
                <path
                  d="M7 6.75A1.75 1.75 0 0 1 8.75 5h6.5A1.75 1.75 0 0 1 17 6.75v10.5A1.75 1.75 0 0 1 15.25 19h-6.5A1.75 1.75 0 0 1 7 17.25Z"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                />
                <path d="M10 9h4M10 12h4M10 15h2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
              </svg>
            </span>
            <span class="metric-label">Word count</span>
          </div>
          <strong>{{ wordCount }}</strong>
          <p>{{ helperText }}</p>
        </div>
      </aside>
    </section>
  </main>
</template>

<style scoped>
.create-page {
  display: grid;
  gap: 1.6rem;
}

.create-hero,
.editor-panel,
.side-panel {
  border-radius: 28px;
  border: 1px solid var(--color-border);
  box-shadow: var(--color-shadow);
}

.text-link {
  color: var(--color-heading);
}

.top-link {
  justify-self: start;
  font-weight: 600;
}

.create-hero {
  display: grid;
  gap: 1.25rem;
  padding: 1.5rem;
  background:
    radial-gradient(circle at top right, rgba(51, 92, 255, 0.14), transparent 23%),
    linear-gradient(135deg, #ffffff, #f6f9ff 55%, #eef4ff);
}

.hero-copy {
  display: grid;
  gap: 0.7rem;
  max-width: 58ch;
}

.eyebrow {
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-primary-dark);
}

.hero-copy h1 {
  color: var(--color-heading);
  font-size: clamp(2rem, 4vw, 3.2rem);
  line-height: 1;
}

.hero-copy p {
  color: var(--color-text-muted);
  font-size: 1rem;
}

.hero-chip {
  display: grid;
  gap: 0.2rem;
  align-self: end;
  min-width: 210px;
  padding: 1rem 1.1rem;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(51, 92, 255, 0.12);
}

.hero-chip-label {
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.hero-chip strong {
  color: var(--color-heading);
  font-size: 1.1rem;
}

.editor-shell {
  display: grid;
  gap: 1.5rem;
}

.editor-panel,
.side-panel {
  background: var(--color-surface);
}

.editor-panel {
  padding: 1.5rem;
}

.section-head {
  margin-bottom: 1.35rem;
}

.section-head h2 {
  margin-bottom: 0.35rem;
  color: var(--color-heading);
  font-size: clamp(1.9rem, 3vw, 2.5rem);
  line-height: 1.05;
}

.section-head p {
  color: var(--color-text-muted);
  max-width: 58ch;
}

.field {
  display: grid;
  gap: 0.6rem;
  margin-bottom: 1.15rem;
}

.field span {
  font-weight: 700;
  color: var(--color-heading);
}

.field input,
.field textarea {
  width: 100%;
  border: 1px solid rgba(15, 23, 42, 0.12);
  border-radius: 20px;
  padding: 1rem 1.05rem;
  background: rgba(255, 255, 255, 0.98);
  color: var(--color-text);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.field textarea {
  min-height: 280px;
  resize: vertical;
}

.field input:focus,
.field textarea:focus {
  outline: none;
  border-color: rgba(51, 92, 255, 0.45);
  box-shadow: 0 0 0 4px rgba(51, 92, 255, 0.12);
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
  font-size: 0.95rem;
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
  padding: 1.1rem;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.05);
}

.metric-card.accent {
  background: linear-gradient(180deg, #f3f9ff, #e2f2ff);
}

.metric-head {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.metric-icon {
  display: inline-grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border-radius: 12px;
  background: var(--color-primary-soft);
  color: var(--color-primary-dark);
}

.metric-icon svg {
  width: 1rem;
  height: 1rem;
}

.metric-label {
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.78rem;
  font-weight: 700;
}

.metric-card strong {
  display: block;
  margin: 0.7rem 0 0.35rem;
  color: var(--color-heading);
  font-size: 1.45rem;
  line-height: 1.15;
}

.metric-card p {
  color: var(--color-text-muted);
}

.primary-button {
  border: 1px solid transparent;
  border-radius: 999px;
  padding: 0.95rem 1.3rem;
  cursor: pointer;
  font-weight: 700;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    background 0.2s ease;
}

.primary-button {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: #eef2ff;
  box-shadow: 0 16px 34px rgba(51, 92, 255, 0.24);
}

.primary-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 20px 36px rgba(51, 92, 255, 0.28);
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
  .create-hero {
    grid-template-columns: minmax(0, 1.25fr) auto;
    align-items: end;
  }

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
