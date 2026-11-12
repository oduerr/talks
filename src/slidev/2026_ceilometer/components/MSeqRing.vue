<!-- Drei Ringe je Code (N = 31): innen derselbe Code um tau gedreht (= zyklisch verschoben), Mitte der Code fest,
     außen das Produkt c_k · c_{k-tau}. Orange = 1, grau = 0; in jedem Segment steht der Wert.
     In der Mitte die Summe des äußeren Rings (Überlapp); darunter der Überlapp für alle tau bis zum aktuellen.
     Links die m-Folge aus dem 5-Bit-Schieberegister x^5 + x^2 + 1, rechts ein fester Zufallscode mit ebenfalls 16 Einsen.
     tau = Anzahl Klicks auf der Folie (Frontmatter `clicks: 30`).
     Prop `at` (0..1) setzt tau fest (für Export/Prüfung). Inline-Styles, weil das Deck-CSS SVG-Attribute überschreibt. -->
<script setup lang="ts">
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'

const props = defineProps<{ at?: number }>()
const N = 31

function lfsr5(): number[] {           // c_{k+5} = c_k XOR c_{k+2}
  let s = 1; const out: number[] = []
  for (let i = 0; i < N; i++) { out.push(s & 1); const fb = (s ^ (s >> 2)) & 1; s = (s >> 1) | (fb << 4) }
  return out
}
const codes = [
  { title: 'm-Folge', c: lfsr5() },
  { title: 'Zufallscode, auch 16 Einsen', c: '0011101000000011011111111001010'.split('').map(Number) },
]
const overlap = (c: number[], t: number) => c.reduce((acc, v, i) => acc + v * c[(i - t + N) % N], 0)
const curves = codes.map(k => Array.from({ length: N }, (_, t) => overlap(k.c, t)))

const { $clicks } = useSlideContext()
const tau = computed(() => props.at !== undefined ? Math.min(N - 1, Math.floor(props.at * N)) : Math.min(N - 1, $clicks.value))

const ORANGE = '#d9822b', GREY = '#d3d8de', TXT1 = '#fff', TXT0 = '#6b7785'
// Radien: Produkt außen, Code Mitte, verschobener Code innen
const RINGS = [
  { ro: 140, ri: 121, fs: 10 },   // Produkt (mit Abstand zu den Code-Ringen)
  { ro: 112, ri: 92, fs: 10 },    // c fest
  { ro: 88, ri: 68, fs: 9 },      // c um tau gedreht
]
function mid(cx: number, cy: number, r: number, i: number) {
  const a = (2 * Math.PI * (i + 0.5)) / N - Math.PI / 2
  return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) }
}
function seg(cx: number, cy: number, ro: number, ri: number, i: number) {
  const a0 = (2 * Math.PI * i) / N - Math.PI / 2, a1 = (2 * Math.PI * (i + 1)) / N - Math.PI / 2
  const p = (r: number, a: number) => `${cx + r * Math.cos(a)} ${cy + r * Math.sin(a)}`
  return `M ${p(ro, a0)} A ${ro} ${ro} 0 0 1 ${p(ro, a1)} L ${p(ri, a1)} A ${ri} ${ri} 0 0 0 ${p(ri, a0)} Z`
}
const centers = [150, 450], CY = 162, BASE = 372, SCALE = 4
const rings = computed(() => codes.map((k, j) => {
  const cx = centers[j], t = tau.value
  const vals = [
    k.c.map((v, i) => v * k.c[(i - t + N) % N]),   // Produkt
    k.c,                                           // fest
    k.c.map((_, i) => k.c[(i - t + N) % N]),       // gedreht
  ]
  const segs = RINGS.flatMap((R, r) => vals[r].map((v, i) => ({
    key: `${r}-${i}`, d: seg(cx, CY, R.ro, R.ri, i), v, fs: R.fs, p: mid(cx, CY, (R.ro + R.ri) / 2, i),
  })))
  return { cx, segs, ov: curves[j][t], title: k.title, curve: curves[j] }
}))
const barX = (cx: number, t: number) => cx - 124 + t * 8
</script>

<template>
  <svg viewBox="0 0 600 400" class="w-full">
    <g v-for="(r, j) in rings" :key="j">
      <text :x="r.cx" y="14" text-anchor="middle" style="font-size: 15px; font-weight: 700; fill: #333">{{ r.title }}</text>
      <path v-for="s in r.segs" :key="'p' + s.key" :d="s.d" :style="{ fill: s.v ? ORANGE : GREY, stroke: '#fff', strokeWidth: 1.2 }" />
      <text v-for="s in r.segs" :key="'t' + s.key" :x="s.p.x" :y="s.p.y + s.fs * 0.35" text-anchor="middle"
            :style="{ fontSize: s.fs + 'px', fontWeight: 700, fill: s.v ? TXT1 : TXT0 }">{{ s.v }}</text>
      <text :x="r.cx" :y="CY - 8" text-anchor="middle" style="font-size: 13px; fill: #555">τ = {{ tau }}</text>
      <text :x="r.cx" :y="CY + 16" text-anchor="middle" :style="{ fontSize: '20px', fontWeight: 700, fill: ORANGE }">Σ = {{ r.ov }}</text>
      <!-- Überlapp für alle tau -->
      <line :x1="barX(r.cx, 0) - 4" :y1="BASE" :x2="barX(r.cx, N - 1) + 10" :y2="BASE" style="stroke: #999; stroke-width: 1" />
      <rect v-for="(v, t) in r.curve" :key="'b' + t" :x="barX(r.cx, t)" :y="BASE - v * SCALE" width="6" :height="v * SCALE"
            :style="{ fill: t === tau ? ORANGE : (t === 0 ? '#bbb' : '#0070c0'), opacity: t <= tau || t === 0 ? 1 : 0.18 }" />
      <line :x1="barX(r.cx, 0) - 4" :y1="BASE - 8 * SCALE" :x2="barX(r.cx, N - 1) + 10" :y2="BASE - 8 * SCALE" style="stroke: #d9822b; stroke-width: 0.8; stroke-dasharray: 3 3" />
    </g>
    <text x="300" y="392" text-anchor="middle" style="font-size: 12px; fill: #777">Überlapp für τ = 0 … 30 (grau: τ = 0, gestrichelt: 8)</text>
  </svg>
</template>
