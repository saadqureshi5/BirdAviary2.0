<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

export interface PedigreeNode {
  id: number
  ring_id: string | null
  name: string | null
  mutation: string | null
  sex: string | null
  photo_url: string | null
  father: PedigreeNode | null
  mother: PedigreeNode | null
}

defineOptions({ name: 'PedigreeTree' })

const props = withDefaults(defineProps<{
  node: PedigreeNode | null
  depth?: number
  maxDepth?: number
  relation?: 'self' | 'father' | 'mother'
}>(), {
  depth: 0,
  maxDepth: 4,
  relation: 'self',
})

const router = useRouter()

const showParents = computed(() => {
  return (
    props.node != null &&
    props.depth < props.maxDepth &&
    (props.node.father != null || props.node.mother != null)
  )
})

const sexIcon = computed(() => {
  if (!props.node?.sex) return '?'
  return props.node.sex === 'male' ? '♂' : props.node.sex === 'female' ? '♀' : '?'
})

const sexClass = computed(() => {
  if (!props.node?.sex) return 'unknown'
  return props.node.sex === 'male' ? 'male' : props.node.sex === 'female' ? 'female' : 'unknown'
})

function navigateToProfile() {
  if (props.node?.id) {
    router.push(`/birds/${props.node.id}`)
  }
}
</script>

<template>
  <div class="pedigree-branch" :style="{ '--anim-delay': `${depth * 0.12}s` }">
    <!-- ── Node Card ──────────────────────────────────── -->
    <div
      class="node-card"
      :class="[
        `sex-${sexClass}`,
        {
          'root-node': depth === 0,
          'unknown-node': !node,
          clickable: !!node?.id,
        },
      ]"
      @click="navigateToProfile"
      :title="node ? `${node.ring_id} — Click to view profile` : 'Unknown ancestor'"
    >
      <!-- Relation tag (Sire / Dam) -->
      <div v-if="depth > 0" class="relation-label" :class="`rel-${sexClass}`">
        {{ relation === 'father' ? 'Sire' : 'Dam' }}
      </div>

      <!-- Gen badge on root -->
      <div v-if="depth === 0" class="gen-badge">Subject</div>

      <!-- Avatar -->
      <div class="node-avatar" :class="`av-${sexClass}`">
        <span class="avatar-icon">{{ node ? sexIcon : '?' }}</span>
      </div>

      <!-- Info -->
      <div class="node-info">
        <div class="node-ring">{{ node?.ring_id || 'Unknown' }}</div>
        <div class="node-detail">{{ node?.mutation || '—' }}</div>
      </div>

      <!-- Tiny chevron when expandable -->
      <svg
        v-if="showParents"
        class="expand-chevron"
        xmlns="http://www.w3.org/2000/svg"
        width="12"
        height="12"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="m9 18 6-6-6-6" />
      </svg>
    </div>

    <!-- ── Parent branches with connectors ─────────── -->
    <template v-if="showParents">
      <div class="h-connector"></div>

      <div class="parent-tracks">
        <!-- Father (top) -->
        <div class="track track-top">
          <PedigreeTree
            :node="node!.father"
            :depth="depth + 1"
            :maxDepth="maxDepth"
            relation="father"
          />
        </div>

        <!-- Mother (bottom) -->
        <div class="track track-bottom">
          <PedigreeTree
            :node="node!.mother"
            :depth="depth + 1"
            :maxDepth="maxDepth"
            relation="mother"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
/* ═══════════════════════════════════════════════
   BRANCH LAYOUT
   ═══════════════════════════════════════════════ */
.pedigree-branch {
  display: flex;
  align-items: center;
  animation: branchIn 0.45s ease-out both;
  animation-delay: var(--anim-delay, 0s);
}

