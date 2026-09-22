<!--
  Live prior-predictive explorer for the TIDIT Bayes talk.

  Drag the sliders during the talk: the fan of prior curves, the simulated
  patients and the "share below 0 mmHg" read-out all update immediately.
  Everything runs in the browser, so there is nothing to install and nothing
  that can fail on stage. Press "condition on the data" to run a small
  Metropolis sampler over the same model and see the posterior.
-->
<template>
  <div class="pe">
    <div class="pe-controls">
      <label v-for="s in sliders" :key="s.key">
        <span class="pe-name" v-html="s.label"></span>
        <input type="range" :min="s.min" :max="s.max" :step="s.step"
               v-model.number="p[s.key]" @input="showPost = false" />
        <span class="pe-val">{{ p[s.key].toFixed(s.dp) }}</span>
      </label>

      <div class="pe-buttons">
        <button @click="reseed">↻ resample</button>
        <button :class="{ active: showData }" @click="showData = !showData">
          observed data
        </button>
        <button :class="{ active: showPost }" @click="condition">
          condition on the data
        </button>
      </div>
    </div>

    <svg :viewBox="`0 0 ${W} ${H}`" class="pe-svg">
      <defs>
        <clipPath id="pe-clip">
          <rect :x="ml" :y="mt" :width="W - ml - mr" :height="H - mt - mb" />
        </clipPath>
      </defs>
      <g clip-path="url(#pe-clip)">
      <!-- NB: every paint property goes through :style, never through an
           attribute. UnoCSS attributify rewrites stroke/fill/opacity
           attributes into utilities (stroke-opacity="0.45" becomes 0.45%),
           which silently makes things invisible. Inline styles win. -->

      <!-- zero line -->
      <line :x1="ml" :x2="W - mr" :y1="sy(0)" :y2="sy(0)" :style="sZero" />
      <text :x="ml + 4" :y="sy(0) - 5" class="pe-lbl">0 mmHg</text>

      <!-- prior (or posterior) curves -->
      <path v-for="(d, i) in curves" :key="i" :d="d" :style="sCurve" />

      <!-- one simulated data set -->
      <circle v-for="(pt, i) in simulated" :key="'s' + i"
              :cx="sx(pt.x)" :cy="sy(pt.y)" r="4" :style="sSim" />

      <!-- the real data -->
      <template v-if="showData">
        <circle v-for="(pt, i) in DATA" :key="'d' + i"
                :cx="sx(pt[0])" :cy="sy(pt[1])" r="4.5" :style="sObs" />
      </template>
      </g>

      <!-- axes -->
      <line :x1="ml" :x2="W - mr" :y1="H - mb" :y2="H - mb" :style="sAxis" />
      <line :x1="ml" :x2="ml" :y1="mt" :y2="H - mb" :style="sAxis" />
      <text v-for="t in xTicks" :key="'x' + t" :x="sx(t)" :y="H - mb + 16"
            text-anchor="middle" class="pe-lbl">{{ t }}</text>
      <text v-for="t in yTicks" :key="'y' + t" :x="ml - 6" :y="sy(t) + 4"
            text-anchor="end" class="pe-lbl">{{ t }}</text>
      <text :x="(W - mr + ml) / 2" :y="H - 4" text-anchor="middle" class="pe-lbl">
        age [years]
      </text>
    </svg>

    <div class="pe-readout" :class="{ bad: pctNeg > 2 && !showPost }">
      <template v-if="showPost">
        posterior after conditioning:
        <b>a = {{ post.a.toFixed(2) }}</b>
        [{{ post.aLo.toFixed(2) }}, {{ post.aHi.toFixed(2) }}] mmHg/year
        &nbsp;·&nbsp; b = {{ post.b.toFixed(0) }}
        &nbsp;·&nbsp; σ = {{ post.s.toFixed(1) }}
      </template>
      <template v-else>
        simulated patients: 1–99% = <b>{{ q01 }}</b> … <b>{{ q99 }}</b> mmHg
        &nbsp;·&nbsp; below zero: <b>{{ pctNeg.toFixed(1) }}%</b>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

// SBP vs age, 33 North American women (Sick & Duerr, ch. 1)
const AGE = [22, 41, 52, 23, 41, 54, 24, 46, 56, 27, 47, 57, 28, 48, 58, 9, 49,
  59, 30, 49, 63, 32, 50, 67, 33, 51, 71, 35, 51, 77, 40, 51, 81]
