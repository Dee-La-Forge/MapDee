# ADR-012 — Seuil PRÉ-ENREGISTRÉ du transfert HL→Binance (porte S6)

**Date** : 2026-07-31 · **Statut** : ACCEPTÉ (validé par Meddy le 31/07 — seuils figés avant tout chiffre) · **Contexte** : plan P3 approuvé, S6 ; le transfert est la raison d'être du
programme (P4 : le nœud HL ne se monte que s'il tient).

## Le critère — deux barres, TOUTES DEUX requises, sur les DEUX symboles

Modèle entraîné sur HL (features L2 communes uniquement), évalué sur l'archive Binance du
recorder sandbox (label MOYEN : retrait mesuré à 100 ms), populations appariées par
quantiles (f_dist, f_mult, side, heure UTC) :

1. **Barre absolue** : AUC pairwise Binance ≥ **0,55** avec **IC excluant 0,5**
   (bootstrap par clusters de base, schéma corrigé du 30/07).
2. **Barre de rétention** : edge Binance ≥ **50 %** de l'edge HL
   (edge = AUC − 0,5, mesuré sur les populations appariées, même modèle, même bootstrap).

La barre absolue protège quand l'edge HL est petit ; la rétention protège quand il est
grand (0,65 HL → 0,55 Binance passerait l'absolue en n'ayant gardé qu'un tiers du signal —
échec, à raison : on transférerait un artefact résiduel, pas la structure).

## Clauses héritées (sans elles le critère est attaquable)

- **Métriques de RANG uniquement** — la calibration ne transfère pas (mesuré dès P0 :
  BTC ECE 0,118 en domaine). Aucune lecture en probabilité.
- **Les deux symboles** doivent passer les deux barres — règle anti-artefact BTC-ETH.
- **Cas dégradé pré-écrit** : < 60 clusters Binance dans une cellule → verdict
  « PUISSANCE INSUFFISANTE », relance UNIQUE quand le recorder a ≥ 7 jours d'archive
  (il accumule seul — la relance ne coûte que de l'attente), pas de troisième passage.
- **Prérequis (S5-S6, plan)** : la GLU doit avoir rendu le label moyen « bruité non
  différentiel » (ou biais caractérisé corrigeable), et le rang du proxy commun
  (tradé/(tradé+retiré)) doit suivre celui de y_post fort sur HL (Spearman, IC par
  cluster) — sinon le Δ de rang Binance ne se lit pas.

## Faiblesse assumée, écrite d'avance

**Venue et époque sont CONFONDUES** (HL = mai 2026, Binance = fin juillet 2026). Un échec
ne dira pas lequel des deux a tué le transfert. Le désenchevêtrement exigerait une fenêtre
L4 simultanée à l'archive recorder — hors périmètre P3, candidat naturel si le nœud HL
se monte (P4).

## Ce qu'un GO déclenche / ce qu'un NO-GO clôt

- **GO** : la porte P4 (nœud HL non-validant) s'ouvre à l'arbitrage ; P5 (pictos carnet)
  devient plausible. Le modèle de production est celui du jalon 1 (cas A ou B).
- **NO-GO net** (barres ratées avec puissance suffisante) : l'hypothèse de transfert
  direct L2 est morte sur ces features ; retour arbitrage (autres features communes,
  autre cible, ou attente du désenchevêtrement venue/époque). Le nœud HL ne se monte pas.
