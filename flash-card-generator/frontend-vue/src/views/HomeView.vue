<script setup lang="ts">
import axios from 'axios'
import { computed, ref } from 'vue'

type Flashcard = {
  id: number
  content: string
  order: number
  created_at: string
}

type GenerateResponse = {
  learning_unit_id: number
  title: string
  flashcards: Flashcard[]
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
})

const title = ref('')
const rawContent = ref('')
const flashcards = ref<Flashcard[]>([])
const generatedTitle = ref('')
const isSubmitting = ref(false)
const errorMessage = ref('')

const canSubmit = computed(() => {
  return title.value.trim().length > 0 && rawContent.value.trim().length >= 20 && !isSubmitting.value
})

const cardCountLabel = computed(() => {
  return flashcards.value.length === 1 ? '1 flashcard ready' : `${flashcards.value.length} flashcards ready`
})

async function generateFlashcards() {
  if (!canSubmit.value) {
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const learningUnitResponse = await api.post('/learning-units/', {
      title: title.value.trim(),
      raw_content: rawContent.value.trim(),
    })

    const { data } = await api.post<GenerateResponse>(
      `/learning-units/${learningUnitResponse.data.id}/generate-cards/`,
    )

    generatedTitle.value = data.title
    flashcards.value = data.flashcards
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errorMessage.value =
        error.response?.data?.detail ||
        'The generator could not create flashcards from that text. Try adding more complete sentences.'
    } else {
      errorMessage.value = 'Something went wrong while talking to the backend.'
    }
  } finally {
    isSubmitting.value = false
  }
}

function loadSample() {
  title.value = 'Photosynthesis'
  rawContent.value =
    'Photosynthesis is the process plants use to convert light energy into chemical energy. Chlorophyll in the chloroplast absorbs sunlight, especially from the blue and red parts of the spectrum. Plants take in carbon dioxide from the air through small pores called stomata and absorb water through their roots. During the light-dependent reactions, energy from sunlight helps split water molecules and produces oxygen as a byproduct. The energy captured is stored in ATP and NADPH. In the Calvin cycle, plants use ATP and NADPH to turn carbon dioxide into glucose. This glucose can be used immediately for energy or stored for later growth and repair.'
}
</script>

<template>
  <main class="page-shell">
    <section class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Study Smarter</p>
        <h1>Turn long notes into clean, study-ready flashcards.</h1>
        <p class="hero-text">
          Paste a lesson, chapter summary, or revision notes. The frontend now sends it to your
          Django API and lays the generated cards out instantly.
        </p>
      </div>

      <div class="hero-panel">
        <div class="stat">
          <span class="stat-label">Workflow</span>
          <strong>Vue + Django API</strong>
        </div>
        <div class="stat">
          <span class="stat-label">Best for</span>
          <strong>Lecture notes, summaries, concepts</strong>
        </div>
      </div>
    </section>

    <section class="workspace">
      <form class="composer" @submit.prevent="generateFlashcards">
        <div class="section-heading">
          <h2>Create a card set</h2>
          <button class="ghost-button" type="button" @click="loadSample">Load sample</button>
        </div>

        <label class="field">
          <span>Title</span>
          <input
            v-model="title"
            type="text"
            maxlength="255"
            placeholder="Example: Cell respiration"
          />
        </label>

        <label class="field">
          <span>Learning content</span>
          <textarea
            v-model="rawContent"
            rows="12"
            placeholder="Paste a paragraph, lesson summary, or notes here..."
          />
        </label>

        <div class="composer-footer">
          <p class="hint">Use complete sentences for better chunking and clearer flashcards.</p>
          <button class="primary-button" type="submit" :disabled="!canSubmit">
            {{ isSubmitting ? 'Generating...' : 'Generate flashcards' }}
          </button>
        </div>

        <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>
      </form>

      <section class="results">
        <div class="section-heading">
          <div>
            <h2>Generated cards</h2>
            <p v-if="flashcards.length" class="result-meta">
              {{ generatedTitle }} · {{ cardCountLabel }}
            </p>
          </div>
        </div>

        <div v-if="flashcards.length" class="card-grid">
          <article v-for="card in flashcards" :key="card.id" class="flashcard">
            <div class="flashcard-order">Card {{ card.order }}</div>
            <p>{{ card.content }}</p>
          </article>
        </div>

        <div v-else class="empty-state">
          <h3>No flashcards yet</h3>
          <p>Generate a set to see the backend response rendered here.</p>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.page-shell {
  display: grid;
  gap: 2rem;
}

