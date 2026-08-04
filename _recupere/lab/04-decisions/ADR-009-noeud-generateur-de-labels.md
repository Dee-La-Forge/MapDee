# ADR-009 — Le nœud Hyperliquid est un GÉNÉRATEUR DE LABELS, pas une infra

**Statut** : acceptée (2026-07-29, proposition Meddy)

## Contexte
L'ADR-008 fait du nœud auto-hébergé la voie normale. Le risque immédiat est de
laisser Hyperliquid s'infiltrer partout : un champ `oid` ici, un `user` là, une
hypothèse sur la cadence en blocs dans une feature. Le jour où la source change,
il faudrait tout réécrire — et on ne pourrait même pas comparer deux sources
entre elles, ce qui est pourtant le cœur du test de transfert.

## Décision
Le nœud n'est **pas** une brique d'infrastructure dont le reste dépend. C'est
**une source de vérité parmi d'autres**, derrière une frontière explicite.

Cette frontière est du **code**, pas une intention : `gondetect/labelsource.py`
définit `LabelEvent` (le couple observable/vérité) et le protocole `LabelSource`.
Tout l'aval — features, modèle, ablation, calibration, backtest, transfert — ne
connaît que ces deux types.

**Aucun champ propre à une venue** (`oid`, `user`, `coin`, `cloid`, `hash`…) ne
franchit la frontière : il reste dans `provenance`, non typé. Un garde-fou
exécutable (`check_boundary`) le vérifie.

## Ce que ça permet

**Interchangeabilité** — remplacer Hyperliquid par une autre source de vérité
revient à écrire une classe. Rien d'autre ne bouge.

**Comparabilité** — trois sources coexistent déjà, de force croissante :
`weak` (archive prod 10 s), `medium` (recorder 100 ms + transactions),
`strong` (nœud L4). Toutes émettent le MÊME type. C'est ce qui rend « est-ce que
ça transfère ? » **mesurable** : on entraîne sur `strong` et on vérifie sur
`weak`, exactement la porte P4.

**Reconstruction fidèle du L2 dégradé** — `raw_book_diffs` permet de reconstituer
le carnet **sans divergence**. Le L2 agrégé qu'on fabrique en détruisant
l'identité est donc bien celui qu'aurait vu un observateur extérieur, pas une
approximation. Sans ça, les couples (observable, vérité) seraient biaisés à la
racine et tout le programme reposerait sur du sable.

**Un parser, trois usages** — le même passage sur les données du nœud produit :
(1) les labels forts, (2) le L2 dégradé, (3) l'alignement temporel avec le
recorder multi-venue. On ne relit pas trois fois.

## Ce qu'on accepte
Une indirection de plus, et l'interdiction d'utiliser des champs Hyperliquid
« juste pour voir ». C'est le prix de la modularité, et il est faible.

## Signal d'alerte
Si un champ spécifique à une venue devient nécessaire dans le pipeline
d'apprentissage, ce n'est pas la frontière qu'il faut assouplir : c'est le signe
qu'on a trouvé une signature **non transférable** (cf. le risque « cadence en
blocs » du programme §4). Elle doit être identifiée comme telle, pas dissimulée.
