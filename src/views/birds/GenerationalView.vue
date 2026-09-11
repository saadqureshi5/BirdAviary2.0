<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '@/composables/useApi'
import PedigreeTree from '@/components/birds/PedigreeTree.vue'
import type { Bird } from '@/types'
import type { PedigreeNode } from '@/components/birds/PedigreeTree.vue'

const route = useRoute()
const router = useRouter()
const { get, loading } = useApi()

const birdId = computed(() => route.params.id as string)
const activeTab = ref<'ancestry' | 'descendants'>('ancestry')
const depth = ref(3)
const bird = ref<Bird | null>(null)
const ancestryTree = ref<PedigreeNode | null>(null)
const descendantsTree = ref<any>(null)
const treeLoading = ref(false)

// Depth options
const depthOptions = [2, 3, 4, 5]

onMounted(async () => {
  await Promise.all([fetchBird(), fetchTree()])
})

watch([activeTab, depth], () => {
  fetchTree()
})

async function fetchBird() {
  try {
    bird.value = await get<Bird>(`/birds/${birdId.value}`)
  } catch (e) {
    console.error('Failed to fetch bird', e)
  }
}

async function fetchTree() {
  treeLoading.value = true
  try {
    if (activeTab.value === 'ancestry') {
      ancestryTree.value = await get<PedigreeNode>(
        `/birds/${birdId.value}/ancestry/tree?depth=${depth.value}`
      )
    } else {
      descendantsTree.value = await get<any>(
        `/birds/${birdId.value}/descendants/tree?depth=${depth.value}`
      )
    }
  } catch (e) {
    console.error('Failed to fetch tree', e)
  } finally {
    treeLoading.value = false
  }
}

const sexIcon = computed(() => {
  if (!bird.value?.sex) return '?'
  return bird.value.sex === 'male' ? '♂' : bird.value.sex === 'female' ? '♀' : '?'
})

const sexColor = computed(() => {
  if (!bird.value?.sex) return 'text-slate-400'
  return bird.value.sex === 'male' ? 'text-blue-400' : bird.value.sex === 'female' ? 'text-pink-400' : 'text-slate-400'
})
</script>

