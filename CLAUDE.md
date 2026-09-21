# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

A collection of public conference talks by Oliver Dürr, primarily on AI agents, LLMs, and related topics. Presentations are stored in `src/` and rendered to `docs/` for GitHub Pages hosting.

## Shared Toolchain

The `package.json` at the repository root declares the Slidev toolchain once for
all decks. Run `npm install` there a single time; Node resolves `node_modules`
upwards, so a deck in `src/slidev/<name>/` finds it without a local install.
Do **not** add a `package.json` or run `npm install` inside a talk folder.

`node_modules/` and `package-lock.json` are gitignored. A Slidev build also drops
a small `node_modules/.slidev` scratch folder in the talk directory; that is
covered by the same rule.

## Presentation Technologies

There are three presentation stacks in use:

**Slidev** (current — `src/slidev/2026_autostan/`):
- Source: `autostan.md` (Markdown with Slidev frontmatter and layout directives)
- Dev server: `cd src/slidev/2026_autostan && npx slidev autostan.md`
- Build to the Pages root:
  ```
  cd src/slidev/2026_autostan
  npx slidev build autostan.md --base /talks/autostan/ --out ../../../docs/autostan
  ```
  The `--base` must match the Pages sub-path, otherwise assets 404 on the live site.
- Slidev emits a directory, not a single file, so this talk lives at `docs/autostan/`
  rather than `docs/<name>.html` like the older ones
- Known quirk: Slidev writes `<link rel="preload" as="image">` hints pointing at the
  unhashed `./imgs/...` source paths, which 404 in the build. They are only hints —
  the slides themselves use the hashed `assets/` copies — but they are stripped from
  `index.html` and `404.html` after a build to keep the console clean
- Images live in `./imgs/` relative to the source file

**Marp** (`src/slidev/2026_skills/`):
- Despite the folder and file name, this deck is Marp, not Slidev: it uses Marp's
  `<style> section { ... }` scoping and `docs/cli_and_skills.html` is a Marp Core export
- Source: `first_version_slidev.md`
- Build/export: `npx @marp-team/marp-cli first_version_slidev.md -o ../../../docs/cli_and_skills.html`
  (Marp is not in the root `package.json`; `npx` fetches it on demand)
- Images live in `./imgs/` relative to the source file

**Quarto + Reveal.js** (older talks — `src/quarto/`):
- Source: `.qmd` files with `format: revealjs` YAML header
- Render: `quarto render <file>.qmd`
- Shared theme: `src/quarto/shared_stuff/oliver_slides.scss`

**LaTeX** (`ki_handout/`):
- Handout materials rendered with pdfLaTeX via RStudio

## Directory Layout

```
src/
├── slidev/
│   ├── 2026_autostan/  # Current talk: "AutoStan: Autonomous Bayesian Model
│   │                   #   Improvement via Predictive Feedback" (Slidev)
│   └── 2026_skills/    # "CLI Agents, Skills & the Return of the Shell" (Marp)
└── quarto/
    ├── 2025_agents/    # "Groking Agents" (Quarto/Reveal.js)
    ├── interactive/    # Interactive Reveal.js demo
    ├── ki_2023/        # KI 2023 conference talk (Quarto/Reveal.js)
    ├── ki_handout/     # KI 2023 handout (LaTeX)
    └── shared_stuff/   # Shared SCSS theme, logos, images
docs/                   # Generated static site (GitHub Pages output)
```

## Key Conventions

- The `.gitignore` excludes Slidev build artifacts (`slidev/`, `node_modules/`, lock files, generated HTML in `2026_skills/`) — commit only the Markdown source and images
- The `docs/` folder is committed and serves as the GitHub Pages root, published at
  <https://oduerr.github.io/talks/> (source: branch `main`, path `/docs`). There is no
  `index.html` there, so `README.md` is the entry point and links to each talk directly
- `.gitignore` has a blanket `*.html` rule with a `!docs/**/*.html` exception. The `**`
  matters: a Slidev build lands in `docs/<talk>/index.html`, which a plain `!docs/*.html`
  would not rescue. Add new rendered talks under `docs/` and check with
  `git status --untracked-files=all docs/<talk>` that nothing is silently dropped
- Quarto-generated HTML files (`*_files/`, `.html`) in `to_docs/` are also gitignored
- Speaker notes use `<!--` HTML comments inside slide definitions
- Slide layouts use Slidev directives like `---`, `layout: cover`, `layout: two-cols`
