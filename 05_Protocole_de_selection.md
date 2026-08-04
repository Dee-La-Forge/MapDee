# Le banc — comment une grandeur entre dans MapDee

> **Document de cadrage.** Il fixe les règles **avant** le premier calcul, et il
> est commité avant — sinon son antériorité ne vaut rien.
>
> Il ne porte aucun chiffre hérité. Les leçons des itérations précédentes y
> figurent par leur **mécanisme**, jamais par leur mesure : les mesures ont été
> faites sur un instrument qu'on reconstruit, elles ne valent rien.

---

## 0. À quoi ça sert

On va tester beaucoup d'idées : la pression du carnet, son potentiel, son
entropie, la vitesse à laquelle il se reforme, la probabilité qu'un ordre au
repos meure dans la seconde. `03_EconoPhysique.md` en catalogue des centaines.

**Le risque n'est pas de se tromper. Le risque est de se mentir à soi-même** :
tester, ne rien trouver, changer un peu la règle, retester, et finir par
« trouver » quelque chose qui n'existe pas.

Ce projet l'a fait quatre fois en une nuit — quatre « événements » qui
survenaient dans la quasi-totalité des cas, donc qui ne voulaient rien dire.

Le remède est bête : **écrire les règles avant de jouer**, et les mêmes pour
tout le monde.

---

## 1. Ce qu'est un candidat

Une grandeur calculée depuis le carnet ou le flux d'ordres, dont on pense
qu'elle aide à répondre à la question du projet : **quels mécanismes font bouger
le prix, où il va, et pourquoi il y va.**

Un candidat se déclare **avant d'être calculé**, par une fiche de quatre lignes :

```
nom          :
définition   :  la formule, sans ambiguïté
ce qu'elle   :  en une phrase, quel mécanisme elle prétend capter
  prétend       et pourquoi ce ne serait pas déjà capté par un candidat retenu
coût         :  temps de calcul par jour de données
```

**Pas de fiche, pas de test.** Une grandeur définie après coup n'est pas un
candidat, c'est un résultat déguisé.

---

## 2. La cible est fixée avant, et ne bouge plus

Toutes les grandeurs sont jugées contre **la même cible**.

> **Cible retenue : le déplacement du prix.** Où il va, à partir de l'instant où
> la grandeur devient connaissable.

**Pourquoi celle-là, et pas la fraction exécutée.** La fraction exécutée mesure
ce qui a été *consommé*. Or un leurre réussi n'est **jamais** exécuté — c'est sa
définition. Une cible d'exécution récompense donc le leurre **raté** ou l'ordre
sincère : on apprendrait à reconnaître exactement ce qu'on ne cherche pas. Et
elle partage son terme de volume avec les grandeurs qui la prédisent, ce qui
fabrique de la corrélation mécanique.

La cible retenue est aussi la seule qui réponde à la question posée : *où va le
prix, et pourquoi il y va.*

**Interdit, sans exception** : changer la cible, la métrique ou un seuil après
avoir vu un résultat. Un changement nécessaire se fait **par ADR**, et **tous
les candidats déjà jugés repassent** sous la nouvelle règle.

---

## 3. Deux garde-fous, avant même la première épreuve

Ils s'appliquent à toute grandeur qui définit un **événement** ou une **cible
binaire**. Ils coûtent trois lignes de code et ils ont attrapé les quatre fautes
d'origine, plus deux autres depuis.

* **l'événement doit être rare** — s'il survient dans plus de **60 %** des cas,
  ce n'est pas un événement, c'est l'état normal du marché. On redéfinit la
  condition, pas le modèle ;
* **la cible doit avoir deux classes** — au moins **5 %** dans la classe
  minoritaire et au moins **200** exemples.

Implémentés dans `_recupere/garde/`. Le symptôme qu'ils attrapent est toujours
le même : **une classe à 100 %**.

---

## 4. Le banc : cinq épreuves, de la moins chère à la plus chère

**Une épreuve échouée arrête le candidat.** On ne passe pas à la suivante.

L'ordre n'est pas arbitraire : on élimine avec ce qui coûte des secondes avant
de dépenser des heures.

