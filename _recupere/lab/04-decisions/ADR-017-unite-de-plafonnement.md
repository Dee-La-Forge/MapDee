# ADR-017 — Séparer l'unité de PLAFONNEMENT de l'unité de VARIANCE

**Date** : 2026-08-03, 03 h 50 · **Statut** : **APPLIQUÉ**, mesures ci-dessous
faites AVANT tout verdict sur le jeu OPEN BOOK.

> Écrit avant d'avoir lancé le jalon une seule fois sur ce jeu. Les seuls
> nombres regardés sont ceux de la partition et de six traits BRUTS pris un par
> un — jamais un modèle entraîné, jamais une barre.

---

## Le fait qui force la décision

Sur le jeu OPEN BOOK (3 jours, BTC+ETH, 164 362 paliers-instants), la composante
connexe `(palier-épisode ∪ wallet)` **percole totalement** :

| | G | plus gros cluster | top-10 |
|---|---|---|---|
| BTCUSDT | 131 | **99,8 %** | 99,8 % |
| ETHUSDT | 50 | **99,9 %** | 100,0 % |

Ce n'est pas l'aggravation d'un défaut connu, c'est un **changement de régime**.
Le banc était à 93,7 % / 95,7 % ; la densité du nouveau jeu (169 040
paliers-instants en 3 jours contre 83 035 en 11 jours) fait franchir le seuil.

**Ni l'une ni l'autre arête ne percole seule :**

| arête seule | G | plus gros | top-10 |
|---|---|---|---|
| palier-épisode | 32 164 | 0,0 % | 0,2 % |
| wallet non borné | 862 | 10,5 % | 45,4 % |
| wallet borné 5 min | 18 739 | 1,2 % | 8,4 % |
| wallet borné 1 min | 35 910 | 0,2 % | 1,2 % |
| **union (en vigueur)** | **131** | **99,8 %** | **99,8 %** |

Les paliers pontent les wallets et les wallets pontent les paliers. **Borner la
session de wallet ne répare donc rien** : à 1 minute, le wallet seul tombe à
0,2 % mais l'union reste à 24,4 %. Toutes les options de l'ADR-016 échouent la
jambe 1 sur ce jeu (plafond : plus gros ≤ 5 %, top-10 ≤ 25 %).

## La conséquence, mesurée

`_build_pairs` plafonne à 200 paires **par couple de clusters**. Avec un bloc à
99,8 %, le couple (C, C) — qui porte la quasi-totalité des paires — est ramené
à 200, tandis que chaque petit cluster garde les siennes.

    paires décidables   1 429 542
    paires retenues        12 962   =  0,9 %      (le banc : 17 %)

**L'univers de mesure est inversé par rapport à la donnée** : 200 paires pour
les 99,8 % de la masse, ~12 700 pour les 0,2 % restants.

Et ça ne se contente pas de faire du bruit — **ça fabrique du signal** :

| trait brut | unité en vigueur + plafond | plafond LEVÉ (vérité) | palier-épisode + plafond |
|---|---|---|---|
| f_mult | **0,5656** | 0,4953 | 0,4953 |
| f_logmag | **0,5656** | 0,4953 | 0,4953 |
| f_dist | 0,4401 | 0,4574 | 0,4574 |
| f_side | 0,4710 | 0,5347 | 0,5347 |
| f_occ | 0,5403 | 0,5610 | 0,5610 |
| f_conv | 0,5853 | 0,5970 | 0,5970 |

`f_mult` et `f_logmag` ne portent **rien** (0,4953, indiscernable de 0,5). Le
régime en vigueur les remonte à 0,5656 : **+0,07 d'AUC créés sur un trait nul.**

## La décision

**Le plafonnement des paires et l'estimation de la variance n'ont aucune raison
d'utiliser la même partition.** Ils répondent à deux questions différentes :

* le plafond corrige un **déséquilibre quadratique** dans l'univers des paires ;
* le bootstrap estime une **incertitude** sous dépendance.

On les sépare :

1. **Unité de PLAFONNEMENT = `palier_ep`** (palier-épisode seul).
   Jambe 1 : plus gros 0,0 %, top-10 0,2 % — passe avec trois ordres de marge.
   Jambe 3 : **le plafond ne mord jamais** (1 840 517 / 1 840 517 retenues), la
   colonne est identique à la vérité sur les six traits. Le régime n'introduit
   donc aucun déplacement, et là où le régime en vigueur en introduisait un, il
   le RETIRE (−0,07 sur f_mult) : jamais il ne remonte le point.

