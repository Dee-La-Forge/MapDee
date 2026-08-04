# ADR-018 — Purger du côté ENTRAÎNEMENT, pas du côté test

**Date** : 2026-08-03, 04 h 25 · **Statut** : **PROPOSÉ — à valider par Meddy.**
**Aucun verdict rendu sous ce régime avant validation.**

> Toutes les mesures ci-dessous sont faites avec un **score aléatoire**. Aucun
> modèle n'a été entraîné, aucune AUC réelle n'a été regardée. Ce document ne
> parle que de **puissance**, jamais de résultat.

---

## Le fait

Sur le jeu OPEN BOOK (3 jours, BTC+ETH), le LODO purgé de `p3_dataset.lodo_folds`
vide le jeu de test :

| sym | jour | test complet | après purge | % | paires décidables |
|---|---|---|---|---|---|
| BTCUSDT | 20251201 | 27 079 | 321 | 1,2 % | 290 |
| BTCUSDT | 20251202 | 22 510 | 334 | 1,5 % | 459 |
| BTCUSDT | 20251203 | 25 070 | 289 | 1,2 % | 315 |
| ETHUSDT | 20251201 | 31 819 | 143 | 0,4 % | 100 |
| ETHUSDT | 20251202 | 24 817 | 112 | 0,5 % | **43** |
| ETHUSDT | 20251203 | 33 067 | 175 | 0,5 % | 97 |

La barre 1 se juge sur ce périmètre (`p3_train.py:410` : `f["purged"]`). Elle se
jugerait donc sur **43 à 459 paires**, là où le banc en portait 46 239.

**Et ça empire avec les jours.** Plus de jours d'entraînement = plus de wallets
connus = plus de lignes de test écartées. Ajouter les jours 04-07 rendrait la
mesure PLUS FAIBLE. Le jeu de jours à 7 déclaré à 03 h 20 est donc caduc pour
des raisons de puissance, mesurées avant tout résultat.

## Pourquoi ça arrive ici et pas sur le banc

Rien de cassé : le marché réel est peuplé de teneurs qui reviennent **chaque
jour**. Sur le banc (instrument grossier, 58,6 % des ordres perdus) la purge
laissait 5 % des lignes. Sur la sortie brute de la bourse, elle en laisse 1,2 %.
Plus l'instrument est fidèle, plus la purge mord.

## Ce que la purge garantit, exactement

> **Aucun `dom_wallet` n'apparaît à la fois dans l'entraînement et dans le test.**

C'est le bon garde-fou : sans lui, le modèle est récompensé d'avoir mémorisé une
identité plutôt qu'un comportement (ADR-010/011).

Mais cet invariant est **symétrique**. `lodo_folds` l'obtient en supprimant les
lignes de TEST dont le wallet est vu au train. On l'obtient tout aussi bien en
supprimant les lignes d'ENTRAÎNEMENT dont le wallet est dans le test. Le
protocole en vigueur a choisi le côté destructeur — sans que ce choix ait jamais
été argumenté, parce que sur le banc il ne coûtait rien.

## La proposition

Découpage croisé **jour × groupe de wallets**, 3 groupes tirés une fois pour
toutes (graine 20251201) :

* **test** = (jour = d) ∩ (wallets ∈ W)
* **entraînement** = (jour ≠ d) ∩ (wallets ∉ W)

Les deux gardes sont conservées — jour différent ET wallets disjoints — et
l'invariant est **vérifié cellule par cellule**, pas supposé.

| sym | train | test | paires décidables | wallets train / test | chevauchement |
|---|---|---|---|---|---|
| BTCUSDT | 26 572 – 39 145 | 5 576 – 12 308 | 10 190 – 24 245 | ~450 / ~155 | **0** |
| ETHUSDT | 36 586 – 43 719 | 7 838 – 12 123 | 12 320 – 28 673 | ~320 / ~120 | **0** |

**43–459 paires → 10 190–28 673 paires.** Même garantie, ~100× la puissance.

## Ce que ça change, et qu'il faut accepter en connaissance de cause

1. **9 cellules par symbole au lieu de 3.** Les barres en proportion (ADR-013)
   deviennent ceil(0,8 × 9) = **8/9** et ceil(0,6 × 9) = **6/9**. Le seuil
   relatif est inchangé ; le seuil absolu bouge parce que le dénominateur bouge.
