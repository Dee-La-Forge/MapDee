# C5 — Les protagonistes

> **Protocole PRÉ-ENREGISTRÉ.** Écrit et commité **avant** le premier calcul.
> Aucune donnée n'a été regardée à l'écriture de ce document. Les seuils
> ci-dessous ne se renégocient pas après avoir vu un résultat : un seuil déplacé
> après coup n'est pas un seuil, c'est une justification.
>
> Chantier du `06_Plan_exploration.md`. Il ne dépend d'aucun verrou.

---

## 1. Le problème

L'objectif du projet a deux moitiés : les **comportements** et les
**protagonistes**. La seconde n'a jamais été travaillée, alors qu'elle est la
moins chère.

Hyperliquid publie **qui** fait quoi : l'archive identifie l'auteur de chaque
changement du carnet — placement, retrait, modification — et les deux
contreparties de chaque transaction. C'est capté depuis le début et **personne
ne l'a jamais lu**.

La question de ce chantier :

> **Le devenir d'une masse posée dépend-il de qui l'a posée — et cette
> dépendance est-elle stable dans le temps ?**

## 2. Ce que ce chantier ne fera pas

Trois bornes, écrites avant de commencer.

* **Il ne nomme aucune intention.** Ni « spoofeur », ni « manipulateur ». On
  mesure des **comportements** et leur stabilité. Qualifier une intention
  dépasse ce que la donnée montre, et c'est en plus une qualification juridique.
* **Il ne traverse pas vers Binance.** Binance ne publie aucune identité. Ce
  chantier sert à **fabriquer la vérité** et à comprendre, pas à afficher — sauf
  à démontrer un observable de substitution, ce qui serait un autre travail. **À
  écrire dans tout rendu.**
* **Il ne produit aucune liste nominative publiée.** Les identifiants restent
  dans le registre interne du chantier. Ce qui sort est une **structure**, pas
  une accusation.

## 3. Le piège, écrit avant de mesurer

C'est l'erreur évidente, et elle est déjà documentée dans les archives du
laboratoire précédent :

> **Annuler beaucoup n'est pas un signe. C'est le métier d'un teneur de marché.**

La quasi-totalité du flux d'ordres est annulée sur toutes les places liquides.
Un discriminant fondé sur le **taux d'annulation** désignera donc les teneurs de
marché, c'est-à-dire l'inverse de ce qu'on cherche.

**Conséquence opératoire** : le taux d'annulation est **mesuré et rapporté**,
mais il est **interdit comme discriminant** de ce chantier. Toute grandeur qui
lui corrèle au-delà de `|ρ| ≥ 0,70` est traitée comme un doublon de lui.

## 4. Les grandeurs de comportement

Calculées **par portefeuille et par jour**, sur le flux d'ordres identifié.
Aucune n'est le taux d'annulation.

| grandeur | ce qu'elle prétend capter |
|---|---|
| durée de vie médiane de ses ordres au repos | patience — un ordre posé pour être exécuté n'a pas le même temps de séjour qu'un ordre posé pour être vu |
| taille de ses ordres **relative à sa propre norme** | l'anomalie interne, pas la taille absolue : un gros acteur pose gros tout le temps |
| asymétrie de côté | pose-t-il des deux côtés, ou d'un seul |
| distance au mid à la pose | où il se place |
| rapport entre ce qu'il **pose** et ce qu'il **exécute** | son engagement effectif |
| cadence de replacement au même palier | se repositionne-t-il, ou tient-il |

**Ce sont des candidats, pas des acquis.** Chacune passe le garde-fou du §6
avant d'entrer dans un classement.

## 5. Le critère de réussite, et il est pré-enregistré

Le chantier réussit si, et seulement si, les **trois** conditions sont
satisfaites :

| | condition | seuil, fixé ici |
|---|---|---|
| **P — persistance** | le classement des portefeuilles, appris sur une période, se retrouve sur une période **disjointe** | Spearman **ρ ≥ 0,50** |
| **B — il bat le hasard** | le groupe élu bat un placebo tiré **à activité appariée** | au-dessus du **95ᵉ centile** de **200 tirages** minimum |
| **N — l'échantillon existe** | portefeuilles présents dans les deux périodes | **≥ 200** |

**Pourquoi 0,50 et pas autre chose.** Ce n'est pas un seuil de significativité,
c'est un seuil d'**utilisabilité** : une table de réputation construite hors
ligne ne sert que si le classement d'hier vaut encore demain. Sous 0,50, il
faudrait la reconstruire en permanence — donc elle ne s'utilise pas en direct,
et le canal n'a pas de valeur produit quelle que soit sa significativité.

