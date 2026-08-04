> ⚠ **ERRATA** — ce rapport contient des affirmations FAUSSES, etablies par
> l audit du 02/08. Ne pas le lire seul : voir `lab/ERRATA-2026-08-02.md`.

# Diagnostic de PUISSANCE — « où est passé le N ? » · 2026-08-02

_Script : `experiments/diag_power.py`, rejouable. Calculé sur les prédictions
archivées du jalon (`p3-preds-*-512be8b879ef.parquet`). Ne renégocie aucun
seuil : le verdict C du jalon est rendu et reste rendu._

## Question

Le jalon demande « le rang est-il certifiable FOLD PAR FOLD ? » → non.
Ce diagnostic demande « le signal EXISTE-t-il, à N complet ? ».

## 1. Le vrai N par fold — la purge garde 4 à 8 %

| BTC fold | lignes du jour | après purge | % gardé | G clusters | largeur IC |
|---|---|---|---|---|---|
| 05-04 | 9 065 | 752 | 8,3 % | 253 | 0,260 |
| 05-05 | 6 301 | 308 | 4,9 % | 154 | 0,421 |
| 05-06 | 6 627 | 350 | 5,3 % | 166 | 0,360 |
| 05-07 | 5 479 | 273 | 5,0 % | 159 | 0,199 |
| 05-08 | 4 442 | 242 | 5,4 % | 128 | 0,535 |
| 05-09 | 1 618 | 98 | 6,1 % | 37 | **0,726** |
| 05-10 | 3 824 | 164 | 4,3 % | 75 | 0,413 |
| 05-11 | 5 571 | 215 | 3,9 % | 110 | 0,320 |
| 05-12 | 4 787 | 188 | 3,9 % | 94 | **0,752** |
| 05-13 | 4 469 | 240 | 5,4 % | 159 | 0,312 |
| 05-14 | 7 643 | 516 | 6,8 % | 143 | 0,321 |

**83 035 lignes dans le jeu. 4 508 atteignent un test purgé — 5,4 %.**

## 2. L'échec est un échec de PUISSANCE

`Spearman(G clusters, largeur d'IC) = −0,692 · p = 0,018` (BTC). Les folds qui
échouent sont les petits.

## 3. Les AUC brutes — un signal stable, pas du bruit

```
BTC : 0.713 0.690 0.664 0.822 0.633 0.767 0.679 0.777 0.801 0.673 0.555
ETH : 0.620 0.764 0.721 0.688 0.784
```

**16 cellules sur 16 au-dessus de 0,5.** Médianes 0,690 (BTC) et 0,721 (ETH),
écarts-types 0,079 et 0,065.

## 4. À N complet, le signal est là

| | AUC poolée hors-fold | IC95 bootstrap cluster | p de permutation (200) |
|---|---|---|---|
| **BTC** | **0,7022** | [0,635 ; 0,764] — **exclut 0,5** | **≤ 0,005**, au-delà du max des nulles |
| ETH | 0,6684 | [0,434 ; 0,737] — n'exclut pas | 0,010 |

Témoin de nullité propre : moyenne **0,5046 ± 0,025** (BTC), **0,4999 ± 0,046**
(ETH) sur 200 permutations. *(Un tirage permuté UNIQUE avait rendu 0,5736 — le
maximum des 200 : lire un seul tirage comme la nulle est une erreur, c'est la
distribution qui fait foi.)*

## 5. LE DÉFAUT DE CONCEPTION — la relance était auto-défaisante

`p3_dataset.py:293` : la purge compare les wallets du test à ceux de **tous**
les jours d'entraînement. **Ajouter des jours purge donc davantage chaque fold
déjà existant.** Mesuré sur les 5 folds communs aux deux runs du jalon :

| fold | G_test à 5 jours | à 11 jours | paires 5 j | paires 11 j |
|---|---|---|---|---|
| 05-04 | 308 | **253** | 937 | **658** |
| 05-05 | 191 | **154** | 200 | **153** |
| 05-06 | 208 | **166** | 383 | **223** |
| 05-07 | 207 | **159** | 504 | **264** |
| 05-08 | 168 | **128** | 207 | **139** |

−18 à −24 % de clusters, −24 à −45 % de paires, **sur des folds dont les
données n'ont pas changé**. La relance a donc porté la barre de 4 à 9 folds
**et** affaibli chacun des folds déjà là.

Effet second, plus grave qu'une perte de puissance : à mesure qu'on ajoute des
jours, le test purgé ne garde que les wallets présents **un seul jour**. La
population évaluée dérive vers les acteurs transitoires — **l'estimand change
avec N**.

## Lecture

Le verdict C n'est pas « le rang n'est pas certifiable à cette maille ». C'est
**« le protocole de certification exige plus d'information qu'il n'en laisse
survivre »** — et l'ajout de données réduit ce qui survit.

Conséquence pour la suite : toute porte future doit juger sur l'ensemble
poolé et purger les wallets **dominants récurrents**, pas toute apparition.
Sinon le même piège se referme au banc S4.
