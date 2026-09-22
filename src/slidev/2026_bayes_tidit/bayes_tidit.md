---
theme: default
title: "Bayesian Statistics: Running the Model Backwards"
info: |
  Oliver Dürr — TIDIT Group Retreat
  Part 1: the Bayesian workflow on one example. Part 2: Bayesian neural networks.
class: text-center
drawings:
  persist: false
transition: fade
mdc: true
lineNumbers: false
---

# Bayesian Statistics

**Running the model backwards**

<br>

Oliver Dürr — TIDIT Retreat

<!--
Two parts. First 30 minutes: one example, start to finish, most of it live.
Last 10: what happens when the model is a neural network — which is the
research part.
-->

---

# Two directions

<svg viewBox="0 0 800 300" class="w-full max-w-3xl mx-auto mt-2">
  <defs>
    <marker id="arrF" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" style="fill:#2d5986" />
    </marker>
    <marker id="arrB" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" style="fill:#c0392b" />
    </marker>
  </defs>
  <ellipse cx="150" cy="150" rx="115" ry="50" style="fill:#eef3f8;stroke:#2d5986;stroke-width:2" />
  <text x="150" y="158" style="text-anchor:middle;font-size:26px;font-weight:600;fill:#1a3a5c">Model</text>
  <ellipse cx="650" cy="150" rx="115" ry="50" style="fill:#eef3f8;stroke:#2d5986;stroke-width:2" />
  <text x="650" y="158" style="text-anchor:middle;font-size:26px;font-weight:600;fill:#1a3a5c">Data</text>

  <path d="M 235 108 Q 400 15 565 108" style="fill:none;stroke:#2d5986;stroke-width:3" marker-end="url(#arrF)" />
  <text x="400" y="22" style="text-anchor:middle;font-size:18px;fill:#2d5986;font-weight:600">probability theory</text>
  <text x="400" y="44" style="text-anchor:middle;font-size:15px;fill:#2d5986">the forward pass — simulate data from parameters</text>

  <path d="M 565 192 Q 400 285 235 192" style="fill:none;stroke:#c0392b;stroke-width:3" marker-end="url(#arrB)" />
  <text x="400" y="266" style="text-anchor:middle;font-size:18px;fill:#c0392b;font-weight:600">statistics</text>
  <text x="400" y="288" style="text-anchor:middle;font-size:15px;fill:#c0392b">the backward pass — infer parameters from data</text>
</svg>

<div v-click class="mt-4 text-center">
Plan for today: write the forward pass in plain numpy — then find out what it takes to run it backwards.
</div>

<!--
Everything in this talk is this picture. Forward is easy: you all do it, it is
called simulation. Backward is what statistics is. The Bayesian claim is that
the backward pass should be *the same program*, run in the other direction.
-->

---

# One example, all the way through

**33 North American women.** Two numbers each: age, and systolic blood pressure.

<v-clicks>

- We will **not look at the blood pressures yet**
- Before looking, what do we believe?
  - blood pressure rises with age — but how fast?
  - a newborn already has *some* blood pressure
  - not everyone of the same age has the same pressure
- Those three sentences are the model. Let us write them down.

</v-clicks>

<div v-click class="mt-8 p-3 border-l-4 border-blue-700 bg-blue-50 text-sm">

→ **notebook** &nbsp; 1. the story, in numpy &nbsp;·&nbsp; 2. run it 200 times &nbsp;·&nbsp; 3. look at the data &nbsp;·&nbsp; 4. run it backwards

</div>

<!--
Ask the room for numbers here: how much does blood pressure rise per year?
Whatever they say goes into the notebook. Then switch.

The point of not showing the scatter plot: the workflow says you write down
your beliefs before you look. Make them experience that, do not just say it.
-->

---

# Why numpy cannot run backwards

<div class="text-sm">

| forward only | both directions |
|---|---|
| `a = np.random.normal(1, 0.4)` | `a = numpyro.sample("a", dist.Normal(1, 0.4))` |
| `b = np.random.normal(90, 15)` | `b = numpyro.sample("b", dist.Normal(90, 15))` |
| `sigma = abs(np.random.normal(0, 20))` | `sigma = numpyro.sample("sigma", dist.HalfNormal(20))` |
| `sbp = np.random.normal(b + a*age, sigma)` | `numpyro.sample("sbp", dist.Normal(b + a*age, sigma), obs=sbp)` |

</div>

<v-clicks class="text-sm mt-2">

- **numpy forgets.** `np.random.normal(1, 0.4)` returns `0.87` — that it *came from* N(1, 0.4) is gone. The name in `sample("a", …)` is how the program remembers its own structure.
- **numpy can only draw, not evaluate.** It samples from N(1, 0.4) but cannot say how probable `0.87` was. `dist.Normal` is a sampler *and* a density — the backward pass needs the density.
- **`obs=` is the switch.** Same function: `sbp=None` runs forward, `sbp=data` runs backward.

