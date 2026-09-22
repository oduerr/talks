# Talk: Bayesian Statistics — Running the Model Backwards

Context for working on this talk. Read this before touching anything here.
The repo-level CLAUDE.md covers the shared Slidev toolchain; this file covers the talk.

## What it is

- **Venue:** TIDIT group retreat, internal. Audience is mixed: the DS group
  (computer scientists, think in code) and the PAIR group (applied statisticians,
  think in estimates and uncertainty). Neither side should feel talked down to.
- **Length:** 40 minutes. Part 1 (~30 min) is this deck plus the notebook.
  Part 2 (~10 min) is Oliver's existing BNN research slides, dropped in after
  slide 9 ("Part 2" divider). Part 2 is not in this folder and not our concern.
- **One example carried all the way through:** systolic blood pressure vs. age,
  33 North American women. Data is from Sick & Dürr, *Probabilistic Deep
  Learning* (Manning), ch. 1. It contains a woman aged 9 — that is in the
  published data, leave it.

## The story (agreed, do not reshuffle without asking)

Model ↔ data. Forward pass = probability theory (simulate data from
parameters). Backward pass = statistics (infer parameters from data). The
Bayesian claim: the backward pass is *the same program run in the other
direction*. Slide 2 is this diagram.

| min | beat | where |
|---|---|---|
| 0–3 | the two directions; the example; *don't look at the data yet*; what do we believe? | slides 1–3 |
| 3–10 | write the DGP in **plain numpy**, four lines; ask the room for the priors | notebook §1 |
| 10–15 | prior predictive: run it 200 times; the priors give negative blood pressure; fix them | notebook §2 |
| 15–20 | reveal the scatter; translate the same four lines to **NumPyro**; `obs=` ; posterior | notebook §3–4 |
| 20–24 | same problem with `statsmodels`; same numbers; the interval now *means* something | slides 4–6 |
| 24–28 | frequentist vs Bayesian; the recipe scales to neural nets, classical *uncertainty* does not → Part 2 | slides 7–8 |

Key decisions and why:

- **numpy first, NumPyro second** (not PyMC, not NumPyro from the start). With
  numpy nothing stands between the audience and the priors. The translation
  is line-for-line, and the *reason* you need a new framework is the didactic
  point: numpy forgets which distribution a number came from, and it can draw
  from a distribution but not evaluate it. A PPL is a language whose programs
  remember what they did and can be evaluated, not just run. That is slide 4.
- **The scatter plot stays hidden until the notebook's step 3.** The workflow
  says you write down beliefs before looking. Make the room experience that.
- **Do not oversell "credible intervals are narrower."** Ours are ~24% narrower
  *because the prior on the intercept is informative*. With a flat prior the
  intervals coincide (verified, table below). The honest point: weak prior →
  same answer as OLS; real prior knowledge → tighter, and you can see what you
  paid for it.
- **The bridge claim is about uncertainty, not estimation.** Deep learning *is*
  frequentist statistics (maximum likelihood) and point estimates scale fine.
  What does not scale is classical uncertainty (curvature of the likelihood at
  the optimum). Do not say "frequentist statistics doesn't scale" — the DS
  people will correctly object.
- **PyMC was rejected** because it requires `with pm.Model():` for every
  variable (passing `model=` to a distribution is a TypeError). Route B
  (NumPyro under `handlers.seed`) was rejected for Route C (numpy) above.
- `sigma` must be positive: `HalfNormal(20)`, in numpy `abs(normal(0, 20))`.
  Oliver's original `rnorm(5, 100)` would be mostly negative.

## Files

| file | role |
|---|---|
| `bayes_tidit.md` | the Slidev deck, 11 slides (9 for Part 1, a Part-2 divider, 2 backup) |
| `bayes_workflow.ipynb` | the live notebook for min 3–20. **Executed, outputs saved.** This is the artifact Oliver presents from |
| `build_notebook.py` | generated the notebook. **If the .ipynb has been edited by hand, do not re-run this — it overwrites.** Treat the .ipynb as the source of truth from now on |
| `components/PriorExplorer.vue` | in-browser prior-predictive explorer with sliders and a small Metropolis sampler. Backup slide 11, in case the notebook misbehaves |
| `make_figs.py` | static figures in `imgs/` (data, OLS fit, prior predictive, ...). Not referenced by the current deck; kept as fallback |
| `fit_stan.py`, `model.stan` | the same model in Stan, used as an independent cross-check of the numbers. Needs `cmdstanpy` + CmdStan. The compiled binary `model` is gitignored |
| `requirements.txt` | Python deps for the notebook and scripts |

