# ADR-007 — Un plancher de couverture par jour-symbole : la garde cesse d'être binaire

**Statut : EN RÉDACTION** — la valeur du plancher appartient à Meddy.
Écrite le 06/08/2026, à la découverte de 20251213 BTC (172 photos, compté
« OK ») et de 20251215 (44-54 %, compté « OK »).

## Le problème, mesuré

La garde de `construit/` est binaire : 0 photo = refus, > 0 = compté. Elle
a correctement refusé 20251213 ETH (0) et laissé passer :

| jour-symbole | photos | part d'une journée pleine |
|---|---|---|
| 20251213 BTC | 172 | ≈0,14 % — un trou de facto |
| 20251215 BTC | 53 688 | ≈44 % |
| 20251215 ETH | 56 216 | ≈54 % |
| 20251212 BTC | 82 447 | ≈69 % |
| 20251212 ETH | 86 339 | ≈75 % |

Les heures perdues sont l'après-midi et le soir — 3 à 5 fois plus de flux
que le matin : **les jours partiels sont biaisés vers le calme, tous dans
le même sens**. L'unité statistique d'É3/É4 est le JOUR (Student à poids
égaux) ; σ inter-journalier (C6) dimensionnera la réserve avec ça dedans.

## Honnêteté préalable

Ce plancher est proposé APRÈS l'observation de deux jours dégradés — le
choix de sa valeur ne peut donc pas prétendre à la pré-déclaration pure.
Ce qui reste pré-déclarable : le MÉCANISME (cette ADR), et une valeur
justifiée par l'instrument (une journée-unité de Student doit
échantillonner le cycle diurne entier), arbitrée par Meddy AVANT le gel de
C3 et tout É4 réel.

## La règle proposée

1. **Le manifeste porte la couverture** : `heures_a_zero_photo` (0-24) et
   `couverture = deep_snaps / attente` — l'attente étant le pas de photo
   déclaré, pas une référence externe.
2. **`lot.py` refuse sous plancher** : un jour construit sous X % sort en
   ÉCHEC nommé (« jour partiel : N h à zéro photo »), comme le 0-photo
   d'aujourd'hui. Correction en file, jamais sous un run.
3. **Le préflight refuse un périmètre** contenant un jour sous plancher
   pour toute épreuve à l'unité JOUR (É3, É4, C6). É0-É2 (corrélations sur
   photos existantes) tolèrent les jours dégradés documentés.
4. **Valeur proposée à l'arbitrage : X = 90 %** avec exclusion explicite
   par ADR pour tout jour entre le plancher et le trou (cf. ADR-006 : la
   sortie d'un jour du périmètre se re-déclare, elle ne se tait pas).
5. Défense existante en attendant : le plancher k/n d'É4 (`05` §4) refuse
   déjà mécaniquement un jour à 172 observations pour tout bloc non
   trivial.

## Conséquence immédiate, déclarée avant le tir J8

Rien n'empêche É0/É2 de tourner sur J8 avant que cette ADR ne soit
tranchée — mais si le plancher accepté sort le 12 ou le 15, `05` §7
impose de faire repasser tous les candidats jugés. Donc, ÉCRIT D'AVANCE :
**tout verdict calculé sur un périmètre contenant 20251212 ou 20251215
est PROVISOIRE au regard de cette ADR** — il repasse si le plancher les
exclut, sans discussion. Le tir l'imprime, le rapport le portera.

## Ce que ça ne décide pas

La valeur X (Meddy), et le sort statistique des jours 44-75 % déjà dans
J8 : pondération, exclusion d'É3/É4 seulement, ou acceptation documentée —
à trancher dans la même ADR quand elle sera arbitrée.
