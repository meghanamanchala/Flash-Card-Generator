<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { api, type LearningUnit } from '../services/api'

const route = useRoute()

const deck = ref<LearningUnit | null>(null)
const activeCardIndex = ref(0)
const isLoading = ref(true)
const errorMessage = ref('')

const activeCard = computed(() => {
  return deck.value?.flashcards[activeCardIndex.value] ?? null
})

const createdLabel = computed(() => {
  if (!deck.value) {
    return ''
  }

  return new Date(deck.value.created_at).toLocaleString()
})

async function loadDeck() {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const { data } = await api.get<LearningUnit>(`/learning-units/${route.params.id}/`)
    deck.value = data
    activeCardIndex.value = 0
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errorMessage.value = error.response?.data?.detail || 'This saved deck could not be loaded.'
    } else {
      errorMessage.value = 'Something went wrong while loading the deck.'
    }
  } finally {
    isLoading.value = false
  }
}

function showPreviousCard() {
  if (!deck.value?.flashcards.length) {
    return
  }

  activeCardIndex.value =
    activeCardIndex.value === 0 ? deck.value.flashcards.length - 1 : activeCardIndex.value - 1
}

function showNextCard() {
  if (!deck.value?.flashcards.length) {
    return
  }

  activeCardIndex.value =
    activeCardIndex.value === deck.value.flashcards.length - 1 ? 0 : activeCardIndex.value + 1
}

watch(
  () => route.params.id,
  () => {
    void loadDeck()
  },
)

onMounted(() => {
  void loadDeck()
})
</script>

<template>
  <main class="deck-page">
    <section class="deck-header">
      <div>
        <p class="eyebrow">Saved Deck</p>
        <h1>{{ deck?.title || 'Flashcard deck' }}</h1>
        <p class="deck-subtitle">
          {{ deck ? `${deck.flashcards.length} cards generated • saved ${createdLabel}` : 'Loading deck...' }}
        </p>
      </div>
      <div class="header-actions">
        <RouterLink class="ghost-link" to="/">Dashboard</RouterLink>
        <RouterLink class="primary-link" to="/create">Create another</RouterLink>
      </div>
    </section>

    <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>

    <section v-if="deck && !isLoading" class="deck-layout">
      <aside class="deck-sidebar">
        <div class="sidebar-card">
          <span class="label">Source title</span>
          <strong>{{ deck.title }}</strong>
        </div>
        <div class="sidebar-card">
          <span class="label">Chosen max cards</span>
          <strong>{{ deck.max_flashcards }}</strong>
        </div>
        <div class="sidebar-card">
          <span class="label">Stored content</span>
          <p>{{ deck.raw_content }}</p>
        </div>
      </aside>

      <section class="review-panel">
        <article v-if="activeCard" class="hero-card">
          <div class="hero-card-meta">
            <span>Card {{ activeCard.order }}</span>
            <span>{{ activeCardIndex + 1 }} / {{ deck.flashcards.length }}</span>
          </div>
          <p>{{ activeCard.content }}</p>
        </article>

        <div class="review-controls">
          <button class="ghost-button" type="button" @click="showPreviousCard">Previous</button>
          <button class="ghost-button" type="button" @click="showNextCard">Next</button>
        </div>

        <div class="card-strip">
          <button
            v-for="(card, index) in deck.flashcards"
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
      </section>
    </section>

    <section v-else-if="isLoading" class="empty-state">
      <h2>Loading saved deck...</h2>
      <p>We are pulling the stored title, source content, and generated flashcards from the backend.</p>
    </section>
  </main>
</template>

<style scoped>
.deck-page {
  display: grid;
  gap: 1.5rem;
}

.deck-header,
.deck-sidebar,
.review-panel,
.empty-state {
  border-radius: 28px;
  border: 1px solid var(--color-border);
  box-shadow: 0 18px 50px rgba(120, 98, 77, 0.08);
}

.deck-header {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.5rem;
  background:
    radial-gradient(circle at 80% 20%, rgba(100, 181, 255, 0.28), transparent 20%),
    linear-gradient(135deg, #1b2753 0%, #1c3357 52%, #1f4d68 100%);
  color: #fff9ef;
}

.eyebrow,
.label,
.hero-card-meta span,
.strip-card span {
  font-size: 0.78rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.deck-header h1 {
  margin: 0.45rem 0 0.35rem;
  font-size: clamp(2.2rem, 5vw, 4rem);
  line-height: 0.98;
}

.deck-subtitle {
  color: rgba(255, 249, 239, 0.76);
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.ghost-link,
.primary-link,
.ghost-button {
  border-radius: 999px;
  padding: 0.85rem 1.15rem;
  text-decoration: none;
  font: inherit;
}

.primary-link {
  background: linear-gradient(135deg, #7dd3fc, #4f46e5);
  color: #eef2ff;
}

.ghost-link,
.ghost-button {
  background: rgba(255, 255, 255, 0.1);
  color: #fff9ef;
  border: 0;
  cursor: pointer;
}

.deck-layout {
  display: grid;
  gap: 1.5rem;
}

.deck-sidebar,
.review-panel,
.empty-state {
  padding: 1.35rem;
  background: rgba(255, 250, 243, 0.78);
}

.deck-sidebar {
  display: grid;
  gap: 1rem;
  align-content: start;
}

.sidebar-card {
  padding: 1rem;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(17, 24, 39, 0.08);
}

.sidebar-card strong {
  display: block;
  margin-top: 0.3rem;
  color: var(--color-heading);
  font-size: 1.15rem;
}

.sidebar-card p {
  margin-top: 0.4rem;
  color: var(--color-text);
  white-space: pre-wrap;
}

.label {
  color: var(--color-text-muted);
}

.review-panel {
  display: grid;
  gap: 1rem;
}

.hero-card {
  min-height: 280px;
  padding: 1.35rem;
  border-radius: 26px;
  background:
    radial-gradient(circle at top right, rgba(125, 211, 252, 0.24), transparent 20%),
    linear-gradient(165deg, #fcfdff, #edf4ff);
  border: 1px solid rgba(79, 70, 229, 0.2);
}

.hero-card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
  color: #4338ca;
}

.hero-card p {
  font-size: clamp(1.1rem, 2.3vw, 1.5rem);
  line-height: 1.45;
  color: #2f2417;
}

.review-controls {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
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
  font: inherit;
}

.strip-card span {
  display: block;
  margin-bottom: 0.3rem;
  color: #4338ca;
}

.strip-card p {
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  color: var(--color-text);
}

.strip-card.active {
  border-color: rgba(79, 70, 229, 0.35);
  background: linear-gradient(135deg, rgba(239, 244, 255, 0.98), rgba(227, 239, 255, 0.88));
  box-shadow: 0 12px 24px rgba(79, 70, 229, 0.08);
}

.empty-state {
  min-height: 320px;
  display: grid;
  place-items: center;
  text-align: center;
}

.error-banner {
  border-radius: 18px;
  padding: 0.95rem 1rem;
  background: rgba(220, 38, 38, 0.08);
  color: #991b1b;
}

@media (min-width: 940px) {
  .deck-layout {
    grid-template-columns: minmax(290px, 0.7fr) minmax(0, 1.3fr);
    align-items: start;
  }

  .card-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .deck-header {
    align-items: start;
    flex-direction: column;
  }
}
</style>
