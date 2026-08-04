# 04/08/2026 — Hyperliquid seul : Binance sort du chemin critique

Décision de Meddy. Elle supprime la phase la plus risquée du projet, et elle
mérite d'être écrite avec son raisonnement — parce qu'un jour quelqu'un voudra
la rouvrir.

---

## 1. La décision

> On construit sur Hyperliquid. On affiche sur Hyperliquid.
> **Binance sort du chemin critique.**

Formulée par Meddy le 04/08/2026 : *« je commencerais directement sur
Hyperliquid »*.

## 2. Ce que ça remplace

Le programme d'origine tenait en une phrase : apprendre là où la vérité est
observable (Hyperliquid), puis **transférer** vers là où elle ne l'est pas
(Binance). Le transfert était la phase P7, et c'était le pari central.

C'était aussi le point le plus fragile, pour trois raisons qui s'additionnent.

**On ne peut pas vérifier sur Binance.** Sans identité de portefeuille, la vérité
forte n'y est pas calculable. Le transfert ne serait jamais validé contre la
vérité, seulement contre un substitut mesuré à **Spearman +0,20**. Un pont dont
on ne peut pas tester la solidité.

**Les deux côtés ne se recouvrent pas dans le temps.** Le L4 Hyperliquid couvre
décembre 2025 ; l'enregistreur multi-venues tourne depuis le 28 juillet 2026.
Sept mois d'écart. Le seul chevauchement disponible fait **trois jours**
(29 au 31 juillet).

**Le constat qui avait tué P7 n'a jamais été audité.** Le « 98,5 % de murs qui
fuient » venait d'un instrument dont un audit voisin a montré qu'il datait le
contact sur une grille **117 fois trop grossière** et écartait **58,6 % des
ordres** pour être morts avant leur première photo — une sélection directe sur
la grandeur étudiée. On ne sait donc même pas si P7 était mort.

Autrement dit : une phase à haut risque, non vérifiable, sur une donnée
décalée, et fondée sur un négatif douteux.

## 3. Ce que la décision apporte

**On peut vérifier ce qu'on affiche, tous les jours.** Sur Hyperliquid, la vérité
est là : identité de chaque ordre, durée de vie exacte, cycle complet. Un modèle
se contrôle en direct au lieu d'être extrapolé.

**Le décalage de sept mois cesse d'exister** comme problème.

**Le plafond structurel disparaît.** « Le transfert ne pourra jamais être validé
contre la vérité » ne borne plus rien, puisqu'il n'y a plus de transfert.

## 4. Ce que ça ne dispense pas de faire

**Le nœud reste indispensable.** Le flux public d'Hyperliquid ne donne que
**20 paliers par côté**, soit ±0,031 % du mid — très en deçà de la bande étudiée
(0,12 à 0,80 %). Sans nœud, l'affichage ne verrait pas les objets qu'on mesure.
La décision déplace donc le nœud du statut « utile un jour » à **condition de
l'affichage**.

**Les grandeurs doivent toujours passer le filtre d'admissibilité.** Calculables
en direct, dans un navigateur, à la cadence du flux. Retirer Binance ne
transforme pas la recherche en produit.

## 5. Comment la rouvrir

Binance n'est pas abandonné, il est **hors chemin critique**. La question
« est-ce que ça transfère ? » reste légitime et pourra être reposée — mais elle
ne conditionne plus rien, et la rouvrir demande un **ADR** : contexte,
alternatives, décision, justification, conséquences.

Deux choses la rendraient à nouveau pertinente : un produit qui l'exige
commercialement, ou l'apparition d'une donnée Binance porteuse d'identité — ce
qui n'existe pas aujourd'hui.

## 6. Effet sur les documents

* `00_Prompt_MapDee.md` §1 — le 3ᵉ objectif devient « Hyperliquid, et
  Hyperliquid seul » ; la table d'arbitrage est mise à jour ;
* `00_Prompt_MapDee.md` §11 — **P7 est barré** de la séquence, avec le renvoi ;
* le plafond du §9 (validation contre proxy à +0,20) reste écrit, mais ne borne
  plus le projet.

Rien n'est effacé. La phase P7 reste lisible, barrée, avec sa raison.
