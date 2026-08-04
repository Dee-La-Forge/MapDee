# JALON 1 — VERDICT : CAS D — ARRÊT ET AUTOPSIE
run `2026-08-03T060328Z` · config `3a71ae94b47a` · grille ADR-011 appliquée dans l'ordre D -> A -> B -> C, cellules LODO PURGÉES font foi

- **Symboles CERTIFIANTS** (jeu de jours complet) : BTCUSDT, ETHUSDT
- **Barre 1** (témoin IC > 0,5, seuil >= 80% des folds) : BTCUSDT 0/7 (seuil 6) · ETHUSDT 0/7 (seuil 6)
- **Barre 2** (dAUC IC excluant 0 positivement, seuil >= 60% des folds) : BTCUSDT 0/7 (seuil 5) · ETHUSDT 0/7 (seuil 5)
- **Cellules fautives (point < 0,5, cas D)** — aucune suite avant l'autopsie :
  - BTCUSDT fold 20251202, témoin : AUC point 0.487
  - BTCUSDT fold 20251203, témoin : AUC point 0.486
  - BTCUSDT fold 20251204, ranker : AUC point 0.484
  - BTCUSDT fold 20251205, témoin : AUC point 0.464
  - BTCUSDT fold 20251206, ranker : AUC point 0.407
  - ETHUSDT fold 20251201, ranker : AUC point 0.494
  - ETHUSDT fold 20251202, ranker : AUC point 0.499
  - ETHUSDT fold 20251203, témoin : AUC point 0.498
  - ETHUSDT fold 20251203, ranker : AUC point 0.463
  - ETHUSDT fold 20251204, ranker : AUC point 0.471
  - ETHUSDT fold 20251205, témoin : AUC point 0.486
  - ETHUSDT fold 20251205, ranker : AUC point 0.486
  - ETHUSDT fold 20251206, témoin : AUC point 0.474
  - ETHUSDT fold 20251206, ranker : AUC point 0.460

## Configuration du run (hashée)
```json
{
  "bar1_frac": 0.8,
  "bar2_frac": 0.6,
  "calib_frac": 0.25,
  "code_sha": "cfd56b3755ec",
  "days": [
    "20251201",
    "20251202",
    "20251203",
    "20251204",
    "20251205",
    "20251206",
    "20251207"
  ],
  "decidable": 0.1,
  "feature_cols": [
    "f_mult",
    "f_logmag",
    "f_dist",
    "f_side",
    "f_occ",
    "f_conv",
    "f_peak_ratio",
    "f_persist",
    "f_age",
    "f_turnover",
    "f_absorb_hist",
    "f_withdraw_hist",
    "f_wd_ratio_hist",
    "f_spec_flatness",
    "f_spec_tonality",
    "f_spec_centroid",
    "f_spec_flux",
    "f_coh_neighbours",
    "f_gap_rows"
  ],
  "force_partial": true,
  "go_coverage": 0.7,
  "hurdle_stage1": {
    "l2_regularization": 1.0,
    "learning_rate": 0.06,
    "max_iter": 250,
    "max_leaf_nodes": 15,
    "random_state": 12345
  },
  "l4_only_excluded": [
    "placed",
    "n_orders",
    "n_wallets",
    "age_med_ms",
    "dist"
  ],
  "max_pairs_per_cluster": 200,
  "min_boot_valid": 20,
  "n_boot": 400,
  "quantile_levels": [
    0.05,
    0.15,
    0.25,
    0.35,
    0.45,
    0.55,
    0.65,
    0.75,
    0.85,
    0.95
  ],
  "ranker_params": {
    "learning_rate": 0.05,
    "min_child_samples": 20,
    "n_estimators": 300,
    "num_leaves": 31,
    "objective": "lambdarank",
    "random_state": 12345
  },
  "seed": 12345,
  "symbols": [
    "BTCUSDT",
    "ETHUSDT"
  ],
  "tag": "AUTOPSIE-nulle-permutee",
  "window_ms": 300000,
  "witness_params": {
    "C": 1.0,
    "max_iter": 1000,
    "solver": "lbfgs"
  }
}
```
`confighash = 3a71ae94b47a` — sha256(config + code_sha), code_sha = sha256 de gondetect/{p3_dataset.py, p3_models.py, p3_metrics.py, p3_target.py, cluststats.py, hl_features.py, ../experiments/p3_train.py}.

