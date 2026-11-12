# %% [markdown]
# # Ceilometer: DGP und Stichprobenverteilung der Schätzer
#
# Dieses Notebook gehört zu den Folien 11 bis 15 des Ceilometer-Decks.
# Als Skript: `uv run dgp_sim.py` schreibt die Bilder nach `public/ceilometer/`.
# Als Text-Notebook: in Cursor / VS Code die Zellen (`# %%`) einzeln ausführen ("Run Cell");
# dann werden die Bilder nur angezeigt, nicht gespeichert.
#
# **Modell**, eine Periode p = 1..F, Chip k = 0..1022:
# - Laser an (c_k = 1): im Mittel n Photonen gehen hoch, ihre Zahl ist Poisson(n) (Laserlicht).
#   Jedes kommt mit Wahrscheinlichkeit q zurück und wird gezählt. Ausdünnung: Poisson(n·q) = Poisson(s) Klicks,
#   exakt. Sie kommen d Bins später an.
# - Hintergrund: Poisson(b) Klicks in jedem Bin.
#
# Zahlen wie im Rest des Decks: s = n·q = 0,01, b = 0,10, d = 100.
# F = 100 Perioden (10 ms), damit der Schätzer für d manchmal danebenliegt (SNR etwa 4,9).
# Bei F = 9775 (1 s) trifft er immer.

# %%
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "matplotlib", "scipy"]
# ///
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

try:                                   # als Skript: Bilder speichern
    OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "ceilometer")
    SAVE = os.path.isdir(OUT)
except NameError:                      # im Notebook gibt es kein __file__: nur anzeigen
    OUT, SAVE = None, False

BLUE, GREY, RED = "#0070c0", "#8a8a8a", "#b5523b"
plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False,
                     "font.family": ["Helvetica Neue", "DejaVu Sans"]})


def show(fig, name):
    if SAVE:
        fig.savefig(os.path.join(OUT, name), dpi=160, bbox_inches="tight", facecolor="white")
        plt.close(fig)
    else:
        plt.show()


# %% [markdown]
# ## Pseudozufallsfolge und Parameter
#
# Die m-Folge der Länge 1023 aus einem 10-Bit-Schieberegister, wie `fogcast.prn_processing.sequence`.
# 512 Chips sind an, 511 aus.

# %%
def m_sequence(N=1023, seed=0x3FF):
    """LFSR x^10 + x^3 + 1."""
    state, out = seed, []
    for _ in range(N):
        out.append(state & 1)
        fb = (state ^ (state >> 3)) & 1
        state = (state >> 1) | (fb << 9)
    return np.array(out)


N = 1023
c = m_sequence()
n, q = 10**11, 1e-13            # Photonen je An-Chip, Wahrscheinlichkeit zurück und gezählt
s, b, d, F = n * q, 0.10, 100, 100
print(f"An-Chips: {c.sum()}, Aus-Chips: {N - c.sum()}, s = n*q = {s}")

#%%
# Strip Chart der Klicks über die Chips 
plt.plot(np.arange(N)[0:100], c[0:100], color=BLUE, lw=0.7)
plt.xlabel("Chip k")
plt.ylabel("Klicks c_k")
plt.title("Strip Chart der Klicks über die Chips")
plt.show()


# %% [markdown]
# ## Der DGP, wörtlich als Schleife (Folie 11)
#
# Danach derselbe DGP vektorisiert: die Summe von F unabhängigen Poisson(n·q) ist Poisson(F·n·q),
# die Summe von F unabhängigen Poisson(b) ist Poisson(F·b).

# %%
def dgp_loop(rng):
    h = np.zeros(N, dtype=np.int64)
    for p in range(F):                       # Perioden
        for k in range(N):                   # Chips
            if c[k] == 1:                    # Laser an
                treffer = rng.poisson(n * q)   # Pois(n) Photonen, je mit q gezählt: Pois(n·q)
                h[(k + d) % N] += treffer       # kommt d Bins später an
            h[k] += rng.poisson(b)              # Hintergrund in jedem Bin
    return h


def dgp_fast(rng):
    signal = np.where(np.roll(c, d) == 1, rng.poisson(F * n * q, size=N), 0)
    return signal + rng.poisson(F * b, size=N)