.hero {
  display: grid;
  gap: 1.5rem;
  padding: 2rem;
  border: 1px solid var(--color-border);
  border-radius: 28px;
  background:
    radial-gradient(circle at top left, rgba(244, 183, 64, 0.28), transparent 32%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(28, 25, 23, 0.92));
  color: #f8fafc;
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.18);
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 0.78rem;
  color: rgba(248, 250, 252, 0.75);
}

.hero h1 {
  margin-top: 0.6rem;
  font-size: clamp(2.2rem, 5vw, 4.4rem);
  line-height: 0.96;
  max-width: 11ch;
}

.hero-text {
  margin-top: 1rem;
  max-width: 60ch;
  color: rgba(248, 250, 252, 0.82);
}

.hero-panel {
  display: grid;
  gap: 1rem;
}

.stat {
  padding: 1rem 1.1rem;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
}

.stat-label {
  display: block;
  margin-bottom: 0.35rem;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: rgba(248, 250, 252, 0.6);
}

.workspace {
  display: grid;
  gap: 1.5rem;
}

.composer,
.results {
  padding: 1.5rem;
  border-radius: 24px;
  border: 1px solid var(--color-border);
  background: rgba(255, 252, 247, 0.84);
  box-shadow: 0 18px 45px rgba(148, 163, 184, 0.12);
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.section-heading h2 {
  font-size: 1.25rem;
}

.field {
  display: grid;
  gap: 0.45rem;
  margin-bottom: 1rem;
}

.field span {
  font-weight: 600;
  color: var(--color-heading);
}

.field input,
.field textarea {
  width: 100%;
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 16px;
  padding: 0.95rem 1rem;
  background: rgba(255, 255, 255, 0.82);
  font: inherit;
  color: var(--color-text);
}

.field textarea {
  resize: vertical;
}

.field input:focus,
.field textarea:focus {
  outline: 2px solid rgba(217, 119, 6, 0.25);
  border-color: rgba(217, 119, 6, 0.5);
}

.composer-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.hint,
.result-meta {
  color: var(--color-text-muted);
}

.primary-button,
.ghost-button {
  border: 0;
  border-radius: 999px;
  padding: 0.85rem 1.25rem;
  font: inherit;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    opacity 0.2s ease;
}

.primary-button {
  background: linear-gradient(135deg, #d97706, #b45309);
  color: #fff;
  box-shadow: 0 16px 30px rgba(217, 119, 6, 0.28);
}

.ghost-button {
  background: rgba(15, 23, 42, 0.06);
  color: var(--color-heading);
}

.primary-button:hover,
.ghost-button:hover {
  transform: translateY(-1px);
}

.primary-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.error-banner {
  margin-top: 1rem;
  border-radius: 16px;
  padding: 0.9rem 1rem;
  background: rgba(220, 38, 38, 0.1);
  color: #991b1b;
}

.card-grid {
  display: grid;
  gap: 1rem;
}

.flashcard {
  position: relative;
  overflow: hidden;
  padding: 1.25rem;
  border-radius: 22px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(255, 247, 237, 0.96)),
    #fff;
  border: 1px solid rgba(251, 191, 36, 0.26);
  box-shadow: 0 14px 28px rgba(217, 119, 6, 0.08);
}

.flashcard::after {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 6px;
  background: linear-gradient(180deg, #f59e0b, #ea580c);
}

.flashcard-order {
  margin-bottom: 0.75rem;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #b45309;
}

.empty-state {
  display: grid;
  place-items: center;
  min-height: 280px;
  border: 1px dashed rgba(148, 163, 184, 0.45);
  border-radius: 20px;
  text-align: center;
  padding: 1.5rem;
  color: var(--color-text-muted);
}

@media (min-width: 900px) {
  .hero,
  .workspace {
    grid-template-columns: 1.1fr 0.9fr;
  }

  .results {
    min-height: 100%;
  }
}
</style>
