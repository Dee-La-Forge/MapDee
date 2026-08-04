# RÉPLICATION — l'écart du carnet à 537 ms tient-il sur les 7 jours BTC ?

_02/08/2026. Extension de `mesure-instrument-carnet-fin-20260802.md`, qui avait
mesuré **un seul jour** (BTC 2026-05-08) et le disait comme limite explicite
(§5.2). Ce document rejoue les **6 autres jours** qui disposent du carnet publié
à 537 ms, avec **la méthode de ce rapport, sans la modifier** : `hl_labels._resolve`
dévié à l'exécution pour router `hl_book` vers la racine du carnet fin, les
`hl_orders`/`hl_fills` restant **ceux du jalon**._

**Aucune AUC, aucun entraînement, aucun comptage de barre, aucun verdict.**
Populations et distributions uniquement. `p3_train.py` et `s6_transfer.py` n'ont
pas été lancés. **Aucun fichier de `gondetect/`, `experiments/` ou `data/` n'a été
modifié** — écriture : ce fichier seul.

---

## Réponse en trois lignes

1. **Oui — l'effet se réplique sur 7 jours sur 7, sans exception et sans
   changement de signe.** Le carnet fin fait apparaître **148 715
   ordres-événements BTC** invisibles au carnet du banc (**68,4 %** du bras fin ;
   **61,6 % à 77,1 %** selon le jour). Chaque jour, ces ordres forment la même
   population distincte : vie médiane **38,7 s contre 724,7 s** (÷5,9 à ÷37,5
   selon le jour), taille affichée **×13,3** (×8,7 à ×21,1), taux de fuite
   **84,6 % contre 23,8 %**, `E[y_post]` **0,0156 contre 0,1372** (÷7,4 à ÷12,7).
   **La part écartée pour « invisible » tombe de 58,35 % à 4,11 %** — un facteur
   **12,0 à 16,1** selon le jour, jamais moins.
2. **Ce n'est toujours pas un effet de durée de vie, et l'appariement n'absorbe
   plus rien du tout.** À décile de durée de vie fixé, l'écart de cible subsiste
   sur **7 jours sur 7**, avec le **même signe dans chaque décile exploitable de
   chaque jour**. Sur l'agrégat, l'appariement ne réduit pas l'écart : **−0,1318
   brut, −0,1371 apparié**. Le 05-08 (12,5 % absorbé) était le cas le **plus
   favorable** à l'explication « durée de vie » de toute la semaine ; sur 3 des
   7 jours l'appariement **agrandit** l'écart au lieu de le réduire.
3. **L'effondrement des clusters se reproduit lui aussi sur 7 jours sur 7 :
   2 433 → 1 052 (×0,43)**, entre ×0,35 et ×0,76 selon le jour, pendant que le
   nombre de lignes **double** (×1,78). Le coût, lui, reste petit et **entièrement
   localisé** : **+5,9 %** de temps sur les 7 jours (**+105 s** au total), dont
   **+155 s dans `_build_events`** et **rien** dans le scan des `hl_orders`.

---

## 0. Ce qui a été comparé, et pourquoi la comparaison est propre

### 0.a — Les 7 jours existent et sont intacts (vérifié avant de lancer)

Le carnet publié fin couvre **BTC 2026-05-08 → 05-14, 7 fichiers, 175,2 Mo**
(25,0 Mo/jour). Contrôle d'intégrité sur chacun : pied de page lisible, **24,0 h
de couverture**, **100 % BTC**, 20 niveaux, `dt` médian **537-539 ms**,
**aucun `dt` > 300 s**, aucun mid nul ou négatif. `dt` maximum : 2,4 s (05-10)
à 64,9 s (05-11). **Aucun jour ne manque et aucun n'est corrompu.**

### 0.b — Le bras grossier n'est pas le même fichier selon le jour, et c'est le jalon qui l'impose

C'est le seul point où j'ai dû faire un choix, et il ne déplace rien — mais il
doit être dit.

| jours | racine du jalon | carnet grossier | `hl_orders` |
|---|---|---|---|
| BTC **05-08** | `data/l4/perps10` | 1 373 photos, 10 coins | perps10, 1 359 339 864 lignes (dont 922 391 247 BTC) |
| BTC **05-09 → 05-14** | `data/l4/relance` | 1 380 photos, BTC niveau 1 | relance = **les fichiers Kaggle eux-mêmes** (liens durs) |