**Pourquoi l'appariement du placebo est non négociable.** Un tirage de
portefeuilles au hasard sans contrainte tire surtout des portefeuilles peu
actifs. Comparer les élus à ça mesure **l'activité**, pas **l'identité**. Le
placebo doit être tiré parmi des portefeuilles de **volume et de nombre d'ordres
comparables**.

## 6. Les garde-fous, avant tout classement

* **dégénérescence** : une grandeur qui range plus de **60 %** des portefeuilles
  dans une même classe n'est pas un discriminant. Elle est rapportée et écartée.
* **deux classes** : au moins **5 %** dans la classe minoritaire, au moins
  **200** portefeuilles.
* **doublon du taux d'annulation** : `|ρ| ≥ 0,70` avec lui → écartée (§3).

## 7. L'unité statistique et le contrôle négatif

* **unité de rééchantillonnage : le JOUR.** Jamais le portefeuille, jamais
  l'ordre — un portefeuille actif produit des dizaines de milliers d'ordres
  corrélés entre eux.
* **intervalle de confiance : Student** sur les jours.
* **contrôle négatif : décalage circulaire**, jamais permutation i.i.d. Ici, le
  décalage porte sur l'appariement portefeuille ↔ période : on compare le
  classement d'un portefeuille à celui **d'un autre**, en préservant la structure
  temporelle de chacun.

## 8. Le périmètre, déclaré avant le calcul

| | |
|---|---|
| **jours** | **08 à 16 décembre uniquement** |
| **symboles** | BTC et ETH |
| **interdits** | **17-23** — réserve, ni construction ni lecture · **24-31** — zone d'extension de la réserve, ni construits ni regardés tant que l'écart-type n'est pas connu · **01-07** — jours de certification consommée |

Le périmètre ne s'étend pas après avoir vu un résultat. L'étendre exige un ADR
et le rejugement de ce qui a déjà été mesuré.

**Découpage des périodes** : la persistance se mesure entre deux tranches
**disjointes** de ce périmètre, fixées avant le calcul et non ajustées ensuite.

## 9. Les sorties, et la forme de l'échec

**Sortie attendue** : une note de chantier portant, pour chaque grandeur du §4,
sa distribution, son résultat aux trois garde-fous du §6, et — pour celles qui
survivent — le triplet P / B / N du §5 avec ses intervalles.

**Formes d'échec, toutes publiables :**

| échec | ce qu'il veut dire |
|---|---|
| **aucune grandeur ne passe les garde-fous** | les portefeuilles ne se distinguent pas sur ces axes. Le canal est vide **tel qu'interrogé** — d'autres axes restent possibles, et il faut le dire ainsi. |
| **le classement ne persiste pas (P < 0,50)** | il existe des différences instantanées mais pas d'identité stable. Une table de réputation hors ligne est impossible : le canal n'a pas de valeur produit. |
| **il persiste mais ne bat pas le placebo apparié** | on mesurait l'activité, pas l'identité. **C'est l'échec le plus probable et le plus instructif.** |

**Ce qui n'est pas un échec** : trouver que les portefeuilles à comportement
extrême sont des teneurs de marché. C'est un résultat, et il ferme proprement
une hypothèse.

## 10. Ce qui est interdit dans ce chantier

* déplacer un seuil du §5 ou du §6 après avoir vu un résultat ;
* étendre le périmètre du §8 après avoir vu un résultat ;
* utiliser le taux d'annulation comme discriminant ;
* conclure sans intervalle de confiance ;
* nommer une intention.


---

## Addendum du 05/08/2026 — le nul du §7 portait un mauvais nom (audit de Meddy)

**Aucun classement n'a encore été calculé** : cette correction précède tout
usage du nul — elle ne suit aucun résultat.

Le §7 nommait « décalage circulaire » un réappariement de portefeuilles entre
périodes. **C'est une permutation d'étiquettes** : les portefeuilles n'ont pas
d'ordre naturel, et décaler circulairement une liste arbitraire, c'est la
permuter. La procédure reste la bonne — pour tester la persistance, casser le
lien d'identité est le bon nul — mais la raison du « jamais i.i.d. » (préserver
l'autocorrélation **temporelle**) ne s'applique pas ici : le lien détruit n'en a
pas. Le §7 se lit donc : **nul = permutation d'étiquettes, appariée** — et le
nom « décalage circulaire » ne doit pas être recopié ailleurs sur la foi de ce
protocole.

Et le facteur à contrôler réellement est nommé : **tous les portefeuilles
partagent les mêmes jours** — un facteur de marché commun peut gonfler la
persistance apparente. Le placebo apparié en activité y répond en partie ; la
part restante est **publiée comme réserve** avec le résultat de persistance.
