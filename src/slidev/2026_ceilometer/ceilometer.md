---
theme: default
title: "Ceilometer: Modell, ML-Schätzer und Kreuzkorrelation"
info: |
  Oliver Dürr, November 2026. Zweite Fassung, nach meinen Notizen vom 10.11.2026
  (Vault: 04_learning/physic/Ceilometer_ML_Kreuzkorrelation).
class: text-center
aspectRatio: 16/9
transition: fade
mdc: true
lineNumbers: false
# presenter addon (oduerr/presenter): keep the drawings; blank pages for b / w at the end
drawings:
  persist: true
---

# Ceilometer: Modell, ML-Schätzer und Kreuzkorrelation

**Die Signalverarbeitung des Fogcast-Ceilometers (statistical viewpoint)**

<div class="grid grid-cols-3 gap-6 mt-12 text-left text-[0.95rem]">
<div class="card">

**1 · Messprinzip**<br>Laser, Muster, Poisson-Zählungen.

</div>
<div class="card">

**2 · ML-Schätzer**<br>Likelihood, $\hat d$, $\hat s$, Stichprobenverteilung.

</div>
<div class="card">

**3 · Kreuzkorrelation**<br>$E[C(d)\mid d_0]$: Nadel auf flachem Sockel, Profil.

</div>
</div>

<p class="!mt-12 text-sm opacity-60">Oliver Dürr · November 2026 · Code: <a href="https://github.com/FogCast-Konstanz/ceilometer/tree/main/software/instrument/src/fogcast">Fogcast-Verzeichnis im Ceilometer-Repo</a> · <a href="https://github.com/oduerr/talks/blob/main/src/slidev/2026_ceilometer/dgp_sim.py">Didaktik-Code dgp_sim.py</a></p>

<!--
Zweite Fassung. Inhalt nur, was in den Notizen vom 10.11.2026 steht (Vault: 04_learning/physic/Ceilometer_ML_Kreuzkorrelation.md, Originale im PDF daneben). Erste Fassung: ceilometer_alt.md (Talk ceilometer-alt). Bis 12.11.2026 hieß dieses Deck ceilometer2.md.
-->

---

# Messprinzip

<div class="grid grid-cols-[5fr_6fr] gap-8 mt-2 text-left text-[0.86rem]">
<div>

Der Laser sendet dauernd ein festes Ein/Aus-Muster $c_k$, $k=0,\dots,1022$:

- $c_k=1$: Laser feuert, $c_k=0$: kein Signal.
- 1 Bin $\,\hat=\,$ 100 ns $\,\hat=\,$ 15 m Höhe. Das Licht läuft hin und zurück: $\Delta z=\tfrac12\,c\,\Delta t=\tfrac12\cdot 3\cdot10^8\,\tfrac{\text m}{\text s}\cdot 10^{-7}\,\text s=15\,\text m$.
- Das Licht, das in Chip $k-d_0$ losgeschickt wurde, kommt $d_0$ Bins später in Bin $k$ an.

Die Anzahl $X_k$ der Photonen, die in einer Periode im Bin $k$ ankommen, ist Poisson-verteilt (der Laser schickt ja auch Poisson). War der Laser an, dann
$$X_k\sim\mathrm{Pois}(b+s)$$

- $b$: Background-Photonen
- $s$: Signalstärke, $\sim$ Ausgangsleistung $\cdot$ Streuung

</div>
<div>

<LidarBeam />

<div class="text-[0.7rem] text-gray-500 -mt-1">Raum-Zeit-Bild: waagrecht die Zeit in Bins, senkrecht die Höhe. Gezeigt ist nur der Strahl aus Chip 0; das Muster ist schematisch.</div>

</div>
</div>

---

# Vom Bin einer Periode zum Histogramm $h_k$

<div class="grid grid-cols-2 gap-10 mt-4 text-left text-[0.95rem]">
<div>

Allerdings kommt $s$ nur dazu, wenn der Laser wirklich an war, d.h. $c_{k-d_0}=1$ ist:
$$\Rightarrow\quad X_k\sim\mathrm{Pois}\bigl(b+s\,c_{k-d_0}\bigr)$$

Wir summieren über $F\approx 10\,000$ Perioden (zusammen 1 s) und nehmen periodische Randbedingungen, die durch das Messprinzip gegeben sind:
$$c_{-1}=c_{1022}$$

</div>
<div>

Weil die Summe von Poisson wieder Poisson ist, gilt für die Anzahl der Photonen in einem Bin:
$$h_k\mid d_0\;\sim\;\mathrm{Pois}\bigl(F\,(b+s\,c_{k-d_0})\bigr)$$