const SBP = [131, 139, 128, 128, 171, 105, 116, 137, 145, 106, 111, 141, 114,
  115, 153, 123, 133, 157, 117, 128, 155, 122, 183, 176, 99, 130, 172, 121,
  133, 178, 147, 144, 217]
const DATA = AGE.map((a, i) => [a, SBP[i]])

const p = reactive({ aMean: 1, aSd: 5, bMean: 100, bSd: 50, sig: 20 })
const sliders = [
  { key: 'aMean', label: 'a &nbsp;mean', min: -2, max: 4, step: 0.1, dp: 1 },
  { key: 'aSd', label: 'a &nbsp;sd', min: 0.05, max: 6, step: 0.05, dp: 2 },
  { key: 'bMean', label: 'b &nbsp;mean', min: 40, max: 160, step: 1, dp: 0 },
  { key: 'bSd', label: 'b &nbsp;sd', min: 1, max: 60, step: 1, dp: 0 },
  { key: 'sig', label: 'σ &nbsp;scale', min: 1, max: 60, step: 1, dp: 0 },
]

const seed = ref(1)
const showData = ref(false)
const showPost = ref(false)
const N_CURVES = 60

// --- deterministic RNG so a redraw is stable until you press resample ------
function mulberry(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}
function normal(rnd, mu, sd) {
  const u = Math.max(rnd(), 1e-12), v = rnd()
  return mu + sd * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
}
const reseed = () => { seed.value = (seed.value * 7919 + 13) % 100000; showPost.value = false }

// --- prior draws -----------------------------------------------------------
const draws = computed(() => {
  const rnd = mulberry(seed.value)
  const out = []
  for (let i = 0; i < N_CURVES; i++) {
    out.push({
      a: normal(rnd, p.aMean, p.aSd),
      b: normal(rnd, p.bMean, p.bSd),
      s: Math.abs(normal(rnd, 0, p.sig)),
    })
  }
  return out
})

// stats over the full prior predictive (mean curve + observation noise)
const ppStats = computed(() => {
  const rnd = mulberry(seed.value + 999)
  const vals = []
  for (let i = 0; i < 400; i++) {
    const a = normal(rnd, p.aMean, p.aSd)
    const b = normal(rnd, p.bMean, p.bSd)
    const s = Math.abs(normal(rnd, 0, p.sig))
    for (const age of AGE) vals.push(normal(rnd, b + a * age, s))
  }
  vals.sort((x, y) => x - y)
  const q = (f) => vals[Math.floor(f * (vals.length - 1))]
  return { lo: q(0.01), hi: q(0.99), neg: vals.filter((v) => v < 0).length / vals.length }
})
const q01 = computed(() => Math.round(ppStats.value.lo))
const q99 = computed(() => Math.round(ppStats.value.hi))
const pctNeg = computed(() => ppStats.value.neg * 100)

// --- posterior via a small random-walk Metropolis ---------------------------
const post = reactive({ a: 0, b: 0, s: 0, aLo: 0, aHi: 0, draws: [] })
function condition() {
  if (showPost.value) { showPost.value = false; return }
  const rnd = mulberry(4242)
  const lpost = (a, b, s) => {
    if (s <= 0) return -Infinity
    let ll = 0
    for (let i = 0; i < AGE.length; i++) {
      const r = SBP[i] - (b + a * AGE[i])
      ll += -0.5 * (r / s) ** 2 - Math.log(s)
    }
    // the same priors the sliders control
    ll += -0.5 * ((a - p.aMean) / p.aSd) ** 2
    ll += -0.5 * ((b - p.bMean) / p.bSd) ** 2
    ll += -0.5 * (s / p.sig) ** 2            // half-normal
    return ll
  }
  let a = 1, b = 90, s = 20, lp = lpost(a, b, s)
  const keep = []
  for (let it = 0; it < 60000; it++) {
    const na = a + normal(rnd, 0, 0.08)
    const nb = b + normal(rnd, 0, 3.5)
    const ns = s + normal(rnd, 0, 1.2)
    const nlp = lpost(na, nb, ns)
    if (Math.log(Math.max(rnd(), 1e-12)) < nlp - lp) { a = na; b = nb; s = ns; lp = nlp }
    if (it > 10000 && it % 25 === 0) keep.push([a, b, s])
  }
  const col = (j) => keep.map((k) => k[j]).sort((x, y) => x - y)
  const mean = (j) => keep.reduce((t, k) => t + k[j], 0) / keep.length
  const as = col(0)
  post.a = mean(0); post.b = mean(1); post.s = mean(2)
  post.aLo = as[Math.floor(0.025 * as.length)]
  post.aHi = as[Math.floor(0.975 * as.length)]
  post.draws = keep.filter((_, i) => i % Math.ceil(keep.length / N_CURVES) === 0)
  showData.value = true          // you are conditioning on it, so show it
  showPost.value = true
}

