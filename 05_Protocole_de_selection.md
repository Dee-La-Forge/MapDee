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
nom            :
mesure         :  ce que la grandeur capte, en une phrase
définition     :  la formule ou la règle, sans ambiguïté
observable     :  ce qu'il faut avoir pour la calculer
à l'exécution  :  ce que ça change quand on doit poster, retirer ou traverser
É1             :  traverse / traverse dégradée / fabrique la vérité seulement
redite         :  de quoi elle est probablement le doublon
coût           :  temps de calcul par jour de données
```

**La ligne « à l'exécution » est un critère de mort, pas une description.**
Si elle est vide, la fiche ne sert pas au produit — elle propose une analogie,
pas une grandeur. Une seule ligne suffit à rouvrir un concept écarté : qu'on
démontre ce qu'il change quand on doit poster, retirer ou traverser.

**La ligne « É1 » est remplie à la fiche, pas après.** C'est ce qui rend
l'épreuve É1 gratuite : elle est déjà répondue quand le candidat se présente.

**Pas de fiche, pas de test.** Une grandeur définie après coup n'est pas un
candidat, c'est un résultat déguisé.

---

## 2. La nature de la cible est fixée avant, et ne bouge plus

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

**Ce qui est gelé ici, et ce qui ne l'est pas.** Le gel porte sur la **nature**
de la cible — le déplacement du prix — et sur l'**interdiction d'en changer**.
C'est un gel de nature, **pas un gel de formule**.

Reste à écrire : la **définition opératoire**. À partir de quel instant. Sur
quel horizon. Sur quelle grille. Ce qui compte comme déplacement. Tant que ces
quatre points ne sont pas écrits, É3 ne peut pas donner le signe de la relation
à la cible, et É4 ne peut pas produire d'intervalle de confiance sur elle.

> **Le banc ne tourne pas avant que la définition opératoire ne soit écrite et
> commitée par ADR.** Elle se fige au même titre que le reste : une fois
> commitée, elle ne bouge plus qu'en rejugeant tous les candidats déjà passés.

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
  ÉS  banc synthétique         préalable  ←  aucun jour de marché consommé (§8)
  É0  doublon interne          secondes   ←  élimine la majorité du catalogue
  É1  admissible au produit    minutes    ←  papier, aucun calcul
  É2  redit-elle un candidat déjà retenu ?   minutes
  É3  survit-elle à l'échelle  heures
  É4  apporte-t-elle ?         heures     ←  la seule qui coûte vraiment
```

**ÉS est une étape préalable, pas une épreuve du banc.** Elle se franchit
**avant É0** et elle est **obligatoire** : une méthode qui ne l'a pas passée
n'entre pas dans la séquence. Ses règles sont au §8.

### É0 — Est-ce un doublon d'un autre candidat ?

Beaucoup de concepts sont la même idée sous un autre nom. « Potentiel »,
« courbure », « énergie », « paysage énergétique » peuvent être un seul calcul
déguisé quatre fois.

**Mesure** : corrélation de rang (Spearman) entre candidats, deux à deux.

**Règle** : si `|ρ| ≥ 0,90` entre deux candidats, ils sont **le même objet**. On
garde **le moins cher à calculer** ; l'autre est éliminé et inscrit au registre
avec son chiffre.

**Sur quoi ça se calcule.** Une corrélation se calcule sur des données : É0
**touche du marché**. Il tourne sur un **périmètre minimal** — un petit nombre
de jours d'exploration, **jamais la réserve**. Ce périmètre est **déclaré dans
la fiche avant le calcul**, et il ne s'étend pas après avoir vu le résultat.

### É1 — Pourra-t-elle vivre dans le produit ?

Quatre questions, réponse oui/non, aucun calcul.

