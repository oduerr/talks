# Images in public/ceilometer/

| file | source | what | rights |
|---|---|---|---|
| rate_klicks.png | `plots.py` in this talk folder (`uv run plots.py`), written by Claude (agent) 2026-11-04 | Rate λ_k and one simulated period (Poisson, Seed 7) | own |
| autokorrelation.png | `plots.py`, same | autocorrelation of the 1023-chip m-sequence (`sequence()` from the Fogcast repo) | own |
| snr_panels.png | `plots.py`, same | correlation profiles for F = 1, 100, 9775 (`process()` from the Fogcast repo) | own |
| snr_hintergrund.png | `plots.py`, same | SNR against background b (theory) | own |
| erste_chips.png | `plots.py`, same | first 64 chips of the m-sequence | own |
| raumzeit.png | `plots.py`, same | space-time diagram photons to the cloud and back, detector bins (schematic, d = 6) | own |
- dgp_ein_lauf.png, dgp_viele_laeufe.png: eigene Simulation, dgp_sim.py (2026-11-08)
- dgp_h_schaetzer.png: eigene Simulation, dgp_sim.py (2026-11-08)
- dgp_profil.png: eigene Simulation, dgp_sim.py (2026-11-08; Legende 2026-11-12)
- dgp_h.png: eigene Simulation, dgp_sim.py (November 2026, nach den Notizen vom 10.11.), Histogramm h eines Laufs, Seed 12, F = 100
- dgp_dhat.png: eigene Simulation, dgp_sim.py (November 2026, nach den Notizen vom 10.11.), Verteilung von d̂, 2000 Läufe, F = 100, Seed 7
- dgp_S_von_d.png: eigene Simulation, dgp_sim.py (November 2026, nach den Notizen vom 10.11.), S(d) für F = 30 und F = 100, Seed 0
- codes_vergleich.png: eigene Simulation, dgp_sim.py (2026-11-08)
- ueberlapp_1023.png: eigene Rechnung, dgp_sim.py (2026-11-12), Überlapp m-Folge gegen Zufallscode bei N = 1023, Seed 0
- 2026-11-12: dgp_ein_lauf.png, dgp_h_schaetzer.png, dgp_viele_laeufe.png, dgp_h.png, dgp_dhat.png, dgp_S_von_d.png neu gezogen, Signal jetzt Poisson(n·q) statt Binomial(n, q); gleiche Seeds, andere Zufallszahlen. Die Zahlen im Text des alten Decks (ceilometer_alt.md) sind nicht angepasst.
