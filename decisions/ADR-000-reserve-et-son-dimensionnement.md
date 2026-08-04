# ADR-000 — La réserve 17-23, et comment sa taille sera fixée

> **La numérotation repart de zéro.** Décision de Meddy, 04/08/2026. MapDee est
> une reconstruction, pas une reprise : les ADR-001 à 021 de
> `_recupere/lab/04-decisions/` appartiennent aux deux dépôts morts. Ils restent
> lisibles comme archives, ils ne portent plus aucune autorité ici. Cet ADR est
> **le premier du projet**, et il porte le numéro 0 parce qu'il précède la
> première construction.
>
> Une seule conséquence à retenir : quand ce dossier cite « ADR-020 » ou
> « ADR-021 », il parle de l'**ancien** dépôt, jamais d'un document de MapDee.
> Les ADR de MapDee vivent dans `decisions/`, ceux de l'archive dans
> `_recupere/lab/04-decisions/`, et les deux séries se recoupent en numéros.

> ⚠️ **ADDENDUM DU 04/08/2026, 22 h 20 — une affirmation de ce document est
> fausse. Voir l'addendum en fin de fichier.** Le corps du texte n'est pas
> réécrit : « effacer une faute est pire que l'avoir commise ».

**Date** : 2026-08-04, 22 h 10 · **Statut** : **ACCEPTÉE** — validée par Meddy
le 04/08/2026 à 22 h 02, **avant** le lancement de la reconstruction du mois.
Aucun jour de 17-23 n'a été ouvert à cette heure.

> **Antériorité** : cet ADR ne vaut que s'il est **commité avant** la première
> construction qu'il encadre. Doctrine du dossier : « un document qui affirme
> avoir été écrit avant un résultat doit être commité avant ce résultat, sinon
> son antériorité ne vaut rien. »

---

## Contexte