<div class="mt-6"><ShiftSketch /></div>

</div>
</div>

<!--
Notizen S1 (10.11.2026). Periodisch: Das Muster läuft ohne Pause weiter, das Licht der letzten Chips einer Periode landet in den ersten Bins der nächsten; allgemein c_k = c_(k mod 1023). Genau: F = floor(10^7/1023) = 9775 Perioden in 1 s, eine Periode 102,3 µs.
-->

---

# Der datengenerierende Prozess als Schleife

<div class="grid grid-cols-[1fr_1fr] gap-6 mt-2 text-left text-[0.8rem]">
<div>

```python {lines:false}
n, q = 10**11, 1e-13    # Photonen je An-Chip, P(zurück und gezählt)
b, d0, F = 0.10, 100, 100   # s = n*q = 0.01
h = np.zeros(1023)
for p in range(F):                  # Perioden
    for k in range(1023):           # Chips
        if c[k] == 1:               # Laser an
            treffer = rng.poisson(n * q)  # Pois(n) Photonen, je mit q
            h[(k + d0) % 1023] += treffer  # d0 Bins später
        h[k] += rng.poisson(b)      # Hintergrund
```

</div>
<div>

<img src="/ceilometer/dgp_h.png" class="w-full" />

<div class="text-[0.75rem]">Ein Lauf mit F = 100 Perioden (10 ms), Seed 12. Die Wolke bei d₀ = 100 sieht man im Histogramm nicht.</div>

</div>
</div>

<div class="src">Zum Selbstrechnen: <a href="https://github.com/oduerr/talks/blob/main/src/slidev/2026_ceilometer/dgp_sim.py">dgp_sim.py</a>, Zellen „Der DGP als Schleife“ und „Nur das Histogramm h“.</div>

<!--
Notizen S2 (10.11.2026): „Hier DGP in einer Schleife“, Kasten nur für h, daneben das Histogramm h_k. Im Skript heißt d0 noch d. Poisson(n·q): Der Laser schickt Pois(n) Photonen, jedes wird mit q zurückgestreut und gezählt; nach dem Ausdünnungssatz exakt Poisson(n·q = s). Bis 12.11.2026 stand hier Binomial(n, q), das nimmt genau n Photonen an (numerisch gleich, physikalisch schief); F = 100 statt 9775, damit die Simulation schnell ist.
-->

---

# Maximum-Likelihood-Schätzer: der Ansatz

<div class="grid grid-cols-2 gap-10 mt-4 text-left text-[0.95rem]">
<div>

Wir haben eine Wolke bei $d_0$:
$$h_k\sim\mathrm{Pois}\bigl(\underbrace{F\,(b+s\,c_{k-d_0})}_{\text{Rate }\lambda_k(d_0)}\bigr)$$

PMF$^{(*)}$:
$$\prod_k\frac{\lambda_k^{h_k}\,e^{-\lambda_k}}{h_k!}$$

</div>
<div>

Negative Log-Likelihood:
$$\mathrm{NLL}=\sum_k\lambda_k-\sum_k h_k\ln\lambda_k+\underbrace{\cancel{\sum_k\ln h_k!}}_{\text{unabh. von }\lambda\text{, also von }b,\,d,\,s}$$

<div class="ok mt-8 text-[0.85rem]">

$^{(*)}$ **Wieso dürfen wir hier Unabhängigkeit annehmen?** In den $\lambda_k$ steht die Abhängigkeit drin; was zusätzlich zur gegebenen Rate zufällig dazukommt, ist unabhängig von Bin zu Bin.

</div>

</div>
</div>

<!--
Notizen S2 (10.11.2026). Zur Unabhängigkeit: bedingt auf die Raten; die Bins sind disjunkte Zeitfenster eines Poisson-Prozesses. Verletzt erst durch Totzeit, Afterpulsing oder eine Rate, die sich während der Messung ändert. Die feste Folge c spielt dafür keine Rolle.
-->

---

# Maximum Likelihood: mit einem Kandidaten $d$

<div class="grid grid-cols-2 gap-10 mt-1 text-left text-[0.82rem]">
<div>

Wir rechnen jetzt mit einem Kandidaten $d$:
$$\sum_k\lambda_k(d)=F\Bigl(\sum_{k}b+s\sum_{k}c_{k-d}\Bigr)=F\,b\,N+F\,s\,\tfrac{N+1}{2}$$

<div class="ok text-[0.8rem]">

**Was wir von der Folge brauchen:** $\sum_k c_{k-d}$ ist die Anzahl der An-Chips, für jedes $d$ gleich (zyklisches Verschieben ändert die Zahl der Einsen nicht). Bei der m-Folge: $\tfrac{N+1}{2}=512$.

