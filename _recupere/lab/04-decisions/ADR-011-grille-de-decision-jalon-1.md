# ADR-011 — Grille de décision du JALON 1, gravée AVANT le premier cache réel

**Date** : 2026-07-30 soir · **Statut** : accepté · **Décideurs** : Meddy (structure en quatre
cas, exigence du dénominateur, directive de silence) + les barres déjà pré-enregistrées
d'ADR-010. **Écrite avant l'arrivée du premier `hl_prodrows` réel** — après, chaque ligne
aurait valu moitié moins.

## Rappel des barres (ADR-010, inchangées)

- **Barre 1 (prédictibilité)** : le TÉMOIN TRIVIAL — logistique sur Δfeatures des paires
  décidables — obtient une AUC pairwise avec **IC > 0,5 sur ≥ 4/5 folds LODO PURGÉ par
  wallet, pour CHACUN des 2 symboles** (bootstrap par clusters de base, schéma corrigé du
  30/07, IC absent = échec).
- **Barre 2 (loyer)** : le lambdarank n'est conservé que si **ΔAUC(ranker − témoin) a un IC
  excluant 0 sur ≥ 3/5 folds pour chaque symbole**.

## Les QUATRE cas — l'ordre d'examen est celui-ci, D d'abord

### D — Un point passe sous 0,5 quelque part → ARRÊT ET AUTOPSIE
Si l'AUC pairwise POINT du témoin (ou du ranker) tombe sous 0,5 dans UNE cellule
fold×symbole : le signal directionnel — jamais démenti en 16 cellules univariées — l'est
pour la première fois. **Aucune suite (features, GLU, transfert) avant l'autopsie** :
inspection des paires de la cellule fautive, vérification de fuite inversée, comparaison
avec la cellule univariée correspondante. Ce cas PRIME sur tous les autres.

### A — Le ranker bat le témoin (barres 1 ET 2) → cadrage établi, P3 continue
Le cadrage par rang est ÉTABLI (la certitude qu'ADR-010 attendait). Le lambdarank devient
le modèle de référence, sa fiche porte le loyer payé. Prochain jalon : le TRANSFERT (S5-S6),
avec le ranker.

### B — Témoin certifié, ranker ne le bat pas → LE CAS PROBABLE, décidé d'avance
Attente honnête écrite depuis ADR-010 : le gain du ranker sera faible. Décision gravée :
**le signal est ÉTABLI, l'architecture est SIMPLIFIÉE** — le modèle de production est la
**logistique sur Δfeatures**, le lambdarank est abandonné SANS REGRET (fiche : Supprimé,
loyer non payé). C'est un BON résultat : un modèle plus simple qui suffit — plus
transférable, moins cher, plus lisible. **Le transfert (S5-S6) se teste avec la
logistique.** Aucune tentative de « sauver » le ranker par du tuning : le tuning est
interdit à N=5 jours (ADR-010).

### C — Rien ne se certifie, points toujours > 0,5 → verdict de PUISSANCE, une seule relance
Ni échec ni établissement : la maille manque de clusters. Relance UNIQUE, aux paramètres
fixés ICI :
- **Ajout de données pré-engagé** : les **6 jours BTC restants du dataset BTC-only déjà
  identifié** (2026-05-09 → 2026-05-14, ~58 Go, source connue, coût zéro) — BTC passe à
  ~11 jours ; ETH reste à 5 (pas d'autre source gratuite) et devient témoin de réplication
  directionnelle, pas de certification.
- **Un seul re-run**, mêmes barres, folds LODO recalculés sur le nouvel ensemble.
- **Clause de fin de boucle** : si après cette relance la barre 1 ne passe toujours pas sur
  BTC, le verdict FINAL est « **non certifiable à cette maille d'événement** » — retour à
  l'arbitrage du programme (autre définition d'événement, ou attente du nœud HL), PAS de
  troisième essai sur ces données.

## Le dénominateur — MESURÉ le 30/07 soir (avant le premier cache de features)

Comptage réel sur les labels des 5 jours (partition wallet ∪ palier-épisode de
`p3_target.assign_clusters`, wallets NON scopés par jour — c'est le choix gelé en S1) :

| grandeur | valeur |
|---|---|
| paliers-instants | 55 628 |
| **G_total (clusters)** | **1 966** (BTC 1 356 · ETH 610) — PAS « ~10 000 » ni « 23 962 épisodes » (ce chiffre-là était scopé par jour) |
| clusters s'étendant sur ≥ 2 jours | 397 (20,2 %) — mais ils portent **96,3 % des événements** |
| wallets dominants présents ≥ 2 jours | 1 192 / 3 331 (35,8 %) |
| top-10 clusters | **93,7 % des événements** — l'union-find biparti forme des composantes GÉANTES (percolation : un palier actif relie beaucoup de wallets) |

Lecture honnête, écrite avant le jalon : le LODO purgé par wallet écartera l'essentiel des
événements de test (96,3 % vivent dans des clusters multi-jours) — **les G par fold après
purge seront petits, et c'est le VRAI pouvoir statistique du jalon**. Si cela conduit au cas
C, c'est le protocole qui parle, pas un accident. La définition du cluster ne sera PAS
retouchée entre ici et le verdict — une définition qu'on change en voyant les chiffres
n'est plus une définition.

## Rappel : ces chiffres doivent AUSSI figurer dans le document du verdict

Le rapport du jalon DOIT contenir, à côté du verdict (pour que « ~10 000 clusters » soit lu
avec son vrai dénominateur) :
- G_total (clusters de la partition wallet ∪ palier-épisode, 5 jours × 2 symboles) ;
- **nombre et % de clusters qui S'ÉTENDENT sur plus d'un jour** (wallets récurrents — ce
  sont eux que le LODO purgé écarte du test) ;
- G effectif par fold APRÈS purge, par symbole — le vrai N de chaque cellule ;
- concentration : % des événements portés par les 10 plus gros clusters.

## Protocole de silence (directive Meddy, 30/07)

La grille étant écrite, **aucune consultation supplémentaire entre elle et le verdict** —
tout avis intermédiaire ne pourrait qu'inciter à la réinterpréter. Le protocole tranche ;
personne d'autre. Les résultats intermédiaires (couverture, entraînements) s'exécutent et
se consignent sans commentaire stratégique. Retour vers Meddy AVEC le verdict, quel qu'il
soit, cellules et dénominateur à l'appui.
