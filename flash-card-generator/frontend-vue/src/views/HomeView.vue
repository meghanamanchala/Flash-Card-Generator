<script setup lang="ts">
import axios from 'axios'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { api, type LearningUnit } from '../services/api'

const router = useRouter()
const decks = ref<LearningUnit[]>([])
const isLoading = ref(true)
const errorMessage = ref('')
const searchQuery = ref('')
const openMenuId = ref<number | null>(null)
const deletingDeckId = ref<number | null>(null)

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

function formatCreatedTimeline(value: string) {
  const createdAt = new Date(value).getTime()
  const diffInSeconds = Math.max(0, Math.floor((Date.now() - createdAt) / 1000))

  if (diffInSeconds < 60) {
    return 'Just now'
  }

  if (diffInSeconds < 3600) {
    return `${Math.floor(diffInSeconds / 60)}m ago`
  }

  if (diffInSeconds < 86400) {
    return `${Math.floor(diffInSeconds / 3600)}h ago`
  }

  if (diffInSeconds < 604800) {
    return `${Math.floor(diffInSeconds / 86400)}d ago`
  }

  if (diffInSeconds < 2592000) {
    return `${Math.floor(diffInSeconds / 604800)}w ago`
  }

  if (diffInSeconds < 31536000) {
    return `${Math.floor(diffInSeconds / 2592000)}mo ago`
  }

  return `${Math.floor(diffInSeconds / 31536000)}y ago`
}

function getDeckPattern(deck: LearningUnit) {
  const seed = deck.id + deck.generated_flashcards_count
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

function toggleDeckMenu(deckId: number) {
  openMenuId.value = openMenuId.value === deckId ? null : deckId
}

function closeDeckMenu() {
  openMenuId.value = null
}

function goToDeck(deckId: number) {
  closeDeckMenu()
  void router.push({
    name: 'deck',
    params: { id: deckId.toString() },
  })
}

function editDeck(deckId: number) {
  closeDeckMenu()
  void router.push({
    name: 'create',
    query: { deckId: deckId.toString() },
  })
}

async function deleteDeck(deck: LearningUnit) {
  const confirmed = window.confirm(`Delete "${deck.title}"? This will remove the deck and its cards.`)

  if (!confirmed) {
    return
  }

  deletingDeckId.value = deck.id
  closeDeckMenu()
  errorMessage.value = ''

  try {
    await api.delete(`/learning-units/${deck.id}/`)
    decks.value = decks.value.filter((item) => item.id !== deck.id)
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errorMessage.value =
        error.response?.data?.detail || 'This deck could not be deleted right now.'
    } else {
      errorMessage.value = 'Something went wrong while deleting the deck.'
    }
  } finally {
    deletingDeckId.value = null
  }
}

function handleDocumentClick() {
  closeDeckMenu()
}

onMounted(() => {
  window.addEventListener('click', handleDocumentClick)
  void loadDecks()
})

onBeforeUnmount(() => {
  window.removeEventListener('click', handleDocumentClick)
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
        <article
          v-for="deck in filteredDecks"
          :key="deck.id"
          class="deck-card"
        >
          <div class="deck-card-top">
            <button class="deck-main" type="button" @click="goToDeck(deck.id)">
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
                  <span>{{ deck.generated_flashcards_count }} cards</span>
                </span>

                <span class="meta-chip">
                  <svg viewBox="0 0 24 24" role="presentation">
                    <path
                      d="M7 4.75V6.5M17 4.75V6.5M5 9h14M6.75 6.5h10.5A1.75 1.75 0 0 1 19 8.25v9A1.75 1.75 0 0 1 17.25 19H6.75A1.75 1.75 0 0 1 5 17.25v-9A1.75 1.75 0 0 1 6.75 6.5Z"
                      fill="none"
                      stroke="currentColor"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="1.6"
                    />
                  </svg>
                  <span>{{ formatCreatedTimeline(deck.created_at) }}</span>
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
            </button>

            <div class="deck-menu-shell" @click.stop>
              <button
                class="menu-button"
                type="button"
                aria-label="Deck actions"
                :aria-expanded="openMenuId === deck.id"
                @click="toggleDeckMenu(deck.id)"
              >
                <span />
                <span />
                <span />
              </button>

              <div v-if="openMenuId === deck.id" class="deck-menu">
                <button class="menu-item" type="button" @click="goToDeck(deck.id)">Study</button>
                <button class="menu-item" type="button" @click="editDeck(deck.id)">Edit</button>
                <button
                  class="menu-item danger"
                  type="button"
                  :disabled="deletingDeckId === deck.id"
                  @click="deleteDeck(deck)"
                >
                  {{ deletingDeckId === deck.id ? 'Deleting...' : 'Delete' }}
                </button>
              </div>
            </div>
          </div>
        </article>

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
  padding: 1.6rem 0 0;
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
  position: relative;
}

.deck-card-top {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: start;
}

.deck-main {
  display: grid;
  gap: 1rem;
  padding: 0;
  border: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.deck-card h2 {
  font-size: 1.55rem;
  font-weight: 700;
  color: var(--color-heading);
}

.deck-menu-shell {
  position: relative;
}

.menu-button {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.18rem;
  width: 2.25rem;
  height: 2.25rem;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.92);
  color: var(--color-text-muted);
  cursor: pointer;
}

.menu-button span {
  width: 0.2rem;
  height: 0.2rem;
  border-radius: 999px;
  background: currentColor;
}

.deck-menu {
  position: absolute;
  top: calc(100% + 0.55rem);
  right: 0;
  z-index: 2;
  min-width: 140px;
  display: grid;
  padding: 0.4rem;
  border: 1px solid var(--color-border);
  border-radius: 16px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.99), rgba(244, 247, 252, 0.98)),
    var(--color-surface);
  box-shadow: 0 18px 32px rgba(15, 23, 42, 0.12);
}

.menu-item {
  padding: 0.75rem 0.85rem;
  border: 0;
  border-radius: 12px;
  background: transparent;
  color: var(--color-heading);
  text-align: left;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.menu-item:hover,
.menu-item:focus-visible {
  outline: none;
  background: rgba(59, 108, 255, 0.08);
}

.menu-item:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.menu-item.danger {
  color: #c24144;
}

.menu-item.danger:hover,
.menu-item.danger:focus-visible {
  background: rgba(194, 65, 68, 0.08);
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
    padding: 1rem 0 0;
  }

  .deck-card h2 {
    font-size: 1.3rem;
  }
}
</style>