## Couverture (recette S3)
- verdict de couverture : **GO S3** (global 97.1%, seuil 70%)

| sym | jour | labels | couverts | couverture |
|---|---|---|---|---|
| BTCUSDT | 20251201 | 27,485 | 27,079 | 98.5% |
| BTCUSDT | 20251202 | 22,919 | 22,510 | 98.2% |
| BTCUSDT | 20251203 | 25,992 | 25,070 | 96.5% |
| BTCUSDT | 20251204 | 19,004 | 18,615 | 98.0% |
| BTCUSDT | 20251205 | 20,335 | 20,237 | 99.5% |
| BTCUSDT | 20251206 | 4,712 | 4,610 | 97.8% |
| BTCUSDT | 20251207 | 16,308 | 16,236 | 99.6% |
| ETHUSDT | 20251201 | 32,572 | 31,819 | 97.7% |
| ETHUSDT | 20251202 | 26,103 | 24,817 | 95.1% |
| ETHUSDT | 20251203 | 33,969 | 33,067 | 97.3% |
| ETHUSDT | 20251204 | 29,323 | 28,774 | 98.1% |
| ETHUSDT | 20251205 | 32,927 | 32,514 | 98.7% |
| ETHUSDT | 20251206 | 8,523 | 8,376 | 98.3% |
| ETHUSDT | 20251207 | 26,215 | 23,202 | 88.5% |

