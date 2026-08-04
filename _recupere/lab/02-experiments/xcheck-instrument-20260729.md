# Vérité-contre-vérité & BTC/ETH à instrument égal — 2026-05-08

_généré le 2026-07-29 · scripts : `experiments/xcheck_day1.py`, `experiments/btc_eth_meme_instrument.py`
· données : jour 2026-05-08 dans les DEUX datasets Kaggle (BTC-only book 537 ms ; 10-perps book ~15 s)_

## Verdict

1. **L'instrument n'est pas interchangeable.** Le book 15 s ne retient que
   **27,5 %** des ordres du canonique (11 224 vs 33 177) et **renverse le taux
   de fuite agrégé** (69,7 % → 32,5 %). Cause mesurée : contacts datés en
   retard (Δt_contact p50 = +35,6 s, p90 = +313 s) → les retraits sortent de la
   pré-fenêtre 30 s → la population retenue s'enrichit en ordres qui tiennent.
2. **La mécanique de vérité est saine** : sur les 9 114 ordres vus par les
   deux, accord y_flee = **94,3 %**. C'est la SÉLECTION que l'instrument
   déforme, pas le verdict.
3. **BTC ≈ ETH à instrument égal** — le résultat fort du jour :

   | même book 15 s, 2026-05-08 | n | P(y>0) | q90 | q99 | E[y·y>0] |
   |---|---|---|---|---|---|
   | BTC perps10 | 4 468 | **27,9 %** | 1,000 | 1,000 | **0,686** |
   | ETH perps10 | 3 189 | **29,6 %** | 1,000 | 1,000 | **0,689** |

   L'« instabilité de la queue ×2,9-5,0 » affichée par le rapport P2a.5 du
   29/07 (BTC dense 10,1 % vs ETH grossier 29,6 %) était **entièrement un
   artefact d'instrument**. À instrument égal, la géométrie de la cible est
   quasi identique d'un symbole à l'autre — réplication inter-symbole
   excellente, pas de normalisation par symbole justifiée à ce stade.

## Règles qui en découlent

- **Ne comparer qu'à instrument égal.** Le banc P2a.5 multi-jours tourne sur
  le SEUL perps10 (5 jours × BTC+ETH, book 15 s uniforme). Le jour canonique
  BTC-only (book 537 ms) sort du banc et devient la **référence d'étalonnage**
  de l'instrument.
- Le niveau ABSOLU de y dépend fortement de la densité du book
  (P(y>0) : 10,1 % dense → 27,9 % grossier, même jour même symbole). Toute
  comparaison avec une autre source (Binance L2, recorder P1) devra être
  ré-étalonnée.
- Option qualité si le 15 s s'avère trop grossier pour P3 :
  reconstruire le mid depuis `hl_orders` (`gondetect/hl_book_reconstruct.py`),
  qui redonne une cadence arbitraire — coût CPU à mesurer.

## Réserves

- Un seul jour de recoupement (le seul présent dans les deux datasets).
- Les 523 désaccords y_flee sur ordres communs n'ont pas de délai de retrait
  exploitable (cancel_lead absent côté holds) — cause précise non identifiée,
  5,7 % des communs, non bloquant.
