"""Condition the DGP on the observed data with Stan, and plot the posterior.

Run:  ~/miniconda3/bin/python fit_stan.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from cmdstanpy import CmdStanModel

HERE = os.path.dirname(os.path.abspath(__file__))
IMGS = os.path.join(HERE, "imgs")

from make_figs import x, y, XG, C_DATA, C_FIT, C_BAND, style, save  # noqa: E402

STAN = """
data {
  int<lower=0> N;
  vector[N] x;
  vector[N] y;
  int<lower=0> G;
  vector[G] xg;
}
parameters {
  real a;                       // slope   [mmHg per year]
  real b;                       // intercept at age 0
  real<lower=0> sigma;          // spread of the data
}
model {
  a ~ normal(1, 0.4);           // SBP rises with age, but we are not certain
  b ~ normal(90, 15);           // a newborn has some blood pressure
  sigma ~ normal(0, 20);        // half-normal, sigma is positive
  y ~ normal(b + a * x, sigma); // <- the only line that mentions the data
}
generated quantities {
  vector[G] mu_g = b + a * xg;              // posterior mean curve
  vector[G] y_g;                            // posterior predictive
  for (g in 1:G) y_g[g] = normal_rng(mu_g[g], sigma);
}
"""

stan_file = os.path.join(HERE, "model.stan")
with open(stan_file, "w") as f:
    f.write(STAN)

model = CmdStanModel(stan_file=stan_file)
fit = model.sample(data={"N": len(x), "x": x, "y": y, "G": len(XG), "xg": XG},
                   chains=4, iter_sampling=2000, iter_warmup=1000,
                   seed=42, show_progress=False, show_console=False)

summ = fit.summary()
print(summ.loc[["a", "b", "sigma"], ["Mean", "StdDev", "5%", "95%", "R_hat", "ESS_bulk"]])

mu = fit.stan_variable("mu_g")      # (draws, G)
yg = fit.stan_variable("y_g")
mu_lo, mu_md, mu_hi = np.percentile(mu, [2.5, 50, 97.5], axis=0)
y_lo, y_hi = np.percentile(yg, [2.5, 97.5], axis=0)

fig, ax = plt.subplots(figsize=(7, 4.3))
ax.fill_between(XG, y_lo, y_hi, color=C_BAND, alpha=.13,
                label="95% posterior predictive")
ax.fill_between(XG, mu_lo, mu_hi, color=C_BAND, alpha=.35,
                label="95% credible interval for the mean")
ax.plot(XG, mu_md, color=C_FIT, lw=2.2, label="posterior mean")
ax.scatter(x, y, s=45, color=C_DATA, zorder=3, label="observed data")
style(ax, "Posterior: the DGP conditioned on the observed data")
ax.set_xlim(0, 90)
ax.legend(frameon=False, fontsize=11, loc="upper left")
save(fig, "05_posterior.png")

# prior -> posterior for the slope
fig, ax = plt.subplots(figsize=(7, 3.4))
grid = np.linspace(-0.5, 2.5, 400)
prior = np.exp(-0.5 * ((grid - 1) / 0.4) ** 2) / (0.4 * np.sqrt(2 * np.pi))
ax.plot(grid, prior, color="#7f8c8d", lw=2, ls="--", label="prior  a ~ N(1, 0.4)")
ax.hist(fit.stan_variable("a"), bins=60, density=True, color=C_BAND,
        alpha=.65, label="posterior")
ax.set_xlabel("slope a  [mmHg per year]")
ax.set_ylabel("density")
ax.set_title("Conditioning on 33 women sharpens the belief about the slope")
ax.legend(frameon=False, fontsize=11)
save(fig, "06_prior_posterior.png")

a_s = fit.stan_variable("a")
print(f"\nP(slope > 0 | data) = {np.mean(a_s > 0):.4f}")
print(f"posterior slope mean {a_s.mean():.3f}, 95% CrI "
      f"[{np.percentile(a_s, 2.5):.3f}, {np.percentile(a_s, 97.5):.3f}]")
print("OLS for comparison: slope 1.105, 95% CI [0.685, 1.525]")