`data/l4/perps10` **n'existe que jusqu'au 05-08** : il n'y a pas de carnet 10-coins
pour les 6 autres jours. Le jalon du dépôt les a étiquetés depuis `data/l4/relance`,
dont les `hl_orders`/`hl_fills` sont **physiquement les mêmes fichiers** que ceux du
dataset Kaggle (mêmes inodes, `nlink` ≥ 2, mêmes comptes de lignes à l'unité).

Conséquence, et elle est favorable : sur les 6 jours ajoutés, **les deux bras
lisent littéralement le même fichier d'ordres**. Le facteur « flux d'ordres
différent », que le rapport du 05-08 devait neutraliser par un argument de
comptage, est ici **structurellement nul**. Seul `hl_book` change.

### 0.c — Contrôle de non-régression : le bras grossier reproduit le jalon à l'octet

Sur **chacun des 7 jours**, le bras grossier rejoué redonne le fichier du dépôt :
**mêmes `oid`**, **mêmes `t_contact`**, **mêmes `t_obs`**, **mêmes `y_post`**.
Sur 05-09, les 14 compteurs d'entonnoir du `_stats.json` sont identiques au
chiffre près (`n_open_rows` 15 392 094, `n_candidates` 250 905,
`n_invisible_sub_snapshot` 108 813, `n_events` 3 122, `n_wallets` 518), et le
parquet produit fait exactement la même taille que celui du dépôt.
**Le harnais ne déforme rien.**

### 0.d — ETH : la réplication inter-symbole est impossible sur cet instrument

Le dataset Kaggle est `hyperliquid-**BTC**-high-frequency-microstructure`. Il
n'existe **aucun carnet publié à 537 ms pour ETH**, aucun jour. Je n'ai pas
fabriqué de substitut ETH et je n'en présente aucun comme une mesure : le rapport
du 05-08 avait utilisé le mid reconstruit à 500 ms comme **bras secondaire
explicitement dégradé**, et rien ici ne l'améliore. **La réplication
inter-symbole n'est pas mesurable avec cet instrument.** Les 7 jours ci-dessous
sont 7 jours du **même symbole**, ce qui est une réplication temporelle, pas une
réplication de symbole.

---

## 1. L'entonnoir, jour par jour

| jour | photos GROS | photos FIN | candidats GROS | candidats FIN | % « invisible » GROS | % « invisible » FIN | facteur | événements GROS | événements FIN | ×  | taux de fuite GROS | taux de fuite FIN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 05-08 | 1 373 | 159 966 | 546 252 | 474 670 | 58,58 % | 4,14 % | **÷14,2** | 11 224 | **33 219** | ×2,96 | 32,5 % | **69,6 %** |
| 05-09 | 1 380 | 159 990 | 250 905 | 243 235 | 43,37 % | 2,96 % | **÷14,6** | 3 122 | **6 892** | ×2,21 | 29,1 % | **58,3 %** |
| 05-10 | 1 380 | 159 961 | 481 971 | 366 563 | 60,56 % | 3,92 % | **÷15,5** | 9 072 | **31 102** | ×3,43 | 30,2 % | **72,8 %** |
| 05-11 | 1 380 | 159 836 | 636 500 | 511 161 | 59,24 % | 3,87 % | **÷15,3** | 15 022 | **41 512** | ×2,76 | 33,4 % | **70,3 %** |
| 05-12 | 1 380 | 159 888 | 457 993 | 372 187 | 57,39 % | 3,56 % | **÷16,1** | 11 105 | **26 818** | ×2,41 | 39,3 % | **66,8 %** |
| 05-13 | 1 380 | 159 896 | 413 616 | 349 659 | 58,34 % | 4,61 % | **÷12,7** | 11 251 | **25 632** | ×2,28 | 36,2 % | **61,4 %** |
| 05-14 | 1 380 | 160 032 | 604 052 | 460 871 | 62,41 % | 5,19 % | **÷12,0** | 27 027 | **52 289** | ×1,93 | 29,1 % | **56,6 %** |
| **7 jours** | – | – | 3 391 289 | 2 778 346 | 58,35 % | 4,11 % | **÷14,2** | 87 823 | **217 464** | ×2,48 | 32,6 % | **65,4 %** |

**Le chiffre central de l'audit tient sur les 7 jours.** La part de candidats
écartés pour « invisible sous la photo » vaut **57,4 % à 62,4 % sous carnet
grossier** — sauf le 05-09, jour creux, à 43,4 % — et **2,96 % à 5,19 % sous
carnet fin**. Le facteur ne descend jamais sous **12,0** et ne monte jamais
au-dessus de **16,1**. Ce n'est pas un jour particulier : c'est le régime de
l'instrument.

Le nombre d'événements retenus est multiplié par **1,93 à 3,43** selon le jour
(**×2,48** sur l'agrégat). Le taux de fuite du bras fin est systématiquement
**environ le double** de celui du bras grossier (56,6-72,8 % contre 29,1-39,3 %).

Deux régularités méritent d'être nommées parce qu'elles nuancent le tableau :

- Le nombre de **candidats diminue** avec le carnet fin sur les 7 jours
  (3 391 289 → 2 778 346, soit **−18,1 %**). Le carnet fin ne fait pas
  qu'ajouter : un mid plus précis renvoie davantage d'ordres hors de la bande de
  distance utile. La population ne grossit pas, **elle est retriée**.
- Le **05-14 est le jour le moins spectaculaire** sur presque tous les axes
  (facteur invisible 12,0, événements ×1,93, fuite 56,6 %) et c'est aussi le
  jour où le bras grossier retient le plus (4,47 % de ses candidats). Le **05-09
  est le plus petit** (15,4 M lignes `open` contre 23-32 M ailleurs). L'effet est
  le plus fort au milieu de la semaine, pas aux extrémités — mais il est
  **présent partout**.

---

## 2. Recouvrement des populations

| jour | GROSSIER | FIN | communs | **FIN SEUL** | % du bras fin | GROSSIER SEUL | % du bras grossier |
|---|---:|---:|---:|---:|---:|---:|---:|
| 05-08 | 11 224 | 33 219 | 9 184 | **24 035** | 72,4 % | 2 040 | 18,2 % |
| 05-09 | 3 122 | 6 892 | 2 629 | **4 263** | 61,9 % | 493 | 15,8 % |
| 05-10 | 9 072 | 31 102 | 7 107 | **23 995** | 77,1 % | 1 965 | 21,7 % |
| 05-11 | 15 022 | 41 512 | 11 905 | **29 607** | 71,3 % | 3 117 | 20,7 % |
| 05-12 | 11 105 | 26 818 | 8 703 | **18 115** | 67,5 % | 2 402 | 21,6 % |
| 05-13 | 11 251 | 25 632 | 9 139 | **16 493** | 64,3 % | 2 112 | 18,8 % |
| 05-14 | 27 027 | 52 289 | 20 082 | **32 207** | 61,6 % | 6 945 | 25,7 % |
| **7 jours** | 87 823 | 217 464 | 68 749 | **148 715** | 68,4 % | 19 074 | 21,7 % |

**Le recouvrement est partiel dans les deux sens, sur les 7 jours.** Le bras fin
n'est **pas un sur-ensemble** du bras grossier : entre **15,8 % et 25,7 %** des
événements du jalon (19 074 au total, **21,7 %**) n'existent pas dans le bras
fin — leur contact y est daté ailleurs, ou tombe hors des filtres. Cette perte
est stable jour après jour, elle n'est pas un accident du 05-08.

Symétriquement, la part apparue avec le carnet fin va de **61,6 % (05-14)** à
**77,1 % (05-10)**. Le 05-08 publié (72,4 %) était dans la fourchette, ni haut
ni bas.

---

## 3. La population retrouvée — COMMUN vs FIN SEUL

Tout est mesuré **dans le bras fin**, donc avec le même instrument des deux
côtés. `COMMUN` = `oid` présent dans les deux bras ; `FIN SEUL` = apparu avec le
carnet fin.

| jour | groupe | n | vie médiane (s) | taille affichée méd. | dist méd. (%) | masse à 0 | P(y>0) | E[y\|y>0] | **E[y_post]** | taux de fuite |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 05-08 | COMMUN | 9 184 | 859,1 | 0,0063 | 0,2053 | 84,49 % | 15,51 % | 0,9932 | 0,1540 | 22,6 % |
| 05-08 | FIN SEUL | 24 035 | **37,7** | 0,1016 | 0,1486 | 98,46 % | 1,54 % | 0,9841 | **0,0151** | **87,5 %** |
| 05-09 | COMMUN | 2 629 | 1271,6 | 0,0164 | 0,1728 | 95,13 % | 4,87 % | 0,9724 | 0,0473 | 21,3 % |
| 05-09 | FIN SEUL | 4 263 | **216,3** | 0,2230 | 0,1456 | 99,44 % | 0,56 % | 1,0000 | **0,0056** | **81,1 %** |
| 05-10 | COMMUN | 7 107 | 575,7 | 0,0070 | 0,2076 | 75,52 % | 24,48 % | 0,9951 | 0,2436 | 23,1 % |
| 05-10 | FIN SEUL | 23 995 | **15,3** | 0,0608 | 0,1504 | 97,25 % | 2,75 % | 0,9942 | **0,0273** | **87,6 %** |
| 05-11 | COMMUN | 11 905 | 693,0 | 0,0062 | 0,2077 | 84,90 % | 15,10 % | 0,9936 | 0,1501 | 24,0 % |
| 05-11 | FIN SEUL | 29 607 | **30,9** | 0,0986 | 0,1473 | 98,81 % | 1,19 % | 0,9936 | **0,0118** | **88,9 %** |
| 05-12 | COMMUN | 8 703 | 734,0 | 0,0080 | 0,1994 | 90,64 % | 9,36 % | 0,9957 | 0,0932 | 28,6 % |
| 05-12 | FIN SEUL | 18 115 | **49,5** | 0,1232 | 0,1481 | 98,72 % | 1,28 % | 0,9888 | **0,0126** | **85,2 %** |
| 05-13 | COMMUN | 9 139 | 970,0 | 0,0080 | 0,2029 | 89,25 % | 10,75 % | 0,9944 | 0,1069 | 23,2 % |
| 05-13 | FIN SEUL | 16 493 | **71,5** | 0,1669 | 0,1511 | 98,59 % | 1,41 % | 0,9929 | **0,0140** | **82,5 %** |
| 05-14 | COMMUN | 20 082 | 571,7 | 0,0080 | 0,2095 | 87,07 % | 12,93 % | 0,9968 | 0,1289 | 23,0 % |
| 05-14 | FIN SEUL | 32 207 | **55,9** | 0,1691 | 0,1541 | 98,56 % | 1,44 % | 0,9932 | **0,0143** | **77,5 %** |
| **7 j** | **COMMUN** | 68 749 | **724,7** | 0,0080 | 0,2046 | 86,21 % | 13,79 % | 0,9947 | **0,1372** | 23,8 % |
| **7 j** | **FIN SEUL** | 148 715 | **38,7** | 0,1060 | 0,1499 | 98,43 % | 1,57 % | 0,9917 | **0,0156** | 84,6 % |
| **7 j** | _tout le bras grossier_ | 87 823 | 618,6 | 0,0098 | 0,1824 | 93,19 % | 6,81 % | 0,9905 | 0,0674 | 32,6 % |

---

## 4. LE POINT QUI DÉCIDE — l'écart se réplique-t-il ?

| jour | vie méd. COM (s) | vie méd. FIN SEUL (s) | ÷ | taille méd. COM | taille méd. FIN SEUL | × | E[y] COM | E[y] FIN SEUL | ÷ | fuite COM | fuite FIN SEUL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 05-08 | 859,1 | 37,7 | **÷22,8** | 0,0063 | 0,1016 | **×16,1** | 0,1540 | 0,0151 | **÷10,2** | 22,6 % | **87,5 %** |
| 05-09 | 1271,6 | 216,3 | **÷5,9** | 0,0164 | 0,2230 | **×13,6** | 0,0473 | 0,0056 | **÷8,4** | 21,3 % | **81,1 %** |
| 05-10 | 575,7 | 15,3 | **÷37,5** | 0,0070 | 0,0608 | **×8,7** | 0,2436 | 0,0273 | **÷8,9** | 23,1 % | **87,6 %** |
| 05-11 | 693,0 | 30,9 | **÷22,4** | 0,0062 | 0,0986 | **×15,9** | 0,1501 | 0,0118 | **÷12,7** | 24,0 % | **88,9 %** |
| 05-12 | 734,0 | 49,5 | **÷14,8** | 0,0080 | 0,1232 | **×15,4** | 0,0932 | 0,0126 | **÷7,4** | 28,6 % | **85,2 %** |
| 05-13 | 970,0 | 71,5 | **÷13,6** | 0,0080 | 0,1669 | **×20,9** | 0,1069 | 0,0140 | **÷7,6** | 23,2 % | **82,5 %** |
| 05-14 | 571,7 | 55,9 | **÷10,2** | 0,0080 | 0,1691 | **×21,1** | 0,1289 | 0,0143 | **÷9,0** | 23,0 % | **77,5 %** |
| **7 jours** | 724,7 | 38,7 | **÷18,7** | 0,0080 | 0,1060 | **×13,3** | 0,1372 | 0,0156 | **÷8,8** | 23,8 % | **84,6 %** |

**Réponse : oui, 7 jours sur 7.** Sur les cinq grandeurs de la mesure du 05-08,
le signe est le même **chaque jour**, sans une seule exception :

| direction mesurée | jours où elle tient | fourchette |
|---|---|---|
| FIN SEUL vit **moins longtemps** que COMMUN | **7 / 7** | ÷5,9 à ÷37,5 |
| FIN SEUL affiche une taille **plus grosse** | **7 / 7** | ×8,7 à ×21,1 |
| FIN SEUL est **plus proche du prix** | **7 / 7** | 0,146-0,154 % contre 0,173-0,210 % |
| FIN SEUL a un `E[y_post]` **plus bas** | **7 / 7** | ÷7,4 à ÷12,7 |
| FIN SEUL a un taux de fuite **plus haut** | **7 / 7** | 77,5-88,9 % contre 21,3-28,6 % |
| masse à 0 **plus haute** chez FIN SEUL | **7 / 7** | 97,25-99,44 % contre 75,52-95,13 % |

**L'amplitude varie, la direction jamais.** Le 05-08 n'était donc pas un jour
choisi : sur le rapport de durée de vie il est **au milieu** (÷22,8 pour une
fourchette ÷5,9 à ÷37,5), sur le rapport de taille il est **au milieu** (×16,1
pour ×8,7 à ×21,1), sur le rapport de cible il est **le plus fort mais de peu**
(÷10,2 pour ÷7,4 à ÷12,7).

Un point à ne pas surinterpréter : `E[y | y>0]` reste **0,97-1,00 dans les deux
groupes et tous les jours**. Comme au 05-08, **toute la différence est dans
`P(y>0)`**, jamais dans l'ampleur de l'exécution quand elle a lieu. La valeur
`1,0000` du 05-09 chez FIN SEUL porte sur **24 ordres** (0,56 % de 4 263) : elle
n'est pas informative, elle est petite.

---

## 5. Est-ce un artefact de durée de vie ? (appariement par décile)

Reprise exacte de la procédure du 05-08 : déciles de durée de vie **du bras fin**,
écart `E[y_post]` moyenné sur les déciles où **les deux groupes ont ≥ 30
observations**, pondéré par `min(n_COMMUN, n_FIN SEUL)`.

| jour | écart brut E[y] | écart **apparié** | absorbé par l'appariement | déciles exploitables | signe constant |
|---|---:|---:|---:|---:|---|
| 05-08 | -0,1415 | **-0,1238** | 12,5 % | 7 / 10 | oui |
| 05-09 | -0,0429 | **-0,0529** | -23,2 % | 8 / 10 | oui |
| 05-10 | -0,2261 | **-0,2558** | -13,1 % | 6 / 10 | oui |
| 05-11 | -0,1427 | **-0,1297** | 9,1 % | 6 / 10 | oui |
| 05-12 | -0,0822 | **-0,0790** | 3,9 % | 7 / 10 | oui |
| 05-13 | -0,0944 | **-0,1137** | -20,5 % | 8 / 10 | oui |
| 05-14 | -0,1429 | **-0,1414** | 1,1 % | 8 / 10 | oui |
| **7 jours** | -0,1318 | **-0,1371** | -4,1 % | 8 / 10 | oui |

**L'appariement n'absorbe pas l'écart.** Sur l'agrégat des 7 jours, l'écart brut
vaut **−0,1318** et l'écart apparié **−0,1371** : l'appariement en « absorbe »
**−4,1 %**, c'est-à-dire qu'il n'en absorbe rien. Jour par jour, l'absorption va
de **+12,5 % (05-08)** à **−23,2 % (05-09)** ; elle est **négative sur 3 jours
sur 7** — 05-09, 05-10 et 05-13, où l'appariement **agrandit** l'écart — et
n'atteint 12,5 % qu'une seule fois, sur le 05-08. Sur les 4 jours où elle est
positive, elle vaut 1,1 %, 3,9 %, 9,1 % et 12,5 %.

**Le 05-08, seul jour publié jusqu'ici, était donc le cas le plus favorable à
l'explication concurrente** — celle qui dirait « le carnet fin ne récupère que
des ordres courts, et les ordres courts sont différents ». Sur les six autres
jours cette explication marche moins bien encore.

Et la colonne « signe constant » vaut **oui sur les 7 jours** : dans **chaque**
décile où les deux groupes ont au moins 30 observations, `FIN SEUL` a un
`E[y_post]` plus bas que `COMMUN`. Sur 7 jours, cela fait **50 déciles
exploitables**, et **aucun** ne renverse le signe.

*Limite inchangée, et elle est structurelle* : le nombre de déciles exploitables
va de **6 à 8 sur 10**. Dans les déciles de vie les plus courts, `COMMUN` est
vide **par construction** — le carnet grossier ne peut pas produire d'ordre
vivant 5 s. Pour cette portion des ordres retrouvés il n'existe **aucun
contrefactuel** ; on ne peut pas dire qu'ils ressemblent aux autres, on peut
seulement dire que le bras grossier n'en a aucun.

---

## 6. Clusters d'indépendance — la percolation s'aggrave-t-elle partout ?

| jour | lignes GROS | **clusters GROS** | lignes FIN | **clusters FIN** | × lignes | **× clusters** | ordres/ligne GROS | ordres/ligne FIN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 05-08 | 4 464 | **407** | 8 866 | **144** | ×1,99 | **×0,35** | 2,51 | 3,75 |
| 05-09 | 1 622 | **196** | 2 523 | **149** | ×1,56 | **×0,76** | 1,92 | 2,73 |
| 05-10 | 3 826 | **267** | 7 900 | **101** | ×2,06 | **×0,38** | 2,37 | 3,94 |
| 05-11 | 5 783 | **394** | 11 030 | **168** | ×1,91 | **×0,43** | 2,60 | 3,76 |
| 05-12 | 4 834 | **315** | 8 178 | **161** | ×1,69 | **×0,51** | 2,30 | 3,28 |
| 05-13 | 4 500 | **475** | 7 605 | **181** | ×1,69 | **×0,38** | 2,50 | 3,37 |
| 05-14 | 7 706 | **379** | 12 057 | **148** | ×1,56 | **×0,39** | 3,51 | 4,34 |
| **somme 7 j** | 32 735 | **2 433** | 58 159 | **1 052** | ×1,78 | **×0,43** | – | – |

**L'effondrement se reproduit sur 7 jours sur 7.** Le nombre de lignes
palier-instant est multiplié par **1,56 à 2,06**, et le nombre de clusters
d'indépendance est **divisé** par un facteur compris entre **1,3 (05-09) et
2,8 (05-08)** — jamais il n'augmente. Sur la somme des 7 jours : **2 433 → 1 052
clusters, ×0,43**, pendant que les lignes passent de 32 735 à 58 159.

Le mécanisme est le même que celui documenté le 02/08 : le carnet fin agrège
**plus d'ordres par palier-instant** (2,73-4,34 contre 1,92-3,51) et raccroche
davantage de paliers au même wallet. **La percolation du clustering s'aggrave,
elle ne se résorbe pas** — et elle s'aggrave partout.

Le 05-09 est le jour où l'effondrement est le plus faible (×0,76) : c'est aussi
le plus petit jour de la semaine. Le 05-10 est le plus fort (×0,38 avec
seulement **101 clusters** pour 7 900 lignes).

Composition des lignes du bras fin — même découpage qu'au 05-08 :

| classe de ligne | n | clusters | masse à 0 | P(y>0) | E[y\|y>0] | E[y] | âge méd. (s) | taille méd. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 % nouveau | 8 693 | 638 | 92,10 % | 7,90 % | 0,6092 | 0,0481 | 477,4 | 0,1669 |
| 100 % nouveaux | 29 247 | 263 | 96,79 % | 3,21 % | 0,2532 | 0,0081 | 56,4 | 1,5289 |
| mixte | 20 219 | 319 | 79,95 % | 20,05 % | 0,0677 | 0,0136 | 172,3 | 3,5483 |

part des lignes 100 % nouvelles : 50,3 %

---

## 7. Datation

| jour | n communs | médiane (s) | moyenne (s) | q99 (s) | part ≤ 0 | part > 60 s | Kendall τ-b | **% changeant de seau 60 s** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 05-08 | 9 184 | 35,6 | 146,7 | 2570,1 | 0,22 % | 30,5 % | 0,9905 | **58,09 %** |
| 05-09 | 2 629 | 25,1 | 125,3 | 1718,1 | 0,34 % | 22,2 % | 0,9945 | **49,22 %** |
| 05-10 | 7 107 | 28,9 | 116,3 | 1740,7 | 1,44 % | 26,4 % | 0,9834 | **52,88 %** |
| 05-11 | 11 905 | 26,9 | 112,4 | 1468,6 | 1,81 % | 25,6 % | 0,9935 | **46,72 %** |
| 05-12 | 8 703 | 25,1 | 95,3 | 1325,9 | 2,41 % | 22,5 % | 0,9954 | **46,15 %** |
| 05-13 | 9 139 | 33,5 | 103,5 | 1093,9 | 1,17 % | 27,9 % | 0,9959 | **56,09 %** |
| 05-14 | 20 082 | 28,7 | 138,3 | 1922,2 | 1,76 % | 24,0 % | 0,9906 | **51,82 %** |
| **7 jours** | 68 749 | **29,6** | 122,1 | 1836,1 | 1,48 % | 25,6 % | – | – |

Même lecture qu'au 05-08, confirmée sur les 7 jours : le retard de datation du
carnet grossier est **quasi universel** (part ≤ 0 entre 0,22 % et 2,41 %),
**médian autour de 25-36 s**, avec une queue lourde (q99 entre 1 094 s et
2 570 s).

L'ordre **global** reste très bien conservé (Kendall τ-b entre **0,9834** et
**0,9959**), mais c'est le point que le rapport du 05-08 demandait de ne pas
confondre : **entre 46,2 % et 58,1 % des événements changent de seau de 60 s**,
le seau qui définit l'unité « palier-instant » dans `p3_target.aggregate`. Sur
les 7 jours, **jamais moins de 46 %**. Le τ presque parfait ne protège pas
l'agrégation.

---

## 8. Ce que ça a coûté, mesuré

| jour | mur GROSSIER (s) | mur FIN (s) | surcoût | scan GROS | scan FIN | `_build_events` GROS | `_build_events` FIN | RSS FIN (Mo) | jalon `elapsed_s` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 05-08 | 356,3 | 389,6 | +9,3 % | 347,0 | 354,1 | 5,5 | **31,6** | 1455 | 435,6 |
| 05-09 | 189,7 | 197,5 | +4,1 % | 184,5 | 177,6 | 2,7 | **17,4** | 937 | 210,3 |
| 05-10 | 229,8 | 240,0 | +4,4 % | 221,9 | 207,7 | 4,8 | **27,6** | 1156 | 251,1 |
| 05-11 | 265,5 | 280,4 | +5,6 % | 254,7 | 241,5 | 6,3 | **34,9** | 1208 | 324,9 |
| 05-12 | 245,0 | 254,3 | +3,8 % | 236,6 | 225,1 | 4,8 | **25,7** | 1108 | 321,2 |
| 05-13 | 238,3 | 239,6 | +0,5 % | 230,4 | 212,2 | 4,2 | **23,5** | 1142 | 307,5 |
| 05-14 | 261,1 | 289,3 | +10,8 % | 250,2 | 255,8 | 6,1 | **28,8** | 1168 | 281,4 |

**Conditions de mesure.** Les 12 bras des jours 05-09 → 05-14 ont été rejoués
**strictement séquentiellement, un seul processus lourd à la fois**, sur la même
machine et dans la même session — donc **non contendus**, contrairement aux
mesures du 05-08 qui portaient la réserve d'un autre process Python concurrent.
Le couple 05-08 est repris tel quel du rapport précédent et garde sa réserve.
`experiments/fetch_l4_recent.py` (41 Mo) tournait en fond pendant toute la
séance, identiquement pour les deux bras.

**Bilan sur les 7 jours :**

| | GROSSIER | FIN | écart |
|---|---:|---:|---:|
| mur total, 7 jours | **1 785,7 s** (0,50 h) | **1 890,7 s** (0,53 h) | **+105,0 s = +5,9 %** |
| dont scan `hl_orders` | 1 725,3 s | 1 674,0 s | −51,3 s |
| dont `_build_events` | 34,4 s | **189,5 s** | **+155,1 s** (+22,2 s/jour) |

**Le surcoût est entièrement dans `_build_events`, et il n'est pas ailleurs.**
Le scan des `hl_orders` — **68,1 Go et 6,534 milliards de lignes par bras**, soit
**136,1 Go et 13,07 milliards de lignes** pour les deux bras des 7 jours —
domine le temps total (94 %) et **ne dépend pas du carnet** : il varie de ±10 %
d'un rejeu à l'autre, au point que sur 4 jours sur 7 le scan du bras fin est
sorti **plus rapide** que celui du bras grossier. C'est du bruit de machine, pas
un gain. La seule quantité structurelle est le **+22 s/jour** de recherche du
premier contact sur ~6 700 photos d'horizon au lieu de ~57.

Le surcoût par jour va de **+0,5 % à +10,8 %** ; cette dispersion est du bruit de
scan, pas un effet de jour. **Sur l'agrégat, +5,9 %**, à comparer aux +9,3 %
mesurés sur le seul 05-08.

À titre de repère, l'étiquetage de ces mêmes 7 jours par le jalon du dépôt a
coûté **2 132,0 s** (somme des `elapsed_s` des 7 `_stats.json`), soit plus que
mes 1 785,7 s pour le bras grossier — les deux mesures ne sont pas comparables
directement (conditions machine différentes) et je ne les compare pas.

**Ce que j'ai gaspillé, et je le dis** : une première tentative à 3 processus
concurrents a été lancée puis **interrompue** au bout de ~200 s par processus.
Elle n'a produit aucun fichier et aucun chiffre de ce document n'en provient ;
elle a coûté ≈ **10 minutes** de machine. Le débit disque agrégé y était
meilleur (≈ 24 Mo/s contre 13 Mo/s en séquentiel), mais les temps par bras
auraient été **contendus donc inutilisables** pour le tableau ci-dessus.

### 8.b — Volume disque réellement consommé

| poste | mesuré |
|---|---:|
| carnet FIN publié, 7 jours (déjà sur disque) | **175,2 Mo** (25,0 Mo/jour) |
| carnet GROSSIER `relance`, 7 jours | **0,096 Mo** |
| `hl_orders` relus pour cette mesure (7 j × 2 bras) | **136,1 Go lus**, **0 octet écrit** |
| labels produits par cette mesure (12 bras) | **13,1 Mo** |
| tables de candidats bruts (12 bras, diagnostic seul) | **73,1 Mo** |
| journaux, `_stats.json`, sorties texte | 0,1 Mo |
| **total écrit par cette mesure (scratchpad, hors dépôt)** | **86,4 Mo** |

Le volume n'est un obstacle sur aucun axe. Disque libre sur E: — 203 Go.

---

## 9. Ce que je n'ai PAS pu faire

À lire avant d'utiliser un chiffre de ce document.

1. **ETH : impossible, et non contourné.** Aucun carnet publié fin n'existe pour
   ETH (§0.d). Je n'ai produit aucun substitut. La réplication démontrée ici est
   **temporelle, sur un seul symbole**.
2. **Les 9 autres jours-symboles du banc restent hors de portée.** BTC 05-04 →
   05-07 (le dataset Kaggle commence au 05-08) et ETH 05-04 → 05-08. Sur les 16
   jours-symboles du banc, **7 sont mesurés ici, 9 ne le sont pas**.
3. **Le côté FEATURES n'a pas été touché**, exactement comme dans le rapport du
   05-08. Les `hl_prodrows` (nappe 10 s) n'ont pas été régénérés, la jointure
   `features_at_contact` n'a pas été rejouée. Je ne sais donc **rien** de la
   couverture qu'atteindraient ces labels fins sur la nappe 10 s. **La nappe
   reste à 10 s pendant que le contact passe sous la seconde.**
4. **Aucune AUC, aucun entraînement, aucun jalon rejoué** — hors périmètre par
   consigne. Ce document ne dit **rien** sur ce que deviendrait un résultat du
   jalon. L'effondrement des clusters (§6) n'est **pas** interprété en termes de
   puissance.
5. **Le contrefactuel manque pour 42,7 % des ordres retrouvés.** L'appariement
   (§5) n'est possible que sur les déciles où les deux groupes ont ≥ 30
   observations ; dans les déciles de vie courte le bras grossier n'en a
   **aucune**, par construction. Mesuré sur les 7 jours : **83 146 des 145 132
   ordres FIN SEUL (57,3 %) sont appariables**, les **42,7 % restants n'ont aucun
   contrefactuel** (de 31,0 % le 05-13 et le 05-14 à 55,6 % le 05-11). Sur cette
   portion, ce n'est pas une comparaison faible — c'est une comparaison
   inexistante.

   > **Écart avec le rapport du 05-08, signalé et non tranché.** Sa §5.5 écrit
   > « le contrefactuel manque pour **60 %** des ordres retrouvés » ; je mesure
   > **41,3 %** pour ce même jour. Son propre tableau §2.c donne 14 867 ordres
   > `FIN SEUL` dans les déciles 3-9 sur 24 035, soit **61,9 % d'appariables** —
   > donc ~38 % de non-appariables, cohérent avec ma mesure et non avec sa phrase.
   > La formulation « 60 % » du 05-08 semble désigner la part **non couverte**
   > alors que le texte la présente comme couverte. **Je ne corrige pas ce
   > document-là** ; je signale la divergence et je donne ci-dessus le chiffre que
   > je mesure, avec sa définition explicite (≥ 30 observations dans **les deux**
   > groupes).
6. **Le sens de `y_post` sous carnet fin n'a pas été audité** (limite reprise du
   05-08). `t_contact` se déplace, donc les deux fenêtres qui définissent
   `y_post` se déplacent aussi. Je mesure que la cible **change** ; je ne dis pas
   laquelle des deux mesure « la survie au contact ».