## Running things

All commands from this folder. Slidev comes from the root `package.json`
(`npm install` once at the repo root, never here).

```
npx slidev bayes_tidit.md                        # dev server, localhost:3030
npx slidev bayes_tidit.md --remote --port 3030   # also on the LAN / Tailscale; presenter mode is then open to anyone on the network
npx slidev build bayes_tidit.md --base /talks/bayes_tidit/ --out ../../../docs/bayes_tidit   # only if this ever goes public

pip install -r requirements.txt
jupyter nbconvert --to notebook --execute --inplace bayes_workflow.ipynb   # re-execute, checks every cell runs in order
python make_figs.py                              # regenerate imgs/
python fit_stan.py                               # Stan cross-check (optional)
```

The notebook kernel is named `miniconda` / "Python (miniconda)" on the Mac
mini. On another machine, register whatever env has the requirements:
`python -m ipykernel install --user --name <name>` and pick it in VS Code.

## Verified numbers (do not change slides without re-verifying)

Priors: `a ~ N(1, 0.4)`, `b ~ N(90, 15)`, `sigma ~ HalfNormal(20)`.

| method | slope a | 95% interval |
|---|---|---|
| OLS (`statsmodels`) | 1.105 | [0.685, 1.525] |
| NumPyro NUTS — the notebook, `PRNGKey(2)` | **1.06** | **[0.74, 1.38]** |
| Stan NUTS (`fit_stan.py`) | 1.075 | [0.754, 1.399] |
| PyMC NUTS | 1.078 | [0.748, 1.399] |
| browser Metropolis (`PriorExplorer.vue`) | 1.083 | [0.769, 1.413] |
| NumPyro with flat priors | 1.097 | [0.685, 1.520] |

OLS full table: intercept 87.671 (se 10.076), slope 1.105 (se 0.206), residual
sd 19.28, R² 0.481. Reproduces the R output in the book's source exactly.

Prior predictive at the data level (mean curve + noise), 1–99 %:
original priors `a~N(1,5), b~N(100,50)` → −490 … 810 mmHg, ~25 % of simulated
patients below zero. Tightened priors → 57 … 230 mmHg, ~0 % below zero.

## Gotchas that cost real time

- **UnoCSS attributify hijacks SVG paint attributes.** In a Slidev deck or Vue
  component, `stroke="#..."`, `stroke-opacity="0.45"`, `fill=`, `opacity=` on
  SVG elements get rewritten into utilities — `0.45` is read as 0.45 %, so
  things render invisibly. The build passes and nothing warns. **Put every
  paint property in `style="..."` / `:style`**, never in an attribute. Slide 2
  and `PriorExplorer.vue` both do this; keep it that way.
- **Markdown tables eat `[0.74, 1.38]`** (link syntax). Escape: `\[0.74, 1.38\]`.
- `numpyro.sample(...)` called bare, outside a function or handler, fails with
  an empty `AssertionError`. It needs `handlers.seed` or to live inside the
  model function. In the notebook it is always inside `model()`.
- NumPyro's first NUTS call JIT-compiles: ~1 s on the Mac mini. Not a problem
  live, but run the cell once before going on stage anyway.
- Slidev counts of slides via `noteHTML:` in the bundle are unreliable. Count
  separators in the markdown, merging `layout:` frontmatter blocks into the
  slide that follows.
- Headless render checks work: `playwright` is installed in miniconda with
  chromium. `http://localhost:3030/<n>?clicks=99` shows slide *n* fully
  revealed; measure `.slidev-page-<n> .slidev-layout` `scrollHeight` vs
  `clientHeight` for overflow (should be 552/552).

## Status

- Deck and notebook are complete for Part 1 and verified (every slide renders,
  no overflow, notebook executes end to end with zero warnings).
- Not published to `docs/` — internal talk. Source is committed.
- Open: nothing for Part 1. Part 2 slides are Oliver's, added after slide 9.