</div>

$$\sum_k h_k\ln\lambda_k=\sum_k\Bigl\{h_k\ln F+h_k\ln b+h_k\ln\bigl(1+\tfrac sb\,c_{k-d}\bigr)\Bigr\}$$

$c_{k-d}=0$: $\ln 1=0$; $\;c_{k-d}=1$: $\ln(1+\tfrac sb)$ $\;\Rightarrow\;\ln(1+\tfrac sb\,c_{k-d})=c_{k-d}\ln(1+\tfrac sb)$

</div>
<div>

Mit $H=\sum_k h_k$ ($-H\ln F$ ist konstant):
$$\mathrm{NLL}=-H\ln b-\ln\bigl(1+\tfrac sb\bigr)\,S(d)+F\bigl(b\,N+s\,\tfrac{N+1}{2}\bigr)$$
$$S(d)=\sum_k h_k\,c_{k-d}\qquad\text{zyklisch: }c_{k-d}=c_{(k-d)\bmod 1023}$$

Wir minimieren die NLL. Nur in $S(d)$ steckt $d$, mit dem Vorfaktor $-\ln(1+\tfrac sb)<0$ für $s>0$. Kleinste NLL heißt also größtes $S(d)$:

<div class="text-[1.1rem] mt-4">

$$\boxed{\;\hat d=\arg\max_d S(d)\;}$$

</div>

$S(d)$: die Klicks in den An-Bins bei Verschiebung $d$.

</div>
</div>

<!--
Notizen S3 (10.11.2026). Im Notizbuch steht beim ersten Gleichheitszeichen „für Folgen, bei denen etwa die Hälfte 0 ist“; auf der Folie genauer: Die Summe hängt für jeden periodischen Code nicht von d ab, nur der Wert (N+1)/2 = 512 ist m-Folgen-spezifisch (N = 2^10 − 1 = 1023, der Nullzustand fehlt).
-->

---

# $S(d)$ ausrechnen: direkt und als Faltung

<div class="grid grid-cols-[1.15fr_1fr] gap-6 mt-1 text-left text-[0.8rem]">
<div>

```python {lines:false}
def h_run(F, seed):          # Folie 4, ohne Schleifen
    r = np.random.default_rng(seed)
    sig = np.where(np.roll(c, d0) == 1,
                   r.poisson(F * n * q, size=N), 0)
    return sig + r.poisson(F * b, size=N)

h = h_run(F=30, seed=0)

# 1) direkt: Code um d verschieben, An-Bins summieren
#    np.roll(c, d)[k] = c[(k - d) % 1023]: zyklisch
S = np.array([h @ np.roll(c, d) for d in range(N)])

# 2) als Faltung, über die FFT
S_fft = np.fft.irfft(np.fft.rfft(h)
                     * np.conj(np.fft.rfft(c)), N)

np.allclose(S, S_fft)   # True
S.argmax()              # 926 (daneben)
# mit h_run(F=100, seed=0): 100 (Treffer)
```

</div>
<div>

$S(d)=\sum_k h_k\,c_{(k-d)\bmod 1023}$ ist eine **zyklische Kreuzkorrelation**. Das Modulo ist kein Rechentrick: Das Messprinzip ist periodisch, wie `(k + d0) % 1023` auf Folie 4.

Mit dem gespiegelten Code $\tilde c_k=c_{-k}$ ist es eine **zyklische Faltung**:
$$S(d)=\sum_k h_k\,\tilde c_{d-k}=(h\circledast\tilde c)(d)$$

Faltungssatz, mit $\mathcal F$ für die DFT ($c$ reell, also $\mathcal F\tilde c=\overline{\mathcal F c}$):
$$\mathcal F S=\mathcal F h\cdot\overline{\mathcal F c}$$

Die DFT ist selbst zyklisch. Darum passt die FFT hier genau, ohne Zero-Padding.

Aufwand: direkt $N^2\approx10^6$, mit FFT $N\log N\approx10^4$.

</div>
</div>

<div class="src">Die zwei Läufe sind die Beispiele der nächsten Folie. <a href="https://github.com/oduerr/talks/blob/main/src/slidev/2026_ceilometer/dgp_sim.py">dgp_sim.py</a>, Zelle „S(d) ausrechnen: direkt und als Faltung“. Im Gerät rechnet <a href="https://github.com/FogCast-Konstanz/ceilometer/blob/main/software/instrument/src/fogcast/prn_processing.py">prn_processing.process</a> dieselbe FFT-Zeile, mit u statt c, also C(d).</div>

