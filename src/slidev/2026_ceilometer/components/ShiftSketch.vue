<!-- Skizze: Damit Bin k Signal bekommt, muss der Laser d0 Bins vorher (Chip k - d0) gefeuert haben.
     Muster schematisch. Inline-Styles, weil das Deck-CSS SVG-Attribute wie font-size überschreibt. -->
<script setup lang="ts">
const n = 14, x0 = 20, w = 34, y = 70, h = 28, kf = 3, d0 = 7
const c = [0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0]   // schematisch, c[kf] = 1
const cx = (i: number) => x0 + (i + 0.5) * w
</script>

<template>
  <svg viewBox="0 0 520 150" class="w-full">
    <g v-for="i in n" :key="i">
      <rect :x="x0 + (i - 1) * w" :y="y" :width="w" :height="h"
            :style="{ fill: c[i - 1] ? '#7fb2dc' : '#e8eef5', stroke: '#fff', strokeWidth: 2 }" />
    </g>
    <!-- Feuerevent in Chip k - d0 -->
    <rect :x="x0 + kf * w" :y="y" :width="w" :height="h" style="fill: none; stroke: #0070c0; stroke-width: 3" />
    <text :x="cx(kf)" :y="y - 36" text-anchor="middle" style="font-size: 20px">💥</text>
    <text :x="cx(kf)" :y="y + h + 20" text-anchor="middle" style="font-size: 14px; fill: #0070c0">k − d₀</text>
    <text :x="cx(kf)" :y="y + h + 38" text-anchor="middle" style="font-size: 12px; fill: #0070c0">c = 1: Laser feuert</text>
    <!-- Ankunft in Bin k -->
    <rect :x="x0 + (kf + d0) * w" :y="y" :width="w" :height="h" style="fill: none; stroke: #d9822b; stroke-width: 3" />
    <text :x="cx(kf + d0)" :y="y + h + 20" text-anchor="middle" style="font-size: 14px; fill: #d9822b">k</text>
    <text :x="cx(kf + d0)" :y="y + h + 38" text-anchor="middle" style="font-size: 12px; fill: #d9822b">Pois(b + s)</text>
    <!-- Bogen d0 Bins -->
    <path :d="`M ${cx(kf)} ${y - 4} Q ${(cx(kf) + cx(kf + d0)) / 2} ${y - 62} ${cx(kf + d0)} ${y - 4}`"
          style="fill: none; stroke: #555; stroke-width: 1.6" marker-end="url(#ar2)" />
    <text :x="(cx(kf) + cx(kf + d0)) / 2" :y="y - 38" text-anchor="middle" style="font-size: 14px; fill: #333">d₀ Bins später</text>
    <text :x="x0 + n * w" :y="y + h + 20" text-anchor="end" style="font-size: 12px; fill: #777">Zeit →</text>
    <defs>
      <marker id="ar2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" style="fill: #555" />
      </marker>
    </defs>
  </svg>
</template>