La réserve `20251217 → 20251223` est appliquée par le code
(`_recupere/construit/jour.py`, constante `RESERVE`, refus à l'écriture) et
citée par le prompt et le document de passation.

**Elle n'est fondée par aucun ADR.** Le seul ADR qui partitionne les jours,
l'ADR-020, dit le contraire — « 2025-12-09 → 31 : EXPLORATION — libre,
23 jours » — et se termine par :

> « La tranche de la PROCHAINE certification devra être découpée dans les 09-31
> **avant** de commencer à explorer, et jamais ouverte pendant l'exploration.
> **À décider AVANT de commencer l'exploration, pas après.** Non décidé ici. »

L'exploration commence maintenant : 48 constructions sont sur le point d'être
lancées sur les jours 01-16 et 24-31. L'échéance que l'ADR-020 s'était fixée
est donc **aujourd'hui**. Sans cet ADR, le seul titre de la réserve est une
constante dans un fichier — et une réserve dont la raison n'est pas opposable
ne certifie rien.

## Le problème de dimensionnement, et pourquoi il ne peut pas être résolu maintenant

Tout le dossier — prompt §3, passation §6, journal du 04/08 — répète qu'il faut
« une vingtaine de jours » pour distinguer un effet de 0,8 bp de zéro, sur la
foi d'un écart-type inter-journalier de **1,35 bp**.

Ce chiffre a été retracé le 04/08/2026 jusqu'à sa source unique :
`_recupere/lab/02-experiments/p2-deux-portes-20260804.md:26`. Il vient de
**quatre jours** (09 au 12/12), d'**une seule expérience**, sur l'**instrument
non audité** — P2 est l'une des quatre mesures que le dossier a lui-même
désavouées.

Un écart-type estimé sur 4 points a 3 degrés de liberté :

```
σ̂ = 1,354        IC 95 % :  σ ∈ [0,77 ; 5,05] bp        (χ², 3 ddl)
```

Reporté sur le nombre de jours nécessaires pour détecter 0,8 bp
(α = 5 % bilatéral, puissance 80 %) :

| σ vrai | jours nécessaires |
|---|---|
| 0,77 (borne basse) | **8** |
| 1,354 (l'estimation) | 23 |
| 5,05 (borne haute) | **313** |

**Dimensionner une réserve sur ce chiffre serait dimensionner à un facteur 6,5
près.** Et décembre 2025 est le seul mois disponible : le `README.md` du jeu
Zenodo établit que les *book diffs* et les *order statuses* couvrent Dec 1-31
et rien d'autre — seuls les *trades* vont d'octobre à janvier. L'échappatoire
qu'envisageait l'ADR-020 (« soit un mois différent ») **n'existe pas pour le
carnet**.

## Alternatives

1. **Geler 7 jours maintenant, sans mesure.** Simple et opposable, mais on ne
   saura qu'après coup si la réserve pouvait certifier quoi que ce soit. Si
   σ est haut, on aura gelé sept jours pour rien.
2. **Ne rien geler, décider plus tard.** Interdit par l'ADR-020 et par le bon
   sens : une tranche découpée après exploration a déjà été regardée.
3. **Geler maintenant, dimensionner ensuite sur une mesure faite hors
   réserve.** ← retenu.

## Décision

**a. La réserve `20251217 → 20251223` est confirmée**, sept jours, gelée à la
construction **et** à la mesure. Le refus reste appliqué par le code.

**b. Sa taille définitive sera fixée par σ mesuré sur l'unité JOUR**, avant
tout usage de la réserve, et **sur les seuls jours d'exploration** —
`20251209-16` et `20251224-31`, jamais 17-23.

C'est légitime, et la raison tient en une phrase : **σ est une propriété de
l'instrument et du marché, pas de l'hypothèse testée.** Le mesurer sur les
jours d'exploration ne consomme aucune information sur la réserve, et ne dit
rien du résultat qu'on y cherchera.

**c. Si le σ mesuré impose plus de sept jours**, la tranche s'étend sur
`20251224-31` — qui sont aujourd'hui non construits et non regardés — dans
l'ordre décroissant des dates (31, 30, 29 …), et l'extension est actée par un
addendum daté **avant** la construction des jours concernés.

**d. Si le σ mesuré montre que même 31 jours ne suffisent pas** pour l'effet
visé, ce n'est pas la réserve qu'on agrandit : c'est **la cible de
certification qu'on relève**, par ADR, avant tout tir. Un effet qu'on ne peut
pas mesurer avec le matériel disponible ne se certifie pas — il se déclare
hors de portée.

**e. Ce qui entame la réserve malgré tout, et qui est assumé ici** : la chauffe
de huit heures du jour `20251224` rejoue les huit dernières heures du `23`
(`jour.py`, plan de chauffe). C'est l'état du carnet à minuit, pas une mesure
et pas un label, et c'est physiquement inévitable si l'on veut la continuité du
livre. **Aucune autre lecture de 17-23 n'est autorisée.** La garde actuelle ne
protège que l'écriture ; la garde en lecture reste à construire (dette
identifiée, prompt §8 piège n° 11).

## Conséquences

* Le mois se construit sur **24 jours** : 01-16 et 24-31, deux symboles.
* σ inter-journalier devient une **mesure due avant toute certification**, et
  non un chiffre hérité. Elle est bon marché une fois les 24 jours construits.
* Le « il faut une vingtaine de jours » cesse d'être cité comme un fait dans
  les documents du projet ; il y est remplacé par l'IC ci-dessus.
* Si l'extension (c) est déclenchée, l'exploration perd des jours qu'elle
  croyait avoir. C'est le coût de ne pas savoir σ, et il est payé d'avance
  plutôt que découvert.

---

## Addendum du 04/08/2026, 22 h 20 — la réserve *était* fondée par un ADR

**Ce document affirme, deux fois, que la réserve 17-23 « n'est fondée par aucun
ADR ». C'est faux.** Trouvé en lisant `_recupere/lab/DETTE-20260803.md` §C2,
qui y renvoie explicitement, puis vérifié à la source.

`_recupere/lab/04-decisions/ADR-021-unite-configuration-et-impact.md`, daté du
**2026-08-03 à 10 h 15**, statut **GELÉ**, porte une section « Partition des
jours — révision de l'ADR-020 » :

| jours | statut |
|---|---|
| 2025-12-09 → 16 | EXPLORATION |
| **2025-12-17 → 23** | **RÉSERVE DE CERTIFICATION — jamais ouverte** |
| 2025-12-24 → 31 | réserve libre |

> « Les jours 17-23 ne sont ni construits, ni étiquetés, ni regardés, tant que
> le protocole n'est pas pré-inscrit. Le garde-fou `_refuse_si_gele` sera
> étendu à cette tranche. »

Et l'en-tête de cet ADR précise qu'aucune donnée d'exploration n'était ouverte
à son écriture. **L'antériorité de la réserve est donc réelle et datée** — un
jour de plus que ce que je lui prêtais.

### Comment j'ai commis l'erreur

J'ai cherché la réserve par `grep` dans `04-decisions/`, lu l'ADR-020 en
entier, constaté qu'il disait « 09-31 exploration », et conclu. **L'ADR-021
figurait dans les résultats de ce même `grep` et je ne l'ai pas ouvert.** La
faute n'est pas la conclusion, c'est de l'avoir tirée d'une lecture partielle
alors que `00_Prompt_MapDee.md` §0 prescrit de lire `_recupere/lab/` en entier
avant d'écrire — ce que je n'avais pas fait.

C'est aussi, mot pour mot, la faute que le journal du 04/08 (« M2 ») consigne
en §0 : *« J'ai passé la première moitié de la nuit à réparer l'instrument sans
avoir lu `lab/`. Deux de mes contributions étaient des redécouvertes. »*
Troisième occurrence dans ce dossier.

### Ce qui change, et ce qui ne change pas

**Ne change pas — la décision.** MapDee repart de zéro : les ADR de
`_recupere/` sont des archives sans autorité ici (décision Meddy, 04/08).
Il faut donc bien un ADR **de MapDee** pour porter la réserve, et c'est
celui-ci. Le dimensionnement par un σ mesuré, le refus de se fonder sur les
1,35 bp de quatre jours, l'extension prévue sur 24-31 et l'aveu sur la chauffe
du 24 sont intacts — aucun ne dépendait de la prémisse fausse.

**Change — la formulation exacte.** Partout où ce document écrit « la réserve
n'est fondée par aucun ADR », lire :

> « la réserve n'est fondée par aucun ADR **de MapDee**, et l'ADR-021 de
> l'archive, qui l'établissait, n'a plus autorité ici. »

**Change aussi — un point de fait.** La DETTE §C2 signalait que la garde
`_refuse_si_gele` ne couvrait pas encore 17-23. Elle le couvre aujourd'hui
(`jour.py`, constante `RESERVE`, vérifié le 04/08). Cette dette est éteinte.

**Et un gain, non prévu.** L'ADR-021 classe les jours **24-31 en « réserve
libre »**, pas en exploration ordinaire. L'extension prévue au point (c) de cet
ADR tombe donc sur une tranche que l'archive destinait déjà à cet usage : les
deux décisions sont cohérentes, prises à un jour d'intervalle et sans
concertation.

---

## Addendum du 04/08/2026, 23 h 55 — trois renvois devenus morts, et une dette à ne pas perdre

Les documents de cadrage ont été réécrits dans la nuit. **Le corps de cet ADR
n'est pas retouché** — il porte une décision datée. Mais trois de ses renvois ne
résolvent plus, et il faut le dire ici plutôt que de les corriger en place.

| dans cet ADR | renvoyait à | où c'est maintenant |
|---|---|---|
| « prompt §3 » pour l'écart-type hérité | l'ancien §3 | **nulle part, et c'est voulu** — l'affirmation « il faut une vingtaine de jours » a été retirée des cadrages, conformément à la conséquence n° 3 de cet ADR. Le grief reste vérifiable dans l'archive du laboratoire mort. |
| « prompt §8 piège n° 11 » pour la garde en lecture | l'ancien §8 | `FAITS.md` §8, piège n° 9 |
| « `00_Prompt` §0 prescrit de lire `_recupere/lab/` en entier » | l'ancien §0 | `00_Prompt_MapDee.md` §13, ordre de lecture — **l'obligation avait été supprimée dans la même nuit ; elle est restaurée** |

**Et une dette que cet ADR est aujourd'hui le seul à porter, donc à ne pas
perdre** : la garde contre le **mélange de générations** existe à l'écriture et
dans les manifestes d'artefacts, **pas à la lecture**. Un chargeur qui balaie un
dossier peut encore concaténer deux générations en silence. Elle est désormais
consignée dans `FAITS.md` §8, piège n° 9 et §13.

Le point (e) du corps — la chauffe du dernier jour construit lit la veille, qui
appartient à la réserve — **reste valable et non traité**.

---

## Addendum du 05/08/2026 — la convention de gel, complétée

**Le corps de cet ADR n'est pas retouché.** Il portait la réserve et son
dimensionnement. Il lui manquait **deux statuts que le code applique pourtant**,
et cette absence bloquait trois chantiers.

`05_Protocole_de_selection.md` fait du **jour de banc d'instrument** une
condition d'arrêt explicite : *« tant que ce jour n'est pas nommé dans l'ADR,
l'observation ne démarre pas »*. Il n'y était pas nommé. C2 était donc bloqué, et
C3 puis C4 derrière lui. Le jour n'existait que dans un **commentaire de
script** — ce qui n'est ni opposable, ni lisible par quelqu'un qui suit l'ordre
de lecture.

### La convention complète

| jours | statut | ce qui est autorisé |
|---|---|---|
| **2025-12-01 → 07** | **TABLES PRINCIPALES FIGÉES** | seul le carnet profond se fabrique. Les tables d'ordres et de carnet **ne se réécrivent pas** : elles portent des contrôles croisés rendus, et les reconstruire détruirait la pièce à conviction. Le code refuse toute autre phase. |
| **2025-12-08** | **BANC D'INSTRUMENT** | validation de l'ingestion et **observation des trajectoires brutes**. Ni certification, ni conception de grandeurs — un jour dont on a mesuré la qualité d'instrument n'est plus vierge pour un verdict. |
| **2025-12-09 → 16** | **EXPLORATION** | libre |
| **2025-12-17 → 23** | **RÉSERVE** | **rien, jamais** — ni construction, ni lecture, ni mesure |
| **2025-12-24 → 31** | **EXPLORATION, ET SEULE ZONE D'EXTENSION** | ⚠️ **ni construits ni regardés** tant que l'écart-type n'a pas dit si la réserve suffit. Ce sont les seuls jours jamais regardés qui restent : les ouvrir ferme l'unique issue prévue par la règle asymétrique du corps de cet ADR. |

### Ce que ça débloque et ce que ça n'autorise pas

* **C2 peut démarrer** dès que le jour 08 est construit — l'observation des
  trajectoires une par une se fait sur lui, et sur lui seul.
* **Ça ne rend pas le jour 08 utilisable pour autre chose.** L'observation qu'on
  y fait le consomme comme jeu vierge : aucune certification ne s'y rendra.
* **Le code fait déjà respecter les deux gels** — la réserve et les tables
  figées. Le banc d'instrument, lui, **n'est porté par aucune garde** : c'est une
  convention d'usage, pas un refus. Elle tient par discipline, pas par
  construction, et il faut le savoir.

### Réserve d'honnêteté

Cette convention n'est pas décidée ici : elle est **transcrite**. Elle vivait
dans le code et dans les commentaires du lanceur, et elle vient d'une itération
antérieure. La porter dans l'ADR la rend opposable et lisible — **ça ne la
valide pas**. Si un jour on veut un autre découpage, il se décide, il ne se
déduit pas de ce qui existait.


---

## Addendum n° 2 du 05/08/2026 — le périmètre de σ, corrigé (audit de Meddy)

**Le corps n'est pas retouché.** Sa décision (b) disait : σ mesuré « sur les
seuls jours d'exploration — `20251209-16` et `20251224-31` ». Deux défauts,
trouvés par l'audit du 05/08 :

* **circularité (I.3)** — le plan interdit de toucher 24-31 tant que σ n'est
  pas connu ; (b) voulait pourtant les compter dans σ. Les deux règles étaient
  incompatibles, **et c'est le document qui engage qui portait la version
  cassée** ;
* **puissance (I.4)** — exclure 01-08 sans raison écrite laissait σ sur
  **8 jours** (IC de σ à un rapport haut/bas de **3,1**) au lieu de **16**
  (rapport **2,1**). Cet ADR rejetait à raison un σ à 4 jours parce qu'il
  dimensionnait « à un facteur 6,6 » ; sa propre clause menait à 3,1. La
  frontière du 09 venait d'un ADR d'archive **sans autorité**.

**Décision (b), version corrigée — formulation de Meddy :**

> **σ se mesure sur les jours d'exploration effectivement construits, hors
> zone d'extension.**

Elle casse la circularité, récupère jusqu'à 16 jours, et ne suppose rien de ce
que le code refuse d'écrire.

**Réserve à porter avec la mesure** : si la grandeur journalière dont on prend
l'écart-type consomme les tables `hl_*` des jours 01-07, celles-ci sont d'une
**génération antérieure** (piège du mélange, `FAITS` §8 n° 9). Dans ce cas σ se
restreint aux jours homogènes — et le dit dans son rapport.
