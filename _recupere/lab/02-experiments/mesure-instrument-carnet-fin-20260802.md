# MESURE D'INSTRUMENT — que change le carnet à 537 ms ? (BTC + ETH, 2026-05-08)

_02/08/2026. Mesure en LECTURE SEULE : aucun fichier de `gondetect/`,
`experiments/` ou `data/` n'a été modifié. Tous les chiffres ont été produits
avec `E:\Python\Python310\python.exe` par des scripts de scratchpad qui
**réutilisent le code du dépôt sans le réécrire** — seule la localisation du
carnet est déviée à l'exécution (`hl_labels._resolve` monkey-patché : `hl_book`
depuis une autre racine, `hl_orders`/`hl_fills` inchangés, ceux du jalon)._

_Fait suite à `audit-distance-contact-hl-20260802.md` §5.c, dont le point 3
était explicitement une **inférence**. Ce document la remplace par une mesure._

**Ce document ne contient aucune AUC, aucun entraînement, aucun comptage de
barre et aucun verdict.** Il mesure des populations et des distributions.

---

## Réponse en trois lignes

1. **Une population, pas des lignes.** Le carnet fin fait apparaître **24 035
   ordres-événements BTC (72,4 % du bras fin) et 28 999 ETH (84,8 %)** que le
   carnet grossier n'a jamais vus ; ils sont **23× plus courts** (vie médiane
   37,7 s vs 859,1 s), **16× plus gros** (0,1016 vs 0,0063 BTC affiché),
   **plus proches du prix** (0,149 % vs 0,205 %) et leur cible est d'un autre
   ordre : **E[y_post] 0,0151 vs 0,1540**, masse à 0 **98,5 % vs 84,5 %**.
2. **Et ce n'est pas seulement un effet de durée de vie.** À décile de durée de
   vie **fixé**, l'écart de cible subsiste presque entier : **−0,124** (apparié)
   contre **−0,142** (brut) sur BTC ; **−0,108** contre **−0,123** sur ETH.
   L'instrument grossier ne perd donc pas « les ordres courts » — il perd un
   régime de comportement qui reste distinct une fois la durée de vie neutralisée.
3. **Le coût de l'instrument fin est négligeable là où la donnée existe, et
   c'est la donnée qui manque.** Ré-étiqueter un jour-symbole coûte **+9,3 %**
   de temps (390 s vs 356 s BTC) et **25 Mo** de carnet. Mais le carnet publié à
   537 ms n'existe que pour **BTC, 05-08 → 05-14 : 7 des 16 jours-symboles du
   banc**. Les 9 autres exigeraient la voie reconstruite, soit **~2,3 h de rejeu
   par coin-jour** (chiffre du dépôt, `export_mid.py`), ≈ **18 h** au total.

---

## 0. Ce qui a été comparé, et la vérification que la comparaison est propre

Le jalon étiquette avec `data/l4/perps10` : carnet BTC **1 373 photos/jour,
dt médian 62 642 ms**. Le carnet fin publié (Kaggle, `data/l4/cache/datasets/
marvingozo/hyperliquid-btc-high-frequency-microstructure/versions/1`) porte
**159 966 photos, dt médian 537 ms** pour le même 2026-05-08.

Les deux racines contiennent des `hl_orders` différents **en apparence
seulement** : perps10 fait 1 359 339 864 lignes dont 436 948 617 d'autres coins,
soit **922 391 247 lignes BTC — exactement le compte du fichier BTC-only
(922 391 247)**. Les deux arms lisent donc le même flux d'ordres. Pour l'éliminer
complètement comme facteur, **les deux bras de cette mesure lisent les
`hl_orders`/`hl_fills` de perps10** ; seul `hl_book` change.

| bras | carnet | photos/j | dt médian | `hl_orders` |
|---|---|---|---|---|
| **GROSSIER** (le jalon) | `perps10/hl_book` | 1 373 | 62 642 ms | perps10 |
| **FIN** | Kaggle `versions/1/hl_book` | 159 966 | **537 ms** | perps10 |

Ni l'un ni l'autre n'a de trou : aucun `dt` > 5 min des deux côtés (fin : max
21,4 s ; grossier : max 125,7 s).

