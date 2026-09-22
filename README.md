# talks

A (hopefully) growing collections of public talks

Slides are published with GitHub Pages at **<https://oduerr.github.io/talks/>**.

## Talks

| Talk | Slides | Source |
| --- | --- | --- |
| **AutoStan: Autonomous Bayesian Model Improvement via Predictive Feedback** (2026)<br>A CLI coding agent builds and improves Stan models on its own, guided by the NLPD on held-out data. | [slides](https://oduerr.github.io/talks/autostan/) | [`src/slidev/2026_autostan`](src/slidev/2026_autostan) |
| **CLI Agents, Skills & the Return of the Shell** (2026)<br>From chat to agentic CLI, and why the shell turned out to be the right interface. | [slides](https://oduerr.github.io/talks/cli_and_skills.html) | [`src/slidev/2026_skills`](src/slidev/2026_skills) |
| **Bayesian Statistics: Running the Model Backwards** (2026)<br>The Bayesian workflow on one example, from a numpy simulation to NumPyro inference. Slides plus a live notebook. | — (internal, TIDIT retreat) | [`src/slidev/2026_bayes_tidit`](src/slidev/2026_bayes_tidit) |
| **Groking Agents** (2025)<br>Looking under the hood of the agentic coding tools. | — (not published yet) | [`src/quarto/2025_agents`](src/quarto/2025_agents) |
| **KI im Jahre 2023**<br>Was ist das, was kann es, was kann es nicht? With Prof. Georg Umlauf. | [slides](https://oduerr.github.io/talks/ki_2023.html) | [`src/quarto/ki_2023`](src/quarto/ki_2023) |
| **Interactive Presentation — Using Observable**<br>A demo of interactive Reveal.js slides. | [slides](https://oduerr.github.io/talks/interactive_obs.html) | [`src/quarto/interactive`](src/quarto/interactive) |

## Building

The rendered slides live in [`docs/`](docs), which is the GitHub Pages root and is
committed to the repository.

Slidev and Marp decks share one toolchain, declared in the `package.json` at the
repository root — run `npm install` once there, and every deck in `src/slidev/*`
picks it up. Quarto talks are rendered with `quarto render <file>.qmd`.

See [CLAUDE.md](CLAUDE.md) for the per-talk build commands.