## Cellules — LODO PURGÉ par wallet (FAIT FOI)
| sym | fold | AUC témoin [IC95] | AUC ranker [IC95] | dAUC r-t [IC95] | CRPS skill [IC95] | G_test | n_purged | paires | B1 ? | B2 ? |
|---|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT | 20251201 | 0.503 [0.452;0.551] (nbv 400) | 0.532 [0.481;0.578] (nbv 400) | +0.029 [-0.047;+0.114] (nbv 400) | N/A (1er jour) | G=26 | 0 | 136590 | — | — |
| BTCUSDT | 20251202 | 0.487 [0.429;0.543] (nbv 400) | 0.502 [0.460;0.538] (nbv 400) | +0.015 [-0.066;+0.093] (nbv 400) | -0.002 [-1.389;-0.002] (nbv 400) | G=41 | 0 | 150431 | — | — |
| BTCUSDT | 20251203 | 0.486 [0.430;0.538] (nbv 400) | 0.540 [0.478;0.592] (nbv 400) | +0.053 [-0.021;+0.123] (nbv 400) | -0.007 [-1.088;-0.007] (nbv 400) | G=49 | 0 | 145075 | — | — |
| BTCUSDT | 20251204 | 0.516 [0.450;0.572] (nbv 400) | 0.484 [0.435;0.551] (nbv 400) | -0.032 [-0.120;+0.078] (nbv 400) | -0.007 [-1.270;-0.007] (nbv 400) | G=36 | 0 | 63364 | — | — |
| BTCUSDT | 20251205 | 0.464 [0.404;0.518] (nbv 400) | 0.507 [0.423;0.565] (nbv 400) | +0.043 [-0.050;+0.129] (nbv 400) | -0.004 [-0.179;+0.007] (nbv 400) | G=31 | 0 | 108617 | — | — |
| BTCUSDT | 20251206 | 0.509 [0.385;0.647] (nbv 400) | 0.407 [0.301;0.538] (nbv 400) | -0.102 [-0.279;+0.090] (nbv 400) | -0.008 [-1.390;-0.008] (nbv 400) | G=30 | 0 | 4419 | — | — |
| BTCUSDT | 20251207 | 0.516 [0.463;0.562] (nbv 400) | 0.515 [0.459;0.584] (nbv 400) | -0.001 [-0.081;+0.077] (nbv 400) | -0.003 [-1.168;-0.003] (nbv 400) | G=42 | 0 | 112877 | — | — |
| ETHUSDT | 20251201 | 0.501 [0.456;0.561] (nbv 400) | 0.494 [0.434;0.546] (nbv 400) | -0.007 [-0.106;+0.066] (nbv 400) | N/A (1er jour) | G=12 | 0 | 122541 | — | — |
| ETHUSDT | 20251202 | 0.519 [0.468;0.576] (nbv 400) | 0.499 [0.451;0.554] (nbv 400) | -0.020 [-0.095;+0.057] (nbv 400) | -0.009 [-0.337;+0.013] (nbv 400) | G=13 | 0 | 114512 | — | — |
| ETHUSDT | 20251203 | 0.498 [0.440;0.544] (nbv 400) | 0.463 [0.415;0.508] (nbv 400) | -0.035 [-0.102;+0.041] (nbv 400) | -0.012 [-3.355;-0.012] (nbv 400) | G=20 | 0 | 186175 | — | — |
| ETHUSDT | 20251204 | 0.507 [0.457;0.554] (nbv 400) | 0.471 [0.428;0.514] (nbv 400) | -0.036 [-0.097;+0.033] (nbv 400) | -0.001 [-2.930;-0.001] (nbv 400) | G=20 | 0 | 184171 | — | — |
| ETHUSDT | 20251205 | 0.486 [0.428;0.532] (nbv 400) | 0.486 [0.438;0.533] (nbv 400) | +0.000 [-0.063;+0.072] (nbv 400) | -0.005 [-1.782;-0.005] (nbv 400) | G=17 | 0 | 207862 | — | — |
| ETHUSDT | 20251206 | 0.474 [0.385;0.565] (nbv 400) | 0.460 [0.364;0.570] (nbv 400) | -0.014 [-0.165;+0.128] (nbv 400) | +0.002 [-1.920;+0.002] (nbv 400) | G=19 | 0 | 22369 | — | — |
| ETHUSDT | 20251207 | 0.511 [0.453;0.556] (nbv 400) | 0.503 [0.456;0.547] (nbv 400) | -0.008 [-0.064;+0.067] (nbv 400) | +0.000 [-1.474;+0.000] (nbv 400) | G=23 | 0 | 217599 | — | — |

