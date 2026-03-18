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
      <div class="stat-card">
        <span class="stat-label">Saved decks</span>
        <strong>{{ isLoading ? '...' : decks.length }}</strong>
        <p>All generated decks are stored in the backend database.</p>
      </div>
      <div class="stat-card accent">
        <span class="stat-label">Workflow</span>
        <strong>Dashboard → Create → Review</strong>
        <p>The app now uses separate pages for creation and card browsing.</p>
      </div>
    </section>

    <section class="saved-panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow muted">Library</p>
          <h2>{{ deckSummary }}</h2>
        </div>
        <RouterLink class="panel-link" to="/create">Create deck</RouterLink>
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
        <h3>Create your first saved set</h3>
        <p>Use the star button above, enter a title, paste your content, and generate the cards.</p>
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
  gap: 1.5rem;
}

.saved-panel,
.stat-card {
  border-radius: 30px;
  border: 1px solid var(--color-border);
  box-shadow: 0 18px 50px rgba(120, 98, 77, 0.08);
}

.eyebrow {
  font-size: 0.78rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.eyebrow.muted {
  color: var(--color-text-muted);
}

.stats-row {
  display: grid;
  gap: 1rem;
}

.stat-card,
.saved-panel {
  background: rgba(255, 250, 243, 0.76);
}

.stat-card {
  padding: 1.15rem 1.2rem;
}

.stat-card strong {
  display: block;
  margin: 0.2rem 0 0.35rem;
  color: var(--color-heading);
  font-size: 1.35rem;
}

.stat-label {
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-size: 0.76rem;
}

.stat-card.accent {
  background: linear-gradient(135deg, rgba(234, 241, 255, 0.95), rgba(215, 236, 255, 0.82));
}

.saved-panel {
  padding: 1.35rem;
}

.panel-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.panel-head h2 {
  color: var(--color-heading);
}

.panel-link {
  border-radius: 999px;
  padding: 0.85rem 1.1rem;
  background: rgba(17, 24, 39, 0.06);
}

.deck-grid {
  display: grid;
  gap: 1rem;
}

.deck-card {
  display: grid;
  gap: 0.75rem;
  padding: 1.1rem;
  border-radius: 24px;
  border: 1px solid rgba(17, 24, 39, 0.08);
  background:
    radial-gradient(circle at top right, rgba(120, 196, 255, 0.18), transparent 20%),
    rgba(255, 255, 255, 0.82);
  color: inherit;
}

.deck-badge {
  justify-self: start;
  padding: 0.3rem 0.65rem;
  border-radius: 999px;
  background: rgba(79, 70, 229, 0.1);
  color: #4338ca;
  font-size: 0.8rem;
}

.deck-card h3 {
  color: var(--color-heading);
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
}

.empty-state {
  min-height: 260px;
  display: grid;
  gap: 0.85rem;
  place-items: center;
  text-align: center;
  padding: 1.2rem;
  border-radius: 24px;
  border: 1px dashed rgba(17, 24, 39, 0.14);
  background: rgba(255, 255, 255, 0.54);
}

.empty-state.loading {
  min-height: 180px;
}

.empty-badge {
  padding: 0.32rem 0.65rem;
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.07);
  font-size: 0.82rem;
}

.error-banner {
  margin-bottom: 1rem;
  border-radius: 18px;
  padding: 0.95rem 1rem;
  background: rgba(220, 38, 38, 0.08);
  color: #991b1b;
}

@media (min-width: 840px) {
  .stats-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .deck-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