**Contrôles de non-régression (les deux passent) :**

- Le bras GROSSIER rejoué reproduit le jalon **à l'octet** : 11 224 événements
  BTC et 6 489 ETH, **mêmes `oid`**, **mêmes `t_contact`**, **mêmes `t_obs`**,
  **mêmes `y_post`**. Le harnais ne déforme rien.
- Le bras FIN reproduit l'artefact **déjà présent au dépôt**,
  `data/cache/xcheck/hl_labels_BTCUSDT_2026-05-08_btconly.parquet` (produit le
  29/07) : 33 219 événements contre 33 177, **33 108 `oid` communs = 99,79 %**,
  et **100,0000 % de `t_contact` identiques sur les communs**. Les compteurs
  d'entonnoir sont identiques au chiffre près (`n_candidates` 474 670,
  `n_out_of_band` 28 541 160, `n_dedup_skipped` 411 421, `n_crossing_orders`
  14 224). L'écart résiduel de 0,13 % vient de l'ordre des lignes dans les deux
  fichiers `hl_orders`, qui déplace quelques déduplications.

> **Fait de contexte, sans commentaire** : la mesure du carnet fin sur BTC
> 05-08 **existait au dépôt depuis le 29/07**, avec quatre variantes
> (`btconly` 537 ms, `perps10` 62,6 s, `degrade` 62,6 s, `recon` 500 ms), toutes
> avec le même `n_open_rows = 29 441 532`. Le banc du jalon (01/08) a été
> étiqueté sur la variante grossière.

### ETHUSDT — ce qui n'est pas mesurable, et le substitut employé

**Le carnet publié fin n'existe pas pour ETH.** Le dataset Kaggle est
`hyperliquid-BTC-high-frequency-microstructure` : ses 3 199 320 lignes du 05-08
sont **100 % BTC**. La comparaison demandée est donc **impossible pour ETH**.

Un substitut existe au dépôt : `data/l4/recon/hl_book/hl_book_2026-05-08.parquet`,
mid **reconstruit** depuis le L4 à **500 ms**, BTC **et** ETH (170 315 photos
chacun), produit par `experiments/export_mid.py`. **Ce n'est pas le même
instrument** — c'est le carnet refabriqué depuis le flux d'ordres, pas le carnet
publié. Il est utilisable ici uniquement parce qu'il est **étalonné sur BTC**,
où les deux existent :

| BTC 05-08 | `n_candidates` | `n_events` | `n_invisible` |
|---|---|---|---|
| carnet publié 537 ms | 474 670 | 33 177 | 19 648 |
| mid reconstruit 500 ms | 470 515 | 31 966 | 22 482 |
| **écart** | **−0,9 %** | **−3,6 %** | +14 % |

Le bras ETH ci-dessous est donc **explicitement un bras secondaire** : il dit
que l'effet se reproduit sur ETH, il ne le chiffre pas avec la même autorité que
BTC. Toute lecture d'un chiffre ETH doit porter cette réserve.

---

## 1. Population

### 1.a — L'entonnoir complet, compteur par compteur (BTC 2026-05-08)

| compteur | GROSSIER 62,6 s | FIN 537 ms | fin/grossier |
|---|---:|---:|---:|
| photos de carnet | 1 373 | 159 966 | ×116,5 |
| `dt` médian (ms) | 62 642 | 537 | ×0,009 |
| lignes `open` lues | 29 441 532 | 29 441 532 | **×1,000** |
| hors bande de distance | 28 151 817 | 28 541 160 | ×1,014 |
| écartés par déduplication | 645 575 | 411 421 | ×0,637 |
| ordres traversants | 97 680 | 14 224 | ×0,146 |
| **candidats** | **546 252** | **474 670** | **×0,869** |
| **écartés « invisibles »** | **319 994** | **19 650** | **×0,061** |
| annulations mécaniques | 1 484 | 1 644 | ×1,108 |
| sans contact sous 1 h | 124 889 | 231 547 | ×1,854 |
| retirés > 30 s avant contact | 88 485 | 188 560 | ×2,131 |
| **événements retenus** | **11 224** | **33 219** | **×2,960** |
| dont « a fui » | 3 649 | 23 109 | ×6,333 |
| wallets distincts | 1 023 | 1 096 | ×1,071 |