<template>
  <div class="space-y-6 animate-fade-in pb-10">
    <!-- ── Breadcrumb ─────────────────────────────── -->
    <nav class="flex text-sm text-slate-400 items-center gap-2">
      <router-link to="/" class="hover:text-white transition-colors">Dashboard</router-link>
      <span class="text-slate-600">/</span>
      <router-link to="/birds" class="hover:text-white transition-colors">Birds</router-link>
      <span class="text-slate-600">/</span>
      <router-link v-if="bird" :to="`/birds/${bird.id}`" class="hover:text-white transition-colors">
        {{ bird.ring_id }}
      </router-link>
      <span v-if="bird" class="text-slate-600">/</span>
      <span class="text-white font-medium">Pedigree</span>
    </nav>

    <!-- ── Bird Summary Header ────────────────────── -->
    <div class="glass-card p-5">
      <div v-if="bird" class="flex items-center gap-5">
        <!-- Avatar -->
        <div class="w-14 h-14 rounded-xl overflow-hidden border-2 border-white/10 flex-shrink-0 bg-surface-800">
          <img v-if="bird.photo_url" :src="'/' + bird.photo_url" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-surface-700 to-surface-800">
            <span class="text-2xl opacity-30">🐦</span>
          </div>
        </div>

        <!-- Info -->
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2 flex-wrap">
            <h1 class="text-xl font-bold text-white">{{ bird.ring_id }}</h1>
            <span :class="sexColor" class="text-xl font-bold">{{ sexIcon }}</span>
            <span v-if="bird.name" class="text-slate-400 text-sm">{{ bird.name }}</span>
          </div>
          <div class="text-sm text-slate-400 mt-0.5">
            {{ bird.mutation || 'No mutation' }}
            <span v-if="bird.cage_number" class="ml-3 text-slate-500">Cage {{ bird.cage_number }}</span>
          </div>
        </div>

        <!-- Back button -->
        <button
          @click="router.push(`/birds/${bird.id}`)"
          class="btn-secondary flex items-center gap-2 text-sm flex-shrink-0"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
          Profile
        </button>
      </div>

      <!-- Loading state -->
      <div v-else class="flex items-center justify-center py-4">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    </div>

    <!-- ── Controls Bar ───────────────────────────── -->
    <div class="glass-card p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <!-- Tab toggle -->
      <div class="flex items-center bg-surface-900/60 rounded-lg p-1 border border-white/5">
        <button
          @click="activeTab = 'ancestry'"
          class="tab-btn"
          :class="{ active: activeTab === 'ancestry' }"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 18a2 2 0 0 0-2-2H9a2 2 0 0 0-2 2"/><rect width="18" height="18" x="3" y="4" rx="2"/><circle cx="12" cy="10" r="2"/><line x1="8" x2="8" y1="2" y2="4"/><line x1="16" x2="16" y1="2" y2="4"/></svg>
          Ancestry
        </button>
        <button
          @click="activeTab = 'descendants'"
          class="tab-btn"
          :class="{ active: activeTab === 'descendants' }"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          Descendants
        </button>
      </div>

      <!-- Depth selector -->
      <div class="flex items-center gap-3">
        <span class="text-xs text-slate-400 uppercase tracking-wider font-medium">Generations</span>
        <div class="flex items-center bg-surface-900/60 rounded-lg p-1 border border-white/5">
          <button
            v-for="d in depthOptions"
            :key="d"
            @click="depth = d"
            class="depth-btn"
            :class="{ active: depth === d }"
          >
            {{ d }}
          </button>
        </div>
      </div>

      <!-- Legend -->
      <div class="flex items-center gap-4 text-xs text-slate-400">
        <div class="flex items-center gap-1.5">
          <div class="w-2.5 h-2.5 rounded-sm bg-blue-400/30 border border-blue-400/40"></div>
          Male
        </div>
        <div class="flex items-center gap-1.5">
          <div class="w-2.5 h-2.5 rounded-sm bg-pink-400/30 border border-pink-400/40"></div>
          Female
        </div>
        <div class="flex items-center gap-1.5">
          <div class="w-2.5 h-2.5 rounded-sm bg-slate-400/20 border border-slate-400/30 border-dashed"></div>
          Unknown
        </div>
      </div>
    </div>

    <!-- ── Tree Container ─────────────────────────── -->
    <div class="glass-card p-6 min-h-[400px] relative">
      <!-- Loading overlay -->
      <div v-if="treeLoading" class="absolute inset-0 flex items-center justify-center bg-surface-900/50 backdrop-blur-sm rounded-xl z-10">
        <div class="flex flex-col items-center gap-3">
          <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-500"></div>
          <span class="text-sm text-slate-400">Loading {{ activeTab === 'ancestry' ? 'ancestry' : 'descendants' }} tree…</span>
        </div>
      </div>

      <!-- Ancestry Tree -->
      <div v-if="activeTab === 'ancestry'" class="overflow-x-auto overflow-y-auto pb-4 pt-2">
        <div v-if="ancestryTree" class="inline-block min-w-max pl-2 pt-4 pb-4">
          <PedigreeTree :node="ancestryTree" :maxDepth="depth" />
        </div>
        <div v-else-if="!treeLoading" class="flex flex-col items-center justify-center py-16 text-center">
          <div class="w-16 h-16 rounded-full bg-surface-800 flex items-center justify-center mb-4 border border-white/10">
            <span class="text-2xl opacity-40">🌳</span>
          </div>
          <h3 class="text-lg font-medium text-white mb-2">No Ancestry Data</h3>
          <p class="text-slate-400 max-w-sm text-sm">This bird has no recorded parents. Add parent information in the bird profile to build the pedigree tree.</p>
          <button @click="router.push(`/birds/${birdId}`)" class="btn-primary mt-4 text-sm">
            Edit Bird Profile
          </button>
        </div>
      </div>

      <!-- Descendants Tree -->
      <div v-if="activeTab === 'descendants'" class="overflow-x-auto overflow-y-auto pb-4 pt-2">
        <div v-if="descendantsTree?.pairings?.length > 0" class="inline-block min-w-max pl-2 pt-4 pb-4">
          <!-- Iterate over each pairing group -->
          <div v-for="(pairing, pIdx) in descendantsTree.pairings" :key="pIdx" class="mb-8 last:mb-0">
            <!-- Pairing Header: Root Bird × Partner -->
            <div class="flex items-center gap-3 mb-4">
              <!-- Root bird node -->
              <div class="desc-node root-desc-node">
                <div class="desc-avatar" :class="bird?.sex === 'male' ? 'desc-av-male' : bird?.sex === 'female' ? 'desc-av-female' : 'desc-av-unknown'">
                  {{ sexIcon }}
                </div>
                <div>
                  <div class="desc-ring">{{ descendantsTree.ring_id }}</div>
                  <div class="desc-name">{{ descendantsTree.name || descendantsTree.mutation || '—' }}</div>
                </div>
              </div>

              <!-- Cross symbol -->
              <span class="text-slate-500 text-lg font-bold">×</span>

              <!-- Partner node -->
              <div
                v-if="pairing.partner"
                class="desc-node partner-node"
                @click="router.push(`/birds/${pairing.partner.id}`)"
              >
                <div class="desc-avatar" :class="pairing.partner.sex === 'male' ? 'desc-av-male' : pairing.partner.sex === 'female' ? 'desc-av-female' : 'desc-av-unknown'">
                  {{ pairing.partner.sex === 'male' ? '♂' : pairing.partner.sex === 'female' ? '♀' : '?' }}
                </div>
                <div>
                  <div class="desc-ring">{{ pairing.partner.ring_id || 'Unknown' }}</div>
                  <div class="desc-name">{{ pairing.partner.name || pairing.partner.mutation || '—' }}</div>
                </div>
              </div>
              <div v-else class="desc-node partner-node partner-unknown">
                <div class="desc-avatar desc-av-unknown">?</div>
                <div><div class="desc-ring">Unknown Partner</div></div>
              </div>
            </div>

            <!-- Offspring from this pairing -->
            <div class="desc-children ml-6">
              <div
                v-for="child in pairing.children"
                :key="child.id"
                class="desc-child-branch"
              >
                <div
                  class="desc-node"
                  @click="router.push(`/birds/${child.id}`)"
                >
                  <div class="desc-avatar" :class="child.sex === 'male' ? 'desc-av-male' : child.sex === 'female' ? 'desc-av-female' : 'desc-av-unknown'">
                    {{ child.sex === 'male' ? '♂' : child.sex === 'female' ? '♀' : '?' }}
                  </div>
                  <div>
                    <div class="desc-ring">{{ child.ring_id || 'Unknown' }}</div>
                    <div class="desc-name">{{ child.name || child.mutation || '—' }}</div>
                  </div>
                </div>

                <!-- If this child also has pairings (grandchildren) -->
                <div v-if="child.pairings?.length" class="desc-grandchildren ml-4 mt-2">
                  <div v-for="(gPairing, gIdx) in child.pairings" :key="gIdx" class="mb-4 last:mb-0">
                    <!-- Grandchild pairing header -->
                    <div class="flex items-center gap-2 mb-2">
                      <span class="text-xs text-slate-500 font-medium">with</span>
                      <div
                        v-if="gPairing.partner"
                        class="desc-node desc-gc-node"
                        @click="router.push(`/birds/${gPairing.partner.id}`)"
                      >
                        <div class="desc-avatar desc-gc-avatar" :class="gPairing.partner.sex === 'male' ? 'desc-av-male' : gPairing.partner.sex === 'female' ? 'desc-av-female' : 'desc-av-unknown'">
                          {{ gPairing.partner.sex === 'male' ? '♂' : gPairing.partner.sex === 'female' ? '♀' : '?' }}
                        </div>
                        <div>
                          <div class="desc-ring" style="font-size: 0.7rem;">{{ gPairing.partner.ring_id || 'Unknown' }}</div>
                          <div class="desc-name">{{ gPairing.partner.name || gPairing.partner.mutation || '—' }}</div>
                        </div>
                      </div>
                      <div v-else class="desc-node desc-gc-node partner-unknown">
                        <div class="desc-avatar desc-gc-avatar desc-av-unknown">?</div>
                        <div><div class="desc-ring" style="font-size: 0.7rem;">Unknown</div></div>
                      </div>
                    </div>
                    <!-- Grandchildren -->
                    <div class="flex flex-wrap gap-1.5 ml-8">
                      <div
                        v-for="gc in gPairing.children"
                        :key="gc.id"
                        class="desc-node desc-gc-node"
                        @click="router.push(`/birds/${gc.id}`)"
                      >
                        <div class="desc-avatar desc-gc-avatar" :class="gc.sex === 'male' ? 'desc-av-male' : gc.sex === 'female' ? 'desc-av-female' : 'desc-av-unknown'">
                          {{ gc.sex === 'male' ? '♂' : gc.sex === 'female' ? '♀' : '?' }}
                        </div>
                        <div>
                          <div class="desc-ring" style="font-size: 0.7rem;">{{ gc.ring_id || 'Unknown' }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="!treeLoading" class="flex flex-col items-center justify-center py-16 text-center">
          <div class="w-16 h-16 rounded-full bg-surface-800 flex items-center justify-center mb-4 border border-white/10">
            <span class="text-2xl opacity-40">🐣</span>
          </div>
          <h3 class="text-lg font-medium text-white mb-2">No Descendants Found</h3>
          <p class="text-slate-400 max-w-sm text-sm">This bird doesn't have any recorded offspring yet. Offspring will appear here once they are added through the breeding module.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ── Tab buttons ─── */
.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.4rem 0.875rem;
  font-size: 0.8rem;
  font-weight: 500;
  border-radius: 0.5rem;
  color: rgba(148, 163, 184, 0.8);
  cursor: pointer;
  background: transparent;
  border: none;
  transition: all 0.2s ease;
  white-space: nowrap;
}
.tab-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.04);
}
.tab-btn.active {
  color: white;
  background: rgba(20, 184, 166, 0.15);
  box-shadow: 0 0 12px rgba(20, 184, 166, 0.1);
}