</v-clicks>

<!--
This is the conceptual centre of the talk. A probabilistic programming
language is a language whose programs remember what they did and can be
evaluated, not just run. That is all it is.
-->

---

# Same problem, the classical way

```python
import statsmodels.api as sm
fit = sm.OLS(sbp, sm.add_constant(age)).fit()
print(fit.summary())
```

```txt
                 coef    std err          t      P>|t|      [0.025      0.975]
const          87.6714     10.076      8.701      0.000      67.120     108.223
age             1.1050      0.206      5.364      0.000       0.685       1.525
```

<v-click>

| | slope | 95% interval |
|---|---|---|
| **Bayes** — what we just did | 1.06 | \[0.74, 1.38\] |
| **least squares** | 1.11 | \[0.69, 1.53\] |

</v-click>

<v-click>

Same answer. The Bayesian interval is ~24% narrower — *because we put in a prior*. With a flat prior it becomes \[0.69, 1.52\] — the classical interval, recovered.

</v-click>

<!--
Do not oversell the narrower interval. Information in, information out. The
honest point is: with weak priors Bayes reproduces the classical result, with
real prior knowledge it uses it, and either way you can see what you assumed.
-->

---

# So what did we gain? The interval *means* something

<div class="grid grid-cols-2 gap-8 mt-4">

<div>

**Confidence interval** [0.69, 1.53]

> If we repeated this study many times, 95% of the intervals built this way would contain the true slope.

A statement about **the procedure**. Says nothing about *this* interval.

</div>

<div v-click>

**Credible interval** [0.74, 1.38]

> Given the data we saw, the slope is in here with 95% probability.

A statement about **the parameter**. The sentence everyone *wants* to say.

</div>

</div>

<div v-click class="mt-8 text-center">

And we may now write things like &nbsp; $P(a > 0 \mid \text{data}) > 0.9999$ &nbsp; — a probability *about a parameter*.

</div>

<!--
The frequentist statement is correct and almost nobody in practice says it.
The Bayesian statement is what people actually mean when they read a CI. That
gap is what you pay a prior to close.
-->

---

# Two ways of thinking

| | frequentist | Bayesian |
|---|---|---|
| parameters | fixed, unknown | uncertain → a distribution |
| data | random | fixed — you observed it |
| the answer | an estimate + a procedure | a distribution $p(\theta \mid \text{data})$ |
| assumptions | in the procedure, implicit | in the prior, written down |
| the workflow | fit | simulate → check → condition → check |
| this example | same numbers | same numbers |

<div v-click class="mt-6 text-center">

For a linear regression on 33 points, the choice does not matter. **So when does it?**

</div>

<!--
Be fair here. On this problem both are fine and both are right. The
difference is not the answer — it is what you may say about it, and, next
slide, what happens when the model gets big.
-->

---

# When the model is a neural network

<div class="grid grid-cols-2 gap-8 mt-2">

<div>

**The recipe does not change.**

```python
def model(x, y=None):
    w = sample("w", Normal(0, 1))    # millions of them
    f = neural_net(x, w)
    sample("y", Normal(f, sigma), obs=y)
```

Priors, likelihood, `obs=`. Same four lines. **The forward pass is deep learning.**

</div>

<div v-click>

**The classical uncertainty machinery does.**

- standard errors come from the curvature of the likelihood at the optimum
- for a million-parameter, non-convex, non-identifiable model that curvature is meaningless
- a confidence interval for weight #3,471,022 is not a thing

Point estimates scale. *Uncertainty* does not.

</div>

</div>

<div v-click class="mt-6 p-3 border-l-4 border-red-500 bg-red-50">

The Bayesian recipe still makes sense — but the backward pass becomes **computationally hard**. Making it tractable is Part 2.

</div>

<!--
This is the bridge. Careful with the claim: deep learning IS frequentist
statistics, it is maximum likelihood, and it scales beautifully. What does
not scale is the uncertainty. That is exactly the gap a Bayesian neural
network fills — and exactly where it gets hard.
-->

---
layout: center
class: text-center
---

# Part 2

## Bayesian neural networks — making the backward pass tractable

<div class="mt-6 text-sm opacity-60">(existing slides)</div>

---
layout: center
class: text-center
---

# Backup

<div class="text-sm opacity-60">only if the notebook misbehaves</div>

---

# Prior predictive, live

<PriorExplorer />

<!--
BACKUP — same demo as the notebook, in the browser. Drag the sliders; the
"below zero" number is the point. "condition on the data" runs a small
Metropolis sampler with whatever priors are set.
-->