**Part écartée pour « invisible » : 58,58 % → 4,14 %.** Le chiffre de l'audit est
confirmé exactement ; le carnet fin le fait tomber d'un facteur **14**.

Taux de rétention global (événements / candidats) : **2,05 % → 7,00 %**.

Deux compteurs **augmentent** avec le carnet fin, et il faut le dire : « sans
contact » (×1,85) et « retiré > 30 s avant contact » (×2,13). Mécanisme :
`t_obs` cesse d'être 32 s après le placement, donc l'horizon de contact d'1 h
démarre plus tôt et un ordre mort en 20 s n'est plus éliminé comme invisible —
il devient un candidat que les filtres avals trient. La population ne fait pas
que grossir : **elle est triée par d'autres filtres**.

### 1.b — Attente de la première photo (`t_obs − t_place`), tous candidats, en s

| bras | q1 | q10 | q25 | **q50** | q75 | q90 | q99 | moy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GROSSIER | 0,71 | 7,72 | 18,56 | **35,48** | 50,15 | 58,09 | 62,41 | 34,21 |
| FIN | 0,01 | 0,06 | 0,14 | **0,28** | 0,42 | 0,54 | 1,02 | 0,31 |

La médiane passe de **35,5 s à 0,28 s** : ×127. C'est la grandeur qui gouverne
tout le reste.

### 1.c — Durée de vie des ordres, retenus vs écartés (s, hors resting EOD)

| bras / groupe | n | q10 | q25 | **q50** | q75 | q90 | moy |
|---|---:|---:|---:|---:|---:|---:|---:|
| **GROSSIER** tous candidats | 542 254 | 0,44 | 2,45 | **14,53** | 76,76 | 321,50 | 236,23 |
| GROSSIER — écartés « invisibles » | 320 051 | 0,27 | 0,74 | **3,85** | 12,12 | 24,21 | 8,28 |
| GROSSIER — écartés (autre motif) | 211 258 | 19,74 | 42,75 | **106,37** | 299,41 | 806,38 | 524,40 |
| **GROSSIER — RETENUS** | **10 945** | 130,44 | 298,68 | **727,68** | 1 652,17 | 2 912,75 | 1 339,81 |
| **FIN** tous candidats | 470 776 | 0,87 | 4,83 | **21,62** | 98,48 | 365,24 | 266,34 |
| FIN — écartés « invisibles » | 19 654 | 0,00 | 0,00 | **0,12** | 0,28 | 0,42 | 0,18 |
| FIN — écartés (autre motif) | 418 290 | 1,45 | 5,86 | **22,30** | 92,49 | 323,14 | 252,43 |
| **FIN — RETENUS** | **32 832** | 2,66 | 15,28 | **100,91** | 527,29 | 1 652,02 | 602,83 |

La lecture est directe. Sous carnet grossier, **être retenu impose de vivre
727 s en médiane**, soit **50× la durée de vie médiane d'un candidat (14,5 s)**
et **35× les 21 s documentés dans `hl_labels.py:55-57`**. Sous carnet fin, la
médiane des retenus tombe à **100,9 s** — encore 4,7× la médiane des candidats
(le filtre « retiré > 30 s avant contact » sélectionne toujours sur la
survie), mais le facteur est **divisé par 7**.

Symétriquement, la classe « invisible » cesse d'être une population : sa durée
de vie médiane passe de **3,85 s à 0,12 s**. À 537 ms, « invisible » redevient
ce que le module dit qu'il est — un ordre né et mort entre deux photos — au lieu
d'être « un ordre normal ».

### 1.d — Taille affichée dans l'entonnoir (`size_placed`, BTC)