## Cellules — test COMPLET (non purgé, pour la prime d'identité)
| sym | fold | AUC témoin [IC95] | AUC ranker [IC95] | dAUC r-t [IC95] | CRPS skill [IC95] | G_test | n_purged | paires |
|---|---|---|---|---|---|---|---|---|
| BTCUSDT | 20251201 | 0.481 [0.438;0.534] (nbv 400) | 0.506 [0.448;0.553] (nbv 400) | +0.025 [-0.069;+0.104] (nbv 400) | N/A (1er jour) | G=26 | 0 | 136590 |
| BTCUSDT | 20251202 | 0.514 [0.473;0.553] (nbv 400) | 0.499 [0.458;0.538] (nbv 400) | -0.015 [-0.080;+0.053] (nbv 400) | -0.002 [-1.340;-0.002] (nbv 400) | G=41 | 0 | 150431 |
| BTCUSDT | 20251203 | 0.487 [0.430;0.544] (nbv 400) | 0.522 [0.467;0.571] (nbv 400) | +0.035 [-0.059;+0.115] (nbv 400) | -0.006 [-1.211;-0.006] (nbv 400) | G=49 | 0 | 145075 |
| BTCUSDT | 20251204 | 0.540 [0.476;0.592] (nbv 400) | 0.540 [0.470;0.608] (nbv 400) | -0.000 [-0.085;+0.096] (nbv 400) | -0.006 [-1.454;-0.006] (nbv 400) | G=36 | 0 | 63364 |
| BTCUSDT | 20251205 | 0.470 [0.410;0.525] (nbv 400) | 0.502 [0.446;0.557] (nbv 400) | +0.032 [-0.047;+0.119] (nbv 400) | -0.005 [-0.132;+0.010] (nbv 400) | G=31 | 0 | 108617 |
| BTCUSDT | 20251206 | 0.576 [0.441;0.701] (nbv 400) | 0.519 [0.356;0.625] (nbv 400) | -0.057 [-0.292;+0.098] (nbv 400) | -0.008 [-1.424;-0.008] (nbv 400) | G=30 | 0 | 4419 |
| BTCUSDT | 20251207 | 0.520 [0.466;0.577] (nbv 400) | 0.476 [0.416;0.536] (nbv 400) | -0.044 [-0.144;+0.057] (nbv 400) | -0.003 [-1.059;-0.003] (nbv 400) | G=42 | 0 | 112877 |
| ETHUSDT | 20251201 | 0.525 [0.469;0.581] (nbv 400) | 0.501 [0.444;0.550] (nbv 400) | -0.023 [-0.123;+0.052] (nbv 400) | N/A (1er jour) | G=12 | 0 | 122541 |
| ETHUSDT | 20251202 | 0.490 [0.433;0.547] (nbv 400) | 0.510 [0.447;0.580] (nbv 400) | +0.020 [-0.050;+0.090] (nbv 400) | -0.010 [-0.601;+0.015] (nbv 400) | G=13 | 0 | 114512 |
| ETHUSDT | 20251203 | 0.521 [0.468;0.572] (nbv 400) | 0.471 [0.421;0.517] (nbv 400) | -0.050 [-0.125;+0.021] (nbv 400) | -0.013 [-3.185;-0.013] (nbv 400) | G=20 | 0 | 186175 |
| ETHUSDT | 20251204 | 0.486 [0.445;0.525] (nbv 400) | 0.488 [0.450;0.536] (nbv 400) | +0.003 [-0.051;+0.064] (nbv 400) | -0.002 [-2.597;-0.002] (nbv 400) | G=20 | 0 | 184171 |
| ETHUSDT | 20251205 | 0.508 [0.463;0.555] (nbv 400) | 0.486 [0.447;0.528] (nbv 400) | -0.022 [-0.080;+0.036] (nbv 400) | -0.006 [-1.927;-0.006] (nbv 400) | G=17 | 0 | 207862 |
| ETHUSDT | 20251206 | 0.546 [0.430;0.644] (nbv 400) | 0.488 [0.396;0.580] (nbv 400) | -0.059 [-0.195;+0.078] (nbv 400) | +0.002 [-1.721;+0.002] (nbv 400) | G=19 | 0 | 22369 |
| ETHUSDT | 20251207 | 0.505 [0.462;0.562] (nbv 400) | 0.505 [0.457;0.560] (nbv 400) | -0.001 [-0.056;+0.054] (nbv 400) | +0.000 [-1.451;+0.000] (nbv 400) | G=23 | 0 | 217599 |

## Prime d'identité par fold — AUC(full) - AUC(purgé)
IC par différence tirage à tirage de deux bootstraps sur des jeux de test DIFFÉRENTS (tirages indépendants : approximation honnête, motif prime_ci de label_transfer).

