# Audit de Meddy — constats ouverts au 05/08/2026

> **Rapport.** Texte intégral, verbatim, de l'audit rendu par Meddy le
> 05/08/2026 — déplacé ici depuis `ADR-001`, où il avait été collé. Un rapport
> ne se réécrit pas.
>
> **État d'intégration** : les constats **I** et **III** sont intégrés — commit
> `5aa3ef7` (douze correctifs) et `ADR-002` pour I.1. Les corrections **II.1,
> II.3, II.4** sont appliquées au corps d'`ADR-001` ; **II.2** est traité dans
> `03` (fiches B1/D1/D2). Plusieurs constats sont donc **résolus depuis** : ce
> document est la trace de l'audit, pas l'état courant — l'état courant est
> `ETAT.md`.

---

# Audit MapDee — constats ouverts au 05/08/2026

Méthode : lecture des documents de la racine uniquement (`00`, `ETAT`, `01`,
`03`, `04`, `05`, `06`, `FAITS`, `decisions/`, `chantiers/`, `journal/`).
`_recupere/` n'a pas été ouvert. Chaque constat est vérifiable en ouvrant le
fichier cité — aucun ne dépend d'une donnée mesurée.

---

## I. CE QUI N'EST DANS AUCUNE LISTE DE BLOCAGES

### I.1 — C5 est déclaré lancé, et il viole `06` §10

`06` §10 : « aucun **jour d'exploration ouvert** avant que C3 ne soit gelé et
commité ». `06` §11 : « **C5 est lancé** ». `chantiers/C5` §8 : périmètre
= **08-16 décembre**. `ADR-000` Conséquences : les jours d'exploration sont
**01-16 et 24-31**.

Donc C5 ouvre neuf jours d'exploration alors que C3 n'est pas gelé. Le même
document déclare C5 « sans verrou » (§9, §11) et interdit ce qu'il fait (§10).

Aggravé par la révision du 05/08 : `ETAT` B2 tranche désormais « **la bonne
réponse est "rien"** : É0 et É2 touchent du marché, et aucun jour d'exploration
ne s'ouvre avant C3 gelé ». Cette phrase interdit explicitement ce que C5 fait,
dans le document de passation lui-même.

**À trancher par ADR** : soit `06` §10 est trop large et vise en réalité
« ouvrir un jour **contre la cible** » — auquel cas C5, É0 et É2 sont légitimes
puisqu'aucun ne référence la cible — soit C5 s'arrête. Les deux règles ne
peuvent pas coexister.

### I.2 — La partition de décembre diffère dans les trois documents qui la portent

| jours | `ADR-000` Contexte + Conséquences | `ADR-000` décision (b) | `chantiers/C5` §8 |
|---|---|---|---|
| 01-07 | exploration, construits | exclus de σ, sans raison | **interdits — « certification consommée »** |
| 08    | exploration | exclu de σ | permis |
| 09-16 | exploration | σ | permis |
| 17-23 | réserve | jamais | interdits |
| 24-31 | exploration / extension | σ | interdits |

Trois frontières différentes dans la même zone (07/08, 08/09), aucune justifiée.
Et **« jours de certification consommée » n'apparaît dans aucun autre document
du dépôt**.

`00` §10 signale déjà le trou : « la convention de gel des jours est portée par
`decisions/ADR-000` — **et elle y est incomplète** […] Il ne dit rien de deux
autres statuts que **le code applique pourtant** […] À compléter avant le
premier lot. »

C5 ne s'est pas contenté d'hériter du trou : **il s'y pré-enregistre**. Or toute
l'autorité d'un protocole pré-enregistré tient à ce qu'il soit opposable. Un
périmètre appuyé sur un statut qu'aucun ADR ne porte n'est opposable à rien.

