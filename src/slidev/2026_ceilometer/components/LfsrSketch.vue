<!-- 10-Bit-Schieberegister x^10 + x^3 + 1: Zelle j enthält c_{k+j}; Ausgabe c_k rechts,
     Rückkopplung c_k XOR c_{k+3} = c_{k+10} links hinein. Inline-Styles, weil das Deck-CSS SVG-Attribute überschreibt. -->
<script setup lang="ts">
const n = 10, x0 = 20, w = 44, y = 70, h = 34
const xOf = (j: number) => x0 + (n - 1 - j) * w          // Zelle j: c_{k+j}, j = 9 links ... 0 rechts
const mid = (j: number) => xOf(j) + w / 2
const xorX = (mid(0) + mid(3)) / 2, xorY = 26
const sub = (j: number) => (j === 0 ? 'k' : `k+${j}`)
</script>

<template>
  <svg viewBox="0 0 500 140" class="w-full">
    <g v-for="j in n" :key="j">
      <rect :x="xOf(j - 1)" :y="y" :width="w" :height="h"
            :style="{ fill: j - 1 === 0 || j - 1 === 3 ? '#dbe9f6' : '#f3f6fa', stroke: '#0070c0', strokeWidth: 1.4 }" />
      <text :x="mid(j - 1)" :y="y + 22" text-anchor="middle" style="font-size: 12px; fill: #333">c<tspan baseline-shift="sub" style="font-size: 9px">{{ sub(j - 1) }}</tspan></text>
    </g>
    <!-- Abgriffe zum XOR -->
    <path :d="`M ${mid(0)} ${y} L ${mid(0)} ${xorY} L ${xorX + 11} ${xorY}`" style="fill: none; stroke: #d9822b; stroke-width: 1.6" />
    <path :d="`M ${mid(3)} ${y} L ${mid(3)} ${xorY} L ${xorX - 11} ${xorY}`" style="fill: none; stroke: #d9822b; stroke-width: 1.6" />
    <circle :cx="xorX" :cy="xorY" r="11" style="fill: #fff; stroke: #d9822b; stroke-width: 1.6" />
    <text :x="xorX" :y="xorY + 6" text-anchor="middle" style="font-size: 17px; fill: #d9822b">⊕</text>
    <!-- Rückkopplung nach links in Zelle 9 -->
    <path :d="`M ${xorX} ${xorY - 11} L ${xorX} 8 L ${x0 - 12} 8 L ${x0 - 12} ${y + h / 2} L ${x0 - 2} ${y + h / 2}`"
          style="fill: none; stroke: #d9822b; stroke-width: 1.6" marker-end="url(#ar4)" />
    <text :x="x0 + 4" y="22" style="font-size: 12px; fill: #d9822b">c<tspan baseline-shift="sub" style="font-size: 9px">k+10</tspan> = c<tspan baseline-shift="sub" style="font-size: 9px">k</tspan> ⊕ c<tspan baseline-shift="sub" style="font-size: 9px">k+3</tspan></text>
    <!-- Ausgabe -->
    <path :d="`M ${x0 + n * w} ${y + h / 2} L ${x0 + n * w + 26} ${y + h / 2}`" style="fill: none; stroke: #333; stroke-width: 1.6" marker-end="url(#ar5)" />
    <text x="496" :y="y + h + 20" text-anchor="end" style="font-size: 12px; fill: #333">Ausgabe c<tspan baseline-shift="sub" style="font-size: 9px">k</tspan></text>
    <text :x="x0" :y="y + h + 20" style="font-size: 12px; fill: #777">jeder Takt: alles eins nach rechts</text>
    <defs>
      <marker id="ar4" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" style="fill: #d9822b" />
      </marker>
      <marker id="ar5" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" style="fill: #333" />
      </marker>
    </defs>
  </svg>
</template>