# %% [markdown]
# ## Schätzer (Folien 9 und 10)
#
# C(d) für alle d auf einmal mit FFT, wie `prn_processing.process`.
# d̂ = argmax C(d). Bei gegebenem d ist ŝ die Differenz der Gruppenmittel geteilt durch F
# (ML = KQ).

# %%
u = 2 * c - 1
U = np.conj(np.fft.rfft(u))


def estimate(h):
    C = np.fft.irfft(np.fft.rfft(h) * U, N) - h.mean()
    dh = int(np.argmax(C))

    def s_at(dd):
        on = np.roll(c, dd) == 1
        return (h[on].mean() - h[~on].mean()) / F

    return C, dh, s_at(dh), s_at(d)


# %% [markdown]
# ## Ein Lauf (Folie 11)
#
# Zuerst eine Probe: die FFT-Korrelation ist gleich der direkten Summe Σ u_{k−d} h_k − h̄.

# %%
rng = np.random.default_rng(12)
h1 = dgp_loop(rng)
C1, dh1, sh1, _ = estimate(h1)
Cdirect = np.array([np.dot(np.roll(u, j), h1) for j in range(N)]) - h1.mean()
assert np.allclose(C1, Cdirect)
print(f"Ein Lauf (Schleife): Klicks {h1.sum()}, d_hat {dh1}, s_hat {sh1:.4f}")

fig, ax = plt.subplots(figsize=(7, 2.8))
ax.plot(np.arange(N), C1, color=BLUE, lw=0.7)
ax.axvline(d, color=RED, ls=":", lw=1)
ax.annotate(f"Schätzung: d̂ = {dh1}, ŝ = {sh1:.4f}".replace(".", ","), (dh1, C1[dh1]), (300, C1[dh1] * 0.92), color=BLUE,
            arrowprops=dict(arrowstyle="->", color=BLUE), fontsize=12)
ax.set_title("wahr: d = 100, s = 0,0100   (rote Linie)", fontsize=12, loc="left", color=RED)
ax.set_xlabel("Verschiebung d"); ax.set_ylabel("C(d)"); ax.set_yticks([])
show(fig, "dgp_ein_lauf.png")

# %% [markdown]
# ## Nur das Histogramm h desselben Laufs (ceilometer.md, Folie DGP)

# %%
fig, axs = plt.subplots(2, 1, figsize=(7, 4.2), gridspec_kw={"height_ratios": [1, 1], "hspace": 0.55})
a = axs[0]
a.vlines(np.arange(N), 0, h1, color=BLUE, lw=0.6)
a.set_xlim(-5, N + 5); a.set_ylabel("$h_k$")
a.set_title(f"alle 1023 Bins, F = {F} Perioden, " + f"{h1.sum():,}".replace(",", " ") + " Klicks", fontsize=11, loc="left")
a = axs[1]
zk = np.arange(90, 130)
a.vlines(zk, 0, h1[zk], color=BLUE, lw=2.2)
a.set_xlim(zk[0] - 1, zk[-1] + 1); a.set_xlabel("Bin k"); a.set_ylabel("$h_k$")
a.set_title("Ausschnitt: Bins 90 bis 129", fontsize=11, loc="left")
show(fig, "dgp_h.png")

# %% [markdown]
# ## Derselbe Lauf: vom Histogramm h zum Schätzer (Folie 12)

