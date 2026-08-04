# Protocole de sélection d'une grandeur

> **Document pré-enregistré.** Il est écrit **avant** le premier calcul, et
> **commité avant** — sinon son antériorité ne vaut rien.
>
> Statut : PROPOSÉ · à geler par commit avant toute mesure
> Annexe de `00_Prompt_MapDee.md` §10.

---

## 0. À quoi ça sert, en clair

On va tester beaucoup d'idées : la pression du carnet, son « énergie », le son
du flux d'ordres, la vitesse à laquelle il se reforme, et une centaine d'autres.

Le risque n'est pas de se tromper. **Le risque est de se mentir à soi-même** :
tester, ne rien trouver, changer un peu la règle, retester, et finir par
« trouver » quelque chose qui n'existe pas.

Ce projet l'a fait **quatre fois en une nuit** — quatre « événements » qui
survenaient dans 85 à 100 % des cas, donc qui ne voulaient rien dire.

Le remède est bête : **écrire les règles avant de jouer**, et les mêmes pour
tout le monde.

---

## 1. Ce qu'est un candidat

Une **grandeur** calculée à partir du carnet ou du flux d'ordres, dont on pense
qu'elle aide à répondre à la question du projet :

> pourquoi le prix choisit-il un mur plutôt que l'autre, et pourquoi un mur
> disparaît-il ?

Un candidat doit être déclaré **avant d'être calculé**, par une fiche de quatre
lignes :

```
nom          :
définition   :  la formule, sans ambiguïté
ce qu'elle   :  en une phrase, ce qu'elle est censée capter
  prétend       et pourquoi ce ne serait pas déjà capté
coût          :  temps de calcul par jour de données
```

Pas de fiche, pas de test. Une grandeur définie après coup n'est pas un candidat,
c'est un résultat déguisé.

---

## 2. La cible est fixée AVANT, et ne bouge plus

Toutes les grandeurs sont jugées contre **la même cible**, décidée et écrite
avant le premier calcul.

**Cible retenue** : la **fraction du mur réellement exécutée** quand le prix
vient au contact.

Pourquoi celle-là : c'est une grandeur **économique** — elle dit combien coûte
de traverser — et c'est la seule que le projet précédent ait vue survivre à ses
propres contrôles. Le critère final du projet n'est pas l'AUC, c'est le coût
d'exécution.

**Interdit, sans exception** : changer la cible, la métrique ou un seuil après
avoir vu un résultat. Si un changement est nécessaire, il se fait par **ADR**,
et **tous les candidats déjà jugés repassent** sous la nouvelle règle.

---

## 3. Le banc : les mêmes épreuves pour tous

Cinq épreuves, dans cet ordre. **Une épreuve échouée arrête le candidat** — on
ne passe pas à la suivante.

L'ordre n'est pas arbitraire : les épreuves sont classées **de la moins chère à
la plus chère**. On élimine avec ce qui coûte des secondes avant de dépenser des
heures.

```
  É0  doublon interne        secondes   ←  élimine la majorité du catalogue
  É1  admissible à l'écran   minutes    ←  papier, aucun calcul
  É2  déjà connu ?           minutes
  É3  survit à l'échelle     heures
  É4  apporte-t-il ?         heures     ←  la seule qui coûte vraiment
```

---

### É0 — Est-ce un doublon d'un autre candidat ?

Beaucoup de concepts sont la même idée sous un autre nom. « Potentiel »,
« courbure », « énergie », « paysage énergétique » sont un seul calcul déguisé
quatre fois.

**Mesure** : corrélation de rang (Spearman) entre les candidats, deux à deux,
sur 3 jours.

**Règle** : si |ρ| ≥ **0,90** entre deux candidats, ils sont **le même objet**.
On garde **le moins cher à calculer** ; l'autre est éliminé et inscrit au
registre avec le chiffre.

---

### É1 — Pourra-t-elle s'afficher dans G-ON ?

Trois questions, réponse oui/non, aucune mesure nécessaire.