<!--
Geprüft mit dgp_sim.py (numpy 2.5.4): direkt, FFT mit conj und Faltung mit gespiegeltem Code (np.roll(c[::-1], 1)) geben dasselbe S(d). F = 30, Seed 0: d̂ = 926, S(d0) = 1710, max 1734. F = 100, Seed 0: d̂ = 100, S(d0) = 5554.
Die Poisson-Ziehungen sind in numpy 2.3 und 2.5 gleich (geprüft). Mit Binomial (bis 12.11.2026) waren sie es nicht.
h_run zieht dieselben Zufallszahlen in derselben Reihenfolge wie im Skript; Poisson(F·n·q) für alle F Perioden auf einmal statt F-mal Poisson(n·q): Summe unabhängiger Poisson-Variablen.
Im Skript heißt d0 noch d.
-->

---

# $S(d)$ und die Stichprobenverteilung von $\hat d$

<div class="grid grid-cols-2 gap-8 -mt-2">
<div>

<img src="/ceilometer/dgp_S_von_d.png" class="h-[255px] mx-auto" />

</div>
<div>

<img src="/ceilometer/dgp_dhat.png" class="h-[255px] mx-auto" />

</div>
</div>

<div class="ok mt-2 text-left text-[0.8rem]">

Wenn man falsch liegt, also nicht $d_0$ schätzt, kann jedes andere $d\neq d_0$ gleich wahrscheinlich auftreten. Im physikalischen Prozess ist das nicht ganz so, z.B. weil der Laser Flanken hat.

</div>

<div class="src">b = 0,10, s = 0,01, d₀ = 100. Links je ein Lauf (F = 30 daneben, F = 100 trifft), rechts 2000 Läufe mit F = 100 (Seed 7). <a href="https://github.com/oduerr/talks/blob/main/src/slidev/2026_ceilometer/dgp_sim.py">dgp_sim.py</a>, Zellen „S(d) für F = 30 und F = 100“ und „Viele Läufe“.</div>

<!--
Notizen S4 unten und S5 oben (10.11.2026).
Im Notizbuch ist die Achse von S(d) bei 512·F·b skizziert. Im Bild liegt der Sockel höher: E[S(d)] = F(512 b + 256 s) für d ≠ d0, und alle S(d) verschieben sich gemeinsam mit der Gesamtzahl H (Mittel über d = 512·H/1023). Der Peak bei d0 liegt nur 256·F·s darüber: bei F = 30 sind das 77 Klicks, bei Rauschen mit SD ≈ 40.
Gleichverteilung der Fehltreffer simuliert: F = 30, 40 000 Läufe, χ²-Test p = 0,90. Grund: Jedes falsche d überlappt mit d0 in genau 256 An-Bins.
Rechts: 1883 von 2000 Läufen treffen (94,2 %), SNR nach Theorie 4,9.
-->

---

# Schätzer für $s$ und $b$

<div class="grid grid-cols-2 gap-10 mt-2 text-left text-[0.85rem]">
<div>

Mit den Signal-Bins, die bei $d$ an sind:
$$\bar h_{\text{an}}(d)=\frac1{512}\sum_{k:\,c_{k-d}=1}h_k=\frac{S(d)}{512}$$
$$\bar h_{\text{aus}}(d)=\frac{H-S(d)}{511}$$
$$\Rightarrow\quad\hat s(d)=\frac{\bar h_{\text{an}}(d)-\bar h_{\text{aus}}(d)}{F},\qquad \hat b(d)=\frac{\bar h_{\text{aus}}(d)}{F}$$

Das gilt für alle $d$. Für die eine Wolke nimmt man $\hat s(\hat d)$ und $\hat b(\hat d)$: zuerst nach $\hat s,\hat b$ ableiten, dann $\hat d$ einsetzen.

</div>
<div>

Statt $S(d)$ nimmt man meist die Kreuzkorrelation mit dem $\pm1$-Code ${u_k=2c_k-1}$, $\sum_k u_k=1$:
$$C(d)=\sum_k (u_{k-d}-\bar u)(h_k-\bar h)=\sum_k u_{k-d}\,h_k-\bar h=2\bigl(S(d)-\bar S\bigr)$$
mit $\bar S=\frac1{1023}\sum_d S(d)$. Ab jetzt rechnen wir mit $C(d)$:
- gleiches $\arg\max$ wie $S(d)$
- schwankt um 0: $\sum_d C(d)=0$ für jeden Datensatz
- gleiche Streuung für alle $d$

</div>
</div>

<div class="ok mt-4">

$$\hat d=\arg\max_d C(d),\qquad \hat s(d)=\frac{C(d)}{511{,}5005\,F},\qquad \hat b(d)=\frac1F\Bigl(\bar h-\frac{C(d)}{1022}\Bigr)$$

