# ADR-010 — Gel du banc P2a.5 : cible y_post, cadrage par RANG, instrument 15 s

**Date** : 2026-07-30 · **Statut** : accepté · **Décideur** : Meddy (critères posés les 29-30/07),
verdicts rendus par `p2a5_target.py` sur 5 jours × 2 symboles (144 686 ordres, 55 628
paliers-instants, 23 962 épisodes).

## Décision

1. **Cible gelée : `y_post`** (Σ exécuté APRÈS contact / Σ affiché, par palier-instant).
   Sa queue est STABLE sur les 10 cellules symbole×jour : P(y>0) ≈ 9-10 % partout, y compris
   le jour de régime aberrant (05-04). `y_total` reste colonne témoin : sa queue dérive ×1,8
   avec le régime (P(y>0) 26 % → 48 %) — c'est le rempli PRÉ-contact qui respire avec le
   marché, pas l'exécution au contact.
2. **Cadrage gelé : par RANG, intra-jour** — statut de la preuve REQUALIFIÉ le 30/07 soir
   (relecture Meddy + `experiments/rank_check.py`, rapport
   `lab/02-experiments/rank-check-pairwise-20260730.md`). Les Spearman de déciles
   (+0,83..+0,98) sont dix points agrégés : un INDICE, pas une preuve. La mesure forte —
   AUC pairwise par jour sur paires contemporaines décidables, sens des features fixé sur
   05-04 seul, évaluation hors-échantillon sur 8 cellules jour×symbole — rend : `placed`
   6/8 cellules avec IC>0,5 (AUC 0,54-0,65, **directionnellement >0,5 sur 8/8**),
   `age` 6/8, `dist` 5/8. **RÉVISION du 30/07 soir, après correction du bootstrap**
   (le schéma par cluster_pair sous-couvrait — relecture Meddy, IC ×1,51 plus larges
   mesurés) : avec les IC honnêtes (schéma par clusters de base, CONSERVATEUR en limite
   singleton ~×1,7), les cellules IC>0,5 tombent à **`placed` 1/8, `age` 0/8** — MAIS les
   POINTS de `placed` restent **>0,5 sur 8/8 cellules (0,54-0,65), sous les deux jours
   d'orientation** (rapports `rank-check-pairwise-20260730*.md`). **Conclusion honnête
   finale : indice DIRECTIONNEL cohérent, sans certitude par cellule-jour — une feature
   seule sur un seul jour n'a pas la puissance sous un schéma prudent.** L'établissement du
   cadrage par rang appartient donc ENTIÈREMENT au JALON 1 (témoin multivarié, folds LODO
   poolant 4 jours → G bien plus grand → IC utilisables). Le cadrage reste gelé (rien n'est
   mieux étayé, la clause de normalisation l'exige), avec ce niveau de certitude écrit juste.
3. **Instrument gelé : book 15 s (perps10), uniforme.** La porte d'étalonnage du mid
   reconstruit est **REFUSÉE** sur son seuil de population (85,8 % < 90 %) — bien que les
   trois critères de QUALITÉ passent largement (accord y_flee **99,9 %**, Δt_contact p90
   0,85 s, fuite à 0,7 pt). Les seuils étaient pré-enregistrés : ils ne se renégocient pas
   après lecture. Cause principale identifiée et honnête : la chauffe de 20 min sans photos
   ampute le début de journée. Un futur export corrigé pourra RE-TENTER la porte — la
   re-tentative d'un instrument amélioré n'est pas une renégociation de seuil.

## Chiffres du gel (référence)

- Variance : y_post 9,7 % hors de 0, variance 0,044 (y_total : 36,3 %, 0,178).
- Paires décidables (|Δy_total| > 0,1) : **41,7 %** de 1 843 975 paires.
- N effectif : ratio épisodes/bruts 0,43.
- Conditionnelle : hurdle « les deux » majoritaire (7/12), mixte sur les extrêmes.
- Famille de modèles imposée : **hurdle 2 étages + ranker pairwise** (plan P3, approuvé).

## Jalon 1 de P3 — barres PRÉ-ENREGISTRÉES (30/07 soir, AVANT tout entraînement)

Deux barres distinctes, dans cet ordre — arbitrage Meddy : « la vraie barre est le témoin
trivial, pas la meilleure feature seule ; battre une combinaison linéaire de cinq features
corrélées est beaucoup plus dur ; écrire le seuil du loyer avant de lancer. »

1. **Barre de PRÉDICTIBILITÉ (établit le cadrage par rang)** : le TÉMOIN TRIVIAL — régression
   logistique sur les Δfeatures des paires décidables (les 5 features de base) — doit obtenir
   une AUC pairwise avec IC > 0,5 sur **≥ 4/5 folds LODO PURGÉ × les 2 symboles**. C'est LUI
   qui prouve (ou non) le rang multivarié, pas le lambdarank.
2. **Barre de LOYER (le lambdarank gagne-t-il sa complexité ?)** : le ranker n'est CONSERVÉ
   que si ΔAUC(ranker − témoin) a un IC par cluster **excluant 0 sur ≥ 3/5 folds pour chaque
   symbole**. Sinon, LE TÉMOIN DEVIENT LE MODÈLE (plus simple, plus transférable, moins cher)
   et le lambdarank est Supprimé avec sa fiche. Attente honnête écrite d'avance : le gain
   sera probablement FAIBLE — un résultat « témoin retenu » est un succès du programme, pas
   un échec du ranker.

Résultat négatif déjà acquis à verser au registre : `n_orders`/`n_wallets` (multi-participation)
ne portent RIEN seuls (1/8 cellules) — probablement des variantes de `placed`. À traiter en
bloc corrélé au banc de features, jamais célébrés isolément.

## Conséquences

- Le banc de features (P3-S4) juge les candidates sur CE banc, gelé — toute retouche de la
  cible après observation d'un gain de feature rouvrirait le débat théorique par la porte
  de derrière (interdit).
- Les niveaux ABSOLUS de y ne se comparent qu'à instrument égal (leçon xcheck-instrument) ;
  toute comparaison inter-source passe par le rang ou un ré-étalonnage explicite.
- Révision possible de l'instrument (mid reconstruit) UNIQUEMENT via une nouvelle porte
  complète, mêmes seuils.