/* ── Depth buttons ─── */
.depth-btn {
  width: 2rem;
  height: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 0.375rem;
  color: rgba(148, 163, 184, 0.7);
  cursor: pointer;
  background: transparent;
  border: none;
  transition: all 0.2s ease;
}
.depth-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.04);
}
.depth-btn.active {
  color: rgb(94, 234, 212);
  background: rgba(20, 184, 166, 0.15);
}

/* ── Descendants tree ── */
.descendants-tree {
  display: flex;
  align-items: flex-start;
  gap: 0;
}

.desc-root {
  flex-shrink: 0;
}

.desc-children {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding-left: 2rem;
  border-left: 2px solid rgba(20, 184, 166, 0.15);
  margin-left: 1rem;
  position: relative;
}

.desc-child-branch {
  position: relative;
  padding-left: 1.25rem;
  display: flex;
  align-items: flex-start;
  gap: 0;
}

.desc-child-branch::before {
  content: '';
  position: absolute;
  left: -2px;
  top: 50%;
  width: 1.25rem;
  height: 2px;
  background: rgba(20, 184, 166, 0.15);
}

.desc-grandchildren {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding-left: 1.25rem;
  border-left: 2px solid rgba(148, 163, 184, 0.1);
  margin-left: 0.75rem;
}