| bras / groupe | n | q25 | **q50** | q75 | q90 | moy | **somme** |
|---|---:|---:|---:|---:|---:|---:|---:|
| GROSSIER tous candidats | 546 252 | 0,0100 | **0,2508** | 1,8420 | 7,8249 | 4,0214 | 2 196 706 |
| GROSSIER — écartés « invisibles » | 320 051 | 0,0200 | **0,4000** | 1,9743 | 16,8316 | 4,7639 | **1 524 693** |
| **GROSSIER — RETENUS** | 11 224 | 0,0006 | **0,0080** | 0,2484 | 1,8714 | 0,5349 | **6 004** |
| FIN tous candidats | 474 670 | 0,0100 | **0,2858** | 1,8871 | 15,6476 | 4,6230 | 2 194 403 |
| FIN — écartés « invisibles » | 19 654 | 0,2670 | **0,5000** | 2,0130 | 7,8529 | 3,2971 | 64 802 |
| **FIN — RETENUS** | 33 219 | 0,0070 | **0,0260** | 1,0349 | 3,5151 | 1,3276 | **44 103** |

Le carnet grossier écarte comme « invisibles » **1 524 693 BTC de profondeur
affichée — 69 % de toute la taille candidate du jour** — et n'en retient que
**6 004 (0,27 %)**. Le carnet fin en retient **44 103, soit 7,3× plus**. Les
ordres retenus par le bras fin sont en moyenne **2,5× plus gros** (1,33 vs
0,53 BTC).

### 1.e — Combien d'événements le carnet fin fait-il apparaître ?

| | BTCUSDT | ETHUSDT (bras secondaire) |
|---|---:|---:|
| ordres-événements, bras grossier | 11 224 | 6 489 |
| ordres-événements, bras fin | 33 219 | 34 177 |
| **communs** | **9 184** | **5 178** |
| **FIN SEUL — apparus** | **24 035** (72,4 % du bras fin) | **28 999** (84,8 %) |
| GROSSIER SEUL — disparus | 2 040 (18,2 % du bras grossier) | 1 311 (20,2 %) |

Le recouvrement est **partiel dans les deux sens** : 18,2 % des événements du
jalon n'existent pas dans le bras fin (leur contact y est daté ailleurs, ou
tombe hors des filtres). Ce n'est pas un sur-ensemble.

Wallets : 1 023 → 1 096, dont **950 communs**. **146 wallets** n'apparaissent
que dans le bras fin. La concentration ne change pas (top-5 wallets = 23,0 % du
bras grossier, 23,4 % des ordres FIN SEUL) : ce n'est pas un acteur unique.

---

## 2. Les événements RETROUVÉS ressemblent-ils aux autres ?

Tout est mesuré **dans le bras fin**, donc avec le même instrument des deux
côtés : `COMMUN` = `oid` présent dans les deux bras, `FIN SEUL` = apparu.

### 2.a — BTCUSDT, niveau ORDRE

| grandeur | COMMUN (n=9 184) | FIN SEUL (n=24 035) | rapport |
|---|---:|---:|---:|
| durée de vie médiane (s) | 859,1 | **37,7** | ÷22,8 |
| durée de vie q25 / q75 (s) | 347,2 / 1 898,2 | 8,0 / 169,6 | |
| taille affichée médiane (BTC) | 0,0063 | **0,1016** | ×16,1 |
| taille affichée moyenne (BTC) | 0,456 | **1,661** | ×3,6 |
| `dist_obs` médiane (% du mid) | 0,2053 | **0,1486** | ÷1,38 |
| `t_contact − t_obs` médian (s) | 587,8 | **44,4** | ÷13,2 |

### 2.b — La CIBLE `y_post` (niveau ordre, bras fin)

| groupe | n | **masse à 0** | **P(y>0)** | **E[y \| y>0]** | E[y] | part « a fui » |
|---|---:|---:|---:|---:|---:|---:|
| **COMMUN** | 9 184 | **84,49 %** | **15,51 %** | 0,9932 | **0,1540** | 22,59 % |
| **FIN SEUL** | 24 035 | **98,46 %** | **1,54 %** | 0,9841 | **0,0151** | **87,51 %** |
| _(rappel)_ COMMUN vus par le bras grossier | 9 184 | 90,41 % | 9,59 % | 0,9911 | 0,0951 | 28,29 % |
| _(rappel)_ tout le bras grossier | 11 224 | 91,11 % | 8,89 % | 0,9910 | 0,0881 | 32,51 % |