# %%
on = np.roll(c, dh1) == 1
m_on, m_off = h1[on].mean(), h1[~on].mean()
print(f"h: Mittel An-Bins {m_on:.2f}, Aus-Bins {m_off:.2f}, s_hat = ({m_on:.2f} - {m_off:.2f})/{F} = {(m_on - m_off) / F:.4f}")
fig, axs = plt.subplots(1, 3, figsize=(14, 3.5), gridspec_kw={"width_ratios": [1.5, 1, 1.2], "wspace": 0.3})
a = axs[0]
zk = np.arange(90, 150)
a.bar(zk, h1[zk], width=0.9, color=np.where(on[zk], BLUE, "#9ec3e6"))
a.axhline(m_off, color="#6a9fd0", ls="--", lw=1); a.axhline(m_on, color=BLUE, ls="--", lw=1)
a.set_xlabel("Bin k (Ausschnitt 90 bis 149 von 1023)"); a.set_ylabel("$h_k$ (Klicks)")
a.set_title(f"1  Histogramm h ({h1.sum()} Klicks); dunkel = An-Bin bei d̂", fontsize=12, loc="left")
a = axs[1]
vals = np.arange(h1.min(), h1.max() + 2) - 0.5
a.hist(h1[~on], bins=vals, color="#9ec3e6", alpha=0.9, label=f"Aus-Bins: Mittel {m_off:.2f}".replace(".", ","))
a.hist(h1[on], bins=vals, histtype="step", color=BLUE, lw=2, label=f"An-Bins: Mittel {m_on:.2f}".replace(".", ","))
a.axvline(m_off, color="#6a9fd0", ls="--", lw=1); a.axvline(m_on, color=BLUE, ls="--", lw=1)
a.set_xlabel("$h_k$"); a.set_yticks([]); a.legend(frameon=False, fontsize=10, loc="upper right")
a.set_ylim(0, a.get_ylim()[1] * 1.5)
a.set_title(f"2  Werte nach An/Aus bei d̂ = {dh1}", fontsize=12, loc="left")
a = axs[2]
a.plot(np.arange(N), C1, color=BLUE, lw=0.6)
a.axvline(d, color=RED, ls=":", lw=1)
a.annotate(f"d̂ = {dh1}", (dh1, C1[dh1]), (330, C1[dh1] * 0.9), color=BLUE, arrowprops=dict(arrowstyle="->", color=BLUE))
a.set_xlabel("Verschiebung d"); a.set_yticks([])
a.set_title("3  Korrelation C(d)", fontsize=12, loc="left")
show(fig, "dgp_h_schaetzer.png")

# %% [markdown]
# ## Schleife gegen vektorisiert
#
# Je 150 Läufe. Haben die beiden DGPs dieselbe Verteilung von ŝ (beim wahren d)?
# Zwei-Stichproben-KS-Test. Dauert etwa eine halbe Minute (die Schleife ist langsam).

# %%
rngA, rngB = np.random.default_rng(1), np.random.default_rng(2)
A = np.array([estimate(dgp_loop(rngA))[3] for _ in range(150)])
B = np.array([estimate(dgp_fast(rngB))[3] for _ in range(150)])
ks = stats.ks_2samp(A, B)
print(f"Schleife vs vektorisiert, s_hat(d wahr): Mittel {A.mean():.5f} vs {B.mean():.5f}, "
      f"SD {A.std():.5f} vs {B.std():.5f}, KS p = {ks.pvalue:.2f}")
assert ks.pvalue > 0.01

# %% [markdown]
# ## Viele Läufe: die Stichprobenverteilung (Folie 13)
#
# 2000 Läufe mit dem vektorisierten DGP. Theorie für die SD von ŝ beim wahren d:
# √((b+s)/(512·F) + b/(511·F)). SNR = (s/2)·√(F·N/(b + s/2)).
# Probiere andere Werte für F (z. B. 30 oder 300) und schau, wie sich die Trefferquote ändert.

# %%
R = 2000
rng = np.random.default_rng(7)
res = np.array([estimate(dgp_fast(rng))[1:] for _ in range(R)])
dh, sh_est, sh_true = res[:, 0].astype(int), res[:, 1], res[:, 2]
hit = dh == d
sd_theory = np.sqrt((b + s) / (F * 512) + b / (F * 511))
snr = (s / 2) * np.sqrt(F * N / (b + s / 2))
print(f"SNR Theorie {snr:.2f}; Treffer d_hat = d: {hit.sum()} von {R} ({hit.mean():.1%})")
print(f"s_hat bei wahrem d: Mittel {sh_true.mean():.5f} (wahr {s}), SD {sh_true.std():.5f}, Theorie SD {sd_theory:.5f}")
print(f"s_hat bei d_hat:    Mittel {sh_est.mean():.5f}; bei Fehltreffern Mittel {sh_est[~hit].mean():.5f}")

