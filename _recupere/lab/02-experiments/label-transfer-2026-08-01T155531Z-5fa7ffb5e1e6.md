# Transfert de labels — le label faible dit-il ce qu'on croit ? · run `2026-08-01T155531Z` · config `5fa7ffb5e1e6`

Source **faible** : `reconstructed_medium` (medium) · source **forte** : `hl-strong-cache` (strong).

```json
{
  "weak": "gondetect.hl_medium:ReconstructedMediumLabels",
  "strong": "gondetect.hl_labels:CachedStrongLabels",
  "symbols": [
    "BTCUSDT",
    "ETHUSDT"
  ],
  "days": [
    "2026-05-04",
    "2026-05-08"
  ],
  "match_tol_ms": 5000,
  "match_tol_rel": 5e-05,
  "n_boot": 400,
  "train_frac": 0.7,
  "embargo_s": 3600.0,
  "seed": 12345,
  "synthetic": false,
  "code_sha": "30ee75e388bf"
}
```

Appariement : même symbole, |Δt| ≤ **5 s**, |Δprix|/prix ≤ **0.5 bp**, **injectif** (un événement fort ne sert qu'une fois — sinon un mur touché trois fois se verrait recopier la même vérité et l'accord serait fabriqué).

**Clés de `provenance` refusées comme covariables** (le harnais ne laisse pas n'importe quoi devenir une feature) :

- `age_at_contact_ms` — horodatage (fuite temporelle possible)
- `cancel_lead_ms` — horodatage (fuite temporelle possible)
- `oid` — identifiant de venue (ADR-009)
- `size_canceled` — grandeur d'issue (circularité avec le label)
- `size_filled` — grandeur d'issue (circularité avec le label)
- `size_filled_pre_contact` — grandeur d'issue (circularité avec le label)
- `t_place_ms` — horodatage (fuite temporelle possible)
- `t_term_ms` — horodatage (fuite temporelle possible)

**Journées illisibles** (capturées, non fatales) :

- BTCUSDT/2026-05-04 : FileNotFoundError — C:/Users/DyBoo/Desktop/LaForge/GON-TV/sandbox/detect/data/l4/cache/datasets/marvingozo/hyperliquid-btc-high-frequency-microstructure/versions/1/hl_book/hl_book_2026-05-04.parquet
- ETHUSDT/2026-05-04 : FileNotFoundError — C:/Users/DyBoo/Desktop/LaForge/GON-TV/sandbox/detect/data/l4/cache/datasets/marvingozo/hyperliquid-btc-high-frequency-microstructure/versions/1/hl_book/hl_book_2026-05-04.parquet

Toute statistique ci-dessous est **clusterisée** sur la partition commune (wallet ∪ épisode, composantes connexes). L'« effet de grappe » est le rapport ET clusterisée / ET naïve : c'est ce qu'on aurait sur-vendu en traitant chaque contact comme indépendant.

---

## BTCUSDT

_pas assez de couples appariés pour conclure._

---

## ETHUSDT

_pas assez de couples appariés pour conclure._

---

## Réplication entre symboles (le juge de paix)

_un seul symbole exploitable — aucune réplication possible, donc aucun verdict ne doit être considéré comme établi._

---

## Robustesse à l'appariement (2 s / 5 s / 10 s)

L'appariement (±Δt, ±Δprix) est une hypothèse : le verdict doit y survivre. On re-déroule ici l'appariement ET l'analyse aux trois tolérances (mêmes données, mêmes graines). Le critère n'est **pas** l'égalité des étiquettes de verdict — un verdict catégoriel peut basculer sur un écart minuscule autour d'un seuil — mais le CHEVAUCHEMENT des IC95 des grandeurs CONTINUES : κ, (α − β) et l'écart de transfert. « NON ROBUSTE » exige des IC **disjoints** entre deux tolérances sur au moins une grandeur. Les étiquettes restent affichées à titre indicatif ; elles ne décident plus.

### BTCUSDT

| tolérance | couples | κ · IC95 | α − β (pts) · IC95 | écart transfert · IC95 | verdict *(indicatif)* |
|---|---|---|---|---|---|
| 2 s | — | — | — | — | _non évaluable (< 200 couples)_ |
| 5 s *(nominale)* | — | — | — | — | _non évaluable (< 200 couples)_ |
| 10 s | — | — | — | — | _non évaluable (< 200 couples)_ |

### ETHUSDT

| tolérance | couples | κ · IC95 | α − β (pts) · IC95 | écart transfert · IC95 | verdict *(indicatif)* |
|---|---|---|---|---|---|
| 2 s | — | — | — | — | _non évaluable (< 200 couples)_ |
| 5 s *(nominale)* | — | — | — | — | _non évaluable (< 200 couples)_ |
| 10 s | — | — | — | — | _non évaluable (< 200 couples)_ |

> **Verdict robuste à l'appariement (2 s / 5 s / 10 s)** — les IC des grandeurs continues se chevauchent entre les trois tolérances.

## Réserves explicites

1. **L'appariement est une hypothèse, pas une donnée.** Deux sources n'observent jamais le même instant. Tout désaccord mesuré ici mélange *désaccord de mesure* et *désaccord d'appariement* ; la seule protection est que la tolérance temporelle (5 s) reste très inférieure à la fenêtre d'issue du label. Depuis le 30/07, ce n'est plus une promesse : le balayage 2 s / 5 s / 10 s est EXÉCUTÉ à chaque run (section « Robustesse à l'appariement »), sur les grandeurs continues et leurs IC.
2. **Les non-appariés ne sont pas aléatoires.** Un événement faible sans homologue fort est probablement un événement d'un type particulier (palier hors de la profondeur publiée, épisode tronqué…). L'analyse ne porte donc que sur l'intersection, qui peut être plus « facile » que la population entière.
3. **Un palier n'est pas un ordre.** Le label faible agrège des ordres de plusieurs acteurs sur un même palier ; le fort suit un ordre. Une part irréductible du désaccord est *définitionnelle* et ne se corrigera par aucun raffinement du proxy.
4. **Les covariables viennent de `provenance`**, donc de ce que les sources ont bien voulu exposer. Une covariable manquante peut cacher un différentiel : « pas de biais détecté » signifie *pas sur les axes regardés*, jamais *pas de biais*.
5. **Le contrôle (d) est un témoin NON DÉCISIF, et c'est mesuré.** Son hypothèse nulle est *l'erreur iid conditionnellement à X* : il ne voit un biais que s'il déforme la PRÉDICTIBILITÉ. Contrôle positif du 29/07 : sur une fixture au biais différentiel planté (retrouvé par (b)), il a rendu p = 0,43. Il est depuis EXCLU du verdict ; il reste calculé parce que seul un POSITIF de sa part serait informatif. Le témoin principal reste (b).
6. **Aucune conclusion économique.** Ce rapport porte sur la signification du label, pas sur sa valeur. Le backtest reste négatif en directionnel (cf. `backtest_eco.py`).

_run en 6407 s · code `30ee75e388bf`_