`E[y | y>0]` est quasi identique partout (0,98-0,99) : quand un ordre est
exécuté après le contact, il l'est **presque intégralement**, dans les deux
populations. **Toute la différence est dans P(y>0) : 15,51 % contre 1,54 %,
un facteur 10.** Et le taux de fuite passe de 22,6 % à 87,5 %.

### 2.c — Est-ce seulement un effet de durée de vie ? NON

Découpage du bras fin en déciles de durée de vie, `COMMUN` et `FIN SEUL`
comparés **dans le même décile** :

| décile | vie médiane (s) | n COM | masse0 COM | E[y] COM | n FIN | masse0 FIN | E[y] FIN |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | 1,0 | 0 | – | – | 3 286 | 0,999 | 0,0006 |
| 1 | 5,6 | 1 | – | – | 3 280 | 0,994 | 0,0058 |
| 2 | 15,3 | 3 | – | – | 3 280 | 0,974 | 0,0259 |
| 3 | 34,3 | 100 | 0,880 | 0,1200 | 3 183 | 0,981 | 0,0192 |
| 4 | 70,8 | 451 | 0,942 | 0,0555 | 2 832 | 0,986 | 0,0131 |
| 5 | 140,8 | 644 | 0,856 | 0,1427 | 2 639 | 0,992 | 0,0070 |
| 6 | 275,4 | 1 097 | 0,923 | 0,0763 | 2 186 | 0,993 | 0,0069 |
| 7 | 527,3 | 1 846 | 0,767 | 0,2320 | 1 437 | 0,953 | 0,0460 |
| 8 | 1 021,6 | 2 340 | 0,824 | 0,1757 | 944 | 0,985 | 0,0148 |
| 9 | 2 662,0 | 2 537 | 0,857 | 0,1416 | 746 | 0,937 | 0,0623 |

> **Écart E[y_post] (FIN SEUL − COMMUN) : brut −0,1415 ; APPARIÉ sur le décile
> de durée de vie −0,1238.** L'appariement n'absorbe que **12,5 %** de l'écart.

Dans **chacun** des sept déciles où les deux groupes ont ≥ 30 observations
(3 à 9), `FIN SEUL` a une masse à 0 **plus haute** et un E[y] **plus bas** que
`COMMUN`. Le signe ne s'inverse jamais. À durée de vie égale, les ordres que le
carnet grossier ne voit pas se comportent **différemment** de ceux qu'il voit.

*Limite honnête* : dans les déciles 0-2 (vie < ~20 s), `COMMUN` est vide par
construction — le carnet grossier **ne peut pas** produire d'ordre y vivant.
L'appariement n'est donc possible que sur les déciles 3-9, c'est-à-dire sur
**~40 % des ordres FIN SEUL**. Pour les 60 % restants, il n'existe aucun
contrefactuel : on ne peut pas dire qu'ils ressemblent aux autres, on peut
seulement dire que le bras grossier n'en a aucun.

### 2.d — Niveau PALIER-INSTANT (l'unité réelle du banc, `p3_target`)

| bras | lignes | **clusters** | ordres/ligne | masse y=0 | P(y>0) | E[y\|y>0] | E[y] |
|---|---:|---:|---:|---:|---:|---:|---:|
| GROSSIER | 4 464 | **407** | 2,51 | 90,05 % | 9,95 % | 0,4635 | 0,0461 |
| FIN | 8 866 | **144** | 3,75 | 90,84 % | 9,16 % | 0,1373 | 0,0126 |

Le nombre de lignes **double**, le nombre de clusters d'indépendance est
**divisé par 2,8** (407 → 144). Le carnet fin agrège plus d'ordres par
palier-instant et raccroche davantage de paliers au même wallet : la
percolation déjà documentée le 02/08 **s'aggrave**, elle ne se résorbe pas.

Lignes du bras fin classées par leur composition en ordres nouveaux :