fig, axs = plt.subplots(1, 2, figsize=(12, 3.6))
a = axs[0]
a.hist(dh[~hit], bins=np.arange(0, N + 32, 32), color=GREY, label=f"daneben: {np.sum(~hit)}")
a.bar([d], [hit.sum()], width=12, color=BLUE, label=f"d̂ = 100: {hit.sum()}")
a.set_yscale("log"); a.set_xlabel("d̂"); a.set_ylabel("Anzahl Läufe (log)")
a.set_title("Stichprobenverteilung von d̂", fontsize=12, loc="left"); a.legend(frameon=False, fontsize=11)
a = axs[1]
bins = np.linspace(0.002, 0.018, 50)
a.hist(sh_true, bins=bins, color=BLUE, alpha=0.6, density=True, label="ŝ beim wahren d")
a.hist(sh_est, bins=bins, histtype="step", color=RED, lw=1.5, density=True, label="ŝ beim geschätzten d̂")
xs = np.linspace(bins[0], bins[-1], 300)
a.plot(xs, stats.norm.pdf(xs, s, sd_theory), color="#222", lw=1, ls="--", label="Theorie N(s, SD²)")
a.axvline(s, color="#222", lw=1)
a.set_xlabel("ŝ"); a.set_yticks([]); a.set_ylim(0, a.get_ylim()[1] * 1.45); a.legend(frameon=False, fontsize=10, loc="upper left")
a.set_title("Stichprobenverteilung von ŝ", fontsize=12, loc="left")
fig.text(0.99, -0.06, f"simuliert, {R} Läufe, F = {F}, b = 0,10, s = 0,01, d = 100, Seed 7", ha="right", fontsize=9, color=GREY)
show(fig, "dgp_viele_laeufe.png")

# nur die Stichprobenverteilung von d̂, für ceilometer.md
fig, a = plt.subplots(figsize=(6, 3.6))
a.hist(dh[~hit], bins=np.arange(0, N + 32, 32), color=GREY, label=f"daneben: {np.sum(~hit)}")
a.bar([d], [hit.sum()], width=12, color=BLUE, label=f"d̂ = d₀ = {d}: {hit.sum()}")
a.set_yscale("log"); a.set_xlabel("d̂"); a.set_ylabel("Anzahl Läufe (log)")
a.set_title(f"P(d̂ | d₀): {R} Läufe, F = {F}", fontsize=12, loc="left"); a.legend(frameon=False, fontsize=11)
show(fig, "dgp_dhat.png")

# %% [markdown]
# ## Mehrere Höhen: C(d) schätzt das ganze Profil (Folie 15)
#
# Jetzt streut Licht aus vielen Höhen zurück: λ_k = b + Σ_j s_j c_{k−j}.
# Hier: Aerosol am Boden (nimmt mit der Höhe ab), eine Wolke bei d = 100 (1,5 km, drei Bins dick)
# und eine dünne Schicht bei d = 400 (6 km). F = 9775 Perioden (1 s), wie im Gerät.
#
# Für jedes d ist ŝ_d = 2·C(d) / (F·(N − 1/N)) = C(d) / (511,5005·F), dieselbe Formel wie für ein Ziel.
# Erwartung (exakt): E[ŝ_d] = s_d − Σ_{j≠d} s_j / 1022 (winziger Abzug durch alle anderen Höhen).
# Varianz: jedes h_k enthält Photonen aus allen Höhen, darum Var(ŝ_d) ≈ 4·(b + Σ_j s_j / 2)/(F·N), gleich für alle d.

# %%
F1 = 9775
j = np.arange(N)
s_prof = np.where(j < 250, 0.002 * np.exp(-j / 40), 0.0)        # Aerosol
s_prof[[99, 100, 101]] += [0.006, 0.01, 0.006]                     # Wolke bei 1,5 km
s_prof[400] += 0.002                                               # dünne Schicht bei 6 km
X = np.array([np.roll(c, jj) for jj in range(N)]).T                # Spalte j = Muster um j verschoben
rng = np.random.default_rng(3)
hm = rng.poisson(F1 * (b + X @ s_prof))
Cm = np.fft.irfft(np.fft.rfft(hm) * U, N) - hm.mean()
s_hat_prof = 2 * Cm / (F1 * (N - 1 / N))
sd_m = np.sqrt(4 * (b + s_prof.sum() / 2) / (F1 * N))
resid = s_hat_prof - (s_prof - (s_prof.sum() - s_prof) / (N - 1))
print(f"Summe s_j = {s_prof.sum():.4f}; SD von s_hat_d: Theorie {sd_m:.5f}, beobachtet {resid.std():.5f}")
print(f"Wolke d=100: wahr {s_prof[100]:.4f}, geschätzt {s_hat_prof[100]:.4f}; Schicht d=400: wahr {s_prof[400]:.4f}, geschätzt {s_hat_prof[400]:.4f}")