2. **Unité de VARIANCE = bootstrap hiérarchique wallet → épisode**, comme
   l'ADR-016 §Décision-2 le retenait déjà. Jambe 2 mesurée là-bas : couverture
   0,977–0,993 pour un nominal de 0,95, à rho ∈ {0,5 ; 0,85 ; 0,98} — jamais
   anti-conservateur. C'est LUI qui porte la dépendance de haut niveau ; le
   plafond n'a jamais eu ce rôle.

3. **`cluster` n'est pas modifié.** La colonne, la purge LODO par identité de
   wallet et tout le reste sont intacts. On ne change QUE l'argument passé au
   plafonnement.

## Ce que ça ne fait pas

* **Ça ne rouvre aucun verdict.** Le cas C du 02/08 reste rendu, sur le banc,
  sous son unité. Ce qui suit est une mesure NOUVELLE, sur un jeu NOUVEAU.
* **Ça ne resserre pas l'IC artificiellement** : l'IC vient du bootstrap
  hiérarchique, pas de la partition de plafonnement.
* **Ça ne touche pas la jambe 2.** Elle reste portée par le hiérarchique, dont
  les réserves de l'ADR-016 tiennent (nichage imparfait, pureté 0,90/0,89 :
  l'IC hiérarchique réel est indicatif et le code le dit bruyamment).

## Réserve honnête

`regret_oracle`, `crps_skill`, `ece` et `ndcg_at_k` bootstrappent toujours
`cluster` à un seul étage. Avec un cluster à 99,8 %, **leurs IC sont sans
valeur sur ce jeu** et doivent être lus comme tels, ou pas lus. Seul
`pairwise_auc` — d'où vient la barre 1 — reçoit le traitement complet.

---

# ADDENDUM du 03/08/2026, 12 h — trois affirmations FAUSSES de ce document

_Ajouté après le verdict et les audits adversariaux du 03/08. (Leur nombre a
été cité de trois façons — sept, douze, quinze — selon la date de rédaction ;
il n'est pas reconstituable a posteriori, aucun de ces comptes ne fait foi.)
Le corps du document
n'est pas réécrit : ses erreurs restent lisibles, datées, à leur place._

## 1. « pureté 0,90 / 0,89 » — FAUX pour le régime réellement tiré

Le §« Ce que ça ne fait pas », puce 3, affirme que les réserves de l'ADR-016
tiennent avec une pureté de nichage de 0,90/0,89.

**Ces chiffres valaient pour l'unité `cluster`.** L'unité effectivement passée
au bootstrap hiérarchique est `palier_ep`, dont la pureté mesurée vaut
**0,358 à 0,816** sur les 14 cellules du tir — **toutes sous 0,90**.

À 0,4, l'étage « wallet » n'enveloppe pas l'étage fin : par le critère écrit
dans le code lui-même, les IC rendus sont **indicatifs, pas des IC de verdict**.
Le rapport du tir les cite sans réserve.

## 2. « et le code le dit bruyamment » — FAUX au moment de l'écriture ET du tir

`p3_train.py` faisait `uw, _pur = _unit_wallet(...)` : la pureté était calculée
puis **jetée**. L'avertissement `[NICHAGE IMPUR]` n'existe que depuis le 03/08
09 h 08, soit **après** le verdict de 07 h 51.

Trois documents affirmaient un comportement du code qui n'existait pas :
celui-ci, l'ADR-016 §Réserves, et le rapport de nuit §10.

## 3. Statut « APPLIQUÉ » — vrai côté MESURE seulement

L'ADR-017 n'a été câblé que sur le plafonnement des paires d'ÉVALUATION. Du
côté ENTRAÎNEMENT, `p3_dataset.build_pairs` plafonnait encore sur `cluster`,
l'unité qui percole à 99,8 %. Mesuré sur le train BTC du pli 20251201 :

    3 346 paires decidables au lieu de 306 376   (91x moins)

et sur le pli qui a déclenché le CAS D, réparer ce seul point déplace le témoin
de **0,488 à 0,558**. Le ranker n'étant pas plafonné, la barre 2 était
structurellement biaisée en sa faveur. Corrigé le 03/08 après le tir.

## 4. Ce que ce document affirmait et qui TIENT

La percolation à 99,8 %, l'inversion de l'univers de paires (0,9 % retenues),
et surtout **la fabrication de signal** : `f_mult` vaut 0,4953 — rien — et le
régime en vigueur le remontait à 0,5656. Tout cela a été reconfirmé.

Une mesure indépendante du 03/08 apporte même un renfort : la fraction de
paires intra-unité vaut **0,17 %** sous `palier_ep` contre **17 %** sous
`cluster`. Le passage à l'unité fine a incidemment réduit d'un facteur cent un
défaut de bootstrap que personne n'avait vu.