| question | si NON |
|---|---|
| se calcule-t-elle **sans le L4** — sans identité d'ordre, sans `oid`, sans cycle de vie ? | elle ne peut servir qu'à **fabriquer la vérité**, jamais à afficher. Réorientée, pas éliminée. |
| tourne-t-elle **dans un navigateur**, à la cadence du flux ? | éliminée pour le produit, sauf si une version simplifiée est démontrée |
| survit-elle à la **dégradation du flux public** — une photo toutes les 2,5 s, filtre sur la médiane, 500 paliers max ? | **à mesurer, jamais à supposer** |

Une grandeur qui échoue aux trois ne sera **jamais affichée**. Autant le savoir
en une minute qu'après trois semaines de travail.

---

### É2 — Dit-elle autre chose que ce qu'on sait déjà ?

C'est l'épreuve que ce projet a payé pour apprendre.

Le programme « sonologie » proposait des descripteurs élégants du spectre du
carnet. Testés honnêtement, ils ont apporté **+0,007 · +0,007 · +0,002 ·
+0,000** — rien. Et deux d'entre eux battaient pourtant, **tout seuls**, la
meilleure grandeur connue.

La raison : ils **redisaient la persistance dans une autre langue**.

Or on sait déjà que **la persistance porte le signal** et que **la taille ne
prédit rien**. Toute grandeur qui mesure « à quel point la liquidité est
concentrée et dure dans le temps » est suspecte de redite.

**Mesure** : corrélation de rang avec le bloc de référence — persistance, âge,
taux d'occupation, taille.

**Règle** :

* |ρ| < 0,50 → passe ;
* 0,50 ≤ |ρ| < 0,70 → passe **sous surveillance** : l'épreuve É4 devra montrer
  un apport net ;
* |ρ| ≥ **0,70** → **doublon présumé**. Le candidat n'est pas éliminé, mais il
  ne peut survivre qu'en passant É4 avec un apport significatif. C'est une
  barre, pas une porte fermée.

---

### É3 — Survit-elle au changement d'échelle ?

Le point le plus profond du dossier, et le seul qui protège au lieu de proposer
un calcul de plus :

> Un vrai phénomène doit rester visible quand on change la finesse
> d'observation. S'il disparaît, c'est probablement un artefact de la façon dont
> on a échantillonné.

Ce projet s'est fait avoir **quatre fois** faute d'appliquer ça.

**Mesure** : calculer la grandeur aux **cinq résolutions** — 100 ms, 500 ms,
1 s, 5 s, 20 s. Le carnet profond permet de le faire **sans rejouer l'archive
cinq fois** : les tables grossières se dérivent exactement des fines.

**Règle**, les deux conditions :

1. le **signe** de la relation à la cible est **identique aux cinq échelles** ;
2. la corrélation de rang entre l'échelle 100 ms et chacune des autres est
   ≥ **0,60**.

Une seule échelle qui change de signe → **éliminée**.

---

### É4 — Apporte-t-elle quelque chose, en plus du reste ?

La seule épreuve coûteuse, et la dernière.

**Ce qu'on mesure** : le gain **par-dessus** le bloc déjà connu (persistance,
âge, occupation, taille) — jamais la performance de la grandeur toute seule.
Une grandeur qui brille seule mais n'ajoute rien est un doublon, pas une
découverte.

**Les quatre conditions, toutes obligatoires :**

| condition | seuil |
|---|---|
| **unité de calcul** | le **jour** — jamais l'observation. Les fenêtres se recouvrent, et l'ignorer fausse l'incertitude d'un facteur 5,5 |
| **intervalle de confiance** | Student sur les jours ; il doit **exclure zéro** |
| **contrôle négatif** | la grandeur doit sortir de sa bande nulle, tirée par **décalage circulaire** — jamais par tirage au hasard, qui se trompe 19 fois sur 48 |
| **réplication** | **même signe sur BTC et sur ETH**. Un effet qui n'apparaît que sur un symbole est un sur-ajustement |