```
  É0  doublon interne          secondes   ←  élimine la majorité du catalogue
  É1  admissible au produit    minutes    ←  papier, aucun calcul
  É2  redit-elle un candidat déjà retenu ?   minutes
  É3  survit-elle à l'échelle  heures
  É4  apporte-t-elle ?         heures     ←  la seule qui coûte vraiment
```

### É0 — Est-ce un doublon d'un autre candidat ?

Beaucoup de concepts sont la même idée sous un autre nom. « Potentiel »,
« courbure », « énergie », « paysage énergétique » peuvent être un seul calcul
déguisé quatre fois.

**Mesure** : corrélation de rang (Spearman) entre candidats, deux à deux.

**Règle** : si `|ρ| ≥ 0,90` entre deux candidats, ils sont **le même objet**. On
garde **le moins cher à calculer** ; l'autre est éliminé et inscrit au registre
avec son chiffre.

### É1 — Pourra-t-elle vivre dans le produit ?

Quatre questions, réponse oui/non, aucun calcul.

| question | si NON |
|---|---|
| se calcule-t-elle **sans le L4** — sans `oid`, sans identité, sans cycle de vie ? | elle ne peut servir qu'à **fabriquer la vérité**. Réorientée, pas éliminée. |
| **traverse-t-elle vers Binance** — existe-t-elle des deux côtés ? | éliminée pour le produit. C'est la contrainte du programme, pas un détail de rendu. |
| tourne-t-elle **dans un navigateur**, à la cadence du flux ? | éliminée, sauf si une version simplifiée est démontrée |
| survit-elle à la **dégradation du flux d'affichage** ? | **à mesurer, jamais à supposer.** Le régime exact est dans `FAITS.md` — et il n'est pas le même pour l'écran et pour l'archive. |

Une grandeur qui échoue aux quatre ne sera **jamais** affichée. Autant le savoir
en une minute qu'après trois semaines.

### É2 — Redit-elle quelque chose qu'on tient déjà ?

C'est l'épreuve que ce projet a payé pour apprendre. Un programme entier de
descripteurs spectraux, élégants et testés équitablement, n'a rien apporté :
deux d'entre eux battaient pourtant, **isolément**, la meilleure grandeur
connue. Ils **ré-encodaient la même chose dans une autre langue**.

**Mesure** : corrélation de rang avec **les candidats déjà retenus**. Le bloc de
référence part vide et grandit au fil du banc — on n'importe aucune conclusion
d'une itération antérieure.

**Règle** :

* `|ρ| < 0,50` → passe ;
* `0,50 ≤ |ρ| < 0,70` → passe **sous surveillance** : É4 devra montrer un apport
  net ;
* `|ρ| ≥ 0,70` → **doublon présumé**. Pas éliminé, mais il ne survit qu'en
  passant É4 avec un apport significatif. C'est une barre, pas une porte fermée.

### É3 — Survit-elle au changement d'échelle ?

Le point le plus profond du dossier, et le seul qui protège au lieu de proposer
un calcul de plus :

> Un vrai phénomène reste visible quand on change la finesse d'observation. S'il
> disparaît, c'est probablement un artefact de la façon dont on a échantillonné.

**Mesure** : la grandeur calculée aux **cinq résolutions** — 100 ms · 500 ms ·
1 s · 5 s · 20 s.

⚠️ **Cette épreuve exige un rejeu événement par événement.** Elle **ne se dérive
pas** des tables existantes : la plus fine d'entre elles n'atteint pas l'échelle
demandée. Voir §9.

**Règle**, les deux conditions :

1. le **signe** de la relation à la cible est **identique aux cinq échelles** ;
2. la corrélation de rang entre l'échelle la plus fine et chacune des autres est
   `≥ 0,60`.

Une seule échelle qui change de signe → **éliminée**.

### É4 — Apporte-t-elle quelque chose, en plus du reste ?

La seule épreuve coûteuse, et la dernière.

**Ce qu'on mesure** : le gain **par-dessus les candidats déjà retenus**, jamais
la performance de la grandeur toute seule. Une grandeur qui brille seule mais
n'ajoute rien est un doublon, pas une découverte.

**Les quatre conditions, toutes obligatoires :**