</div>

<!--
Notizen S4 oben (10.11.2026). Herleitung: Bei festem d zerfällt die Likelihood in zwei Poisson-Gruppen (512 An-Bins mit Rate F(b+s), 511 Aus-Bins mit Rate Fb); ML gibt die Gruppenmittel, wegen Invarianz folgen ŝ und b̂.
Als Funktion von S(d): ŝ(d) = (1023 S(d) − 512 H)/(512·511·F) = 1023/(512·511·F) · (S(d) − S̄), mit S̄ = 512 H/1023 (jedes h_k liegt in 512 der 1023 Verschiebungen im An-Bereich).
C(d) ist N mal die empirische Kovarianz zwischen verschobenem Code und Histogramm (ū = 1/N). Exakt: ŝ(d) = 1023·C(d)/(1024·511·F) = 2C(d)/(F(N − 1/N)); 1024·511/1023 = 511,5005. 511,5 ist die Höhe von E[C(d0)] für F·s = 1. b̂ ist exakt, weil H − S̄ = 511·h̄.
Streuung: Var C(d) ≈ F(N b + 512 Σ s_j), unabhängig von d (Multiplex-Nachteil, später).
Winner's Curse: Bei Fehltreffern ist ŝ(d̂) nach oben verzerrt (Simulation, Zelle „Viele Läufe“: 0,0073 statt 0).
-->

---
clicks: 30
---

# Was wir von der m-Folge brauchen

<div class="grid grid-cols-[1fr_1.05fr] gap-6 mt-0 text-left text-[0.8rem]">
<div>

**Voraussetzung, aus dem Messprinzip:** Der Code wird ohne Pause wiederholt, das Histogramm faltet die Zeit modulo 1023. Verschieben heißt also drehen. Das gilt für jeden Code.

**Was die m-Folge beiträgt**, Länge $N=2^m-1$ (bei uns $m=10$):

