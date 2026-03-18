<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'

import { api, type LearningUnit } from '../services/api'

const decks = ref<LearningUnit[]>([])
const isLoading = ref(true)
const errorMessage = ref('')

const deckSummary = computed(() => {
  return decks.value.length === 1 ? '1 saved deck' : `${decks.value.length} saved decks`
})

const totalDecksLabel = computed(() => {
  return decks.value.length === 1 ? '1 deck' : `${decks.value.length} decks`
})

async function loadDecks() {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const { data } = await api.get<LearningUnit[]>('/learning-units/')
    decks.value = data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errorMessage.value =
        error.response?.data?.detail || 'Saved decks could not be loaded from the backend.'
    } else {
      errorMessage.value = 'Something went wrong while loading the dashboard.'
    }
  } finally {
    isLoading.value = false
  }
}

function formatDate(value: string) {
  return new Date(value).toLocaleString()
}

onMounted(() => {
  void loadDecks()
})
</script>

<template>
  <main class="dashboard">
    

    <section class="stats-row">
      <div class="stat-card library">
        <div class="stat-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" role="presentation">
            <path
              d="M6 5.75A1.75 1.75 0 0 1 7.75 4h8.5A1.75 1.75 0 0 1 18 5.75v12.5A1.75 1.75 0 0 1 16.25 20h-8.5A1.75 1.75 0 0 1 6 18.25Z"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
            />
            <path d="M9 8h6M9 11h6M9 14h4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
          </svg>
        </div>
        <span class="stat-label">Deck count</span>
        <strong>{{ isLoading ? '...' : decks.length }}</strong>
        <p>Every generated set is saved and ready to reopen.</p>
      </div>
      <div class="stat-card workflow">
        <div class="stat-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" role="presentation">
            <path
              d="M4 7h10m0 0-3-3m3 3-3 3M20 17H10m0 0 3-3m-3 3 3 3"
              fill="none"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.8"
            />
          </svg>
        </div>
        <span class="stat-label">Workflow</span>
        <strong>Dashboard → Create → Review</strong>
        <p>The app now uses separate pages for creation and card browsing.</p>
      </div>
    </section>

    <section class="saved-panel">
      <div class="panel-head">
        <div>
          <div class="section-kicker">
            <span class="section-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" role="presentation">
                <path
                  d="M7 5.75A1.75 1.75 0 0 1 8.75 4h7.5A1.75 1.75 0 0 1 18 5.75v12.5A1.75 1.75 0 0 1 16.25 20h-7.5A1.75 1.75 0 0 1 7 18.25Z"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                />
                <path d="M10 8h5M10 11h5M10 14h3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
              </svg>
            </span>
            <p class="eyebrow muted">Library</p>
          </div>
          <h2>{{ deckSummary }}</h2>
          <p class="section-description">Open a deck, continue reviewing, or start a new one.</p>
        </div>
        <RouterLink class="panel-link" to="/create">New deck</RouterLink>
      </div>

      <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>

      <div v-if="!isLoading && decks.length" class="deck-grid">
        <RouterLink
          v-for="deck in decks"
          :key="deck.id"
          class="deck-card"
          :to="{ name: 'deck', params: { id: deck.id.toString() } }"
        >
          <span class="deck-badge">{{ deck.flashcards.length }} cards</span>
          <h3>{{ deck.title }}</h3>
          <p class="deck-copy">{{ deck.raw_content }}</p>
          <div class="deck-meta">
            <span>Max {{ deck.max_flashcards }}</span>
            <span>{{ formatDate(deck.created_at) }}</span>
          </div>
        </RouterLink>
      </div>

      <div v-else-if="!isLoading" class="empty-state">
        <p class="empty-badge">No decks yet</p>
        <h3>Create your first deck</h3>
        <p>Add a title, paste your notes, and generate cards when you are ready.</p>
      </div>

      <div v-else class="empty-state loading">
        <h3>Loading saved decks...</h3>
      </div>
    </section>
  </main>
</template>

<style scoped>
.dashboard {
  display: grid;
  gap: 1.75rem;
}

.hero-panel,
.saved-panel,
.stat-card {
  border-radius: 30px;
  border: 1px solid var(--color-border);
  box-shadow: var(--color-shadow);
}