| condition | règle |
|---|---|
| **unité de calcul** | le **JOUR**, jamais l'observation. Les fenêtres se recouvrent, et l'ignorer fausse l'incertitude — dans le mauvais sens. |
| **intervalle de confiance** | **Student** sur les jours ; il doit **exclure zéro**. |
| **contrôle négatif** | la grandeur doit sortir de sa bande nulle, tirée par **décalage circulaire**. Jamais par permutation i.i.d. : la permutation détruit l'autocorrélation des fenêtres recouvrantes et déclare significatif ce qui ne l'est pas. |
| **réplication** | **même signe sur deux symboles.** Un effet qui n'apparaît que sur un symbole est un sur-ajustement. |

**Et la conséquence mécanique, obligatoire** : l'apport doit s'exprimer comme un
énoncé **falsifiable sur la trajectoire du prix** — où il va, quand, et sous
quelle condition. Un gain de score qui ne se traduit par aucun énoncé de ce type
n'est pas un gain.

> **Il n'y a pas de traduction économique exigée.** Ni points de base, ni P&L, ni
> gain simulé. Décision du 04/08/2026 : le projet cherche des **mécanismes**, pas
> un outil de trading. Une explication n'a pas à se convertir en profit pour
> valoir.

---

## 5. Le registre — rien ne se perd

Chaque candidat, retenu ou éliminé, laisse une ligne dans
`journal/registre-des-grandeurs.md` :

```
nom · date · épreuve où il tombe · le CHIFFRE qui l'a fait tomber · qui l'a proposé
```

**Aucune élimination sur une opinion.** Chacune porte son chiffre. Si on s'est
trompé, on sait exactement pourquoi on l'avait sorti, et on peut rouvrir — par
un ADR, jamais en silence.

**Le registre est un rapport de mesure** : il ne se réécrit pas. Une élimination
se corrige par un ajout.

### Ce que ça coûte, et pourquoi « on refait tout » est faisable

Le catalogue porte des centaines de noms, mais **beaucoup moins d'idées
distinctes** — le même objet y revient sous plusieurs vocabulaires. C'est É0 qui
les fond, et il coûte des secondes.

L'entonnoir attendu : **É0 à É2 éliminent la grande majorité du catalogue en une
journée**, sans toucher une donnée de marché. On en teste sérieusement **une
dizaine**, pas soixante. C'est ce qui rend la reprise complète faisable au lieu
d'infinie — et c'est la raison pour laquelle l'ordre des épreuves est celui du
coût croissant.

---

## 6. Ce qui est interdit

* changer la cible, la métrique ou un seuil après avoir vu un résultat ;
* conclure sans intervalle de confiance ;
* juger une grandeur sur sa performance isolée plutôt que sur son apport ;
* calculer une grandeur avant d'avoir déposé sa fiche ;
* **construire une mesure avant d'avoir regardé la distribution de ce qu'elle
  mesure** ;
* retirer une grandeur du registre.

---

## 7. Ce qui repasse au banc

**Tout.** Y compris ce qui a déjà été jugé, et **y compris ce qui a été jugé
négatif** — parce qu'un résultat négatif produit par un instrument non audité
n'est pas un résultat.

Deux cas méritent d'être nommés :

**Les descripteurs spectraux.** Ils repassent, sans privilège ni handicap. Et ils
ont un vrai argument : ils avaient été jugés sur une série grossièrement
échantillonnée, alors qu'on disposera du flux événement par événement. Un
spectre calculé sur une photo lente ne dit rien du spectre du flux réel. **Ce
n'est pas la même mesure sur une meilleure donnée : c'est un autre objet.**

**Tout ce qui a fermé une piste.** Les négatifs qui ont écarté une hypothèse
sont exactement ceux qu'il faut refaire en premier, parce qu'ils ont coûté une
question.

---

## 8. Avant le banc : le banc synthétique

Une méthode candidate se juge d'abord sur sa capacité à **retrouver un mécanisme
injecté dans un carnet fabriqué**, avant de toucher la moindre donnée de marché.

C'est le seul étage qui ne consomme **aucun jour de marché** et qui ne peut pas
sur-ajuster, puisque la vérité est construite.

Il rend trois choses qu'aucune mesure sur données réelles ne donne :

* le **rappel à faux positifs fixés** ;
* le **plancher de détection** — l'amplitude minimale d'un mécanisme que la
  méthode sait voir. Sans ce chiffre, **aucun négatif futur n'est
  interprétable** : on ne sait pas distinguer « pas de phénomène » de
  « instrument trop faible » ;