z_km = j * 299792458 / (2 * 1e7) / 1000
fig, ax = plt.subplots(figsize=(11, 3.4))
ax.plot(z_km, s_hat_prof, color=BLUE, lw=0.7, label="geschätzt: $\\hat s(d) = C(d)\\,/\\,(511{,}5005\\,F)$, ein Lauf, 1 s", zorder=3)
ax.plot(z_km, s_prof, color=RED, lw=2.2, alpha=0.55, label="wahr: $s_j$", zorder=2)
ax.axhspan(-2 * sd_m, 2 * sd_m, color=GREY, alpha=0.15, lw=0, label="± 2 SD Rauschen")
ax.annotate("Aerosol", (0.25, 0.0021), (1.2, 0.0045), color="#222", fontsize=11, arrowprops=dict(arrowstyle="->", color="#222"))
ax.annotate("Wolke 1,5 km", (1.5, 0.0101), (2.6, 0.0095), color="#222", fontsize=11, arrowprops=dict(arrowstyle="->", color="#222"))
ax.annotate("dünne Schicht 6 km", (6.0, 0.0021), (6.8, 0.0045), color="#222", fontsize=11, arrowprops=dict(arrowstyle="->", color="#222"))
ax.set_xlabel("Höhe z (km)"); ax.set_ylabel("$s$ (Klicks je An-Chip)")
ax.set_xlim(0, 15.3); ax.legend(frameon=False, fontsize=10, loc="upper right")
scale = F1 * (N - 1 / N) / 2                                         # C(d) = scale * s_hat_d
ax2 = ax.secondary_yaxis("right", functions=(lambda v: v * scale / 1000, lambda v: v * 1000 / scale))
ax2.set_ylabel("$C(d)$ (Tausend Klicks)", color=BLUE); ax2.tick_params(axis="y", colors=BLUE)
show(fig, "dgp_profil.png")

# %% [markdown]
# ## Warum man jede Höhe einzeln lesen darf, und nur bei diesem Code (Folie 14, vor dem Profil auf Folie 15)
#
# Das Profil ist eine Regression mit vielen Spalten: E[h_k] = F·b + F·Σ_j s_j·c_{k−j}, Spalte j = Muster um j verschoben.
# Einzeln pro Spalte schätzen (ŝ_d = Differenz der Gruppenmittel bei Verschiebung d) ist nur dann dasselbe wie
# alle gemeinsam zu schätzen, wenn die Spalten unkorreliert sind.
# Vergleich dreier Codes mit je etwa der Hälfte An-Chips, dasselbe Profil wie unten, ohne Rauschen (Erwartungswerte):
# m-Folge, Zufallscode, Block (erst 512 an, dann 511 aus).

# %%
def col_corr(code):
    """Korrelation zwischen Spalte 0 und Spalte l (Muster um l verschoben), für alle l."""
    x = code - code.mean()
    return np.fft.irfft(np.abs(np.fft.rfft(x)) ** 2, N) / (x @ x)


def per_d_estimate(code, h):
    """Für jedes d einzeln: (Mittel An-Bins - Mittel Aus-Bins)/F, An-Bins = Muster um d verschoben."""
    k = code.sum()
    S = np.fft.irfft(np.fft.rfft(h) * np.conj(np.fft.rfft(code)), N)   # Klicks in den An-Bins, für jedes d
    return (S / k - (h.sum() - S) / (N - k)) / F1


def profile_truth():
    jj = np.arange(N)
    sp = np.where(jj < 250, 0.002 * np.exp(-jj / 40), 0.0)
    sp[[99, 100, 101]] += [0.006, 0.01, 0.006]
    sp[400] += 0.002
    return sp


F1 = 9775
s_true = profile_truth()
codes = {"m-Folge": c,
         "Zufallscode": np.random.default_rng(5).permutation(np.r_[np.ones(512, int), np.zeros(511, int)]),
         "Block: 512 an, 511 aus": np.r_[np.ones(512, int), np.zeros(511, int)]}
