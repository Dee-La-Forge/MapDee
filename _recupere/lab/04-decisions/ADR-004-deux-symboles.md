# ADR-004 — Deux symboles : BTC + ETH

**Statut** : acceptée (2026-07-28)

## Contexte
Choix entre 1 symbole (simple), 2, ou les 28 déjà enregistrés.

## Décision
Exactement **deux** : BTCUSDT et ETHUSDT.

## Justification
- **1 ne suffit pas** : aucune réplication indépendante, aucun lead-lag.
- **28 n'apportent rien** : quand BTC décroche tout décroche → événements
  massivement corrélés → **N effectif plat** pour un coût infra linéaire.
- **2 donne** : réplication indépendante (un détecteur qui marche sur BTC mais
  pas ETH est sur-ajusté, et on l'apprend gratuitement), lead-lag BTC→ETH, et un
  carnet ETH plus mince → spoof moins cher → **plus d'événements positifs par
  unité de temps** (argument de puissance statistique).

## Conséquence — vérifiée en P0
Le run P0 confirme l'intérêt : ETH produit **54 641 événements / 16 856 épisodes**
contre **27 246 / 5 604** pour BTC sur la même fenêtre de 29 h. Et l'écart
d'AUC BTC↔ETH est devenu le juge de paix du résultat.