7. **Sept jours consécutifs ne sont pas sept observations indépendantes.**
   05-08 → 05-14 est une seule semaine, sur un seul actif, dans un seul régime de
   marché. La réplication est réelle mais elle ne couvre pas d'autre régime.
8. **Je n'ai pas remesuré** les 2,3 h/coin-jour de `experiments/export_mid.py`
   citées par le rapport du 05-08 pour la voie reconstruite ; ce chiffre reste
   repris du dépôt.

---

## Annexe — reproductibilité

Scripts de scratchpad (non versionnés ; **aucun fichier du dépôt modifié**) :

| script | rôle |
|---|---|
| `d7/check.py` | intégrité des 7 carnets fins + carnets grossiers + orders/fills |
| `d7/run_arm7.py` | rejoue `hl_labels.HyperliquidL4Labels.events()` avec `_resolve` patché ; racine des ordres = celle du jalon du jour |
| `d7/analyse7.py` | non-régression, entonnoir, recouvrement, cible, appariement, clusters, datation, coût |
| `d7/md7.py` | rend les tableaux du présent document |
| `d7/seq.sh` | ordonnancement séquentiel des 10 bras restants |

Sorties : `d7/labels_{coarse,fine}_BTCUSDT_2026-05-{09..14}.parquet` (12 bras),
`d7/cands_*.parquet`, `d7/stats_*.json`, `d7/out7.txt`, `d7/md7_out.txt`.
Le couple 05-08 est repris **tel quel** des sorties du rapport précédent
(`scratchpad/labels_{coarse,fine}_BTCUSDT_2026-05-08.parquet`) ; l'analyse
re-calculée dessus redonne ses chiffres publiés au chiffre près, ce qui vaut
contrôle croisé du présent harnais.

Fichiers LUS : `data/l4/relance/{hl_orders,hl_fills,hl_book}/*_2026-05-{09..14}.parquet`,
`data/l4/perps10/*_2026-05-08.parquet`,
`data/l4/cache/datasets/marvingozo/hyperliquid-btc-high-frequency-microstructure/versions/1/hl_book/*.parquet`,
`data/cache/hl_labels_BTCUSDT_2026-05-{08..14}.parquet` + leurs `_stats.json`.

**Écritures dans le dépôt : ce fichier uniquement.**