| question | si NON |
|---|---|
| se calcule-t-elle **sans le L4** — sans `oid`, sans identité, sans cycle de vie ? | elle ne peut servir qu'à **fabriquer la vérité**. Réorientée, pas éliminée. |
| **traverse-t-elle vers Binance** — existe-t-elle des deux côtés ? | éliminée pour le produit. C'est la contrainte du programme, pas un détail de rendu. |
| tourne-t-elle **dans un navigateur**, à la cadence du flux ? | éliminée, sauf si une version simplifiée est démontrée |
| survit-elle à la **dégradation du flux d'affichage** ? | **à mesurer, jamais à supposer.** Le régime exact est dans `FAITS.md` — et il n'est pas le même pour l'écran et pour l'archive. |

**Règle d'élimination, cas par cas** — chaque question tranche seule :

* échec à **« sans L4 »** → **réorientation**, pas élimination. La grandeur
  passe à la fabrique de vérité ; elle sort du banc d'affichage ;
* échec à **« traverse vers Binance »** → **éliminée pour le produit** ;
* échec à **« tourne dans un navigateur »** → **éliminée pour le produit**, sauf
  version simplifiée démontrée ;
* échec à **« survit à la dégradation »** → **n'élimine pas**. Cette question
  n'est pas une porte : elle **exige une mesure**, qui doit être produite avant
  É4.

Une seule des deux questions produit — Binance ou navigateur — suffit à éliminer.
Autant le savoir en une minute qu'après trois semaines.

### É2 — Redit-elle quelque chose qu'on tient déjà ?

C'est l'épreuve que ce projet a payé pour apprendre. Un programme entier de
descripteurs spectraux, élégants et testés équitablement, n'a rien apporté :
deux d'entre eux battaient pourtant, **isolément**, la meilleure grandeur
connue. Ils **ré-encodaient la même chose dans une autre langue**.

**Mesure** : corrélation de rang avec **les candidats déjà retenus**. Le bloc de
référence part vide et grandit au fil du banc — on n'importe aucune conclusion
d'une itération antérieure.

Comme É0, É2 est une corrélation : il **touche du marché**. Même règle — le
**périmètre minimal** déclaré dans la fiche avant le calcul, jamais la réserve.
Le même périmètre sert à É0 et à É2 pour un candidat donné.

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

**Le premier candidat — le témoin trivial.** Le bloc de référence part vide.
Mesurer un apport par-dessus le vide, c'est mesurer une performance isolée —
exactement ce que le §6 interdit. Donc :

> **Le premier candidat est jugé contre un témoin trivial déclaré d'avance,
> jamais contre le vide.**

Le témoin trivial est une grandeur **volontairement pauvre** — par exemple la
**masse brute au palier**. Il est déclaré **avant le premier calcul**, comme un
candidat à part entière : sa **fiche** au §1, sa **ligne au registre**. Il ne
passe pas les épreuves et **il ne peut jamais être « retenu »** : il ne sert que
de **plancher**. Un premier candidat qui n'apporte rien par-dessus la masse
brute n'apporte rien.

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

### La multiplicité — le défaut qui ne se voit dans aucun candidat pris seul

**Défaut identifié le 05/08/2026.** Il ne se corrige pas dans É4, il se corrige
**au niveau de la collection**, et sans lui le banc fabrique des découvertes.

On jugera **plusieurs dizaines de candidats**, sur **cinq résolutions**, sur
**deux ou trois symboles**. À seuil nominal de 5 %, **un test sur vingt ressort
« significatif » en l'absence totale de phénomène — mécaniquement.** Avec une
soixantaine de candidats, l'espérance est de trois faux positifs, et ils seront
présentés comme des découvertes puisque chacun aura son intervalle de confiance
en règle.

**Trois protections, toutes obligatoires :**

1. **Le nombre de candidats est déclaré AVANT** le premier calcul du banc, et
   inscrit au registre. On ne découvre pas à la fin combien de tests ont été
   faits. Tout candidat ajouté après coup **rouvre le compte** et le déclare.
2. **Contrôle du taux de fausses découvertes sur la collection**, pas seulement
   un IC par candidat. Le seuil s'applique à l'ensemble des candidats jugés à
   É4, résolutions et symboles compris.
