
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
