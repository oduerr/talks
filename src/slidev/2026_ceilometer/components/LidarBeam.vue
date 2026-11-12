<!-- Raum-Zeit-Bild eines Chips: Laser feuert in Chip 0, die Wolke streut einen kleinen Teil zurück,
     der kommt d0 Bins später an. Hintergrund-Photonen fallen in jedes Bin.
     Waagrecht: Zeit in Bins (100 ns), senkrecht: Höhe. Muster schematisch, nicht die echte m-Folge.
     Läuft beim Betreten der Folie einmal durch und bleibt auf dem letzten Bild stehen (kein Wiederholen).
     Prop `at` (0..1) friert die Animation an einer Stelle ein (für Export/Prüfung). -->
<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'
import { onSlideEnter } from '@slidev/client'

const props = defineProps<{ at?: number }>()

const nBins = 16, x0 = 34, w = 31, yBin = 268, hBin = 26, yCloud = 58, d0 = 9
const c = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1]   // schematisch
const T = 7000                                               // ms für den einen Durchlauf

const cx = (k: number) => x0 + (k + 0.5) * w
const start = { x: cx(0), y: yBin }
const apex = { x: cx(0) + d0 * w / 2, y: yCloud }
const end = { x: cx(d0), y: yBin }

const p = ref(props.at ?? 0)
let raf = 0, t0 = 0
onSlideEnter(() => {                 // bei jedem Betreten der Folie einmal von vorn
  if (props.at !== undefined) return
  cancelAnimationFrame(raf); t0 = 0; p.value = 0
  const tick = (t: number) => {
    if (!t0) t0 = t
    p.value = Math.min(1, (t - t0) / T)
    if (p.value < 1) raf = requestAnimationFrame(tick)
  }
  raf = requestAnimationFrame(tick)
})
onBeforeUnmount(() => cancelAnimationFrame(raf))

const lerp = (a: number, b: number, u: number) => a + (b - a) * Math.min(1, Math.max(0, u))
const seg = (u0: number, u1: number) => Math.min(1, Math.max(0, (p.value - u0) / (u1 - u0)))

const upU = computed(() => seg(0.08, 0.38))
const downU = computed(() => seg(0.45, 0.75))
const restU = computed(() => seg(0.38, 0.6))
const fired = computed(() => p.value < 0.2)
const arrived = computed(() => p.value >= 0.75)
const split = computed(() => p.value >= 0.38)

const upPkt = computed(() => ({ x: lerp(start.x, apex.x, upU.value), y: lerp(start.y, apex.y, upU.value) }))
const downPkt = computed(() => ({ x: lerp(apex.x, end.x, downU.value), y: lerp(apex.y, end.y, downU.value) }))
const restPkt = computed(() => ({ x: lerp(apex.x, apex.x + 2.5 * w, restU.value), y: lerp(apex.y, apex.y - 45, restU.value) }))

// Hintergrund-Tropfen: Bin, Startphase (Bin d0 ist dabei)
const drops = [[2, 0.05], [12, 0.18], [5, 0.33], [9, 0.52], [14, 0.62], [7, 0.8], [0, 0.9], [10, 0.27]]
// einmaliger Fall: Start bei 0,75·Phase, Fallzeit 0,25, danach bleibt der Tropfen blass im Bin liegen
const dropPos = (k: number, ph: number) => {
  const u = (p.value - 0.75 * ph) / 0.25
  if (u < 0) return { x: cx(k), y: 14, o: 0 }
  return u <= 1 ? { x: cx(k), y: lerp(14, yBin + 6, u), o: 1 } : { x: cx(k), y: yBin + 6, o: Math.max(0.45, 1 - (u - 1) * 0.6) }
}
</script>

