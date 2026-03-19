# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

A collection of public conference talks by Oliver Dürr, primarily on AI agents, LLMs, and related topics. Presentations are stored in `R/to_docs/` and rendered to `docs/` for GitHub Pages hosting.

## Presentation Technologies

There are two presentation stacks in use:

**Slidev** (current — `src/slidev/2026_skills/`):
- Source: `first_version_slidev.md` (Markdown with Slidev frontmatter and layout directives)
- Dev server: `cd src/slidev/2026_skills && npx slidev first_version_slidev.md`
- Build/export: `cd src/slidev/2026_skills && npx slidev build first_version_slidev.md`
- The VSCode Slidev extension uses `.vscode/settings.json` to register the source file
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
│   └── 2026_skills/    # Current talk: "CLI Agents, Skills & the Return of the Shell"
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
- The `docs/` folder is committed and serves as the GitHub Pages root
- Quarto-generated HTML files (`*_files/`, `.html`) in `to_docs/` are also gitignored
- Speaker notes use `<!--` HTML comments inside slide definitions
- Slide layouts use Slidev directives like `---`, `layout: cover`, `layout: two-cols`