*(L'addendum du 05/08 à `ADR-000` transcrit la convention ; vérifier qu'il
couvre bien les quatre statuts et qu'il rend `C5` §8 opposable.)*

### I.3 — Circularité du périmètre de σ : `ADR-000` (b) contre `06` §9

`ADR-000` (b) : σ mesuré « sur les seuls jours d'exploration — **09-16 et
24-31** ».
`06` §9 : les jours de fin de mois « ne sont **ni construits ni regardés** avant
que l'écart-type ne soit connu ».

Incompatibles : (b) veut mesurer σ sur 24-31, `06` interdit d'y toucher tant que
σ n'est pas connu. Et `06` est un cadrage, pas un ADR — `01` §4 fait primer
l'ADR. **Le document qui engage porte la version cassée.**

### I.4 — `ADR-000` se contredit sur son propre périmètre, et ça coûte de la puissance

Contexte et Conséquences : exploration = **01-16** et 24-31 (24 jours,
48 constructions). Décision (b) : σ sur **09-16** et 24-31. `01-08` sont
construits mais exclus de σ, sans raison écrite. La frontière du 09 vient de
l'`ADR-020` de l'archive, que `00` §7 déclare **sans autorité**.

Combiné à I.3, σ se mesurerait sur **8 jours**. Calcul χ² (même méthode que
l'ADR — elle reproduit exactement son `[0,77 ; 5,05]` à partir de σ̂ = 1,354) :

| jours estimant σ | IC 95 % de σ | rapport haut/bas |
|---|---|---|
| 4 (le chiffre désavoué) | `[0,57 ; 3,73] × σ̂` | 6,6 |
| **8** (09-16 seuls) | `[0,66 ; 2,04] × σ̂` | **3,1** |
| **16** (01-16) | `[0,74 ; 1,55] × σ̂` | **2,1** |
| 24 | `[0,78 ; 1,40] × σ̂` | 1,8 |

L'ADR rejette à raison un σ à 4 jours parce qu'il dimensionne « à un facteur 6,5
près ». Sa propre clause conduit à 3,1. **Correctif proposé, robuste et sans
décision produit** : « σ se mesure sur les jours d'exploration **effectivement
construits, hors zone d'extension** » — formulation qui casse la circularité,
récupère les 16 jours, et ne suppose rien de ce que le code refuse d'écrire.

### I.5 — Le préflight n'est pas un raffinement : le seul lancement le prouve

`journal/construction/20260805-010706-decembre.log`, ligne 4 :
`git : bfa28c4  sale=True`

`06` C9, pièce 4 : le préflight « refuse de démarrer si l'arbre git est sale […]
**Il ne prévient pas, il bloque** ». La seule construction lancée l'a été
exactement dans la condition que le préflight existe pour refuser. Le lanceur l'a
**consigné**, il ne l'a pas **arrêté** — démonstration expérimentale de `ETAT` §6
(« une règle écrite en prose n'arrête personne »). Le préflight passe en tête de
C9, pas en quatrième pièce.

### I.6 — Le contrôle négatif de C5 est une permutation d'étiquettes appelée décalage circulaire

`chantiers/C5` §7 : « contrôle négatif : **décalage circulaire**, jamais
permutation i.i.d. Ici, le décalage porte sur l'appariement portefeuille ↔
période : on compare le classement d'un portefeuille à celui d'un autre. »

Réapparier des portefeuilles est une **permutation d'étiquettes**. Les
portefeuilles n'ont pas d'ordre naturel ; décaler circulairement une liste
arbitraire, c'est la permuter. Et la justification invoquée ne s'applique pas :
si `00` §4, `01` §6 et `05` É4 imposent le décalage, c'est pour **préserver
l'autocorrélation temporelle** — or le lien détruit ici (l'identité entre les
deux périodes) n'en a pas.

**La procédure est probablement bonne** : pour tester la persistance, casser le
lien d'identité est le bon nul. Ce sont le **nom et la raison** qui sont faux, et
c'est le danger : une session ultérieure lira « décalage circulaire », croira la
question temporelle traitée, et recopiera le motif là où elle ne l'est pas.

Et le facteur qu'il faut réellement contrôler n'est pas nommé : **tous les
portefeuilles partagent les mêmes jours**, donc un facteur de marché commun.
C'est lui qui peut gonfler P, pas l'autocorrélation intra-portefeuille.

### I.7 — Le témoin trivial répare É4, pas É2

`05` É4 introduit le **témoin trivial** (masse brute au palier) contre lequel le
premier candidat est jugé. Excellent, et ça règle É4. Mais `05` précise qu'il
« **ne peut jamais être "retenu"** » — il n'entre donc pas dans le bloc de
référence d'É2, qui reste vide.

Le correctif a été appliqué à **une seule des deux épreuves** qui souffraient du
même défaut. `ETAT` B6 (« É2 inerte ») ne tombera donc pas entièrement avec B1 :
même É4 calculable, É2 reste inerte tant qu'aucun candidat n'a été retenu.
**Correctif** : faire entrer le témoin trivial dans le bloc de référence d'É2
comme il entre dans celui d'É4 — un candidat corrélé à `|ρ| ≥ 0,70` avec la masse
brute EST une redite de présence, et c'est exactement ce qu'É2 doit attraper.

### I.8 — `03` décrit É2 avec la définition d'É4

`03`, « Rappel des deux barres » : « **É2** : gain **incrémental** par-dessus le
bloc de persistance, jamais la performance isolée. »

Or `05` É2 est une **corrélation de rang** à trois paliers (0,50 / 0,70). Le
« gain incrémental par-dessus le bloc retenu », c'est **É4**. Et « le bloc de
persistance » ne figure nulle part dans `05`.

Le registre des candidats et le banc qui les juge ne décrivent pas la même
épreuve, dans le paragraphe où `03` prétend rappeler les barres. Un rédacteur de
fiche qui suit `03` remplit sa ligne `redite` contre une épreuve qui n'existe pas.

### I.9 — La renormalisation exige 100 ms ; la place ne produit rien sous ~87 ms

`00` §4 et `01` §5 : même signe à **100 ms · 500 ms · 1 s · 5 s · 20 s**, plus
une corrélation de rang entre **l'échelle la plus fine** et chacune des autres.

`FAITS` §2, mesuré : **~10,2 blocs/s, `dt` médian 87 ms, interdécile 54-155 ms**,
conclusion « **rien à acquérir sous 87 ms** ».

Le barreau à 100 ms tombe **dans l'interdécile de la cadence de blocs** : un bin
de 100 ms contient environ un bloc, parfois zéro. À cette résolution, une part de
ce qui varie est la **discrétisation de la place**, pas le phénomène. Et c'est ce
barreau-là qui sert de **référence** à la corrélation de rang d'É3.

Aucun document ne justifie ce 100 ms contre le 87 ms de `FAITS`. À argumenter
avant gel — É3 est une épreuve à seuil qu'on n'aura plus le droit de retoucher.

### I.10 — `06` §4 fait porter H2 à C8, qui ne peut pas la porter

`06` §4 inscrit C8 comme atténuation de « la trace ne survit pas sans L4 (H2) ».
Mais H2 (§2) est empirique — « cette différence **reste visible** sans le L4 » —
alors que C8 (§6) est « **du papier pour l'essentiel, aucune donnée de marché
touchée** », produisant un classement traverse / ne traverse pas.

Du papier répond à « cette grandeur est-elle **calculable** sans L4 ». Il ne peut
pas répondre à « la **trace survit**-elle ». Le tableau §2 le dit d'ailleurs :
H2 « testable **après H1** », coût « moyen » — ce qui contredit §4 qui la donne
couverte en semaine 1 à coût machine nul.

C8 couvre l'admissibilité et la moitié papier de H3. Lui laisser H2 fait croire
que le second risque le plus fort est traité alors qu'il ne l'est pas.

### I.11 — Le schéma de la table : la sortie de C8 en est le premier brouillon

`00` §6 et §11 signalent que la table n'a aucun schéma et l'inscrivent « à écrire
avant P5 ». Or la sortie de C8 — **l'inventaire colonne par colonne de ce qui
existe des deux côtés**, plus le verdict de traversée — *est* la première moitié
de ce schéma. C8 tourne en semaine 1, sans machine. Personne n'a relié les deux :
le contrat central du projet est traité comme un livrable tardif alors qu'un
chantier de semaine 1 en produit gratuitement la moitié.

---

## II. `ADR-001` — QUATRE DÉFAUTS, NE PAS VALIDER EN L'ÉTAT

*(Deux sont déjà identifiés par l'audit adversarial du 05/08 ; ils sont repris
ici parce que l'un des deux est mal cadré. Les deux suivants sont nouveaux.)*

### II.1 — Dépendance à l'ordre : l'estimande change, ce n'est pas une barre qui monte

Formulation courante : « la barre monte pour les candidats tardifs ». C'est plus
grave. La corrélation partielle de X avec la cible **sachant Z** n'est pas la
même quantité pour deux Z différents. Un candidat jugé en dixième position ne
franchit pas une barre plus haute — **il répond à une autre question**. Les
verdicts ne sont donc pas comparables entre candidats, alors que `05`
§multiplicité exige de juger **la collection**.

Le correctif proposé (geler le bloc au début d'un tour) supprime la dépendance
**intra-tour**, pas **inter-tour** : le tour où un candidat tombe continue de
décider. Et attention — `05` fait grandir le bloc d'É2 **en continu** ; si celui
d'É4 est gelé par tour, « le bloc retenu » désigne deux objets différents selon
l'épreuve. **Le gel doit porter sur É2 et É4 ensemble.**

### II.2 — Contrôle monotone : juste, mais mal attribué, et l'asymétrie est manquée

Le reproche « la corrélation partielle est un contrôle linéaire, elle rate le non
monotone et l'interaction » est exact. Mais **ce n'est pas un défaut d'`ADR-001`** :
É0 et É2 sont déjà du Spearman. Le banc est de rang de bout en bout **avant** cet
ADR ; la métrique d'É4 hérite du défaut, elle ne l'introduit pas. Et les trois
alternatives du tableau de l'ADR sont fermées par des décisions antérieures
(AUC interdite, modèle ajusté interdit avant la porte, économique désavoué).
Rejeter la corrélation partielle sur ce motif ne laisse **rien**.

Ce qui est manqué, c'est l'**asymétrie** :

| | conséquence du monotone-seulement |
|---|---|
| É0, É2 | on rate une **redite** → un doublon passe, É4 le rattrape. **Conservateur.** |
| **É4** | on rate un **apport réel** → le candidat est éliminé. **Destructeur, sans appel.** |

**Correctif qui ne coûte ni test ni multiplicité** : écrire la ligne `définition`
des fiches à mécanisme de seuil pour soumettre au banc une quantité **déjà
monotone** — non pas « taux de disparition » mais son **écart à sa ligne de
base** ; non pas « cascade » mais **taille de grappe**. Concerne **B1, D1, D2**.
Ça se corrige dans `03`, pas dans le banc.

### II.3 — L'ADR argumente pour la puissance, puis définit une collection qui la détruit

Il justifie 10 % plutôt que 5 % par « un faux négatif ferme une piste, et ce
projet en a déjà fermé à tort ». Puis il fixe la collection à « l'ensemble des
candidats jugés à É4 — **résolutions et symboles compris** ». Soit, avec 29
candidats × 5 résolutions × 2 symboles, jusqu'à **290 tests dans
Benjamini-Hochberg**.

Or résolutions et symboles ne sont pas des hypothèses séparées : **É3 exige déjà
le même signe aux cinq résolutions**, et **É4 exige déjà le même signe sur deux
symboles**. Ce sont des **conjonctions internes à un candidat**, portant sur la
même donnée, donc fortement dépendantes. Les compter comme tests indépendants
**corrige deux fois le même risque**.

Et `05` §multiplicité tient exactement le raisonnement inverse, pour les
candidats : « une collection de soixante candidats dont quarante sont des
synonymes **n'est pas soixante tests** ». L'ADR applique ce principe aux doublons
et l'oublie pour les résolutions. **Le passage de 5 % à 10 % récupère beaucoup
moins de puissance que cette définition n'en détruit.**

**Correctif** : la collection est l'ensemble des **candidats** ; la conjonction
résolutions × symboles reste une **condition interne** au candidat, pas une
famille de tests.

### II.4 — Deux règles de décision concurrentes, et rien ne dit laquelle tranche

Le tableau des cinq paramètres donne comme **seuil** « l'IC doit exclure zéro »
(Student 95 %), et comme **collection** un contrôle BH à 10 %. Deux procédures de
décision pour un seul verdict. Un candidat dont l'IC exclut zéro mais qui tombe
sous BH : **retenu ou éliminé ? L'ADR ne le dit pas.**

C'est le défaut le plus bloquant des quatre, parce qu'il attaque la raison d'être
de C9 : « **aucune des cinq épreuves ne demande un jugement** ». En l'état, É4 en
demande un — et `06` prescrit alors que « c'est le **protocole** qu'il faut
corriger, pas le harnais qu'il faut assouplir ».

**Correctif** : nommer BH comme **la** règle de décision, et l'IC de Student comme
la **statistique d'entrée** qui l'alimente.

---

## III. POINTS DÉJÀ ENREGISTRÉS — NE PAS RE-SOUMETTRE

* `ETAT` B5 (fiches de `03` incomplètes) couvre et **étend** le constat sur la
  ligne `coût` : il manque aussi le **périmètre minimal**. Confirmé — zéro ligne
  `coût` dans toute la Partie I de `03`, donc la règle de départage d'É0
  (« on garde le moins cher ») n'a aucune entrée. Défaut connexe : `05` §1
  annonce « une fiche de **quatre lignes** » et en liste **huit** ; `03` annonce
  « **six** lignes fixes ». Trois comptes pour un même objet.
* `ETAT` B2 a adopté « É0 et É2 touchent du marché » — voir I.1 pour la
  contradiction que ça crée avec C5.
* `ETAT` B8 est **trop pessimiste** en disant que l'interdit de « changer un
  seuil après résultat » empêchera d'écrire la multiplicité plus tard : `01` §4
  et `05` §10 prévoient explicitement le changement **par ADR avec repassage de
  tous les candidats**. L'échéance réelle est *avant le premier calcul d'É4*,
  pas *jamais*. Urgent, pas condamné.