// --- paint (inline styles only, see note in the template) ------------------
const sZero = { stroke: 'currentColor', strokeDasharray: '3 3', strokeOpacity: .45 }
const sAxis = { stroke: 'currentColor', strokeOpacity: .8 }
const sSim = { fill: '#c0392b', fillOpacity: .85 }
const sObs = { fill: '#1a3a5c' }
const sCurve = computed(() => ({
  stroke: showPost.value ? '#2d5986' : '#7f8c8d',
  strokeOpacity: showPost.value ? .3 : .45,
  strokeWidth: 1.4,
  fill: 'none',
}))

// --- plotting --------------------------------------------------------------
const W = 720, H = 330, ml = 54, mr = 14, mt = 12, mb = 32
const yRange = computed(() => {
  if (showPost.value) return [40, 240]
  // quantiles, not min/max: one wild draw should not flatten the whole picture
  const vals = draws.value.flatMap((d) => [d.b, d.b + d.a * 90]).sort((x, y) => x - y)
  const q = (f) => vals[Math.floor(f * (vals.length - 1))]
  const lo = Math.min(-20, q(0.04)), hi = Math.max(220, q(0.96))
  const pad = (hi - lo) * 0.08
  return [Math.max(lo - pad, -600), Math.min(hi + pad, 800)]
})
const sx = (v) => ml + (v / 90) * (W - ml - mr)
const sy = (v) => {
  const [lo, hi] = yRange.value
  return H - mb - ((v - lo) / (hi - lo)) * (H - mt - mb)
}
const xTicks = [0, 20, 40, 60, 80]
const yTicks = computed(() => {
  const [lo, hi] = yRange.value
  const step = Math.pow(10, Math.floor(Math.log10((hi - lo) / 4)))
  const s = [1, 2, 5, 10].map((m) => m * step).find((c) => (hi - lo) / c <= 6) || step
  const out = []
  for (let t = Math.ceil(lo / s) * s; t <= hi; t += s) out.push(Math.round(t))
  return out
})
const curves = computed(() => {
  const src = showPost.value
    ? post.draws.map(([a, b]) => ({ a, b }))
    : draws.value
  return src.map((d) => `M ${sx(0)} ${sy(d.b)} L ${sx(90)} ${sy(d.b + d.a * 90)}`)
})
const simulated = computed(() => {
  if (showPost.value) return []
  const rnd = mulberry(seed.value + 7)
  const d = draws.value[0]
  return AGE.map((age) => ({ x: age, y: normal(rnd, d.b + d.a * age, d.s) }))
})
</script>

<style scoped>
.pe { display: flex; flex-direction: column; gap: .25rem; max-height: 76vh; }
.pe-controls { display: flex; flex-wrap: wrap; gap: .2rem .9rem; align-items: center; font-size: .7rem; }
.pe-controls label { display: flex; align-items: center; gap: .35rem; }
.pe-name { opacity: .75; min-width: 3.6rem; }
.pe-val { font-variant-numeric: tabular-nums; min-width: 2.6rem; opacity: .9; }
.pe-controls input[type='range'] { width: 88px; }
.pe-buttons { display: flex; gap: .4rem; }
.pe-buttons button {
  font-size: .68rem; padding: .12rem .5rem; border: 1px solid currentColor;
  border-radius: .25rem; opacity: .6; cursor: pointer;
}
.pe-buttons button:hover { opacity: 1; }
.pe-buttons button.active { opacity: 1; background: #2d5986; color: #fff; border-color: #2d5986; }
.pe-svg { width: 100%; height: 44vh; display: block; }
.pe-lbl { font-size: 10px; fill: currentColor; opacity: .65; }
.pe-readout { font-size: .8rem; text-align: center; opacity: .9; }
.pe-readout.bad { color: #c0392b; font-weight: 600; }
</style>
