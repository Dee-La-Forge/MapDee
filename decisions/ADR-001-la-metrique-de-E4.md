# ADR-001 — Ce qu'É4 mesure

**Date** : 2026-08-05 · **Statut** : **PROPOSÉ** — à trancher par Meddy
**Écrit avant** tout calcul de banc. Aucun candidat n'a été jugé à cette heure.

---

## Contexte

`05_Protocole_de_selection.md` fait d'É4 l'épreuve terminale du banc. Il dit ce
qu'elle mesure :

> « le **gain par-dessus les candidats déjà retenus**, jamais la performance de
> la grandeur toute seule »

**Et il ne nomme jamais la quantité.** Un gain de quoi ?

Les deux réponses évidentes sont **explicitement interdites** :

* **l'AUC** — `00` §4 : *« Il n'est ni l'AUC, ni un gain économique »* ;
* **toute grandeur économique** — points de base, P&L, gain simulé : désavoués
  par l'arbitrage du 04/08.

Il ne reste rien. Trouvé par audit adversarial le 05/08/2026, et **ce trou
n'était dans aucune liste de blocages**.

**Sa portée est maximale.** Sans métrique d'É4 : É4 n'est pas calculable → le
bloc de référence d'É2 ne se remplit jamais, puisqu'un candidat n'y entre
qu'après É4 → É2 est inerte → **rien ne peut être retenu**, et le harnais que
`06` déclare primordial n'a pas de sommet.

## Deux contraintes qui éliminent la plupart des candidates

**1. Aucun entraînement avant la porte.** `00` §6 : le ML se branche après. Une
métrique définie comme « l'amélioration d'un modèle ajusté » est donc exclue —
elle exigerait d'entraîner pour juger, ce que la séquence interdit.

**2. La cible est le déplacement du prix**, une grandeur **continue et signée**.
Sa définition opératoire n'est pas encore écrite (c'est C3) — mais sa **nature**
est gelée, et c'est elle qui contraint la métrique.

## Alternatives

| | pourquoi écartée / retenue |
|---|---|
| **AUC ou aire sous la courbe** | interdite. Et elle exige de binariser une cible continue, ce qui jette de l'information et rouvre la porte aux cibles dégénérées. |
| **amélioration d'un modèle ajusté** (réduction d'erreur, R² incrémental) | exclue par la contrainte 1 : il faudrait entraîner pour juger. |
| **traduction économique** | désavouée le 04/08. |
| **corrélation de rang PARTIELLE** | **retenue** — voir ci-dessous. |

## Décision

> **É4 mesure la corrélation de rang PARTIELLE entre le candidat et le
> déplacement du prix, en contrôlant pour les candidats déjà retenus.**

C'est la version *partielle* de ce que font déjà É0 et É2. Le banc devient
cohérent d'un bout à l'autre : la même statistique, appliquée à trois questions
différentes.

| épreuve | ce qu'elle corrèle |
|---|---|
| **É0** | candidat ↔ candidat → doublons |
| **É2** | candidat ↔ bloc retenu → redite |
| **É4** | candidat ↔ **cible**, *en contrôlant pour le bloc retenu* → **apport** |

### Pourquoi celle-là

* **elle n'entraîne rien** — c'est une statistique de rang, pas un modèle ajusté ;
* **« par-dessus le bloc retenu » est dans sa définition**, pas dans un
  protocole d'ablation qu'il faudrait inventer ;
* **elle est de rang**, donc sans hypothèse de distribution — cohérent avec É0
  et É2, et robuste aux queues lourdes que ce carnet porte partout ;
* **son SIGNE est l'énoncé falsifiable** que `00` §4 exige : il dit de quel côté
  le prix se déplace quand le candidat est élevé. C'est ce qui distingue un
  mécanisme d'un score.

### Les cinq paramètres, fixés ici et non renégociables après

| | valeur | pourquoi |
|---|---|---|
| **estimateur** | Spearman partiel, contrôlé sur les candidats retenus | même statistique qu'É0 et É2 |
| **unité de calcul** | **le JOUR** — un coefficient par jour | les fenêtres se recouvrent ; l'unité observation fausse l'incertitude |
| **intervalle** | **Student sur les jours, bilatéral, niveau 95 %** | le niveau manquait à `05` ; il est écrit ici |
| **seuil** | l'IC doit **exclure zéro** | pas de plancher d'amplitude : c'est É2 qui écarte les redites, pas une magnitude arbitraire |
| **collection** | **contrôle du taux de fausses découvertes à 10 %**, procédure de Benjamini-Hochberg, sur l'ensemble des candidats jugés à É4 — résolutions et symboles compris | à 5 % nominal et 29 candidats, les faux positifs sont mécaniques |

**Pourquoi 10 % et pas 5 % sur la collection** : on est en exploration. Un faux
positif coûte une mesure de plus ; un faux négatif ferme une piste, et ce projet
en a déjà fermé à tort. La barre stricte est la **certification sur la réserve**,
pas le banc.

### Le premier candidat

Le bloc de contrôle est vide. La corrélation partielle **dégénère alors en
Spearman simple** — ce qui est exactement le cas prévu par `05` : le premier
candidat se juge contre un **témoin trivial déclaré d'avance**, jamais contre le
vide. Le témoin entre donc dans le bloc de contrôle dès le départ.

## Ce que cette décision NE tranche pas

* **la définition opératoire de la cible** — à partir de quel instant, sur quel
  horizon, sur quelle grille, ce qui compte comme déplacement. C'est C3, et É4
  reste incalculable tant qu'elle n'est pas écrite et commitée.
* **le traitement des ex æquo** dans le calcul de rang.
* **la conflation méthode / grandeur** — ÉS juge des méthodes, É0-É4 des
  grandeurs, et le harnais boucle sur des fiches. À trancher séparément.

## Conséquences

* **É4 devient calculable et automatisable** dès que C3 est gelé. C9 a un sommet.
* **Le banc devient homogène** : une seule statistique, trois questions. Ça
  réduit d'autant les décisions de conception du harnais.
* **`05` doit être mis à jour** : la métrique nommée, le niveau de confiance
  écrit, la procédure de multiplicité nommée. Trois trous refermés d'un coup —
  ce sont les blocages **B1**, **B8** et **B9** de `ETAT.md`.
* **Une limite à porter dans tout rapport** : une corrélation partielle mesure
  une association, pas une causalité. Le signe donne un énoncé falsifiable sur la
  trajectoire ; il ne dit pas que le candidat *fait* bouger le prix. La
  renormalisation et la réplication renforcent la lecture ; elles ne la
  transforment pas en preuve causale.

## Ce dont je ne suis pas sûr, et qui est écrit ici pour ne pas être pris pour acquis

1. **Que la corrélation partielle reste stable quand le bloc de contrôle
   grandit.** Contrôler pour vingt candidats retenus n'est pas contrôler pour
   deux, et rien ne dit que l'estimateur tienne. **À mesurer sur le banc
   synthétique avant d'y soumettre un vrai candidat.**
2. **Que 10 % soit le bon niveau de fausses découvertes.** C'est un arbitrage
   entre rater et fabriquer, pas un résultat.
3. **Que « exclure zéro » suffise sans plancher d'amplitude.** Un effet minuscule
   mais constant passerait. L'argument est qu'É2 l'écartera comme redite — **il
   n'est pas démontré.**
