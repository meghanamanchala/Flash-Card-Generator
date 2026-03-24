<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'

import { api, type LearningUnit } from '../services/api'

const decks = ref<LearningUnit[]>([])
const isLoading = ref(true)
const errorMessage = ref('')
const searchQuery = ref('')

const filteredDecks = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()

  if (!query) {
    return decks.value
  }

  return decks.value.filter((deck) => {
    return (
      deck.title.toLowerCase().includes(query) ||
      deck.raw_content.toLowerCase().includes(query)
    )
  })
})

function formatRelativeTime(value: string) {
  const createdAt = new Date(value)
  const diffInMinutes = Math.round((createdAt.getTime() - Date.now()) / 60000)
  const formatter = new Intl.RelativeTimeFormat(undefined, { numeric: 'auto' })

  const ranges: Array<[Intl.RelativeTimeFormatUnit, number]> = [
    ['year', 525600],
    ['month', 43200],
    ['week', 10080],
    ['day', 1440],
    ['hour', 60],
    ['minute', 1],
  ]

  for (const [unit, minutes] of ranges) {
    if (Math.abs(diffInMinutes) >= minutes || unit === 'minute') {
      return formatter.format(Math.round(diffInMinutes / minutes), unit)
    }
  }

  return 'just now'
}

function getDeckPattern(deck: LearningUnit) {
  const seed = deck.id + deck.flashcards.length
  return Array.from({ length: 12 }, (_, index) => {
    const value = (seed * (index + 3) + index * 7) % 4
    return value
  })
}

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

onMounted(() => {
  void loadDecks()
})
</script>

<template>
  <main class="dashboard-page">
    <section class="dashboard-frame">
      <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>

      <label class="search-shell">
        <span class="search-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" role="presentation">
            <circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" stroke-width="1.8" />
            <path d="M16 16l4 4" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.8" />
          </svg>
        </span>
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search decks..."
          aria-label="Search decks"
        />
      </label>

      <div v-if="isLoading" class="deck-grid loading-grid">
        <article v-for="index in 4" :key="index" class="deck-card skeleton-card">
          <span class="skeleton-line title" />
          <span class="skeleton-line meta" />
          <span class="skeleton-line bars" />
        </article>
      </div>

      <div v-else-if="filteredDecks.length" class="deck-grid">
        <RouterLink
          v-for="deck in filteredDecks"
          :key="deck.id"
          class="deck-card"
          :to="{ name: 'deck', params: { id: deck.id.toString() } }"
        >
          <h2>{{ deck.title }}</h2>

          <div class="deck-meta">
            <span class="meta-chip">
              <svg viewBox="0 0 24 24" role="presentation">
                <path
                  d="M6.5 7.5 12 4l5.5 3.5L12 11ZM6.5 11.5 12 15l5.5-3.5M6.5 15.5 12 19l5.5-3.5"
                  fill="none"
                  stroke="currentColor"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.6"
                />
              </svg>
              <span>{{ deck.flashcards.length }} cards</span>
            </span>

            <span class="meta-chip">
              <svg viewBox="0 0 24 24" role="presentation">
                <circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="1.6" />
                <path d="M12 8v4l2.5 1.5" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1.6" />
              </svg>
              <span>{{ formatRelativeTime(deck.created_at) }}</span>
            </span>
          </div>

          <div class="deck-pattern" aria-hidden="true">
            <span
              v-for="(value, index) in getDeckPattern(deck)"
              :key="`${deck.id}-${index}`"
              class="pattern-node"
              :class="`size-${value}`"
            />
          </div>
        </RouterLink>

        <RouterLink class="create-card" to="/create">
          <span class="create-plus">+</span>
          <span>Create deck</span>
        </RouterLink>
      </div>

      <div v-else class="empty-state">
        <p class="empty-title">{{ decks.length ? 'No decks matched your search' : 'Create your first deck' }}</p>
        <p class="empty-copy">
          {{
            decks.length
              ? 'Try a different keyword or clear the search field.'
              : 'Paste your notes, generate cards, and your library will show up here.'
          }}
        </p>
        <RouterLink class="empty-link" to="/create">New Deck</RouterLink>
      </div>
    </section>
  </main>
