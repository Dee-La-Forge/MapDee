# ADR-001 — La détection de liquidité fictive est un problème SUPERVISÉ

**Statut** : acceptée (2026-07-28)

## Contexte
Le pipeline précédent (FFT 2D, RMT, ondelettes, diffusion) cherchait à « nettoyer »
le carnet sans définition du propre. Non falsifiable : aucune expérience ne pouvait
le réfuter.

## Décision
Passer en supervisé. Fabriquer les labels : vérité **L4 Hyperliquid** (ordre
individuel, wallet, cycle de vie) → calcul ex post de ce que l'ordre était
vraiment → **destruction volontaire de l'identité** pour ne garder que du **L2
agrégé 100 ms** (ce que donne un CEX) → couples *(observable dégradée, vérité)*.

La question devient « **quelles features L2 trahissent un ordre qui fuit** »,
qui se teste.

## Conséquence
- Le débruitage non supervisé est **enterré**, pas mis en attente.
- Le programme **sonologie** (spectral / cohérence / flatness) redevient testable :
  chaque feature se score contre la survie au contact, via le Feature Registry.
- Critère d'arrêt **économique** : détecteur dont le coût d'évasion rejoint le
  coût d'être sincère (persistance ⊥ cohérence multi-venue, sur l'axe du coût).