| sym | fold | prime témoin [IC95] | prime ranker [IC95] |
|---|---|---|---|
| BTCUSDT | 20251201 | -0.022 [-0.087;+0.057] (nbv 400) | -0.026 [-0.099;+0.040] (nbv 400) |
| BTCUSDT | 20251202 | +0.027 [-0.042;+0.094] (nbv 400) | -0.002 [-0.060;+0.057] (nbv 400) |
| BTCUSDT | 20251203 | +0.001 [-0.077;+0.078] (nbv 400) | -0.017 [-0.090;+0.051] (nbv 400) |
| BTCUSDT | 20251204 | +0.024 [-0.056;+0.107] (nbv 400) | +0.055 [-0.044;+0.130] (nbv 400) |
| BTCUSDT | 20251205 | +0.007 [-0.072;+0.088] (nbv 400) | -0.005 [-0.083;+0.087] (nbv 400) |
| BTCUSDT | 20251206 | +0.067 [-0.135;+0.250] (nbv 400) | +0.112 [-0.099;+0.264] (nbv 400) |
| BTCUSDT | 20251207 | +0.004 [-0.065;+0.084] (nbv 400) | -0.039 [-0.119;+0.050] (nbv 400) |
| ETHUSDT | 20251201 | +0.024 [-0.051;+0.091] (nbv 400) | +0.007 [-0.074;+0.085] (nbv 400) |
| ETHUSDT | 20251202 | -0.028 [-0.115;+0.046] (nbv 400) | +0.011 [-0.065;+0.093] (nbv 400) |
| ETHUSDT | 20251203 | +0.023 [-0.043;+0.101] (nbv 400) | +0.008 [-0.060;+0.077] (nbv 400) |
| ETHUSDT | 20251204 | -0.021 [-0.077;+0.042] (nbv 400) | +0.018 [-0.036;+0.084] (nbv 400) |
| ETHUSDT | 20251205 | +0.022 [-0.040;+0.103] (nbv 400) | -0.000 [-0.062;+0.062] (nbv 400) |
| ETHUSDT | 20251206 | +0.073 [-0.081;+0.211] (nbv 400) | +0.028 [-0.124;+0.163] (nbv 400) |
| ETHUSDT | 20251207 | -0.006 [-0.071;+0.078] (nbv 400) | +0.001 [-0.076;+0.074] (nbv 400) |

## LE DÉNOMINATEUR (ADR-011 — recalculé depuis le df de ce run)
| grandeur | valeur |
|---|---|
| paliers-instants (lignes du jeu) | 316,926 |
| **G_total (clusters)** | **351** (BTCUSDT 238 · ETHUSDT 113) |
| clusters s'étendant sur >= 2 jours | 17 (4.8%) — portant **99.9% des événements** |
| wallets dominants présents >= 2 jours | 683 / 1,777 |
| top-10 clusters | **99.9% des événements** |

G effectif par fold APRÈS purge — le vrai N de chaque cellule :

| sym | fold | G purgé | G full | n test purgé | n purgées |
|---|---|---|---|---|---|
| BTCUSDT | 20251201 | 26 | 26 | 27,079 | 0 |
| BTCUSDT | 20251202 | 41 | 41 | 22,510 | 0 |
| BTCUSDT | 20251203 | 49 | 49 | 25,070 | 0 |
| BTCUSDT | 20251204 | 36 | 36 | 18,615 | 0 |
| BTCUSDT | 20251205 | 31 | 31 | 20,237 | 0 |
| BTCUSDT | 20251206 | 30 | 30 | 4,610 | 0 |
| BTCUSDT | 20251207 | 42 | 42 | 16,236 | 0 |
| ETHUSDT | 20251201 | 12 | 12 | 31,819 | 0 |
| ETHUSDT | 20251202 | 13 | 13 | 24,817 | 0 |
| ETHUSDT | 20251203 | 20 | 20 | 33,067 | 0 |
| ETHUSDT | 20251204 | 20 | 20 | 28,774 | 0 |
| ETHUSDT | 20251205 | 17 | 17 | 32,514 | 0 |
| ETHUSDT | 20251206 | 19 | 19 | 8,376 | 0 |
| ETHUSDT | 20251207 | 23 | 23 | 23,202 | 0 |

## Notes des folds (cellules manquantes, N/A)
- BTCUSDT 20251201 : premier jour : aucun jour antérieur, climato None -> cellule CRPS N/A
- ETHUSDT 20251201 : premier jour : aucun jour antérieur, climato None -> cellule CRPS N/A

## Réserves
- BTCUSDT : 7 folds — seuils recalculés en proportion (barre 1 >= 6, barre 2 >= 5), ADR-013.
- ETHUSDT : 7 folds — seuils recalculés en proportion (barre 1 >= 6, barre 2 >= 5), ADR-013.

Prédictions archivées : `p3-preds-BTCUSDT-3a71ae94b47a.parquet`, `p3-preds-ETHUSDT-3a71ae94b47a.parquet`
