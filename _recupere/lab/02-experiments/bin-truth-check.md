# Le bon test — vérité dégradée au niveau du PALIER

## La vérité, vue au niveau PALIER

- 33,177 événements-ordre → **8,862 paliers-instants**, dont **7,632** où quelque chose bouge
- ordres par palier : médiane 3, max 139
- **taux de fuite PAR PALIER : 98.5 %**  (par ordre : 69.7 %)
- fraction annulée par palier — p10 1.000 · médiane 1.000 · p90 1.000

→ **LE L2 EST FIDÈLE — c'est la CIBLE qui est mal posée.** Au niveau palier, la vérité elle-même dit « a fui » presque toujours. Sur ce marché, un palier perd de la profondeur en permanence : « survivre au contact » ne distingue rien à cette échelle.

## L2 « moyen (mesure directe 100 ms) » vs vérité palier

- **70 appariements** sur 110 événements L2
- L2 dit « a fui » : 100.0 % · vérité palier : 100.0 %
- **accord : 100.0 %**
- corrélation des fractions annulées (Spearman) : `+nan`
- ⚠ le L2 n'a **aucune variance** ici : rien à mesurer au-delà du taux de base.

## L2 « faible (proxy 10 s, celui de P0) » vs vérité palier

- **51 appariements** sur 68 événements L2
- L2 dit « a fui » : 100.0 % · vérité palier : 100.0 %
- **accord : 100.0 %**
- corrélation des fractions annulées (Spearman) : `+nan`
- ⚠ le L2 n'a **aucune variance** ici : rien à mesurer au-delà du taux de base.

## Réserves

- Un seul jour, un seul symbole, et la fenêtre L2 ne couvre que 6 h.
- La vérité palier n'agrège que les ordres **retenus** par la source forte (candidats avec contact sous 1 h) : c'est un sous-ensemble de la population réelle du palier, pas son intégralité.
- `bs` est figé à 2 $ ; un rebase de grille dans la fenêtre décalerait les appariements.