</template>

<style scoped>
.dashboard-page {
  display: grid;
}

.dashboard-frame {
  min-height: calc(100vh - 180px);
  padding: 1.6rem;
  border: 1px solid var(--color-border);
  border-radius: 28px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(245, 247, 252, 0.98)),
    var(--color-surface);
  box-shadow: var(--color-shadow);
}

.search-shell {
  position: relative;
  display: block;
  margin-bottom: 1.5rem;
}

.search-shell input {
  width: 100%;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 18px;
  padding: 1rem 1rem 1rem 3rem;
  background: var(--color-panel);
  color: var(--color-text);
}

.search-shell input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 108, 255, 0.12);
}

.search-icon {
  position: absolute;
  top: 50%;
  left: 1rem;
  display: inline-grid;
  place-items: center;
  width: 1.25rem;
  height: 1.25rem;
  color: var(--color-text-muted);
  transform: translateY(-50%);
}

.search-icon svg {
  width: 1.25rem;
  height: 1.25rem;
}

.deck-grid {
  display: grid;
  gap: 1rem;
}

.deck-card,
.create-card {
  min-height: 148px;
  padding: 1.35rem;
  border: 1px solid var(--color-border);
  border-radius: 20px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(242, 246, 252, 0.94)),
    var(--color-surface);
  box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08);
}

.deck-card {
  display: grid;
  gap: 1rem;
}

.deck-card h2 {
  font-size: 1.55rem;
  font-weight: 700;
  color: var(--color-heading);
}

.deck-meta {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  flex-wrap: wrap;
  color: var(--color-text-muted);
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.98rem;
}

.meta-chip svg {
  width: 1rem;
  height: 1rem;
}

.deck-pattern {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: auto;
  color: var(--color-primary-soft-strong);
}

.pattern-node {
  display: block;
  flex: 1;
  min-width: 0.75rem;
  height: 0.34rem;
  border-radius: 999px;
  background: currentColor;
}

.pattern-node.size-1 {
  height: 1rem;
  max-width: 1.5rem;
}

.pattern-node.size-2 {
  height: 1.35rem;
  max-width: 1.5rem;
}

.pattern-node.size-3 {
  height: 1.65rem;
  max-width: 1.5rem;
}

.create-card {
  display: grid;
  place-items: center;
  gap: 0.4rem;
  border-style: dashed;
  background: rgba(245, 247, 252, 0.74);
  color: var(--color-text);
  box-shadow: none;
}

.create-plus {
  font-size: 2.4rem;
  line-height: 1;
}

.loading-grid {
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.skeleton-card {
  pointer-events: none;
}

.skeleton-line {
  display: block;
  border-radius: 999px;
  background: linear-gradient(90deg, #e6ebf5, #dce4f2, #e6ebf5);
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}

.skeleton-line.title {
  width: 70%;
  height: 1.4rem;
}

.skeleton-line.meta {
  width: 52%;
  height: 1rem;
}

.skeleton-line.bars {
  width: 100%;
  height: 1.25rem;
  margin-top: auto;
}

.empty-state {
  min-height: 320px;
  display: grid;
  place-items: center;
  gap: 0.8rem;
  text-align: center;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-heading);
}

.empty-copy {
  max-width: 42ch;
  color: var(--color-text-muted);
}

.empty-link {
  padding: 0.85rem 1.1rem;
  border-radius: 14px;
  background: linear-gradient(180deg, #3b6cff, #2f5de6);
  color: #ffffff;
  font-weight: 700;
}

.error-banner {
  margin-bottom: 1rem;
  padding: 0.95rem 1rem;
  border-radius: 16px;
  background: #fff1f0;
  color: #c24144;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }

  100% {
    background-position: -200% 0;
  }
}

@media (min-width: 860px) {
  .deck-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .dashboard-frame {
    padding: 1rem;
  }

  .deck-card h2 {
    font-size: 1.3rem;
  }
}
</style>
