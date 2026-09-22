# Bayesian Statistics: Running the Model Backwards

TIDIT group retreat talk. Slides plus a live notebook. See `CLAUDE.md` in this
folder for the full story, the beat sheet, and why things are built the way
they are.

## Install

Python is managed with [uv](https://docs.astral.sh/uv/) — one `.venv` local
to this folder, pinned by `uv.lock`.

```bash
cd src/slidev/2026_bayes_tidit      # this folder
uv sync                             # creates .venv/, installs everything
```

Optional, only for the Stan/PyMC cross-checks (`fit_stan.py`; also needs
[CmdStan](https://mc-stan.org/docs/cmdstan-guide/) installed separately):

```bash
uv sync --extra crosscheck
```

Slidev itself comes from the **repository root**, not from here:

```bash
cd ../../..                         # repo root
npm install                         # once, shared by every talk
```

### Jupyter kernel (first time only, or on a new machine)

```bash
uv run python -m ipykernel install --user --name bayes-tidit \
    --display-name "Python (bayes-tidit)"
```

Then in VS Code / Jupyter, pick the **"Python (bayes-tidit)"** kernel for
`bayes_workflow.ipynb`.

## Start the presentation

```bash
cd src/slidev/2026_bayes_tidit
npx slidev bayes_tidit.md                        # localhost:3030
npx slidev bayes_tidit.md --remote --port 3030    # also reachable on the LAN/Tailscale
```

`--remote` opens presenter mode (which *controls* the deck) to anyone who can
reach this machine on the network — fine on a private retreat network, worth
knowing.

For the live part of the talk (minutes 3–20), open `bayes_workflow.ipynb` in
VS Code with the `bayes-tidit` kernel selected, alongside the slides.

## Everyday commands

```bash
uv run jupyter nbconvert --to notebook --execute --inplace bayes_workflow.ipynb
                                     # re-run the whole notebook, checks every cell in order
uv run python make_figs.py          # regenerate the static figures in imgs/
uv sync --extra crosscheck && uv run python fit_stan.py   # Stan cross-check
uv add <package>                    # add a new dependency (updates pyproject.toml + uv.lock)
```

## Files

See the table in `CLAUDE.md` — it also has the verified numbers, the
agreed story/beat-sheet, and a list of gotchas worth reading before editing
the deck or the notebook (in particular: SVG paint attributes in Slidev/Vue
must go through `style=`, never bare attributes, or UnoCSS silently makes
them invisible).