z_km = np.arange(N) * 299792458 / (2 * 1e7) / 1000
fig, axs = plt.subplots(3, 3, figsize=(14, 5.6), gridspec_kw={"width_ratios": [1, 1, 2.2], "hspace": 0.55, "wspace": 0.28})
for r, (name, code) in enumerate(codes.items()):
    Eh = F1 * (b + np.array([np.roll(code, jj) for jj in range(N)]).T @ s_true)   # Erwartungswert, kein Rauschen
    rho = col_corr(code)
    est = per_d_estimate(code, Eh)
    a = axs[r, 0]
    a.bar(np.arange(60), code[:60], width=1.0, color=BLUE)
    a.set_yticks([]); a.set_xticks([0, 30, 60] if r == 2 else [])
    a.set_title(f"{name}: Chips 0 bis 59", fontsize=11, loc="left")
    a = axs[r, 1]
    a.plot(np.arange(1, N), rho[1:], color=BLUE, lw=0.8)
    a.axhline(0, color=GREY, lw=0.6)
    a.set_ylim(-1.05, 1.05); a.set_yticks([-1, 0, 1]); a.set_xticks([0, 500, 1000] if r == 2 else [])
    a.set_title("Korrelation Spalte 0 mit Spalte l", fontsize=11, loc="left")
    print(f"{name}: max |Korrelation| zweier Spalten {np.abs(rho[1:]).max():.4f}; "
          f"Schätzung bei d=100 {est[100]:.4f}, bei d=400 {est[400]:.4f}, bei d=700 {est[700]:.4f}")
    a = axs[r, 2]
    a.plot(z_km, s_true, color=RED, lw=2.2, alpha=0.55, zorder=2, label="wahr $s_j$")
    a.plot(z_km, est, color=BLUE, lw=1.0, zorder=3, label="jede Höhe einzeln geschätzt (ohne Rauschen)")
    a.axhline(0, color=GREY, lw=0.6)
    a.set_xlim(0, 15.3); a.set_xticks([0, 3, 6, 9, 12, 15] if r == 2 else [])
    if r < 2:
        a.set_ylim(-0.004, 0.012); a.set_title("Profil, für jedes d einzeln geschätzt", fontsize=11, loc="left")
    else:
        a.set_title("Profil, für jedes d einzeln geschätzt (Skala 10-mal größer)", fontsize=11, loc="left", color=RED)
    if r == 0: a.legend(frameon=False, fontsize=9.5, loc="upper right")
axs[2, 0].set_xlabel("Chip"); axs[2, 1].set_xlabel("Verschiebung l"); axs[2, 2].set_xlabel("Höhe z (km)")
show(fig, "codes_vergleich.png")

# %% [markdown]
# ## S(d) für F = 30 und F = 100 (ceilometer.md, Folie zu ŝ und b̂)
#
# S(d) = Klicks in den An-Bins bei Verschiebung d. Je ein Lauf; bei F = 30 der erste Seed, bei dem
# d̂ danebenliegt, bei F = 100 der erste Seed, bei dem d̂ trifft.

# %%
C0 = np.conj(np.fft.rfft(c))


def h_run(Fx, seed):
    r = np.random.default_rng(seed)
    return np.where(np.roll(c, d) == 1, r.poisson(Fx * n * q, size=N), 0) + r.poisson(Fx * b, size=N)


def S_of(hh):
    return np.fft.irfft(np.fft.rfft(hh) * C0, N)