2. **Un jour apparaît dans plusieurs cellules** (une par groupe de wallets). Les
   cellules d'un même jour ne sont pas indépendantes entre elles. Il faut donc
   soit compter la barre par JOUR (une cellule tirée par jour), soit l'assumer
   explicitement. **Non tranché — c'est le point qui demande ton arbitrage.**
3. **Le régime en vigueur reste calculable** et doit être publié à côté, avec
   son compte de paires, pour que l'écart soit lisible.

## Ce que ça ne change pas

* `cluster`, `palier_ep`, le plafond, le bootstrap : rien de l'ADR-017 ne bouge.
* Les seuils en PROPORTION (80 % / 60 %) ne sont pas touchés.
* Aucun verdict antérieur n'est rouvert.

## L'alternative écartée, et pourquoi

**Découpage par wallets seuls** (3 plis, sans contrainte de jour) : 32 327 à
64 887 paires — encore plus puissant. **Écarté** : entraînement et test
partageraient les mêmes journées, donc les mêmes régimes de marché. On
testerait le transfert d'identité sans tester le transfert temporel. Le jalon
perdrait la moitié de ce qu'il est censé établir.

---

# ADDENDUM du 03/08/2026, 12 h — corrigé à 19 h : c'est L'ADDENDUM qui était faux

_Le corps n'est pas réécrit. Statut réel : **ACCEPTÉ** le 03/08 par Meddy,
verdict rendu sous ce régime — le « PROPOSÉ » de l'en-tête est périmé._

## Ce que cet addendum affirmait à 12 h, et qui est FAUX

> « Le §"Le fait" compare 43 à 459 paires par pli à 46 239 paires, et en conclut
> "~100× la puissance". La comparaison est fausse… **le gain réel est de ~3×**. »

**Il n'y a pas d'erreur dans le corps.** Vérifié le 03/08 à 19 h en relisant la
ligne incriminée — c'est la dernière du §« La proposition », ligne 70 :

> **43–459 paires → 10 190–28 673 paires.** Même garantie, ~100× la puissance.

Elle compare **43–459 paires par pli** (l'ancien découpage, tableau du §« Le
fait ») à **10 190–28 673 paires par pli** (le nouveau, tableau du §« La
proposition »). Deux mesures **par pli**, sur le **même jeu OPEN BOOK**, avant
contre après. Le rapport vaut effectivement ~50× à ~240×. **Le « ~100× » est
honnête**, et c'est bien lui qui a servi à valider la décision.

Les 46 239 paires apparaissent ailleurs — au §« Le fait », comme point de
comparaison avec le banc — et ne sont l'argument d'aucune conclusion.

## L'erreur que j'ai commise en écrivant l'addendum de 12 h

J'ai attribué à la ligne 70 une comparaison qu'elle ne fait pas, puis j'ai
calculé un « gain réel » avec un dénominateur lui aussi inexact : j'ai écrit
que le banc portait **139 à 658** paires par pli alors que la plage réelle
relevée est **37 à 658**. **Le « facteur 30 » est une invention de ma part**,
sur les deux termes du rapport.

Deux fautes se cumulent : je n'ai pas relu la ligne que j'accusais, et j'ai
présenté à Meddy comme une erreur grave du dossier ce qui était une erreur de
ma lecture. C'est le motif exact — écrire avant de vérifier — que le plan du
03/08 était censé supprimer.

**Portée** : le « facteur 30 » a été propagé dans le REGISTRE (E5), la DETTE,
l'ERRATA §5.2 et l'index des ADR. Il est retiré des quatre.

## Ce qui justifie la décision, en plus de la puissance

Pas le nombre de paires — **la représentativité**. L'ancien test ne gardait que
**1,2 %** des lignes, et pas n'importe lesquelles : uniquement les wallets
jamais vus à l'entraînement, c'est-à-dire les acteurs **marginaux et
occasionnels**. On mesurait sur une population non représentative du marché.

Le nouveau découpage teste la journée entière, gros teneurs compris, avec le
même invariant — vérifié à l'exécution sur 42 cellules : **0 chevauchement de
wallet**.

## Seuils : voir l'ADR-019 §3

Le §« Ce que ça change » annonce des barres à **8/9 et 6/9** (cellule comme
unité). L'ADR-019 a tranché autrement : **l'unité de pli est le JOUR**, les
cellules d'un jour sont assemblées, et les barres restent **6/7 et 5/7**.
Un lecteur qui s'arrête ici applique les mauvais seuils.
