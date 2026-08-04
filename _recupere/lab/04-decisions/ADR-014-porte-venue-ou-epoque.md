# ADR-014 — Porte « VENUE ou ÉPOQUE ? » (pré-enregistrée avant tout chiffre)

**Date** : 2026-08-02, 06 h 00 · **Statut** : à valider par Meddy · **Écrit AVANT
le premier run.** Aucun chiffre de cette porte n'existe à cette heure.

## Pourquoi cette porte existe

S6 a rendu **NO-GO** deux fois (`s6-…033041Z`, `s6-…034119Z`). Mais S6 compare
**Hyperliquid en mai 2026** à **Binance fin juillet 2026** : la venue ET
l'époque changent ensemble. ADR-012 l'écrivait comme sa faiblesse assumée —
« un échec ne dira pas lequel des deux a tué le transfert » — et déclarait que
le désenchevêtrement exigerait une fenêtre simultanée, donc le nœud.

**C'était inexact, et l'archive le prouve** : le recorder P1 enregistre
**Hyperliquid ET Binance, les mêmes jours, à la même seconde, au même instrument
100 ms, dans la même bande**, depuis le 28/07. Le lecteur `recorder_rows` est
déjà paramétré par venue. La question se tranche donc **sans monter le nœud**.

Cette porte ne rouvre pas S6, qui reste clos avec son verdict. Elle pose une
question **différente** : le transfert échoue-t-il à cause de la **bourse**, ou
de l'**époque** (et du passage L4→observable) ?

## Le dispositif — une variable à la fois

Les deux côtés viennent de la MÊME source (recorder), des MÊMES jours
(2026-07-29 → 2026-08-01), du MÊME code (`recorder_rows` → `rows_to_day` →
`build_events`), avec la MÊME cible (`y = 1 − flee_ratio`, le proxy continu).
**Seule la venue change.**

| entraîné sur | évalué sur | ce que la cellule mesure |
|---|---|---|
| HL juillet | HL juillet (LODO) | **plafond** intra-venue Hyperliquid |
| Binance juillet | Binance juillet (LODO) | **plafond** intra-venue Binance |
| HL juillet | Binance juillet | **le transfert, à époque égale** |
| Binance juillet | HL juillet | le transfert inverse (symétrie) |

Les plafonds ne sont pas décoratifs : sans eux, un transfert faible est
illisible. Si un modèle ne marche déjà pas **à l'intérieur** de Binance, la
question du transfert ne se pose pas.

## Bande commune — la contrainte d'ADR-007, appliquée

Hyperliquid ne publie que **20 paliers par côté**. Les deux populations sont
donc restreintes à la bande où HL a des données : `f_dist ≤ q95(f_dist | HL)`,
mesurée sur HL et appliquée **identiquement aux deux**. Comparer au-delà
reviendrait à demander à HL ce qu'il ne publie pas — l'erreur qu'ADR-005
interdit (absence ≠ retrait).

## Features — 16, les mêmes qu'au second passage de S6

`f_mult` et `f_logmag` restent EXCLUES : elles valent `mag/med`, et `med` se
calcule sur la bande disponible, qui diffère entre une venue à 20 paliers et
une venue au carnet complet. Le défaut corrigé cette nuit n'a aucune raison de
disparaître ici — il serait même pire.

## Seuils — repris d'ADR-012, sans changement

1. **Absolue** : AUC pairwise ≥ **0,55** avec IC95 excluant 0,5.
2. **Rétention** : `edge_transfert ≥ 0,50 × edge_plafond` de la venue **cible**.
3. **Les deux symboles**.
4. **< 60 clusters** dans une cellule → puissance insuffisante pour cette
   cellule, dite comme telle.

Métrique identique au jalon et à S6 : fenêtre 300 s, décidabilité 0,10, plafond
200 paires par couple de clusters, 400 bootstraps **par clusters de base**,
clusters = épisodes. p de permutation (200 tirages) publié en plus,
**informatif, jamais décisoire**.

## Les trois lectures possibles, écrites AVANT

- **Le transfert TIENT à époque égale** → la bourse n'est pas la barrière. Le
  NO-GO de S6 s'explique alors par l'époque, ou par le passage du label fort L4
  (mai) au proxy observable (juillet). Le programme repart, avec une cible
  claire : refaire le lien vérité↔observable sur une fenêtre simultanée.
- **Le transfert ÉCHOUE, plafonds sains** → la venue est bien la barrière. S6
  est confirmé pour la bonne raison, et l'hypothèse du transfert direct L2 est
  morte proprement.
- **Les PLAFONDS eux-mêmes sont bas** → ce n'est ni la venue ni l'époque : le
  proxy observable à 100 ms ne porte pas de signal exploitable, sur aucune des
  deux bourses. C'est le résultat le plus lourd des trois, et il faut
  l'accepter s'il sort.

## Réserve écrite d'avance

Cette porte n'utilise **aucune vérité L4** : elle compare deux observables
entre eux. Elle peut donc dire « les deux bourses se comportent pareil » sans
rien dire de la **valeur** du signal. C'est une mesure de transférabilité, pas
de véracité — et elle ne remplace ni le jalon ni S6.

---

# CLÔTURE — porte INFAISABLE avec les données publiques (02/08, 06 h 00)

Exécutée le 02/08 : **le flux L2 public d'Hyperliquid ne produit pas
d'événements** — 6 sur 4 jours pour BTC comme pour ETH, contre 1 615 et 4 452
côté Binance. Mesure et cause : `lab/02-experiments/flux-public-hyperliquid-inexploitable-20260802.md`.

La porte ne peut donc pas rendre de verdict, et n'en rendra pas. Elle n'est ni
GO ni NO-GO : elle est **sans objet avec ces données**. La question qu'elle
posait — venue ou époque ? — reste ouverte et exige la profondeur complète
d'Hyperliquid, donc le nœud.

Le rapport vide produit par le run a été retiré ; seule la mesure est conservée.
