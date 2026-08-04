# Rapport — remplacement de l'instrument et réparation du protocole

**Nuit du 2 au 3 août 2026** · rédigé le 03/08 à 06 h 10, **avant** toute
certification. Aucun résultat de verdict sur donnée réelle n'existe à cette
heure et aucun n'est cité ici.

---

## 1. Le point de départ

Deux semaines de blocage, une cause identifiée le 02/08 : **l'instrument**. Le
banc Kaggle (`hyperliquid-btc-high-frequency-microstructure`) photographie le
carnet toutes les **62,6 s** là où il documente 537 ms, et perd **58,6 %** des
ordres. Répliqué 7 jours sur 7. Sur un phénomène qui vit une seconde, c'est
inexploitable.

Objectif de la nuit : remplacer cet instrument par la **sortie brute de la
bourse**, et vérifier — pas supposer — qu'elle est meilleure.

## 2. La nouvelle source

**OPEN BOOK** (Zenodo 18184441, CC BY 4.0) : décembre 2025, BTC + ETH + SOL,
trois flux — statuts d'ordres (54 octets, nanoseconde, **toutes** les
tentatives y compris les ~89 % rejetées), diffs du carnet visible (avec wallet
et oid), transactions (les **deux** contreparties). 81 Go téléchargés.

Trois artefacts sont FABRIQUÉS au format que le pipeline lit déjà — `hl_orders`,
`hl_book`, `hl_fills` — pour que `hl_labels`, `hl_features` et `p3_train`
restent **inchangés et déjà audités**.

### Volume produit (3 jours complets au moment de l'écriture, 7 visés)

| | |
|---|---|
| statuts d'ordres, 3 jours × 2 symboles | **493 417 789** |
| dont BTC, 01/12 seul | 116 029 103 |
| placements examinés, BTC 01/12 | 38 905 871 |
| photos de carnet, 01/12 | 121 691 (BTC) · 112 276 (ETH) |
| transactions, 3 jours × 2 symboles | 3 010 181 |

## 3. Ce qui a été vérifié, et comment

### 3.1 Le carnet reconstruit, confronté aux transactions réelles

Source **indépendante** : les transactions ne servent pas à construire le
carnet. Critère : *le prix d'une transaction était-il entre le meilleur achat et
la meilleure vente à cet instant ?*

| | reconstruit | banc officiel |
|---|---|---|
| transactions dans la fourchette | **51,0 %** | 48,6 % |
| âge médian de la photo | **100 ms** | 278 ms |
| cadence médiane | 509 ms | 537 ms |
| écart p90 | 14 $ | 12 $ |
| carnets croisés | **0** sur 22 h | — |
| biais du mid (médiane / moyenne) | **0,00 $** / −0,44 $ | — |

Le critère est intrinsèquement sévère — même la référence officielle n'y arrive
qu'à 48,6 %, parce qu'une photo est toujours en retard sur l'exécution. Le p90
est le seul point en retrait, sur deux journées de volatilité différente : rien
n'en est tiré.

### 3.2 Le rôle Maker/Taker — le point qui pouvait tout retourner

Rien dans la donnée ne dit qui est le Maker. Une inversion aurait **retourné le
sens de la cible**, tout le projet reposant sur « ce mur a-t-il été exécuté ou
retiré ».

Première règle essayée — « le dernier posé est l'agresseur » — fausse dans
**4,68 %** des cas. Cause trouvée en lisant cinq exemples : les ordres à
**déclenchement** (stops, TP/SL) dorment hors du carnet visible pendant des
minutes puis agressent ; ils sont *posés* les premiers tout en étant l'agresseur.

Règle retenue, qui est la définition même du Maker : **la transaction se fait à
son prix limite**.