.desc-node {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.75rem;
  border-radius: 0.625rem;
  border: 1px solid rgba(255, 255, 255, 0.07);
  background: rgba(22, 25, 40, 0.75);
  backdrop-filter: blur(12px);
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.desc-node:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border-color: rgba(20, 184, 166, 0.3);
}

.root-desc-node {
  cursor: default;
  border-width: 2px;
  border-color: rgba(20, 184, 166, 0.3);
  box-shadow: 0 0 16px rgba(20, 184, 166, 0.08);
}
.root-desc-node:hover {
  transform: none;
}

.partner-node {
  border-style: dashed;
  border-color: rgba(148, 163, 184, 0.25);
  background: rgba(30, 35, 55, 0.75);
}
.partner-node:hover {
  border-color: rgba(244, 114, 182, 0.3);
}
.partner-unknown {
  opacity: 0.6;
  cursor: default;
}
.partner-unknown:hover {
  transform: none;
  box-shadow: none;
}

.desc-gc-node {
  padding: 0.3rem 0.5rem;
}

.desc-avatar {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 0.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: 700;
  flex-shrink: 0;
}

.desc-gc-avatar {
  width: 1.375rem;
  height: 1.375rem;
  font-size: 0.7rem;
}

.desc-av-male {
  background: rgba(96, 165, 250, 0.12);
  border: 1px solid rgba(96, 165, 250, 0.2);
  color: rgb(96, 165, 250);
}
.desc-av-female {
  background: rgba(244, 114, 182, 0.12);
  border: 1px solid rgba(244, 114, 182, 0.2);
  color: rgb(244, 114, 182);
}
.desc-av-unknown {
  background: rgba(148, 163, 184, 0.08);
  border: 1px solid rgba(148, 163, 184, 0.12);
  color: rgb(148, 163, 184);
}

.desc-ring {
  font-size: 0.775rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
}

.desc-name {
  font-size: 0.625rem;
  color: rgba(148, 163, 184, 0.7);
  white-space: nowrap;
  margin-top: 1px;
}
</style>
