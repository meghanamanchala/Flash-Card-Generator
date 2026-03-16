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
const activeCardIndex = ref(0)

const canSubmit = computed(() => {
  return title.value.trim().length > 0 && rawContent.value.trim().length >= 20 && !isSubmitting.value
})

const cardCountLabel = computed(() => {
  return flashcards.value.length === 1 ? '1 flashcard ready' : `${flashcards.value.length} flashcards ready`
})

const wordCount = computed(() => {
  const content = rawContent.value.trim()
  return content ? content.split(/\s+/).length : 0
})

const estimatedCards = computed(() => {
  if (!wordCount.value) {
    return 0
  }

  return Math.max(1, Math.ceil(wordCount.value / 55))
})

const activeCard = computed(() => {
  return flashcards.value[activeCardIndex.value] ?? null
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
    activeCardIndex.value = 0
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

function showPreviousCard() {
  if (!flashcards.value.length) {
    return
  }

  activeCardIndex.value =
    activeCardIndex.value === 0 ? flashcards.value.length - 1 : activeCardIndex.value - 1
}

function showNextCard() {
  if (!flashcards.value.length) {
    return
  }

  activeCardIndex.value =
    activeCardIndex.value === flashcards.value.length - 1 ? 0 : activeCardIndex.value + 1
}
</script>

<template>
  <main class="studio">
    <section class="masthead">
      <div class="masthead-copy">
        <p class="eyebrow">Flash Card Generator</p>
        <h1>Build a study deck that feels ready before you even start revising.</h1>
        <p class="lede">
          Drop in raw notes, let the API break them into learning chunks, and review the results in
          a focused reading surface instead of a plain data dump.
        </p>

        <div class="masthead-actions">
          <button class="primary-button" type="button" @click="loadSample">Try sample notes</button>
          <p class="microcopy">Ideal for chapters, lecture summaries, and exam prep sheets.</p>
        </div>
      </div>

      <div class="status-ribbon">
        <div class="status-card">
          <span class="status-label">Input</span>
          <strong>{{ wordCount }} words</strong>
          <p>Enough detail gives the generator better boundaries.</p>
        </div>
        <div class="status-card">
          <span class="status-label">Projected deck</span>
          <strong>{{ estimatedCards }} cards</strong>
          <p>Estimated from your current draft before generation.</p>
        </div>
        <div class="status-card accent">
          <span class="status-label">Current mode</span>
          <strong>{{ flashcards.length ? 'Reviewing' : 'Composing' }}</strong>
          <p>{{ flashcards.length ? cardCountLabel : 'Paste notes to create your first set.' }}</p>
        </div>
      </div>
    </section>

    <section class="workspace">
      <form class="composer-panel" @submit.prevent="generateFlashcards">
        <div class="panel-topline">
          <p class="panel-kicker">Deck Builder</p>
          <span class="panel-tag">Connected to Django</span>
        </div>

        <div class="panel-heading">
          <h2>Create a card set</h2>
          <p>Shape the source material here. The generator will split it into manageable study cards.</p>
        </div>

        <label class="field">
          <span>Deck title</span>
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
            rows="14"
            placeholder="Paste a paragraph, lesson summary, or notes here..."
          />
        </label>

        <div class="composer-insights">
          <div class="insight-box">
            <span>Word count</span>
            <strong>{{ wordCount }}</strong>
          </div>
          <div class="insight-box">
            <span>Estimated cards</span>
            <strong>{{ estimatedCards }}</strong>
          </div>
          <div class="insight-box">
            <span>Best input style</span>
            <strong>Complete sentences</strong>
          </div>
        </div>

        <div class="composer-footer">
          <p class="hint">Use full thoughts instead of fragments for cleaner chunking.</p>
          <button class="primary-button" type="submit" :disabled="!canSubmit">
            {{ isSubmitting ? 'Generating...' : 'Generate flashcards' }}
          </button>
        </div>

        <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>
      </form>

      <section class="review-panel">
        <div class="panel-topline">
          <p class="panel-kicker">Review Space</p>
          <span class="panel-tag muted">{{ flashcards.length ? cardCountLabel : 'Waiting for deck' }}</span>
        </div>

        <div class="panel-heading">
          <h2>{{ flashcards.length ? generatedTitle : 'Generated cards' }}</h2>
          <p>
            {{ flashcards.length
              ? 'Move through the generated cards and spot whether each chunk reads cleanly.'
              : 'Your flashcards will appear here as a navigable study deck.' }}
          </p>
        </div>

        <div v-if="activeCard" class="review-stage">
          <article class="hero-card">
            <div class="hero-card-meta">
              <span>Card {{ activeCard.order }}</span>
              <span>{{ activeCardIndex + 1 }} / {{ flashcards.length }}</span>
            </div>
            <p>{{ activeCard.content }}</p>
          </article>

          <div class="review-controls">
            <button class="ghost-button" type="button" @click="showPreviousCard">Previous</button>
            <button class="ghost-button" type="button" @click="showNextCard">Next</button>
          </div>

          <div class="card-strip">
            <button
              v-for="(card, index) in flashcards"
              :key="card.id"
              class="strip-card"
              :class="{ active: index === activeCardIndex }"
              type="button"
              @click="activeCardIndex = index"
            >
              <span>Card {{ card.order }}</span>
              <p>{{ card.content }}</p>
            </button>
          </div>
        </div>

        <div v-else class="empty-state">
          <p class="empty-badge">Preview area</p>
          <h3>No flashcards yet</h3>
          <p>Generate a set and this space turns into a deck browser with a primary card preview.</p>
          <div class="empty-grid">
            <div class="empty-chip">Paste notes</div>
            <div class="empty-chip">Generate deck</div>
            <div class="empty-chip">Review cards</div>
            <div class="empty-chip">Study faster</div>
          </div>
        </div>
      </section>
    </section>

    <section class="footer-note">
      <div>
        <p class="panel-kicker">Workflow</p>
        <h2>Compose, generate, review.</h2>
      </div>
      <p>
        The UI now behaves more like a study studio: notes on the left, active deck on the right,
        and card-by-card browsing once the response comes back.
      </p>
    </section>
  </main>
</template>

<style scoped>
.studio {
  display: grid;
  gap: 1.5rem;
  padding-bottom: 1rem;
}

.masthead {
  display: grid;
  gap: 1.25rem;
  padding: 1.4rem;
  border-radius: 32px;
  background:
    radial-gradient(circle at 15% 20%, rgba(255, 206, 107, 0.28), transparent 25%),
    radial-gradient(circle at 85% 30%, rgba(123, 92, 255, 0.18), transparent 18%),
    linear-gradient(135deg, #123524 0%, #193b31 48%, #101826 100%);
  color: #f6f6ef;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 28px 80px rgba(16, 24, 38, 0.22);
}

.masthead-copy h1 {
  max-width: 11ch;
  font-size: clamp(2.5rem, 6vw, 5.4rem);
  line-height: 0.92;
  margin: 0.4rem 0 1rem;
}

.eyebrow,
.panel-kicker {
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
}

.lede {
  max-width: 58ch;
  color: rgba(246, 246, 239, 0.8);
}

.masthead-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 1.25rem;
}

.microcopy {
  color: rgba(246, 246, 239, 0.7);
}

.status-ribbon {
  display: grid;
  gap: 0.9rem;
}

.status-card {
  padding: 1rem 1.05rem;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.09);
  backdrop-filter: blur(14px);
}

.status-card strong {
  display: block;
  margin: 0.2rem 0 0.35rem;
  font-size: 1.2rem;
}

.status-card p,
.status-label {
  color: rgba(246, 246, 239, 0.72);
}

.status-card.accent {
  background: linear-gradient(135deg, rgba(244, 114, 36, 0.26), rgba(251, 191, 36, 0.14));
}

.workspace {
  display: grid;
  gap: 1.5rem;
}

.composer-panel,
.review-panel,
.footer-note {
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  border: 1px solid var(--color-border);
  background: rgba(255, 250, 243, 0.72);
  box-shadow: 0 18px 50px rgba(120, 98, 77, 0.08);
}

.composer-panel,
.review-panel {
  padding: 1.35rem;
}

.footer-note {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.35rem;
  background: linear-gradient(135deg, rgba(255, 248, 237, 0.9), rgba(244, 232, 214, 0.72));
}

.panel-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.panel-tag {
  padding: 0.38rem 0.72rem;
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.06);
  font-size: 0.84rem;
}

