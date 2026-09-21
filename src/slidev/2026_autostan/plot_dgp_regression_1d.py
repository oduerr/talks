#!/usr/bin/env python3
"""Generate a 'data only' figure for the regression_1d_large DGP (for the talk).

Shows training scatter data + true underlying function + true noise band.
Outliers (shifted ±10–15 units) are shown as clamped triangles at the plot edge.
No model fit — purely the data generating process.
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parent.parent.parent
TRAIN_CSV = REPO / "datasets" / "regression_1d_large" / "train.csv"
OUT_FILE = Path(__file__).resolve().parent / "extra_figures" / "dgp_regression_1d.png"

YLIM = (-6, 8)


def f_true(x):
    return 2 * np.sin(1.2 * x) + 0.3 * x


def sigma_true(x):
    return 0.3 + 0.8 * np.exp(-0.5 * ((x - 3) / 1.5) ** 2)


def load_train():
    with open(TRAIN_CSV) as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    x = np.array([float(r["predictor"]) for r in rows])
    y = np.array([float(r["response"]) for r in rows])
    return x, y


def scatter_clamped(ax, x, y, ylim, **kw):
    """Plot in-range points normally; outliers as edge-pinned triangles."""
    lo, hi = ylim
    x, y = np.asarray(x), np.asarray(y)
    mask_in = (y >= lo) & (y <= hi)
    mask_hi = y > hi
    mask_lo = y < lo

    if mask_in.any():
        ax.scatter(x[mask_in], y[mask_in], **kw)
    marker_kw = {k: v for k, v in kw.items() if k != "label"}
    if mask_hi.any():
        ax.scatter(x[mask_hi], np.full(mask_hi.sum(), hi - 0.35),
                   marker="^", **marker_kw)
    if mask_lo.any():
        ax.scatter(x[mask_lo], np.full(mask_lo.sum(), lo + 0.35),
                   marker="v", **marker_kw)


def main():
    x_train, y_train = load_train()
    x_grid = np.linspace(-0.2, 5.2, 300)

    fig, ax = plt.subplots(figsize=(5.5, 3.8))

    # True noise band
    ax.fill_between(
        x_grid,
        f_true(x_grid) - 2 * sigma_true(x_grid),
        f_true(x_grid) + 2 * sigma_true(x_grid),
        alpha=0.15,
        color="gray",
        label=r"True $\pm 2\sigma(x)$",
    )

    # True mean function
    ax.plot(
        x_grid,
        f_true(x_grid),
        "k-",
        linewidth=1.8,
        label=r"True $f(x)$",
    )

    # Training data (with clamped outliers as triangles)
    scatter_clamped(
        ax,
        x_train,
        y_train,
        ylim=YLIM,
        s=12,
        color="#1565C0",
        alpha=0.50,
        zorder=4,
        label="Training data",
        linewidths=0,
    )

    ax.set_xlabel("$x$", fontsize=12)
    ax.set_ylabel("$y$", fontsize=12)
    ax.set_ylim(*YLIM)
    ax.legend(fontsize=10, loc="upper left")
    ax.set_title("Data Generating Process (n=500)", fontsize=12, fontweight="bold")

    fig.tight_layout()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FILE, dpi=150, bbox_inches="tight")
    print(f"Saved → {OUT_FILE}")


if __name__ == "__main__":
    main()