.eyebrow {
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.eyebrow.muted {
  color: var(--color-text-muted);
}

.hero-panel {
  display: grid;
  gap: 1.5rem;
  padding: 1.6rem;
  background:
    radial-gradient(circle at right top, rgba(51, 92, 255, 0.18), transparent 22%),
    linear-gradient(135deg, #ffffff, #f4f8ff 58%, #eef4ff);
}

.hero-copy {
  display: grid;
  gap: 0.75rem;
}

.hero-copy h1 {
  color: var(--color-heading);
  font-size: clamp(2.1rem, 4vw, 3.4rem);
  line-height: 1;
}

.hero-text {
  max-width: 54ch;
  color: var(--color-text-muted);
  font-size: 1.02rem;
}

.hero-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.primary-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.8rem;
  border-radius: 999px;
  padding: 0.95rem 1.3rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: #f8fbff;
  font-weight: 700;
  box-shadow: 0 18px 32px rgba(51, 92, 255, 0.24);
}

.cta-icon {
  display: inline-grid;
  place-items: center;
  width: 1.8rem;
  height: 1.8rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
}

.cta-icon svg,
.stat-icon svg,
.section-icon svg {
  width: 1rem;
  height: 1rem;
}

.hero-note {
  display: grid;
  gap: 0.15rem;
  min-width: 180px;
  padding: 0.95rem 1rem;
  border-radius: 20px;
  border: 1px solid rgba(51, 92, 255, 0.12);
  background: rgba(255, 255, 255, 0.88);
}

.hero-note-label {
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.hero-note strong {
  color: var(--color-heading);
  font-size: 1.1rem;
}

.stats-row {
  display: grid;
  gap: 1rem;
}

.stat-card,
.saved-panel {
  background: var(--color-surface);
}

.stat-card {
  display: grid;
  gap: 0.4rem;
  padding: 1.3rem;
}

.stat-icon {
  display: inline-grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 16px;
  margin-bottom: 0.35rem;
}

.stat-card.library .stat-icon {
  background: #fff1e6;
  color: #c2410c;
}

.stat-card.workflow .stat-icon {
  background: #dff3ff;
  color: #0369a1;
}

.stat-card strong {
  display: block;
  margin: 0.2rem 0 0.35rem;
  color: var(--color-heading);
  font-size: 1.5rem;
  line-height: 1.15;
}

.stat-label {
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-size: 0.76rem;
  font-weight: 700;
}

.stat-card p {
  color: var(--color-text-muted);
}

.stat-card.library {
  background: linear-gradient(180deg, #fffdf9, #fff7ed);
}

.stat-card.workflow {
  background: linear-gradient(180deg, #f5fbff, #e6f4ff);
}

.saved-panel {
  padding: 1.5rem;
}

.panel-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
}

.section-kicker {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 0.4rem;
}

.section-icon {
  display: inline-grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border-radius: 12px;
  background: #fff1e6;
  color: #c2410c;
}

.panel-head h2 {
  color: var(--color-heading);
  font-size: clamp(1.85rem, 4vw, 2.5rem);
  line-height: 1;
}

.section-description {
  margin-top: 0.5rem;
  color: var(--color-text-muted);
}

.panel-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  padding: 0.9rem 1.2rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: #f8fbff;
  font-weight: 700;
  box-shadow: 0 14px 28px rgba(51, 92, 255, 0.18);
}

.deck-grid {
  display: grid;
  gap: 1rem;
}

.deck-card {
  display: grid;
  gap: 0.75rem;
  padding: 1.2rem;
  border-radius: 24px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background:
    radial-gradient(circle at top right, rgba(51, 92, 255, 0.1), transparent 24%),
    rgba(255, 255, 255, 0.95);
  color: inherit;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
}

.deck-badge {
  justify-self: start;
  padding: 0.38rem 0.72rem;
  border-radius: 999px;
  background: var(--color-primary-soft);
  color: var(--color-primary-dark);
  font-size: 0.8rem;
  font-weight: 700;
}

.deck-card h3 {
  color: var(--color-heading);
  font-size: 1.2rem;
  line-height: 1.2;
}

.deck-copy {
  color: var(--color-text-muted);
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.deck-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  color: var(--color-text-muted);
  font-size: 0.92rem;
  padding-top: 0.4rem;
  border-top: 1px solid rgba(15, 23, 42, 0.06);
}

.empty-state {
  min-height: 260px;
  display: grid;
  gap: 0.85rem;
  place-items: center;
  text-align: center;
  padding: 1.8rem;
  border-radius: 24px;
  border: 1px dashed rgba(15, 23, 42, 0.16);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(248, 250, 252, 0.92)),
    var(--color-panel);
}

.empty-state.loading {
  min-height: 180px;
}

.empty-badge {
  padding: 0.38rem 0.7rem;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.07);
  font-size: 0.82rem;
  font-weight: 700;
}

.error-banner {
  margin-bottom: 1rem;
  border-radius: 18px;
  padding: 0.95rem 1rem;
  background: rgba(220, 38, 38, 0.08);
  color: #991b1b;
}

@media (min-width: 840px) {
  .hero-panel {
    grid-template-columns: minmax(0, 1.25fr) auto;
    align-items: end;
  }

  .stats-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .deck-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .panel-head,
  .hero-actions {
    align-items: start;
    flex-direction: column;
  }
}
</style>
