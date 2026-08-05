# ADR-003 — La cible opératoire (C3) : structure fixée, constantes au jour de banc

**Date** : 2026-08-05 · **Statut** : **EN RÉDACTION — ne gèle rien.**
La délégation de Meddy (« prends les meilleures décisions ») couvre aussi ce
document, et la meilleure décision ici est de **ne pas geler cette nuit** :
`05` §9.3 impose littérature **puis** observation des trajectoires brutes sur
le jour de banc — et le jour de banc (`20251208`) n'est pas encore construit.
Geler une cible sans avoir regardé serait la faute exacte que le protocole
combat, dans l'autre sens.

**Ce document fixe la STRUCTURE pour que l'observation de C2 sache quoi
remplir, et rien d'autre.**

---

## Ce qui est déjà gelé (hérité, non renégocié ici)

* la **nature** : le déplacement du prix — où il va à partir de l'instant où
  la grandeur devient connaissable (`05` §2, `ADR-001`) ;
* **continue et signée** — pas de binarisation ;
* jugée par corrélation de rang partielle, unité = le jour (`ADR-001`).

## La structure à remplir — quatre trous, pas un de plus

| trou | forme attendue | d'où viendra la constante |
|---|---|---|
| **l'instant de connaissabilité** | la première photo qui suit l'événement générateur de la grandeur — jamais la photo qui le contient (pas de fuite du futur) | définition, pas mesure — à confirmer sur les horodatages réels du jour de banc |
| **l'horizon** | un ou plusieurs horizons fixes en photos ; chaque horizon supplémentaire est une conjonction interne, pas un test de plus (`ADR-001` II.3) | la distribution des temps de premier passage du jour de banc (fiche B5) — l'horizon doit contenir l'essentiel des premiers passages, pas être un chiffre rond |
| **la grille du déplacement** | en paliers de la grille de production (`bs`), pas en dollars ni en pourcentage | déjà fixée — `harnais/grille.py`, `BIN_REL = 2,5e-5` |
| **ce qui compte comme déplacement** | déplacement **net** du mid à l'horizon, en paliers signés ; les allers-retours intra-horizon ne comptent pas (ils sont la matière d'autres fiches — B5, C3) | à confronter aux trajectoires brutes du jour de banc avant gel |

## Le calendrier de gel

1. fin de la construction du jour `20251208` (tranche 1, en cours) ;
2. **C2** : observation des trajectoires brutes, protocole court pré-enregistré
   avant lecture ;
3. remplissage des quatre trous, **gel par commit**, statut ACCEPTÉE soumis à
   Meddy ;
4. alors seulement : É3/É4 exécutables, le harnais lève ses refus.
