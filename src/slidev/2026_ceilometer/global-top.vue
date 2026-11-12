<!-- Slide number bottom right, on all slides except the title slide and the blank drawing pages.
     global-top (not global-bottom): slides with their own background would cover it.
     Intern slides (presenter only, dropped from the export) are not counted, so the numbers match the PDF.
     Same file as in da_instructor/slidev. -->
<script setup lang="ts">
import { computed } from 'vue'
import { useNav } from '@slidev/client'

const { slides, currentSlideNo } = useNav()
const fm = (s: any) => s?.meta?.slide?.frontmatter ?? {}
const isIntern = (s: any) => fm(s).intern === true || fm(s).intern === 'true'
const number = computed(() => slides.value.slice(0, currentSlideNo.value).filter(s => !isIntern(s)).length)
const total = computed(() => slides.value.filter(s => !isIntern(s) && !('blank' in fm(s))).length)
</script>

<template>
  <div v-if="$nav.currentPage > 1 && !$nav.currentSlideRoute?.meta?.slide?.frontmatter?.blank && !isIntern($nav.currentSlideRoute)"
       class="absolute bottom-3 right-5 text-sm opacity-60 pointer-events-none">
    {{ number }} / {{ total }}
  </div>
</template>
