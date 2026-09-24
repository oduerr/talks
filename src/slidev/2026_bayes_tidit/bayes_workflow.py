# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python (bayes-tidit)
#     language: python
#     name: bayes-tidit
# ---

# %% [markdown]
# # Bayesian workflow: blood pressure and age
#
# 33 North American women. We know two numbers per woman: **age** and **systolic blood pressure**.
#
# We will not look at the blood pressures until step 3.

# %%
import numpy as np
import matplotlib.pyplot as plt
np.random.seed(1)
xg = np.linspace(0, 90, 33)   # ages (later we will use the actual ages)

# %% [markdown]
# ## 1. Write down how the data could have come about
#
# Four lines of numpy. Every number is a belief, written down *before* looking at the data. We know the ages of the women, but not their blood pressures. We assume that the blood pressure of a woman is a linear function of her age on average but the age of course this does not fully determine the blood pressure.

# %%
np.random.seed(4)
a     = np.random.normal(1, 5)          # SBP rises with age — how fast? not sure
b     = np.random.normal(100, 50)       # a newborn already has some blood pressure
sigma = abs(np.random.normal(0, 20))    # there is spread +-20 mmHg (numpy has no half-normal)

sbp_sim = np.random.normal(b + a*xg, sigma) 

plt.scatter(xg, sbp_sim, color="C3")
plt.xlabel("age"); plt.ylabel("one simulated data set");

# %% [markdown]
# ## 2. Prior predictive: run the story 200 times
#
# We just drew a single "population" of 33 women, and it looked kind of reasonable. Let's do this for 200 populations and see what happens. We show the expected value (lines) for every population and the simulated data points for the last one.
#
# Does the data this story produces look like data we believe in? **Edit the priors and re-run until it does.**

# %%
sims = []
for i in range(200):
    np.random.seed(i)
    a     = np.random.normal(1, 5)          # tighter: (1, 0.4)
    b     = np.random.normal(100, 50)       # tighter: (100, 15)
    sigma = abs(np.random.normal(0, 20))
    sims.append(np.random.normal(b + a*xg, sigma))
    plt.plot(xg, b + a*xg, color="gray", alpha=.25, lw=1)
sims = np.array(sims)
plt.scatter(xg, sims[-1], color="C3", s=20, zorder=3)   # the last simulated population

plt.axhline(0, ls=":", color="k")
plt.xlabel("age")
plt.ylabel("SBP")
print(f"simulated patients: 1–99% = {np.percentile(sims, 1):.0f} … {np.percentile(sims, 99):.0f} mmHg")
print(f"below zero: {(sims < 0).mean():.1%}")

# %% [markdown]
# Negative blood pressure for a quarter of the patients. The priors *looked* harmless.
#
# Tighter: `a ~ N(1, 0.4)`, `b ~ N(100, 15)` — go back up, change the numbers, re-run.

# %% [markdown]
# ## 3. Now look at the data

# %%
age = np.array([22, 41, 52, 23, 41, 54, 24, 46, 56, 27, 47, 57, 28, 48, 58, 9, 49, 59, 30, 49, 63,
                32, 50, 67, 33, 51, 71, 35, 51, 77, 40, 51, 81])
sbp = np.array([131, 139, 128, 128, 171, 105, 116, 137, 145, 106, 111, 141, 114, 115, 153, 123, 133,
                157, 117, 128, 155, 122, 183, 176, 99, 130, 172, 121, 133, 178, 147, 144, 217])  # <- do not look yet
                
plt.scatter(age, sbp, color="k", s=20)
plt.xlabel("age"); plt.ylabel("systolic blood pressure [mmHg]");

# %% [markdown]
# ## 4. Run the story backwards
#
# numpy only runs forward: it forgets which distribution a number came from, and it can *draw*
# from a distribution but not *evaluate* it. To go backwards we need a language that remembers. There are many so called probabilistic programming languages (Stan, PyMC, TensorFlow Probability, etc.) but we will use NumPyro.
#
# The same four lines (wrapped in a function)

# %%
import numpyro, numpyro.distributions as dist
from numpyro.infer import MCMC, NUTS, Predictive
from jax import random

def model(age, sbp=None):
    a     = numpyro.sample("a",     dist.Normal(1, 0.4))
    b     = numpyro.sample("b",     dist.Normal(100, 15))
    sigma = numpyro.sample("sigma", dist.HalfNormal(20))
    numpyro.sample("sbp", dist.Normal(b + a*age, sigma), obs=sbp)


# %% [markdown]
# **Forward** — no data passed, so `sbp=None`. Exactly the same numpy loop, as before:

# %%
prior = Predictive(model, num_samples=200)(random.PRNGKey(0), age)