* le comportement dans un **bras nul** — le même carnet sans injection. Une
  méthode qui détecte là est disqualifiée.

**Ce qu'il n'achète pas**, et qui doit figurer dans chaque rapport : un carnet
fabriqué n'a pas la structure de dépendance du vrai. Une méthode qui passe le
banc synthétique n'est pas validée — elle est **admise à consommer des jours de
marché**. Un contrôle négatif qui passe ne prouve que l'absence du défaut qu'il
simule.

---

## 9. Ce qui bloque le banc aujourd'hui

1. **É3 n'est pas exécutable.** Il demande l'échelle la plus fine, qui n'existe
   dans aucune table construite. Il faut un **rejeu événementiel**. Tant qu'il
   n'existe pas, tout candidat s'arrête à É2 — et la réhabilitation des
   descripteurs spectraux avec lui.
   **Portée à retenir** : É3 est une épreuve de candidat, pas une table de
   production. Il lui faut **quelques jours**, pas le mois entier.
2. **La cible n'a pas de définition opératoire.** « Le déplacement du prix » fixe
   la nature ; il reste à écrire à partir de quel instant, sur quel horizon, sur
   quelle grille, et ce qui compte comme déplacement.
3. **Les comportements n'ont pas de définition opératoire.** Annulé, mangé,
   rechargé sont nommés, pas définis. Deux routes, dans cet ordre : la
   **littérature**, puis l'**observation des trajectoires brutes** sur le jour de
   banc d'instrument. Jamais l'inverse — définir après avoir regardé, c'est
   fabriquer une cible dégénérée.

   **Et quand ils seront définis, voici comment on les éprouve** — la règle est
   posée maintenant, avant de connaître les définitions, pour qu'elle ne soit pas
   choisie en fonction d'elles.

   Une typologie se valide sur **deux axes distincts**, jamais sur un seul :

   | | ce qui la définit | quand elle est connue |
   |---|---|---|
   | **population** | ce qu'on observe du mur avant | **ex ante** |
   | **type** | annulé / mangé / rechargé | **ex post**, à la révélation |

   La question testable n'est pas « ces populations sont-elles le même objet » —
   des seuils emboîtés sur une même variable se recouvrent **par construction**
   et ne peuvent pas se réfuter. La question est : **la population ex ante
   prédit-elle le type ex post ?**

   Table de contingence **construite à l'intérieur de chaque strate de taille**,
   et publiée par strate. Écarter la taille comme discriminant ne suffit pas : si
   les populations sont définies par elle et que les types y corrèlent, la table
   reste confondue même sans la nommer.

   **Quatre cases de sortie, toutes comptées et toutes publiées :**

   | case | règle | ce qu'elle teste |
   |---|---|---|
   | **classé** | exactement une condition de type se déclenche | — |
   | **ambigu** | ≥ 2 conditions se déclenchent | **falsifie les définitions** : si la case est grosse, les types ne sont pas exclusifs |
   | **résidu** | aucune condition | c'est là qu'un type manquant se lit — **on ne l'invente pas, on le lit** |
   | **muet** | rien ne se termine dans la fenêtre | type **indéfini**, jamais compté à zéro : les déclarer sincères sans preuve fausserait tout dénominateur |

   Et le garde-fou du §3 s'applique à la table elle-même : **si une cellule
   dépasse 60 %, il n'y a pas de typage, il y a une classe majoritaire.**
4. **On ne sait pas si le bootstrap est utilisable.** L'unité de
   rééchantillonnage suppose que les observations d'une même unité ne se
   recouvrent pas. **La fraction de paires intra-unité n'a jamais été mesurée sur
   données réelles.** C'est elle qui décide si l'intervalle de confiance vaut
   quelque chose — et c'est un préalable à É4, pas un raffinement. Dette de
   méthode héritée : elle survit à la refonte, parce qu'elle ne dépend d'aucun
   instrument particulier.

---

## 10. Gel

Ce document est figé par commit avant le premier calcul. Toute modification
ultérieure :

* se fait **par ADR** — contexte, alternatives, décision, justification,
  conséquences ;
* **rejuge tous les candidats déjà passés** sous la nouvelle règle ;
* est **datée et commitée** avant le calcul suivant.

Un protocole qu'on ajuste en cours de route n'est pas un protocole.