@keyframes branchIn {
  from {
    opacity: 0;
    transform: translateX(-14px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* ═══════════════════════════════════════════════
   NODE CARD
   ═══════════════════════════════════════════════ */
.node-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  min-width: 152px;
  max-width: 192px;
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.07);
  background: rgba(22, 25, 40, 0.8);
  backdrop-filter: blur(14px);
  flex-shrink: 0;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}

.node-card.root-node {
  min-width: 196px;
  max-width: 240px;
  padding: 0.675rem 1rem;
  border-width: 2px;
}

.node-card.clickable {
  cursor: pointer;
}

.node-card.clickable:hover {
  transform: translateY(-2px) scale(1.015);
  z-index: 5;
}

.node-card.unknown-node {
  border-style: dashed;
  opacity: 0.4;
  cursor: default;
}

/* ─ Sex accent colours ─ */
.node-card.sex-male {
  border-color: rgba(96, 165, 250, 0.22);
}
.node-card.sex-female {
  border-color: rgba(244, 114, 182, 0.22);
}
.node-card.sex-unknown {
  border-color: rgba(148, 163, 184, 0.14);
}

.node-card.sex-male.clickable:hover {
  border-color: rgba(96, 165, 250, 0.55);
  box-shadow: 0 0 20px rgba(96, 165, 250, 0.12), 0 8px 24px rgba(0, 0, 0, 0.3);
}
.node-card.sex-female.clickable:hover {
  border-color: rgba(244, 114, 182, 0.55);
  box-shadow: 0 0 20px rgba(244, 114, 182, 0.12), 0 8px 24px rgba(0, 0, 0, 0.3);
}
.node-card.sex-unknown.clickable:hover {
  border-color: rgba(148, 163, 184, 0.4);
  box-shadow: 0 0 14px rgba(148, 163, 184, 0.08), 0 8px 24px rgba(0, 0, 0, 0.3);
}

/* Root highlight */
.node-card.root-node.sex-male {
  border-color: rgba(96, 165, 250, 0.4);
  box-shadow: 0 0 22px rgba(96, 165, 250, 0.1);
}
.node-card.root-node.sex-female {
  border-color: rgba(244, 114, 182, 0.4);
  box-shadow: 0 0 22px rgba(244, 114, 182, 0.1);
}
.node-card.root-node.sex-unknown {
  border-color: rgba(20, 184, 166, 0.35);
  box-shadow: 0 0 22px rgba(20, 184, 166, 0.08);
}

/* ═══════════════════════════════════════════════
   RELATION LABEL / GEN BADGE
   ═══════════════════════════════════════════════ */
.relation-label {
  position: absolute;
  top: -0.5rem;
  left: 0.625rem;
  font-size: 0.55rem;
  font-weight: 700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  padding: 0.06rem 0.4rem;
  border-radius: 0.25rem;
  line-height: 1.35;
}
.rel-male {
  background: rgba(96, 165, 250, 0.18);
  color: rgb(147, 197, 253);
}
.rel-female {
  background: rgba(244, 114, 182, 0.18);
  color: rgb(249, 168, 212);
}
.rel-unknown {
  background: rgba(148, 163, 184, 0.12);
  color: rgb(148, 163, 184);
}

.gen-badge {
  position: absolute;
  top: -0.55rem;
  right: 0.5rem;
  font-size: 0.5rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 0.06rem 0.4rem;
  border-radius: 0.25rem;
  background: rgba(20, 184, 166, 0.2);
  color: rgb(94, 234, 212);
  border: 1px solid rgba(20, 184, 166, 0.3);
}

/* ═══════════════════════════════════════════════
   AVATAR
   ═══════════════════════════════════════════════ */
.node-avatar {
  width: 1.875rem;
  height: 1.875rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  font-weight: 700;
}
.root-node .node-avatar {
  width: 2.375rem;
  height: 2.375rem;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-icon {
  font-size: 1rem;
}
.root-node .avatar-icon {
  font-size: 1.2rem;
}

.av-male {
  background: rgba(96, 165, 250, 0.12);
  border: 1px solid rgba(96, 165, 250, 0.22);
  color: rgb(96, 165, 250);
}
.av-female {
  background: rgba(244, 114, 182, 0.12);
  border: 1px solid rgba(244, 114, 182, 0.22);
  color: rgb(244, 114, 182);
}
.av-unknown {
  background: rgba(148, 163, 184, 0.08);
  border: 1px solid rgba(148, 163, 184, 0.14);
  color: rgb(148, 163, 184);
}

/* ═══════════════════════════════════════════════
   NODE INFO
   ═══════════════════════════════════════════════ */
.node-info {
  min-width: 0;
  flex: 1;
}

.node-ring {
  font-size: 0.775rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.92);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.root-node .node-ring {
  font-size: 0.9rem;
}

.node-detail {
  font-size: 0.625rem;
  color: rgba(148, 163, 184, 0.7);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 1px;
}

.expand-chevron {
  color: rgba(148, 163, 184, 0.35);
  flex-shrink: 0;
}

/* ═══════════════════════════════════════════════
   CONNECTORS
   ═══════════════════════════════════════════════ */
.h-connector {
  width: 1.25rem;
  height: 2px;
  flex-shrink: 0;
  background: linear-gradient(to right, rgba(20, 184, 166, 0.3), rgba(20, 184, 166, 0.15));
  border-radius: 1px;
}

.parent-tracks {
  display: flex;
  flex-direction: column;
}

.track {
  position: relative;
  padding-left: 1.25rem;
}

/* Father (top) track — vertical line DOWN from centre + horizontal at centre */
.track-top {
  padding-bottom: 0.35rem;
}
.track-top::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  bottom: 0;
  width: 2px;
  background: linear-gradient(
    to bottom,
    rgba(96, 165, 250, 0.28),
    rgba(168, 140, 218, 0.2)
  );
  border-radius: 1px;
}
.track-top::after {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 1.25rem;
  height: 2px;
  background: rgba(96, 165, 250, 0.25);
  border-radius: 1px;
}

/* Mother (bottom) track — vertical line UP from centre + horizontal at centre */
.track-bottom {
  padding-top: 0.35rem;
}
.track-bottom::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 50%;
  width: 2px;
  background: linear-gradient(
    to bottom,
    rgba(168, 140, 218, 0.2),
    rgba(244, 114, 182, 0.28)
  );
  border-radius: 1px;
}
.track-bottom::after {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 1.25rem;
  height: 2px;
  background: rgba(244, 114, 182, 0.25);
  border-radius: 1px;
}

