<!-- Skizze E[C(d) | d0]: Nadel bei d0 auf einem flachen Sockel knapp unter 0 (Sockel stark überhöht).
     Inline-Styles, weil das Deck-CSS SVG-Attribute wie font-size überschreibt. -->
<script setup lang="ts">
const x0 = 40, x1 = 440, y0 = 104, yFloor = 116, yTop = 22, xd0 = 300
</script>

<template>
  <svg viewBox="0 0 470 140" class="w-full">
    <!-- Null-Linie und Achse -->
    <line :x1="x0" :y1="y0" :x2="x1" :y2="y0" style="stroke: #999; stroke-width: 1.2" marker-end="url(#ar3)" />
    <text :x="x0 - 8" :y="y0 + 4" text-anchor="end" style="font-size: 13px; fill: #777">0</text>
    <text :x="x1" :y="y0 - 8" text-anchor="end" style="font-size: 13px; fill: #777">d</text>
    <!-- Sockel -->
    <line :x1="x0" :y1="yFloor" :x2="x1 - 10" :y2="yFloor" style="stroke: #0070c0; stroke-width: 2.5" />
    <text :x="x0" :y="yFloor + 22" style="font-size: 12px; fill: #0070c0">Sockel −Fs·512/1023 = −Peak/1022 (überhöht gezeichnet)</text>
    <!-- Nadel -->
    <line :x1="xd0" :y1="yFloor" :x2="xd0" :y2="yTop" style="stroke: #d9822b; stroke-width: 4" />
    <circle :cx="xd0" :cy="yTop" r="4" style="fill: #d9822b" />
    <text :x="xd0 + 10" :y="yTop + 6" style="font-size: 13px; fill: #d9822b">Fs·511,5005</text>
    <text :x="xd0 + 8" :y="y0 - 6" style="font-size: 14px; fill: #d9822b">d₀</text>
    <defs>
      <marker id="ar3" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" style="fill: #999" />
      </marker>
    </defs>
  </svg>
</template>
