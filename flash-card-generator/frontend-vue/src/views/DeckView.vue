<script setup lang="ts">
import axios from 'axios'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { api, type Flashcard, type LearningUnit } from '../services/api'

const route = useRoute()

type StudyRating = 'again' | 'hard' | 'good' | 'easy'

const deck = ref<LearningUnit | null>(null)
const activeCardIndex = ref(0)
const isLoading = ref(true)
const errorMessage = ref('')
const isAnswerVisible = ref(false)
const ratingCounts = ref<Record<StudyRating, number>>({
  again: 0,
  hard: 0,
  good: 0,
  easy: 0,
})

const activeCard = computed(() => {
  return deck.value?.flashcards[activeCardIndex.value] ?? null
})

const deckHasCards = computed(() => Boolean(deck.value?.flashcards.length))

const cardProgress = computed(() => {
  if (!deck.value?.flashcards.length) {
    return '0 / 0'
  }

  return `${activeCardIndex.value + 1} / ${deck.value.flashcards.length}`
})

const sessionSummary = computed(() => [
  { label: 'Again', value: ratingCounts.value.again, tone: 'again' },
  { label: 'Hard', value: ratingCounts.value.hard, tone: 'hard' },
  { label: 'Good', value: ratingCounts.value.good, tone: 'good' },
  { label: 'Easy', value: ratingCounts.value.easy, tone: 'easy' },
])

function deriveCardSides(card: Flashcard | null) {
  if (!card) {
    return { question: '', answer: '' }
  }

  const normalized = card.content.replace(/\s+/g, ' ').trim()
  const explicitQa = normalized.match(/Q(?:uestion)?[:.-]\s*(.+?)\s+A(?:nswer)?[:.-]\s*(.+)/i)

  if (explicitQa?.[1] && explicitQa[2]) {
    return {
      question: explicitQa[1].trim(),
      answer: explicitQa[2].trim(),
    }
  }

  const sentences = normalized.split(/(?<=[.!?])\s+/).filter(Boolean)

  if (sentences.length >= 2) {
    const firstSentence = sentences[0] ?? ''
    const restSentences = sentences.slice(1)

    return {
      question: firstSentence.trim(),
      answer: restSentences.join(' ').trim(),
    }
  }

  const words = normalized.split(/\s+/)

  if (words.length > 12) {
    return {
      question: `${words.slice(0, 12).join(' ')}...`,
      answer: normalized,
    }
  }

  return {
    question: 'What should you remember from this card?',
    answer: normalized,
  }
}

const activeCardSides = computed(() => deriveCardSides(activeCard.value))

const activeCardLabel = computed(() => {
  return isAnswerVisible.value ? 'Answer' : 'Question'
})

const activeCardText = computed(() => {
  return isAnswerVisible.value ? activeCardSides.value.answer : activeCardSides.value.question
})

function resetCardState() {
  isAnswerVisible.value = false
}

async function loadDeck() {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const { data } = await api.get<LearningUnit>(`/learning-units/${route.params.id}/`)
    deck.value = data
    activeCardIndex.value = 0
    resetCardState()
    ratingCounts.value = {
      again: 0,
      hard: 0,
      good: 0,
      easy: 0,
    }
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
  resetCardState()
}

function showNextCard() {
  if (!deck.value?.flashcards.length) {
    return
  }

  activeCardIndex.value =
    activeCardIndex.value === deck.value.flashcards.length - 1 ? 0 : activeCardIndex.value + 1
  resetCardState()
}

function revealAnswer() {
  if (!activeCard.value) {
    return
  }

  isAnswerVisible.value = true
}

function rateCard(rating: StudyRating) {
  ratingCounts.value = {
    ...ratingCounts.value,
    [rating]: ratingCounts.value[rating] + 1,
  }
  showNextCard()
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'ArrowLeft') {
    showPreviousCard()
  }

  if (event.key === 'ArrowRight') {
    showNextCard()
  }

  if (event.code === 'Space') {
    event.preventDefault()
    revealAnswer()
  }

  if (!isAnswerVisible.value) {
    return
  }

  if (event.key === '1') {
    rateCard('again')
  }

  if (event.key === '2') {
    rateCard('hard')
  }

  if (event.key === '3') {
    rateCard('good')
  }

  if (event.key === '4') {
    rateCard('easy')
  }
}