/* ═══════════════════════════════════════════════
   PROGRESSIVE SIZE REDUCTION  (deeper → smaller)
   ═══════════════════════════════════════════════ */

/* — depth 2+ — */
.pedigree-branch .pedigree-branch .node-card {
  min-width: 134px;
  max-width: 168px;
  padding: 0.4rem 0.625rem;
}

/* — depth 3+ — */
.pedigree-branch .pedigree-branch .pedigree-branch .node-card {
  min-width: 118px;
  max-width: 152px;
  padding: 0.35rem 0.5rem;
}
.pedigree-branch .pedigree-branch .pedigree-branch .node-avatar {
  width: 1.5rem;
  height: 1.5rem;
}
.pedigree-branch .pedigree-branch .pedigree-branch .avatar-icon {
  font-size: 0.8rem;
}
.pedigree-branch .pedigree-branch .pedigree-branch .node-ring {
  font-size: 0.7rem;
}
.pedigree-branch .pedigree-branch .pedigree-branch .node-detail {
  font-size: 0.55rem;
}

/* — depth 4+ — */
.pedigree-branch .pedigree-branch .pedigree-branch .pedigree-branch .node-card {
  min-width: 100px;
  max-width: 134px;
  padding: 0.3rem 0.4rem;
  gap: 0.35rem;
}
.pedigree-branch .pedigree-branch .pedigree-branch .pedigree-branch .node-avatar {
  width: 1.25rem;
  height: 1.25rem;
}
.pedigree-branch .pedigree-branch .pedigree-branch .pedigree-branch .avatar-icon {
  font-size: 0.65rem;
}
.pedigree-branch .pedigree-branch .pedigree-branch .pedigree-branch .node-ring {
  font-size: 0.625rem;
}
.pedigree-branch .pedigree-branch .pedigree-branch .pedigree-branch .node-detail {
  display: none;
}
.pedigree-branch .pedigree-branch .pedigree-branch .pedigree-branch .relation-label {
  font-size: 0.45rem;
  padding: 0.02rem 0.3rem;
}

/* Connector scale-down at depth 3+ */
.pedigree-branch .pedigree-branch .pedigree-branch .h-connector {
  width: 0.875rem;
}
.pedigree-branch .pedigree-branch .pedigree-branch .track {
  padding-left: 0.875rem;
}
.pedigree-branch .pedigree-branch .pedigree-branch .track-top::after,
.pedigree-branch .pedigree-branch .pedigree-branch .track-bottom::after {
  width: 0.875rem;
}

/* Connector scale-down at depth 4+ */
.pedigree-branch .pedigree-branch .pedigree-branch .pedigree-branch .h-connector {
  width: 0.625rem;
}
.pedigree-branch .pedigree-branch .pedigree-branch .pedigree-branch .track {
  padding-left: 0.625rem;
}
.pedigree-branch .pedigree-branch .pedigree-branch .pedigree-branch .track-top::after,
.pedigree-branch .pedigree-branch .pedigree-branch .pedigree-branch .track-bottom::after {
  width: 0.625rem;
}
.pedigree-branch .pedigree-branch .pedigree-branch .pedigree-branch .track-top,
.pedigree-branch .pedigree-branch .pedigree-branch .pedigree-branch .track-bottom {
  padding-top: 0.2rem;
  padding-bottom: 0.2rem;
}
</style>