**Et la traduction économique**, obligatoire : l'apport doit s'exprimer en
fraction exécutée, en coût de traversée ou en probabilité d'exécution. Un gain
d'AUC qui ne se traduit en rien n'est pas un gain.

---

## 4. Deux garde-fous, avant même É0

Ils s'appliquent à toute grandeur qui définit un **événement** ou une **cible
binaire**. Ils ont attrapé six fautes et coûtent trois lignes de code.

* **l'événement doit être rare** : s'il survient dans plus de 60 % des cas, ce
  n'est pas un événement, c'est l'état normal du marché. Redéfinir la condition,
  pas le modèle ;
* **la cible doit avoir deux classes** : au moins 5 % dans la classe minoritaire
  et au moins 200 exemples.

Les quatre fautes d'origine : 100 %, 99,28 %, 100 %, 85 %.

---

## 5. Ce qui est interdit

* changer la cible, la métrique ou un seuil après avoir vu un résultat ;
* conclure sans intervalle de confiance ;
* juger une grandeur sur sa performance isolée plutôt que sur son apport ;
* calculer une grandeur avant d'avoir déposé sa fiche ;
* **retirer une grandeur du registre.** Une élimination se corrige par un ajout,
  jamais par un effacement.

---

## 6. Le registre — rien ne se perd

Chaque candidat, retenu ou éliminé, laisse une ligne dans
`journal/registre-des-grandeurs.md` :

```
nom · date · épreuve où il tombe · le CHIFFRE qui l'a fait tomber · qui l'a proposé
```

**Aucune élimination sur une opinion.** Chacune porte son chiffre. Si on s'est
trompé, on sait exactement pourquoi on l'avait sorti, et on peut rouvrir — par
un ADR, jamais en silence.

---

## 7. Ce qui repasse au banc

**Tout.** Y compris ce qui a déjà été jugé, et y compris ce qui a été jugé
négatif — parce qu'un résultat négatif produit par un instrument non audité
n'est pas un résultat.

Trois cas méritent d'être nommés :

**La sonologie.** Elle repasse, sans privilège ni handicap. Et elle a un vrai
argument : elle avait été jugée sur une série **échantillonnée toutes les
10 secondes**. On dispose maintenant du flux **événement par événement** —
deux ordres de grandeur d'écart. Un spectre calculé sur une photo toutes les
10 s ne dit rien du spectre du flux réel. **Ce n'est pas la même mesure sur une
meilleure donnée : c'est un autre objet.**

**Le backtest économique.** Il n'a jamais été audité et il tournait sur un rejeu
dont on sait qu'il divergeait de la production. Le résultat directionnel **et**
le rapport 5,1× en sortent tous les deux.

**Le 98,5 %.** Le constat qui a tué le transfert Hyperliquid → Binance. Jamais
audité, et un audit voisin a montré que l'instrument de datation était
**117 fois trop grossier** et écartait **58,6 % des ordres** pour être morts
trop vite — une sélection directe sur ce qu'on étudiait.

---

## 8. Le coût, pour savoir où on met les pieds

| étape | coût |
|---|---|
| déposer une fiche | 10 minutes |
| É0 + É1 + É2 sur tout un catalogue | **une journée**, tout compris |
| É3 sur un survivant | 2 à 3 heures |
| É4 sur un survivant | une demi-journée |

Sur ~300 noms de concepts, il reste en réalité **une soixantaine d'idées
distinctes**. Les épreuves É0 à É2 en éliminent la grande majorité en une
journée. **On teste sérieusement une dizaine de survivants, pas soixante.**

C'est ce qui rend « on refait tout » faisable au lieu d'infini.

---

## 9. Gel

Ce document est figé par commit avant le premier calcul. Toute modification
ultérieure :

* se fait par **ADR** — contexte, alternatives, décision, justification,
  conséquences ;
* **rejuge tous les candidats déjà passés** sous la nouvelle règle ;
* est **datée et commitée** avant le calcul suivant.

Un protocole qu'on ajuste en cours de route n'est pas un protocole.