| classe de ligne | n | clusters | masse y=0 | P(y>0) | E[y\|y>0] | E[y] | âge méd. (s) | taille méd. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 % nouveau | 1 112 | 92 | 91,64 % | 8,36 % | 0,5391 | 0,0451 | 460,7 | 0,2501 |
| **100 % nouveaux** | 4 975 | 34 | **96,80 %** | **3,20 %** | 0,1863 | **0,0060** | **60,7** | 1,6215 |
| mixte | 2 779 | 35 | 79,85 % | 20,15 % | 0,0566 | 0,0114 | 184,8 | 2,9254 |

**56 % des lignes du bras fin (4 975 / 8 866) sont composées exclusivement
d'ordres que le bras grossier n'a jamais vus**, et elles ne portent que
**34 clusters** d'indépendance.

### 2.e — ETHUSDT (bras secondaire, mid reconstruit 500 ms — voir §0)

| groupe | n | vie méd. (s) | taille méd. | dist méd. (%) | masse y=0 | P(y>0) | E[y] | fuite |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| COMMUN | 5 178 | 452,9 | 0,2640 | 0,1917 | 87,33 % | 12,67 % | 0,1257 | 38,1 % |
| **FIN SEUL** | 28 999 | **25,0** | 0,2942 | **0,1471** | **99,22 %** | **0,78 %** | **0,0075** | **93,2 %** |