watch(
  () => route.params.id,
  () => {
    void loadDeck()
  },
)

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  void loadDeck()
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <main class="study-page">
    <section class="study-frame">
      <header class="study-bar">
        <RouterLink class="back-link" to="/">
          <span aria-hidden="true">←</span>
        </RouterLink>
        <span class="study-progress">{{ cardProgress }}</span>
      </header>

      <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>

      <section v-if="deck && !isLoading && deckHasCards" class="study-shell">
        <article class="study-card" role="button" tabindex="0" @click="revealAnswer">
          <span class="card-label">{{ activeCardLabel }}</span>
          <h1>{{ activeCardText }}</h1>
          <p v-if="!isAnswerVisible" class="card-hint">Press Space to reveal</p>
        </article>

        <div v-if="isAnswerVisible" class="rating-row">
          <button class="rating-chip again" type="button" @click="rateCard('again')">1 — Again</button>
          <button class="rating-chip hard" type="button" @click="rateCard('hard')">2 — Hard</button>
          <button class="rating-chip good" type="button" @click="rateCard('good')">3 — Good</button>
          <button class="rating-chip easy" type="button" @click="rateCard('easy')">4 — Easy</button>
        </div>

        <div v-else class="study-actions">
          <button class="ghost-button" type="button" @click="showPreviousCard">Previous</button>
          <button class="primary-button" type="button" @click="revealAnswer">Reveal</button>
          <button class="ghost-button" type="button" @click="showNextCard">Skip</button>
        </div>

        <div class="session-row">
          <span v-for="item in sessionSummary" :key="item.label" class="summary-chip" :class="item.tone">
            {{ item.label }} {{ item.value }}
          </span>
        </div>
      </section>

      <section v-else-if="deck && !isLoading" class="empty-state">
        <h2>No flashcards were generated for this deck.</h2>
        <p>Try creating another deck with more detailed notes or textbook content.</p>
        <RouterLink class="primary-button link-button" to="/create">Create another deck</RouterLink>
      </section>

      <section v-else class="empty-state">
        <h2>{{ isLoading ? 'Loading deck...' : 'Deck unavailable' }}</h2>
        <p>
          {{
            isLoading
              ? 'Preparing your study session.'
              : 'We could not open this study deck right now.'
          }}
        </p>
      </section>
    </section>
  </main>
</template>

<style scoped>
.study-page {
  display: grid;
}

.study-frame {
  min-height: calc(100vh - 120px);
  border: 1px solid var(--color-border);
  border-radius: 28px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(244, 247, 252, 0.98)),
    var(--color-surface);
  box-shadow: var(--color-shadow);
}

.study-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.95rem 1.4rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 999px;
  color: var(--color-text-muted);
}

.study-progress {
  color: var(--color-text-muted);
  font-size: 1.1rem;
  font-weight: 500;
}

.study-shell,
.empty-state {
  min-height: calc(100vh - 220px);
  display: grid;
  place-items: center;
  padding: 1.5rem;
}

.study-shell {
  gap: 1.2rem;
}

.study-card {
  width: min(100%, 720px);
  min-height: 250px;
  display: grid;
  align-content: center;
  gap: 1.5rem;
  padding: 2rem;
  border: 1px solid var(--color-border-strong);
  border-radius: 24px;
  background:
    linear-gradient(180deg, #ffffff, #f6f8fd),
    #ffffff;
  box-shadow: var(--color-shadow-strong);
  cursor: pointer;
}

.card-label {
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font-size: 0.82rem;
  font-weight: 600;
}

.study-card h1 {
  font-size: clamp(1.9rem, 3vw, 2.6rem);
  line-height: 1.35;
  font-weight: 500;
}

.card-hint {
  color: var(--color-text-muted);
  font-size: 1rem;
}

.study-actions,
.rating-row,
.session-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.ghost-button,
.primary-button,
.rating-chip,
.summary-chip {
  border-radius: 14px;
  font: inherit;
}

.ghost-button,
.primary-button,
.rating-chip {
  border: 0;
  padding: 0.9rem 1.15rem;
  cursor: pointer;
  font-weight: 600;
}

.ghost-button {
  background: var(--color-panel);
  color: var(--color-heading);
  border: 1px solid var(--color-border);
}

.primary-button {
  background: linear-gradient(180deg, #3b6cff, #2f5de6);
  color: #ffffff;
  box-shadow: 0 14px 28px rgba(47, 93, 230, 0.18);
}

.rating-chip.again,
.summary-chip.again {
  background: #ffe8e8;
  color: #ff4d4f;
}

.rating-chip.hard,
.summary-chip.hard {
  background: #ece7de;
  color: #7b6b56;
}

.rating-chip.good,
.summary-chip.good {
  background: #dbf2e2;
  color: #1f8a46;
}

.rating-chip.easy,
.summary-chip.easy {
  background: #dde8ff;
  color: #3663f0;
}

.summary-chip {
  padding: 0.55rem 0.85rem;
  font-size: 0.92rem;
  font-weight: 600;
}

.empty-state {
  gap: 0.8rem;
  text-align: center;
}

.empty-state h2 {
  font-size: 1.6rem;
  font-weight: 700;
}

.empty-state p {
  max-width: 40ch;
  color: var(--color-text-muted);
}

.link-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.error-banner {
  margin: 0 1.4rem;
  padding: 0.95rem 1rem;
  border-radius: 16px;
  background: #fff1f0;
  color: #c24144;
}

@media (max-width: 720px) {
  .study-card {
    min-height: 220px;
    padding: 1.5rem;
  }

  .study-card h1 {
    font-size: 1.6rem;
  }
}
</style>