for a_, b_ in zip(prior["a"], prior["b"]):
    plt.plot(xg, b_ + a_*xg, color="gray", alpha=.25, lw=1)
plt.scatter(age, sbp, color="k", s=20, zorder=3)
plt.xlabel("age"); plt.ylabel("SBP");

# %% [markdown]
# **Backward** — pass the data:

# %%
mcmc = MCMC(NUTS(model), num_warmup=1000, num_samples=2000, progress_bar=False)
mcmc.run(random.PRNGKey(2), age, sbp=sbp)
post = mcmc.get_samples()

a_post = np.array(post["a"])
print(f"slope a:  mean {a_post.mean():.2f}   95% credible interval "
      f"[{np.percentile(a_post, 2.5):.2f}, {np.percentile(a_post, 97.5):.2f}]  mmHg per year")
print(f"P(a > 0 | data) = {(a_post > 0).mean():.4f}")

# %%
for a_, b_ in zip(post["a"][::40], post["b"][::40]):
    plt.plot(xg, b_ + a_*xg, color="C0", alpha=.25, lw=1)
plt.scatter(age, sbp, color="k", s=20, zorder=3)
plt.xlabel("age"); plt.ylabel("SBP"); plt.title("the fan collapses onto the data");

# %%
xs = np.linspace(-0.5, 2.5, 300)
plt.hist(a_post, bins=50, density=True, alpha=.6, label="posterior")
plt.plot(xs, np.exp(-0.5*((xs - 1)/0.4)**2) / (0.4*np.sqrt(2*np.pi)), "k--", label="prior  N(1, 0.4)")
plt.xlabel("slope a  [mmHg per year]"); plt.legend();

# %% [markdown]
# ### What this means more formally (skip in the talk)
#
# In the Bayesian view probability is a degree of belief, so the parameters
# $\theta = (a, b, \sigma)$ are random variables too. The first three lines of
# `model` are our belief *before* seeing data, the **prior** $p(\theta)$. The
# fourth line, `sbp = Normal(b + a*age, sigma)`, says how likely a data set $D$
# is for given parameters, the **likelihood** $p(D \mid \theta)$. Running
# forward means sampling $\theta$ from the prior and then $D$ from the
# likelihood. Bayes' rule turns this around and gives the belief *after*
# seeing the data, the **posterior**:
#
# $$p(\theta \mid D) = \frac{p(D \mid \theta)\, p(\theta)}{p(D)} \;\propto\; p(D \mid \theta)\, p(\theta)$$
#
# The numerator is exactly what `model` evaluates when it is run with `obs=sbp`:
# it multiplies the probability of every `sample` line, the three priors and the
# one likelihood term. The denominator $p(D)$ is an integral over all
# parameters. In this three-parameter problem it could be done numerically, but
# in general it cannot, and it is not needed: **MCMC** (Markov chain Monte
# Carlo) produces samples from the posterior using only the unnormalised
# numerator. The sampler walks through parameter space, proposing a move and
# accepting it with a probability that depends on the ratio of posterior
# densities at the new and the old point. The chain spends time in each region
# in proportion to its posterior probability, so a histogram of the chain *is*
# the posterior. NUTS, used above, is a variant that uses the gradient of
# $\log p(D \mid \theta)\, p(\theta)$ to propose good moves, which is why
# it needs a framework that can evaluate and differentiate the model.
#
# Below: the first 150 steps of the chain as a path in the $(a, b)$ plane, on
# top of all 2000 posterior samples. The slope and the intercept are negatively
# correlated (a steeper line has to start lower to still pass through the
# data), which the posterior captures and a table of two separate intervals
# would not.

# %%
a_all, b_all = np.array(post["a"]), np.array(post["b"])
n = 150
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

ax1.plot(a_all[:n], color="C0", lw=1)
ax1.set_xlabel("step of the chain"); ax1.set_ylabel("slope a"); ax1.set_title(f"trace: the first {n} draws of a")

ax2.scatter(a_all, b_all, s=6, color="C0", alpha=.15, label="all posterior samples")
ax2.plot(a_all[:n], b_all[:n], color="k", lw=.8, alpha=.7, label=f"path of the first {n} steps")
ax2.set_xlabel("slope a"); ax2.set_ylabel("intercept b"); ax2.set_title("the chain wandering through the posterior")
ax2.legend(loc="upper right", fontsize=8);

# %% [markdown]
# ## 5. The same problem, the classical way

# %%
import statsmodels.api as sm
fit = sm.OLS(sbp, sm.add_constant(age)).fit()
print(fit.summary(xname=["const", "age"], yname="sbp").tables[1])