> Écart E[y_post] : brut **−0,1225** ; apparié sur le décile de vie **−0,1075**
> (l'appariement absorbe 12,2 % — même proportion que sur BTC).

Palier-instant : 3 189 lignes / **211 clusters** (grossier) → 7 658 lignes /
**45 clusters** (fin). Même sens, même ampleur, mêmes facteurs que BTC. La
différence notable : la taille affichée médiane **ne bouge pas** sur ETH
(0,264 → 0,294) alors qu'elle est ×16 sur BTC.

---

## 3. Datation

Sur les **9 184 ordres-événements communs** (BTC), écart
`t_contact(62,6 s) − t_contact(537 ms)`, en secondes :

| q1 | q10 | q25 | **q50** | q75 | q90 | q99 | **moyenne** |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0,3 | 3,8 | 15,2 | **35,6** | 88,1 | 312,2 | **2 570,1** | **146,7** |

- **part ≤ 0 : 0,218 %** — le retard est quasi universel ;
- part > 60 s : **30,48 %** · part > 300 s : **11,16 %**.

Concordant avec l'audit (médiane 33 s, moyenne 135 s, q99 2 570 s), qui
re-datait les 11 224 labels du jalon à `t_obs` figé ; ici les deux bras sont des
pipelines complets appariés par `oid`, donc `t_obs` bouge aussi.

Décalage de `t_obs` seul : médiane **28,9 s**, moyenne 29,8 s, q90 56,4 s.

**Ordre de contact :**

| mesure | valeur |
|---|---:|
| Kendall τ-b entre les deux datations | **0,9905** |
| ⇒ part de **paires** discordantes | **0,47 %** |
| Spearman ρ | 0,9992 |
| part de paires **adjacentes** (dans l'ordre fin) inversées en grossier | **2,08 %** |
| part d'événements dont le **rang** change | 98,32 % |
| **part d'événements changeant de seau 60 s (`bucket` de `p3_target`)** | **58,09 %** |

Ces cinq lignes disent des choses différentes et il ne faut pas les confondre.
L'ordre **global** est très bien conservé (0,47 % de paires discordantes) : le
retard est massivement **commun**, pas aléatoire. Mais l'ordre **local** ne
l'est pas (2,08 % d'inversions entre voisins immédiats), et surtout
**58,09 % des événements changent de seau de 60 s** — le seau qui définit
l'unité « palier-instant » dans `p3_target.aggregate`. Le presque-parfait τ ne
protège donc pas l'agrégation.

Sur ETH (bras secondaire) : retard médian **23,2 s**, moyenne 88,9 s, q99
1 670,8 s, **0,00 %** ≤ 0, **47,49 %** de changement de seau.

---

## 4. Ce que ça coûte

### 4.a — Temps mesuré, un jour-symbole, même machine, même session

| bras | mur total | dont scan `hl_orders` | dont `_build_events` | RSS |
|---|---:|---:|---:|---:|
| BTC GROSSIER | 356,3 s | 347,0 s | 5,5 s | 1 488 Mo |
| **BTC FIN** | **389,6 s** | 354,1 s | **31,6 s** | 1 455 Mo |
| ETH GROSSIER | 264,1 s | 256,6 s | 5,8 s | 1 297 Mo |
| **ETH 500 ms** | **270,6 s** | 241,3 s | **27,4 s** | 1 297 Mo |

**Surcoût : +9,3 % (BTC), +2,5 % (ETH).** Il est **entièrement** dans
`_build_events` (+26,1 s / +21,6 s), c'est-à-dire la recherche du premier
contact sur 6 700 photos d'horizon au lieu de 57. Le scan des `hl_orders`
(15 Go, 1,36 milliard de lignes) domine et **ne bouge pas** — c'est lui le coût
du L4, pas le carnet.

_Réserve : un autre process Python (`experiments/fetch_l4_recent.py`) tournait
pendant les quatre mesures. Il était présent pour les quatre, donc la
comparaison reste valide ; les valeurs absolues sont majorées de quelques %.
Le `elapsed_s = 435,6` du jalon au dépôt est mesuré dans d'autres conditions._

### 4.b — Volume disque

| | par jour-symbole | pour 16 |
|---|---:|---:|
| carnet FIN publié (BTC, 20 niveaux) | **25,0 Mo** | ~400 Mo |
| carnet grossier `perps10` (10 coins) | 3,13 Mo ⇒ ~0,31 Mo/coin | ~5 Mo |
| carnet grossier `relance` (BTC niveau 1) | **0,014 Mo** | 0,2 Mo |
| mid reconstruit 500 ms (2 coins, niveau 1) | 1,10 Mo | ~9 Mo |
| labels produits — grossier | 0,56 Mo (BTC) / 0,36 (ETH) | ~7 Mo |
| **labels produits — fin** | **1,67 Mo** (BTC) / 1,70 (ETH) | ~27 Mo |

Le volume n'est un obstacle sur aucun axe. Disque libre sur E: — 190 Go.

### 4.c — Extrapolation aux 16 jours-symboles du banc

Coût du banc actuel, **mesuré** (somme des `elapsed_s` des 16
`hl_labels_*_stats.json`) : **5 874,5 s = 1,63 h**.

Ré-étiquetage complet à cadence fine, aux ratios mesurés (×1,093 BTC,
×1,025 ETH) : **≈ 6 300 s ≈ 1,75 h**, soit **+7 minutes sur tout le banc**.
`hl_prodrows` (le cache des features, 2-6 h de rejeu par coin-jour) **n'a pas à
être régénéré** : il est indexé par le temps, indépendant des labels ; seule la
jointure `features_at_contact` est refaite.

**Le coût réel n'est pas le calcul, c'est la disponibilité de la donnée :**

| jour-symbole | carnet fin publié 537 ms ? |
|---|---|
| BTC 2026-05-08 → 05-14 (7) | **oui** (175 Mo déjà sur disque) |
| BTC 2026-05-04 → 05-07 (4) | **non** — le dataset Kaggle commence au 05-08 |
| ETH 2026-05-04 → 05-08 (5) | **non** — le dataset est BTC-only |

**7 des 16 jours-symboles sont couverts.** Pour les 9 autres, la seule voie au
dépôt est la reconstruction (`experiments/export_mid.py`), chiffrée **par son
propre en-tête à ~2,3 h de rejeu par coin-jour**. ETH 05-08 est déjà fait ;
restent **8 coin-jours ≈ 18,4 h** de rejeu (parallélisable par coin-jour),
produisant ~1,1 Mo/jour. À cela s'ajoute que la voie reconstruite est un
**instrument différent**, qui vaut sur BTC −3,6 % d'événements par rapport au
carnet publié (§0).

Bilan : **≈ 20 h de machine et < 0,5 Go** pour porter les 16 jours-symboles à
une cadence de contact sous la seconde — dont **18,4 h pour 8 coin-jours de
reconstruction** et **7 minutes pour l'étiquetage lui-même**.

---

## 5. Ce que je n'ai PAS pu mesurer

À lire avant d'utiliser un chiffre de ce document.

1. **ETH au carnet PUBLIÉ fin : impossible.** Le dataset ne contient pas ETH.
   Tous les chiffres ETH ici viennent du **mid reconstruit à 500 ms**, un autre
   instrument, étalonné sur BTC à −0,9 % de candidats / −3,6 % d'événements.
   Ils indiquent un sens et un ordre de grandeur, pas une valeur.
2. **Un seul jour.** 2026-05-08. Le carnet fin publié existe aussi pour BTC
   05-09 → 05-14 (6 jours de plus, déjà sur disque) — **ils n'ont pas été
   rejoués**. Rien ici ne dit que le 05-08 est représentatif.
3. **Le côté FEATURES n'a pas été touché.** Les `hl_prodrows` (nappe reconstruite
   10 s) n'ont pas été régénérés et la jointure `features_at_contact` n'a pas été
   rejouée sur les labels fins. Je **ne sais donc pas** : quelle couverture
   (`GO_COVERAGE`) atteindraient les 33 219 labels fins sur la nappe 10 s ; ce
   que devient le « 13,2 % de labels sans rangée dans ±TOL » de l'audit ; ce que
   devient le plancher `f_dist ≥ TOL`. **La nappe reste à 10 s pendant que le
   contact passe à 537 ms — le défaut d'appariement d'ADR-012 change de nature,
   il ne disparaît pas.** Aucun chiffre de ce document ne porte là-dessus.