fig, axs = plt.subplots(2, 1, figsize=(7, 4.6), gridspec_kw={"hspace": 0.6})
for a, Fx, want_hit in [(axs[0], 30, False), (axs[1], 100, True)]:
    seed = next(sd for sd in range(1000) if (int(np.argmax(S_of(h_run(Fx, sd)))) == d) == want_hit)
    S_d = S_of(h_run(Fx, seed)); dh = int(np.argmax(S_d))
    a.plot(np.arange(N), S_d, color=BLUE, lw=0.6)
    a.axhline(S_d.mean(), color=GREY, lw=1, ls="--")             # = 512·H/1023
    a.text(N + 8, S_d.mean(), "Mittel", va="center", fontsize=9, color=GREY)
    a.axvline(d, color=RED, ls=":", lw=1.2)
    a.plot([dh], [S_d[dh]], "o", color=BLUE, ms=5)
    a.annotate(f"d̂ = {dh}", (dh, S_d[dh]), (dh + (60 if dh < 700 else -200), S_d[dh]), color=BLUE, fontsize=10, va="center")
    a.set_xlim(-5, N + 5); a.set_ylabel("S(d)")
    lab = "daneben" if dh != d else "trifft"
    a.set_title(f"F = {Fx}, Seed {seed}: d̂ {lab} (rot: d₀ = {d})", fontsize=11, loc="left")
    print(f"F = {Fx}: Seed {seed}, d_hat {dh}, S(d0) {S_d[d]:.0f}, max {S_d.max():.0f}, Mittel {S_d.mean():.0f}, 512Fb {512 * Fx * b:.0f}")
axs[1].set_xlabel("Verschiebung d")
show(fig, "dgp_S_von_d.png")


# %% [markdown]
# ## S(d) ausrechnen: direkt und als Faltung
#
# Zyklisch, wie das Messprinzip: np.roll(c, d)[k] = c[(k − d) % 1023].
# Als Faltung: S = h ⊛ c̃ mit dem gespiegelten Code c̃_k = c_{−k}; über die FFT ist das h^ · conj(c^).
# Mit F = 30 und F = 100, Seed 0 kommen dieselben Läufe heraus wie im Bild oben (numpy 2.5).

# %%
for Fx in (30, 100):
    hx = h_run(Fx, 0)
    S_direkt = np.array([hx @ np.roll(c, dd) for dd in range(N)])          # 1023 Skalarprodukte
    S_fft = np.fft.irfft(np.fft.rfft(hx) * np.conj(np.fft.rfft(c)), N)     # Kreuzkorrelation über FFT
    c_rev = np.roll(c[::-1], 1)                                            # c_rev[k] = c[-k]
    S_falt = np.fft.irfft(np.fft.rfft(hx) * np.fft.rfft(c_rev), N)         # Faltung mit gespiegeltem Code
    print(f"F = {Fx}: gleich (FFT, Faltung) {np.allclose(S_direkt, S_fft)}, {np.allclose(S_direkt, S_falt)}; "
          f"d_hat {S_direkt.argmax()}, S(d0) {S_direkt[d]}")


# %% [markdown]
# ## Überlapp bei N = 1023: m-Folge gegen Zufallscode (Folie „Was wir von der m-Folge brauchen“)
#
# Überlapp(τ) = Σ_k c_k c_{k−τ}, zyklisch. m-Folge: 512 bei τ = 0, sonst immer 256.
# Zufallscode: zufällige Anordnung von ebenfalls 512 Einsen (Seed 0).

# %%
r_code = np.random.default_rng(0).permutation(np.r_[np.ones(512, int), np.zeros(511, int)])
ov_m = np.round(np.fft.irfft(np.abs(np.fft.rfft(c)) ** 2, N)).astype(int)
ov_r = np.round(np.fft.irfft(np.abs(np.fft.rfft(r_code)) ** 2, N)).astype(int)
print(f"Überlapp N = 1023, τ ≠ 0: m-Folge {set(ov_m[1:])}, Zufallscode {ov_r[1:].min()} bis {ov_r[1:].max()}")
fig, ax = plt.subplots(figsize=(7.2, 2.0))
tt = np.arange(1, N)
ax.plot(tt, ov_r[1:], color=GREY, lw=0.7, label=f"Zufallscode, auch 512 Einsen: {ov_r[1:].min()} bis {ov_r[1:].max()}")
ax.plot(tt, ov_m[1:], color="#d9822b", lw=2.2, label="m-Folge: immer 256")
ax.set_xlim(0, N); ax.set_ylim(220, 300)
ax.set_xlabel("Verschiebung τ (τ = 0: 512, nicht gezeigt)", fontsize=11); ax.set_ylabel("Überlapp", fontsize=11)
ax.tick_params(labelsize=10)
ax.legend(frameon=False, fontsize=10, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.22))
show(fig, "ueberlapp_1023.png")