1. Fast balanciert: $2^{m-1}$ Einsen, $2^{m-1}-1$ Nullen. Bei uns 512 und 511.
2. Gleicher Überlapp für **jedes** Paar $d\neq d'$:
$$\sum_k c_{k-d}\,c_{k-d'}=2^{m-2}\quad(\text{bei uns }256)$$
In $\pm1$-Form: $\sum_k u_k\,u_{k-\tau}=-1$ für jedes $\tau\neq0$. Das gilt nur zyklisch.

<div class="ok mt-2">

Aus 2. folgt: Nadel auf flachem Sockel, gleichverteilte Fehltreffer, Profil ohne Übersprechen zwischen den Höhen.

</div>

</div>
<div>

<div class="w-[90%] mx-auto -mt-1"><MSeqRing /></div>

<div class="text-[0.7rem] text-gray-500 -mt-1">N = 31. Innen um τ gedreht (je Klick eins), Mitte der Code, außen das Produkt, Σ seine Summe.</div>

**Bei uns, $m=10$:**
$$\sum_k c_k\,c_{k-\tau}=\begin{cases}512&\tau=0\\256&\tau\neq0\end{cases}\qquad\sum_k c_k\,u_{k-\tau}=\begin{cases}512&\tau=0\\0&\tau\neq0\end{cases}$$

</div>
</div>

<!--
Nicht im Aufschrieb vom 10.11.2026; ergänzt nach Besprechung 12.11.2026.
N = 31: 5-Bit-Schieberegister x^5 + x^2 + 1, 16 Einsen, Überlapp 8 für alle 30 Verschiebungen (nachgerechnet). Zufallscode fest gewählt (Permutation mit 16 Einsen, Seed 1): Überlapp 6 bis 10.
Bei N = 1023: m-Folge Überlapp genau 256 für alle 1022 Verschiebungen; ein Zufallscode mit 512 Einsen schwankt zwischen 233 und 282.
±1-Form: 4·256 − 2·512 − 2·512 + 1023 = −1.
Nur zyklisch: Schneidet man ab und verschiebt mit Nullen statt Umlauf, schwankt der Überlapp auch bei der m-Folge. Das Messprinzip liefert genau die zyklische Verschiebung; darum nimmt man m-Folgen bei Dauerstrich-Verfahren.
Rechts unten: Σ c_k u_{k−τ} = 2·Σ c_k c_{k−τ} − Σ c_k = 2·256 − 512 = 0 für τ ≠ 0, und 2·512 − 512 = 512 für τ = 0. Das ist die Nadel ohne Nebenkeulen in E[C(d) | d0] (Folie 12).
Gebraucht auf: Folie 8 (Fehltreffer gleichverteilt), Folie 12 (Nadel, Sockel), Folie 13 (Profil). Altes Deck: codes_vergleich.png (m-Folge / Zufall / Block).
-->

---

# Für Aficionados: wie man die m-Folge erzeugt

<div class="absolute top-2 right-6 text-[0.7rem] px-2 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-400">TODO: blicken</div>

<div class="grid grid-cols-[1.1fr_1fr] gap-6 mt-0 text-left text-[0.8rem]">
<div>

<LfsrSketch />

```python {lines:false}
state = seed                     # 10 Bit, nicht 0
c = []
for _ in range(1023):
    c.append(state & 1)          # Ausgabe: unterstes Bit
    fb = (state ^ (state >> 3)) & 1   # c_k XOR c_{k+3}
    state = (state >> 1) | (fb << 9)  # schieben, fb oben rein
```

Polynom ${x^{10}+x^3+1}$. Im Repo: [`fogcast.prn_processing.sequence`](https://github.com/FogCast-Konstanz/ceilometer/blob/main/software/instrument/src/fogcast/prn_processing.py), im <a href="https://github.com/FogCast-Konstanz/ceilometer/tree/main/software/instrument/src/fogcast">Fogcast-Verzeichnis</a>.

</div>
<div>

**Warum die Eigenschaften gelten:**

- **Periode 1023:** Das Polynom ist primitiv. Das Register durchläuft alle $2^{10}-1$ Zustände außer dem Nullzustand, jeden genau einmal.
- **512 Einsen, 511 Nullen:** Das unterste Bit ist in 512 der 1024 Zustände 1. Es ist 0 in 512 Zuständen minus dem fehlenden Nullzustand.
- **Überlapp 256:** $c$ und jede Verschiebung erfüllen $c_{k+10}=c_k\oplus c_{k+3}$, also auch ihre Summe $c\oplus c'$. Die ist wieder eine Verschiebung von $c$ und hat 512 Einsen. $c$ und $c'$ unterscheiden sich also an 512 Stellen:
$$\text{Überlapp}=\tfrac12\,(512+512-512)=256$$
- **Seed:** wählt nur den Startpunkt, also eine zyklische Verschiebung derselben Folge.

</div>
</div>

<!--
Nicht im Aufschrieb vom 10.11.2026; ergänzt nach Besprechung 12.11.2026.
Zelle j des Registers enthält c_{k+j}; die Rückkopplung bit0 XOR bit3 ist c_k ⊕ c_{k+3} = c_{k+10}.
Die Summe c ⊕ c' ist nicht null, weil c' eine echte Verschiebung ist (τ ≠ 0 mod 1023); jede Lösung der Rekursion, die nicht null ist, liegt auf dem einen Zyklus aller Zustände ≠ 0, ist also eine Verschiebung von c (shift-and-add). Numerisch geprüft.
Im Repo gibt es auch die Länge 4095 (12 Bit). Literatur: Golomb, Shift Register Sequences; MacWilliams & Sloane 1976.
-->

---

# Erwartungswert von $C(d)$ bei einer Wolke in $d_0$

<div class="grid grid-cols-2 gap-8 mt-0 text-left text-[0.8rem]">
<div>

Nur Linearität des Erwartungswerts, EW von Poisson ist die Rate:
$$E(h_k\mid d_0)=F\,(b+s\,c_{k-d_0}),\qquad E(\bar h\mid d_0)=Fb+Fs\,\tfrac{512}{1023}$$

$$
\begin{aligned}
E(C(d)\mid d_0)&=\sum_k u_{k-d}\,E(h_k\mid d_0)-E(\bar h\mid d_0)\\
&=Fb\underbrace{\sum_k u_{k-d}}_{1}+Fs\sum_k u_{k-d}\,c_{k-d_0}-Fb-Fs\,\tfrac{512}{1023}\\
&=Fs\Bigl\{\sum_k u_{k-d}\,c_{k-d_0}-\tfrac{512}{1023}\Bigr\}
\end{aligned}
$$

$b$ fällt heraus.

</div>
<div>

$d=d_0$: $\;\sum_k u_{k-d_0}c_{k-d_0}=512$ (alle An-Bins mit $+1$)

$d\neq d_0$: $\;\sum_k (2c_{k-d}-1)\,c_{k-d_0}=2\cdot256-512=0$

<div class="ok mt-2">

$$E(C(d)\mid d_0)=Fs\Bigl\{512\,\delta_{d,d_0}-\tfrac{512}{1023}\Bigr\}$$

</div>

<NeedleSketch class="mt-0" />

</div>
</div>

<div class="ok mt-1 text-left text-[0.8rem]">

**Nur ein einziges $d$ bekommt Signal: $d=d_0$.** Für jedes andere $d$ liegen von den 512 Signal-Bins genau 256 auf $+1$ und 256 auf $-1$ und heben sich exakt auf (m-Folge: Überlapp 256 für jedes Paar). Alle $d\neq d_0$ haben denselben Sockel. In Einheiten von $s$ (Folie 9): Nadel der Höhe $s$, Sockel $-s/1022$.

</div>

<!--
Notizen S5 unten bis S6 (10.11.2026).
Keine Unabhängigkeit nötig, nur Linearität; die braucht man erst für die Varianz.
Σ_k u_k = 512 − 511 = 1; Σ_k c_{k−d0} = 512 (Anzahl An-Bins).
Peak minus Sockel: Fs·512. Peak über 0: Fs(512 − 512/1023) = 511,5005·Fs. Sockel −Peak/1022, passend zu Σ_d C(d) = 0: 511,5005·Fs − 1022·Fs·512/1023 = 0.
Zahlen F = 100, s = 0,01 (Fs = 1): Peak 511,5, Sockel −0,50; Simulation über 2000 Läufe: 510,1 und −0,50.
In Einheiten von s (Folie 9, ŝ = C/(511,5005 F)): Nadel der Höhe s, Sockel −s/1022.
Für ein beliebiges Profil (nächste Folie) überlagern sich solche Nadeln, weil der Erwartungswert linear ist.
-->

---

# Beliebiges Profil: eine Nadel pro Höhe

<img src="/ceilometer/dgp_profil.png" class="h-[175px] mx-auto" />

<div class="grid grid-cols-2 gap-10 mt-0 text-left text-[0.78rem]">
<div>

Alle Höhen streuen gleichzeitig, die Raten addieren sich: ${\lambda_k=F\bigl(b+\sum_j s_j\,c_{k-j}\bigr)}$. Der Erwartungswert ist linear, also summiert man Nadel und Sockel jeder Höhe:
$$E(C(d))=\textstyle\sum_j F s_j\Bigl(512\,\delta_{d,j}-\tfrac{512}{1023}\Bigr)=F\Bigl(512\,s_d-\tfrac{512}{1023}\textstyle\sum_j s_j\Bigr)$$

</div>
<div>

Mit $\hat s(d)=C(d)/(511{,}5005\,F)$ von Folie 9:

<div class="ok mt-1">

$$E(\hat s(d))=s_d-\frac1{1022}\sum_{j\neq d}s_j$$

</div>

Jede Höhe wird unverzerrt geschätzt, bis auf einen winzigen Abzug durch alle anderen Höhen. Kein $\arg\max$ mehr: $\hat s(d)$ für jedes $d$ gelesen ist das Höhenprofil.

</div>
</div>

<div class="src">Simuliert mit <a href="https://github.com/oduerr/talks/blob/main/src/slidev/2026_ceilometer/dgp_sim.py">dgp_sim.py</a>: Aerosol am Boden, Wolke bei 1,5 km, Schicht bei 6 km; b = 0,10, F = 9775 (1 s), Seed 3.</div>

<!--
Notizen S6 unten (10.11.2026): „Das erweitert sich natürlich auf ein beliebiges Profil s(d)“, Skizze mit Aerosol, Wolke, dünner Schicht. Bild aus dem alten Deck (Folie 15). Legende seit 12.11.2026: ŝ(d) = C(d)/(511,5005 F), gleich 2C(d)/(F(N − 1/N)).
Herleitung: E(ŝ(d)) = 1023/(1024·511) · (512 s_d − 512/1023 Σ_j s_j) = (1023 s_d − Σ_j s_j)/1022 = s_d − Σ_{j≠d} s_j/1022. (Früher ungenau: s_d − Σ_j s_j/N.)
Es wird eine Überlagerung der Raten summiert, keine Mischverteilung über d.
Simulation: Σ s_j = 0,105, also Abzug ≈ 0,0001, unter dem Rauschen (SD von ŝ_d Theorie 0,00025, beobachtet 0,00026). Wolke wahr 0,0102 (mit Aerosol), geschätzt 0,0101; Schicht wahr 0,0020, geschätzt 0,0021.
Identifizierbarkeit: Für jedes k ist Σ_j c_{k−j} = 512. Ein gemeinsamer Sockel aller s_j ist darum nicht von b zu trennen; das Profil ist nur bis auf eine Konstante bestimmt.
Rauschen (nicht in den Notizen): Var C(d) ≈ F(N b + 512 Σ s_j), gleich für jedes d. Die Wolke rauscht auch bei 6 km mit (Multiplex-Nachteil).
Dass „einzeln je Höhe“ dasselbe ist wie die gemeinsame Schätzung aller s_j, liegt an der m-Folge (Überlapp 256 für jedes Paar).
-->

---
layout: section
---

# Signal-Rausch-Verhältnis

<!--
Abschnitt: Wie gut ist der Schätzer? Ab hier braucht man auch die Unabhängigkeit der h_k (Folie 5), für die Varianz.
-->

---

# Rauschen und Signal-Rausch-Verhältnis

<div class="grid grid-cols-2 gap-10 mt-2 text-left text-[0.85rem]">
<div>

Poisson: $\mathrm{Var}(h_k)=E(h_k)$. Die $h_k$ sind unabhängig (Folie 5), die Gewichte $u=\pm1$ quadrieren sich zu 1, also addieren sich die Varianzen:
$$\mathrm{Var}\,C(d)\approx\sum_k E(h_k)=F\,(N b+512\,s)\approx F N\Bigl(b+\frac s2\Bigr)$$
gleich für jedes $d$. Mit dem Peak $E(C(d_0)\mid d_0)=511{,}5005\,F s$ (Folie 12):
$$\mathrm{SNR}=\frac{E(C(d_0)\mid d_0)}{\sqrt{\mathrm{Var}\,C}}\approx\frac s2\sqrt{\frac{F\,N}{b+s/2}}\;\propto\sqrt F$$

Bei einem Profil steht $512\sum_j s_j$ statt $512\,s$: Die Wolke rauscht in allen Höhen mit.

</div>
<div>

| | Theorie | Simulation |
|---|---|---|
| SNR, $F=9775$ | 48,8 | 47,6 |
| Peak, Mittel aus 200 Läufen | 49 999 | 49 992 |
| Rauschen (SD) | 1025 | 1022 |

Wie bei jedem Mittelwert wächst das SNR mit der Wurzel der Messzeit. Der **Hintergrund $b$ steht im Nenner**: Er ist der Gegner, nicht das schwache Signal.

</div>
</div>

<div class="src">Simulation mit dem Repo-Code, 200 Läufe, Seed 7 (Video-Arbeitsordner work/ceilometer_v3/anim/make_data.py).</div>

<!--
Aus dem alten Deck (Folie „Rauschen und Signal-zu-Rausch-Verhältnis“), Schreibweise an dieses Deck angepasst (d0, Folienverweise).
Genauer: Var C(d) = Σ_k (u_{k−d} − ū)² Var(h_k) mit (u − ū)² = (1 ∓ 1/N)² ≈ 1.
Zahlen: Peak 511,5005 · 9775 · 0,01 = 49 999; SD √(9775 · (102,3 + 5,12)) = 1025; SNR 48,8.
In Einheiten von s (Folie 9): SD(ŝ) = SD(C)/(511,5005 F) ≈ 0,00021 bei F = 9775, 0,00203 bei F = 100.
Bei einem Profil: Var C(d) ≈ F(N b + 512 Σ_j s_j), gleich für jedes d (Multiplex-Nachteil: jede Höhe trägt zum Rauschen aller Höhen bei).
Die Simulation erzeugt nur das Histogramm (Poisson) und rechnet dann mit process() aus dem Repo. Zähler, DMA, Detektor sind nicht simuliert.
-->

---

# Der Peak wächst aus dem Rauschen

<img src="/ceilometer/snr_panels.png" class="w-[92%] mx-auto mt-2" />

<div class="grid grid-cols-3 gap-6 mt-2 text-left text-[0.85rem]">
<div>

**1 Periode** (0,1 ms): nur Rauschen, SNR 0,3.

</div>
<div>

**100 Perioden** (10 ms): ein Peak bei ${d_0=100}$ deutet sich an, SNR 4,5.

</div>
<div>

**9775 Perioden** (1 s): klarer Peak, SNR 47,6.

</div>
</div>

<p class="takeaway">Faktor 100 in der Zeit, Faktor 10 im SNR.</p>

<div class="src">Korrelationsprofile C(d), simuliert mit plots.py (Poisson, Seed 7); jede Grafik auf ihr eigenes Maximum skaliert.</div>

<!--
Aus dem alten Deck (Folie „Der Peak wächst aus dem Rauschen“). Das Bild stammt aus plots.py, nicht aus dgp_sim.py; es zieht schon immer Poisson und ist von der Umstellung am 12.11. nicht betroffen.
SNR 4,5 bei F = 100 passt zur Theorie 4,9 und zur Trefferquote 94 % (Notizen zu Folie 8).
-->