4. **Aucune AUC, aucun entraînement, aucun jalon rejoué** — hors périmètre par
   consigne. Ce document ne dit **rien** sur ce que deviendrait un résultat du
   jalon. En particulier, la chute de 407 à 144 clusters (§2.d) **n'est pas**
   interprétée ici en termes de puissance.
5. **Le contrefactuel manque pour 60 % des ordres retrouvés.** L'appariement sur
   la durée de vie (§2.c) n'est possible que sur les déciles 3-9. Sous ~20 s de
   vie, le bras grossier n'a aucune observation : la comparaison n'est pas
   « faible », elle est **inexistante**.
6. **Le temps mesuré est bruité** par un autre process Python concurrent
   (§4.a), et les 2,3 h/coin-jour de `export_mid.py` sont **repris du dépôt**,
   pas remesurés par moi.
7. **Le sens de `y_post` sous carnet fin n'a pas été audité.** `y_post` compare
   l'exécution dans `[t_contact, t_contact + 30 s]` à l'exécution antérieure.
   Quand `t_contact` se déplace de 35 s en médiane, ces deux fenêtres changent
   toutes les deux. Je mesure que la cible **change** ; je ne dis pas laquelle
   des deux mesure « la survie au contact ».

---

## Annexe — reproductibilité

Scripts (scratchpad, non versionnés ; aucun fichier du dépôt modifié) :

| script | rôle |
|---|---|
| `run_arm.py` | rejoue `hl_labels.HyperliquidL4Labels.events()` avec `_resolve` patché (carnet `fine` / `coarse` / `recon`, ordres+fills toujours perps10) ; écrit labels, **table des candidats bruts** et stats |
| `compare.py` | §0 non-régression, §1 population, §2 cible, §3 datation, §4 coût (BTC) |
| `extra.py` | taille dans l'entonnoir, cible **appariée** sur le décile de durée de vie, wallets |
| `eth.py` | BTC + ETH côte à côte, bras secondaire reconstruit |

Sorties : `compare_out.txt`, `extra_out.txt`, `eth_out.txt`,
`labels_{coarse,fine,recon}_{BTCUSDT,ETHUSDT}_2026-05-08.parquet`,
`cands_*.parquet`, `stats_*.json`.

Fichiers LUS : `data/l4/perps10/{hl_orders,hl_fills,hl_book}/*_2026-05-08.parquet`,
`data/l4/cache/datasets/marvingozo/hyperliquid-btc-high-frequency-microstructure/versions/1/hl_book/hl_book_2026-05-08.parquet`,
`data/l4/recon/hl_book/hl_book_2026-05-08.parquet`,
`data/cache/hl_labels_*_2026-05-08.parquet` + les 16 `_stats.json`,
`data/cache/xcheck/*.parquet` + `*_stats.json`.

**Écritures : ce fichier uniquement.**