<template>
  <svg viewBox="0 0 560 345" class="w-full" style="font-family: inherit">
    <!-- Wolke -->
    <line :x1="x0" :y1="yCloud" :x2="x0 + nBins * w" :y2="yCloud" stroke="#8aa1b8" stroke-width="2" stroke-dasharray="6 4" />
    <text :x="x0 + nBins * w" :y="yCloud - 8" text-anchor="end" style="font-size:14px" fill="#55697d">Wolke in Höhe d₀ · 15 m</text>

    <!-- Höhenachse -->
    <line :x1="x0 - 14" :y1="yBin" :x2="x0 - 14" :y2="yCloud - 20" stroke="#999" marker-end="url(#ar)" />
    <text :x="x0 - 20" :y="(yBin + yCloud) / 2" style="font-size:13px" fill="#777" text-anchor="middle" :transform="`rotate(-90 ${x0 - 20} ${(yBin + yCloud) / 2})`">Höhe</text>

    <!-- Bins mit Muster -->
    <g v-for="k in nBins" :key="k">
      <rect :x="x0 + (k - 1) * w" :y="yBin" :width="w" :height="hBin"
            :style="{ fill: c[k - 1] ? '#7fb2dc' : '#e8eef5', stroke: '#fff', strokeWidth: 2 }" />
    </g>
    <rect :x="x0" :y="yBin" :width="w" :height="hBin" fill="none" :stroke="fired ? '#d9822b' : '#0070c0'" :stroke-width="fired ? 4 : 2" />
    <rect :x="x0 + d0 * w" :y="yBin" :width="w" :height="hBin" fill="none" stroke="#d9822b" stroke-width="2.5" />
    <text :x="cx(0)" :y="yBin + hBin + 16" text-anchor="middle" style="font-size:13px" fill="#333">0</text>
    <text :x="cx(d0)" :y="yBin + hBin + 16" text-anchor="middle" style="font-size:13px" fill="#333">d₀</text>
    <text :x="x0 + nBins * w" :y="yBin + hBin + 36" text-anchor="end" style="font-size:12px" fill="#777">Zeit → (1 Bin = 100 ns ≙ 15 m) · blau: c = 1</text>
    <text v-if="fired" :x="cx(0) + 16" :y="yBin - 34" style="font-size:13px" fill="#d9822b">c₀ = 1: Laser feuert</text>

    <!-- Strahl hoch -->
    <line :x1="start.x" :y1="start.y" :x2="upPkt.x" :y2="upPkt.y" stroke="#0070c0" stroke-width="5" stroke-linecap="round" />
    <circle v-if="!split" :cx="upPkt.x" :cy="upPkt.y" r="8" fill="#0070c0" />

    <!-- an der Wolke: der Großteil geht weiter, ein kleiner Teil kommt zurück -->
    <g v-if="split">
      <line :x1="apex.x" :y1="apex.y" :x2="restPkt.x" :y2="restPkt.y" stroke="#0070c0" stroke-width="5" opacity="0.25" stroke-linecap="round" />
      <text v-if="restU > 0.3" :x="apex.x + 2.6 * w" :y="apex.y - 30" style="font-size:12px" fill="#7a8da0">der Rest: weiter, absorbiert, seitlich</text>
      <line :x1="apex.x" :y1="apex.y" :x2="downPkt.x" :y2="downPkt.y" stroke="#d9822b" stroke-width="1.6" stroke-linecap="round" />
      <circle v-if="!arrived" :cx="downPkt.x" :cy="downPkt.y" r="3" fill="#d9822b" />
      <text :x="apex.x + 10" :y="apex.y + 26" style="font-size:13px" fill="#d9822b">winziger Teil zurück → s</text>
    </g>

    <!-- Hintergrund -->
    <g v-for="(dr, i) in drops" :key="'b' + i">
      <circle :cx="dropPos(dr[0], dr[1]).x" :cy="dropPos(dr[0], dr[1]).y" r="3.2" fill="#8c8c8c" :opacity="dropPos(dr[0], dr[1]).o" />
    </g>
    <text :x="x0" y="20" style="font-size:13px" fill="#777">b: Hintergrund fällt in jedes Bin (grau)</text>

    <!-- Ankunft -->
    <g v-if="arrived">
      <circle :cx="end.x" :cy="yBin + 13" r="5" fill="#d9822b" />
      <text :x="end.x + 22" :y="yBin - 12" style="font-size:14px; font-weight:700" fill="#d9822b">X<tspan baseline-shift="sub" style="font-size:10px">d₀</tspan> ~ Pois(b + s)</text>
    </g>

    <defs>
      <marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#999" />
      </marker>
    </defs>
  </svg>
</template>