.panel-tag.muted {
  background: rgba(180, 83, 9, 0.1);
  color: #9a3412;
}

.panel-heading {
  margin: 0.9rem 0 1.2rem;
}

.panel-heading h2 {
  font-size: 1.45rem;
  margin-bottom: 0.3rem;
  color: var(--color-heading);
}

.panel-heading p {
  color: var(--color-text-muted);
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
  border: 1px solid rgba(63, 63, 70, 0.12);
  border-radius: 18px;
  padding: 1rem 1.05rem;
  background: rgba(255, 255, 255, 0.9);
  font: inherit;
  color: var(--color-text);
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.field textarea {
  resize: vertical;
  min-height: 280px;
}

.field input:focus,
.field textarea:focus {
  outline: none;
  border-color: rgba(180, 83, 9, 0.45);
  box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.12);
}

.composer-insights {
  display: grid;
  gap: 0.8rem;
  margin: 1.1rem 0 1.2rem;
}

.insight-box {
  padding: 0.95rem 1rem;
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(249, 244, 236, 0.9));
  border: 1px solid rgba(180, 83, 9, 0.12);
}

.insight-box span {
  display: block;
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.insight-box strong {
  display: block;
  margin-top: 0.15rem;
  color: var(--color-heading);
  font-size: 1.1rem;
}

.composer-footer,
.review-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.hint {
  color: var(--color-text-muted);
}

.primary-button,
.ghost-button,
.strip-card {
  font: inherit;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    background 0.2s ease,
    border-color 0.2s ease;
}

.primary-button,
.ghost-button {
  border: 0;
  border-radius: 999px;
  padding: 0.9rem 1.25rem;
  cursor: pointer;
}

.primary-button {
  background: linear-gradient(135deg, #ffd36b, #f59e0b);
  color: #1f2937;
  box-shadow: 0 16px 34px rgba(245, 158, 11, 0.24);
}

.ghost-button {
  background: rgba(17, 24, 39, 0.06);
  color: var(--color-heading);
}

.primary-button:hover,
.ghost-button:hover,
.strip-card:hover {
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

.review-stage {
  display: grid;
  gap: 1rem;
}

.hero-card {
  min-height: 280px;
  padding: 1.35rem;
  border-radius: 26px;
  background:
    radial-gradient(circle at top right, rgba(255, 211, 107, 0.28), transparent 20%),
    linear-gradient(165deg, #fffdf9, #fff4de);
  border: 1px solid rgba(245, 158, 11, 0.22);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.hero-card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
  color: #9a3412;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.hero-card p {
  font-size: clamp(1.15rem, 2.4vw, 1.55rem);
  line-height: 1.45;
  color: #2f2417;
}

.card-strip {
  display: grid;
  gap: 0.8rem;
}

.strip-card {
  width: 100%;
  text-align: left;
  border: 1px solid rgba(17, 24, 39, 0.08);
  border-radius: 20px;
  padding: 0.95rem 1rem;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.74);
}

.strip-card span {
  display: block;
  margin-bottom: 0.3rem;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #9a3412;
}

.strip-card p {
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  color: var(--color-text);
}

.strip-card.active {
  border-color: rgba(180, 83, 9, 0.35);
  background: linear-gradient(135deg, rgba(255, 247, 237, 0.98), rgba(255, 237, 213, 0.88));
  box-shadow: 0 12px 24px rgba(180, 83, 9, 0.08);
}

.empty-state {
  display: grid;
  gap: 1rem;
  place-items: start;
  min-height: 420px;
  padding: 1.4rem;
  border-radius: 24px;
  background:
    radial-gradient(circle at top left, rgba(255, 206, 107, 0.18), transparent 20%),
    rgba(255, 255, 255, 0.54);
  border: 1px dashed rgba(17, 24, 39, 0.14);
}

.empty-badge {
  padding: 0.32rem 0.65rem;
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.07);
  font-size: 0.82rem;
}

.empty-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.empty-chip {
  padding: 0.55rem 0.8rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(17, 24, 39, 0.08);
  color: var(--color-text-muted);
}

@media (min-width: 900px) {
  .masthead {
    grid-template-columns: 1.25fr 0.9fr;
    align-items: end;
    padding: 1.8rem;
  }

  .workspace {
    grid-template-columns: minmax(0, 0.92fr) minmax(0, 1.08fr);
    align-items: start;
  }

  .composer-insights {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .card-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .footer-note {
    padding: 1.35rem 1.5rem;
  }
}

@media (max-width: 640px) {
  .masthead-copy h1 {
    max-width: none;
  }

  .footer-note {
    align-items: start;
    flex-direction: column;
  }
}
</style>