3. **É0 pris au sérieux**, parce qu'il change le compte : fondre les doublons
   réduit le nombre de tests **réellement indépendants**. Une collection de
   soixante candidats dont quarante sont des synonymes n'est pas soixante tests.

**Ce que ça interdit** : présenter un candidat comme retenu sur son seul IC, sans
dire contre combien d'autres il a été mis en concurrence. Le nombre de
concurrents fait partie du résultat.

---

## 5. Le registre — rien ne se perd

Chaque candidat, retenu ou éliminé, laisse une ligne dans
`journal/registre-des-grandeurs.md` :

```
nom · date · épreuve où il tombe · le CHIFFRE qui l'a fait tomber · qui l'a proposé
```

⚠️ **Ce fichier n'existe pas encore** : il est à créer **au premier candidat
déposé**, et **aucun calcul ne se fait avant** son existence.

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
journée**. Attention à ne pas se raconter d'histoire sur ce coût : **seul É1 est
réellement du papier**. É0 et É2 sont des corrélations, donc des calculs sur
données — ils tournent sur le **périmètre minimal** déclaré d'avance, un petit
nombre de jours d'exploration, **jamais la réserve**. Ce qui est bon marché ici,
c'est le temps de calcul, pas l'absence de données. On en teste sérieusement
**une dizaine**, pas soixante. C'est ce qui rend la reprise complète faisable au lieu
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

**Règle de sortie — deux façons d'échouer ici, pas une.**

* **le bras nul détecte** → méthode **disqualifiée** ;
* **le plancher de détection est au-dessus de l'amplitude que le phénomène peut
  plausiblement avoir** → la méthode est **écartée à ce stade**. Elle **ne
  consomme aucun jour de marché**. Un instrument qui ne peut pas voir ce qu'on
  cherche ne produira que des négatifs ininterprétables.

Dans les deux cas, **le chiffre du plancher est inscrit au registre** — y
compris quand la méthode passe. Sans lui, aucun négatif futur n'est lisible.
L'amplitude plausible du phénomène est déclarée **avant** la mesure du plancher,
jamais après.

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

   **Quel jour.** Il est fixé par la **convention de gel des jours**, et il doit
   être **nommé dans `decisions/ADR-000`** — pas ici. Ce document ne choisit
   aucun jour. **Tant que ce jour n'est pas nommé dans l'ADR, l'observation ne
   démarre pas.**

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
5. **Le banc synthétique (ÉS) n'existe pas encore.** Ni carnet fabriqué, ni
   mécanisme injecté, ni bras nul. C'est une **étape préalable obligatoire**
   (§4, §8) : tant qu'elle n'est pas construite, **aucune méthode n'est admise à
   consommer un jour de marché**, et aucun plancher de détection n'est
   disponible — donc aucun négatif produit d'ici là ne serait interprétable.

---

## 10. Gel

Ce document est figé par commit avant le premier calcul. Toute modification
ultérieure :

* se fait **par ADR** — contexte, alternatives, décision, justification,
  conséquences ;
* **rejuge tous les candidats déjà passés** sous la nouvelle règle ;
* est **datée et commitée** avant le calcul suivant.

**Ce que ce gel gèle exactement.** Il gèle les **règles du banc** et la
**nature** de la cible — le déplacement du prix — avec l'interdiction d'en
changer. C'est un **gel de nature, pas un gel de formule**.

Il ne gèle pas ce qui n'est pas encore écrit. La **définition opératoire** de la
cible — instant de départ, horizon, grille, ce qui compte comme déplacement —
reste à produire. Elle se fige à son tour, **par ADR séparé**, et **le banc ne
tourne pas avant ce commit** : sans elle, ni É3 ni É4 ne sont calculables (§2,
§9 point 2). Un document gelé sur une cible non définie ne serait pas un gel,
seulement une promesse.

Un protocole qu'on ajuste en cours de route n'est pas un protocole.
