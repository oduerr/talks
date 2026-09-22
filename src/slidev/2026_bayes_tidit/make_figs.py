"""Figures for the TIDIT retreat talk on Bayesian statistics.

Data: systolic blood pressure vs. age, 33 North American women.
Taken from Sick & Duerr, "Probabilistic Deep Learning" (Manning), ch. 1.

Run:  ~/miniconda3/bin/python make_figs.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
IMGS = os.path.join(HERE, "imgs")
os.makedirs(IMGS, exist_ok=True)

rng = np.random.default_rng(42)

# --- data -------------------------------------------------------------------
x = np.array([22, 41, 52, 23, 41, 54, 24, 46, 56, 27, 47, 57, 28, 48, 58,
              9, 49, 59, 30, 49, 63, 32, 50, 67, 33, 51, 71, 35, 51, 77,
              40, 51, 81], float)
y = np.array([131, 139, 128, 128, 171, 105, 116, 137, 145, 106, 111, 141,
              114, 115, 153, 123, 133, 157, 117, 128, 155, 122, 183, 176,
              99, 130, 172, 121, 133, 178, 147, 144, 217], float)

C_DATA, C_FIT, C_BAND, C_PRIOR = "#1a3a5c", "#c0392b", "#2d5986", "#7f8c8d"
plt.rcParams.update({"font.size": 13, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 140})

XG = np.linspace(0, 90, 200)


def style(ax, title):
    ax.set_xlabel("age [years]")
    ax.set_ylabel("systolic blood pressure [mmHg]")
    ax.set_title(title)


def save(fig, name):
    fig.tight_layout()
    p = os.path.join(IMGS, name)
    fig.savefig(p)
    plt.close(fig)
    print("wrote", os.path.basename(p))


# --- 1. the data ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 4.3))
ax.scatter(x, y, s=45, color=C_DATA, zorder=3)
style(ax, f"Systolic blood pressure of {len(x)} North American women")
ax.set_xlim(0, 90)
save(fig, "01_data.png")

# --- 2. classical fit -------------------------------------------------------
res = stats.linregress(x, y)
n = len(x)
yhat = res.intercept + res.slope * x
dof = n - 2
s = np.sqrt(((y - yhat) ** 2).sum() / dof)           # residual sd
sxx = ((x - x.mean()) ** 2).sum()
tcrit = stats.t.ppf(0.975, dof)

se_mean = s * np.sqrt(1 / n + (XG - x.mean()) ** 2 / sxx)
se_pred = s * np.sqrt(1 + 1 / n + (XG - x.mean()) ** 2 / sxx)
line = res.intercept + res.slope * XG

fig, ax = plt.subplots(figsize=(7, 4.3))
ax.fill_between(XG, line - tcrit * se_pred, line + tcrit * se_pred,
                color=C_BAND, alpha=.13, label="95% prediction interval")
ax.fill_between(XG, line - tcrit * se_mean, line + tcrit * se_mean,
                color=C_BAND, alpha=.35, label="95% CI for the mean")
ax.plot(XG, line, color=C_FIT, lw=2.2, label="least-squares fit")
ax.scatter(x, y, s=45, color=C_DATA, zorder=3)
style(ax, f"SBP = {res.intercept:.1f} + {res.slope:.2f} · age")
ax.set_xlim(0, 90)
ax.legend(frameon=False, fontsize=11, loc="upper left")
save(fig, "02_classical.png")

print(f"\nOLS: intercept {res.intercept:.3f} (se {res.intercept_stderr:.3f}), "
      f"slope {res.slope:.3f} (se {res.stderr:.3f}), resid sd {s:.2f}, "
      f"p(slope) {res.pvalue:.2e}")
print(f"     95% CI slope: [{res.slope - tcrit * res.stderr:.3f}, "
      f"{res.slope + tcrit * res.stderr:.3f}]")


# --- 3+4. prior predictive --------------------------------------------------
def prior_predictive(a_mu, a_sd, b_mu, b_sd, sig_scale, ndraw=60):
    a = rng.normal(a_mu, a_sd, ndraw)
    b = rng.normal(b_mu, b_sd, ndraw)
    sig = np.abs(rng.normal(0, sig_scale, ndraw))          # half-normal
    return a, b, sig


def plot_prior(a, b, sig, title, name, show_data=False):
    fig, ax = plt.subplots(figsize=(7, 4.3))
    for ai, bi, si in zip(a, b, sig):
        ax.plot(XG, bi + ai * XG, color=C_PRIOR, alpha=.45, lw=1)
    # one fully simulated data set (mean + noise) to stress it is data, not lines
    ai, bi, si = a[0], b[0], sig[0]
    ax.scatter(x, rng.normal(bi + ai * x, si), s=40, color=C_FIT,
               alpha=.85, zorder=3, label="one simulated data set")
    if show_data:
        ax.scatter(x, y, s=45, color=C_DATA, zorder=4, label="observed data")
    ax.axhline(0, color="k", lw=.8, ls=":")
    style(ax, title)
    ax.set_xlim(0, 90)
    ax.legend(frameon=False, fontsize=11, loc="upper left")
    save(fig, name)


def pp_stats(a_mu, a_sd, b_mu, b_sd, sig_scale, ndraw=4000):
    """Full prior predictive *at the data level* (i.e. including the noise)."""
    a = rng.normal(a_mu, a_sd, ndraw)[:, None]
    b = rng.normal(b_mu, b_sd, ndraw)[:, None]
    sig = np.abs(rng.normal(0, sig_scale, ndraw))[:, None]
    sim = rng.normal(b + a * x[None, :], sig)
    lo, hi = np.percentile(sim, [1, 99])
    return lo, hi, (sim < 0).mean()


a, b, sig = prior_predictive(1, 5, 100, 50, 20)
plot_prior(a, b, sig,
           "Prior predictive: a~N(1,5), b~N(100,50)  →  implausible",
           "03_prior_vague.png")
lo, hi, neg = pp_stats(1, 5, 100, 50, 20)
print(f"\nvague prior predictive: 1%..99% = {lo:.0f} .. {hi:.0f} mmHg, "
      f"P(SBP < 0) = {neg:.1%}")

a2, b2, sig2 = prior_predictive(1, 0.4, 90, 15, 20)
plot_prior(a2, b2, sig2,
           "Prior predictive: a~N(1,0.4), b~N(90,15)  →  plausible",
           "04_prior_tight.png")
lo2, hi2, neg2 = pp_stats(1, 0.4, 90, 15, 20)
print(f"tight prior predictive: 1%..99% = {lo2:.0f} .. {hi2:.0f} mmHg, "
      f"P(SBP < 0) = {neg2:.1%}")
