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