| | |
|---|---|
| accord du côté | 95,26 % → **99,99 %** (BTC) · 99,97 % (ETH) |
| rôle tranché par le prix | 88 % |
| par le temps | 10 % |
| indécis | 1 % |
| écart Maker médian | 2 337 ms (l'ordre dormait) |
| écart Taker médian | **0 ms** |
| Taker posé < 100 ms avant | 95,0 % · Maker : 11,4 % |

### 3.3 La jointure carnet → temps

Les diffs ne portent **aucun** horodatage ; il vient des statuts par `oid`.
C'est le verrou de tout le module : mesuré **100,00 %** (3 manquants sur
1 805 630, tous au bord d'heure).

### 3.4 La couverture de la jointure avec l'observable

| | | |
|---|---|---|
| BTCUSDT | 20251201 | 98,5 % |
| | 20251202 | 98,2 % |
| | 20251203 | 96,5 % |
| | 20251204 | 98,0 % |
| ETHUSDT | 20251201 | 97,7 % |
| | 20251202 | 95,1 % |
| | 20251203 | 97,3 % |
| | 20251204 | 98,1 % |

Seuil de recette : 70 %.

### 3.5 L'unité statistique

| | |
|---|---|
| événements étiquetés, 3 jours × 2 symboles | 951 679 |
| paliers-instants (l'unité réelle) | **169 040** |
| le banc entier, pour comparaison | 83 035 **sur 11 jours** |
| taux de fuite mesuré | 86,8 % |

## 4. Une conclusion antérieure CORRIGÉE

J'avais soutenu le 02/08 que le taux de fuite élevé du banc (77-89 %) était un
artefact de son carnet grossier, en m'appuyant sur 0xArchive qui donnait 21-28 %.

**C'était faux.** Cette source-ci, plus fine que les deux autres et sans trous
déclarés, mesure **86,8 %** : elle confirme le banc. Et 0xArchive est
précisément celle dont on a mesuré 12 % de trous.

Ce qui reste établi contre le banc est autre chose, et tient : sa cadence de
62,6 s et les 58,6 % d'ordres qu'il ne voit pas.

## 5. Deux défauts de PROTOCOLE, trouvés par la mesure

### 5.1 Percolation de l'unité de clustering (ADR-017)

La composante connexe `(palier-épisode ∪ wallet)` s'effondre :

| arête | G | plus gros bloc | top-10 |
|---|---|---|---|
| palier-épisode seul | 32 164 | 0,0 % | 0,2 % |
| wallet non borné | 862 | 10,5 % | 45,4 % |
| wallet borné à 1 min | 35 910 | 0,2 % | 1,2 % |
| **union (en vigueur)** | **131** | **99,8 %** | 99,8 % |

**Aucune des deux arêtes ne percole seule ; c'est leur union.** Les paliers
pontent les wallets et réciproquement. Borner la session de wallet ne répare
donc rien : à 1 minute le wallet seul tombe à 0,2 % mais l'union reste à 24,4 %.
Toutes les options de l'ADR-016 échouent sa jambe 1 sur ce jeu.

Conséquence sur le plafond de 200 paires **par couple de clusters** :

    paires décidables   1 429 542
    paires retenues        12 962   =  0,9 %      (le banc : 17 %)

et l'univers retenu est **inversé** : 200 paires pour les 99,8 % de la masse,
~12 700 pour les 0,2 % restants.

Ça ne fait pas que du bruit — **ça fabrique du signal** :

| trait brut | régime en vigueur | plafond levé (vérité) | palier-épisode |
|---|---|---|---|
| f_mult | **0,5656** | 0,4953 | 0,4953 |
| f_logmag | **0,5656** | 0,4953 | 0,4953 |
| f_dist | 0,4401 | 0,4574 | 0,4574 |
| f_side | 0,4710 | 0,5347 | 0,5347 |
| f_occ | 0,5403 | 0,5610 | 0,5610 |
| f_conv | 0,5853 | 0,5970 | 0,5970 |

`f_mult` et `f_logmag` ne portent **rien** (0,4953). Le régime en vigueur les
remonte à 0,5656 : **+0,07 d'AUC créés sur un trait nul.**

**Décision (ADR-017, appliquée)** : séparer l'unité de PLAFONNEMENT
(`palier_ep`) de l'unité de VARIANCE (bootstrap hiérarchique wallet → épisode).
Sous `palier_ep` le plafond **ne mord jamais** (1 840 517 / 1 840 517 retenues) :
le régime est identique à la vérité non plafonnée, sur les six traits.

### 5.2 La purge d'identité vide le jeu de test (ADR-018)

| sym | jour | test complet | après purge | % | paires décidables |
|---|---|---|---|---|---|
| BTCUSDT | 20251201 | 27 079 | 321 | 1,2 % | 290 |
| BTCUSDT | 20251202 | 22 510 | 334 | 1,5 % | 459 |
| BTCUSDT | 20251203 | 25 070 | 289 | 1,2 % | 315 |
| ETHUSDT | 20251201 | 31 819 | 143 | 0,4 % | 100 |
| ETHUSDT | 20251202 | 24 817 | 112 | 0,5 % | **43** |
| ETHUSDT | 20251203 | 33 067 | 175 | 0,5 % | 97 |

La barre 1 se jugerait sur **43 à 459 paires** (le banc : 46 239). Et **ça
empire avec les jours** : plus de jours d'entraînement = plus de wallets connus
= plus de lignes de test écartées.

Rien de cassé : le marché réel est peuplé de teneurs qui reviennent chaque jour.
Plus l'instrument est fidèle, plus la purge mord.

**L'invariant garanti est symétrique** — « aucun wallet des deux côtés ». Le
protocole l'obtenait en supprimant du côté TEST. On l'obtient identiquement en
supprimant du côté ENTRAÎNEMENT :

    test          = (jour = d) et (wallet ∈ W)
    entraînement  = (jour ≠ d) et (wallet ∉ W)

| sym | train | test | paires décidables | chevauchement |
|---|---|---|---|---|
| BTCUSDT | 26 572 – 39 145 | 5 576 – 12 308 | 10 190 – 24 245 | **0** |
| ETHUSDT | 36 586 – 43 719 | 7 838 – 12 123 | 12 320 – 28 673 | **0** |

**~100× la puissance, même garantie**, vérifiée cellule par cellule à
l'exécution (échec = erreur fatale, pas avertissement).

Bénéfice annexe : les deux périmètres (complet / purgé) couvrent désormais le
**même** échantillon de test et ne diffèrent que par l'entraînement. La prime
d'identité devient une comparaison appariée — elle ne l'était pas
(`p3_train.py` : « jeux de test DIFFÉRENTS → approximation honnête »).

## 6. La règle de décision, gelée avant tout résultat (ADR-019)

**L'unité de pli est le JOUR, pas la cellule.** Trois cellules d'un même jour
partagent la trajectoire de prix ; les compter comme trois plis gonflerait le
dénominateur d'unités corrélées et rendrait la barre plus facile pour une
mauvaise raison. Les 3 modèles d'un jour prédisent chacun sur leur cellule et
leurs prédictions sont **assemblées** en un jeu hors-échantillon couvrant le
jour entier.

**Les barres de l'ADR-013 ne bougent pas** : `ceil(0,80 × n_folds)` et
`ceil(0,60 × n_folds)`. À 7 jours : **6/7** et **5/7**.

Jeu figé : 2025-12-01 → 2025-12-07, BTCUSDT + ETHUSDT, cache isolé des 11 jours
du banc. **Un seul tir. Aucune modification méthodologique ensuite.**

## 7. Contrôles

| contrôle | résultat |
|---|---|
| selftest des 4 mondes truqués, nouveau protocole | **D→D, B→B, C→C, A→A** |
| cible permutée, jeu réel, ancien protocole | **cas D, 0/3** aux deux barres, deux symboles |
| cible permutée, jeu réel, nouveau protocole | en cours à l'heure de rédaction |
| chevauchement de wallet, découpage §5.2 | **0** sur 18 cellules |
| jointure carnet → temps | 100,00 % |

Le contrôle négatif est celui qui compte le plus : sur la vraie donnée avec la
bonne réponse mélangée, **rien ne passe**. Le protocole ne fabrique pas de
signal — garantie qui n'avait jamais été établie sur donnée réelle.

## 8. Défauts de MON code, trouvés et corrigés cette nuit

Listés parce qu'ils conditionnent la confiance dans les chiffres ci-dessus.

1. **Horloge du carnet empoisonnée** — la branche `update` prenait l'instant de
   disparition FUTURE de l'ordre, propulsant l'horloge en fin de journée.
   55 photos/heure au lieu de 3 600. *Diagnostic initial faux* (j'avais accusé
   le mélange `new`/`remove` ; mesuré : 0,00 % de recul).
2. **Paliers par ordre au lieu de par prix** — cinq ordres au meilleur bid
   donnaient cinq « paliers » au même prix, et `hl_labels` lit `level == 1` pour
   le mid. Le mid aurait été faux en silence.
3. **Sortie anticipée d'extraction** comptant les fichiers des autres symboles :
   la journée ETH sortait vide sans une seule erreur.
4. **Raccourci « le fichier existe »** au lieu de « le fichier est intègre » :
   a coûté un parquet de 654 Mo, tronqué par un run tué en cours d'écriture.
5. **Fichier fusionné empilé par symbole** au lieu d'ordonné dans le temps :
   `l2_snapshots` émet la photo AVANT de tester le symbole, donc ETH rendait
   241 photos toutes vides.
6. **`hash()` comme graine** — randomisé par PYTHONHASHSEED : deux exécutions du
   même run n'auraient pas donné le même plafonnement de paires.
7. **Variable `pa` masquant pyarrow** dans ma propre fonction.

## 9. Ce qui reste au 03/08 06 h 10

* jours 01-05 étiquetés ; jour 06 BTC construit ; jour 07 à venir ;
* rejeux prodrows : 01-04 faits, 05-07 en attente ;
* contrôle négatif nouveau protocole : en cours ;
* puis commit (la garde de provenance refuse un verdict sur arbre sale), puis
  **un seul tir**.

## 10. Réserves à porter dans le rapport de certification

* `regret_oracle`, `crps_skill`, `ece`, `ndcg_at_k` bootstrappent toujours
  `cluster` à un étage. Avec un cluster à 99,8 %, **leurs IC sont sans valeur
  sur ce jeu.** Seul `pairwise_auc` — d'où vient la barre 1 — est traité.
* Le nichage épisode ⊂ wallet est imparfait sur données réelles (pureté
  0,90 / 0,89) : l'IC hiérarchique est indicatif, et le code l'imprime
  bruyamment.
* Le jeu OPEN BOOK couvre décembre 2025 ; le banc couvrait mai 2026. **Aucune
  comparaison directe de niveau entre les deux n'est légitime.**

---

# ERRATA du 03/08/2026, 12 h

_Six chiffres de ce rapport sont faux ou périmés. Le corps n'est pas réécrit._

| § | ce que le rapport dit | ce qui est vrai |
|---|---|---|
| 3.1 | « transactions dans la fourchette **51,0 %** » | **61,1 %** après correction des paliers fantômes et de la chauffe. Le 51,0 % était mesuré sur un carnet dont 1,67 % des niveaux 1 étaient de taille nulle |
| 3.1 | « carnets croisés 0 sur **22 h** » | les 22 h SONT le défaut : `WARMUP_H` mangeait 00:00–02:00. Rien n'a été mesuré sur ces deux heures |
| 3.1 | âge médian 100 ms, cadence 509 ms, p90 14 $, biais du mid | **non reproductibles** : mesurés sur le carnet d'avant correction, et les jours sont désormais en lecture seule |
| 3.3 | jointure « **100,00 %** » | 99,99983 % (3 manquants sur 1 805 630). Arrondi trompeur |
| 3.5 | « taux de fuite **86,8 %** » | c'est **BTC, 1er décembre, seul**. Global sur les 14 jeux : **88,97 %**. Amplitude 70,9 %–93,3 %. Et **99,66 %** mesuré en TAILLE, pas en nombre d'ordres |
| 3.5 | « 169 040 paliers-instants » | l'ADR-017 écrit 164 362 pour la même grandeur. Et depuis l'alignement de la grille `_nice` sur celle de la production, le jeu vaut **310 806** lignes couvertes |
| 5.1 | « le plafond ne mord jamais » | vrai côté MESURE, **faux côté ENTRAÎNEMENT** : il y mordait à 91× |
| 5.2 | « 43–459 → 10 190–28 673, **~100×** » | **RETIRÉ le 03/08 à 19 h : cette ligne d'errata était elle-même fausse.** La comparaison est par pli, avant contre après, sur le même jeu — le « ~100× » tient. Le banc portait 37–658 paires, pas 139–658. |
| 5.2 | « la prime d'identité devient appariée » | le code ne l'appariait pas |
| 10 | « le code l'imprime bruyamment » | il la **jetait** |

**Défaut de forme** : ce rapport décrit trois périmètres différents — 3 jours au
§2 et §3.5, 4 jours au §3.4, « 01-05 étiquetés » au §9 — sans les réconcilier.
Il a été écrit pendant que la chaîne tournait.

**Ce qui tient** : le §6 (règle de décision), le §8 (liste de mes défauts de
code), et l'ensemble des contrôles d'intégrité vérifiés depuis par audit
indépendant — décodage des prix, appariement Maker/Taker, absence de fuite
temporelle, absence de carnet croisé.
