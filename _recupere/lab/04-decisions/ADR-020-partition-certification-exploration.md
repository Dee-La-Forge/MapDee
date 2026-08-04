# ADR-020 — Partition du jeu OPEN BOOK : certification / exploration

**Date** : 2026-08-03, 06 h 40 · **Statut** : **GELÉ**, posé AVANT le verdict du
jalon. Décidé avec Meddy le 03/08.

> Écrit avant la certification. Aucun résultat de verdict n'existe à cette heure.
> C'est le seul moment où cette partition peut être décidée sans être suspecte.

---

## Le problème qu'on prévient

Les 19 traits de `features.py` ont été conçus **contre l'instrument
défectueux** : un carnet à 62,6 s de cadence qui perdait 58,6 % des ordres. Ils
sont contraints par ce que cet instrument pouvait montrer.

Or le trait qui porte le plus de signal parmi ceux mesurés est `f_conv` — la
constance de la taille du mur sur une fenêtre (0,597 en concordance brute, 3
jours). C'est précisément le genre de mesure qu'une photo par minute détruit :
entre deux clichés, un mur peut apparaître, grossir, se retirer et revenir sans
laisser de trace.

Le nouvel instrument photographie à **100 ms d'âge médian** — la résolution du
recorder de production (`C.SNAP_MS = 100`). Des traits jusqu'ici inconcevables
deviennent calculables : micro-rythmes de replacement, cadence d'annulation,
réaction à un mouvement de prix en moins d'une seconde.

**Il y a donc très probablement un gisement dans la re-conception des traits.**
Et c'est exactement là que le projet peut se saborder : explorer sur les jours
qui viennent de rendre le verdict, c'est fabriquer du résultat.

## La partition

Le jeu OPEN BOOK couvre **décembre 2025, 31 jours**. On en utilise 7.

| jours | statut | usage autorisé |
|---|---|---|
| **2025-12-01 → 2025-12-07** | **CERTIFICATION — GELÉ** | le tir unique de l'ADR-019, et rien d'autre |
| **2025-12-08 → 2025-12-31** | **EXPLORATION — LIBRE** | conception de traits, tests, itérations, autant qu'on veut |

24 jours n'ont **jamais été regardés** à ce jour : ni construits, ni étiquetés,
ni ouverts. C'est ce qui rend la réserve crédible.

## Ce qui est interdit sur les jours 01-07, après le tir

1. Y mesurer un trait NOUVEAU, quel qu'en soit le prétexte.
2. Y refaire tourner le jalon sous un autre réglage.
3. Y chercher une explication *a posteriori* d'un résultat décevant, sauf
   autopsie explicitement déclarée comme telle et publiée avec la mention
   qu'elle ne peut pas certifier.

## Ce qui est autorisé sur les jours 08-31

Tout. Concevoir, mesurer, jeter, recommencer, regarder les résultats et ajuster.
C'est le rôle d'un jeu d'exploration.

**Avec une seule contrainte** : toute nouveauté qui en sort et qu'on voudra
certifier devra l'être sur un jeu qui n'a servi à rien d'autre. Les jours 01-07
étant consommés par l'ADR-019, il faudra alors soit un mois différent (le jeu
source couvre d'autres périodes), soit une tranche des 08-31 réservée à l'avance
et jamais ouverte pendant l'exploration.

**À décider AVANT de commencer l'exploration, pas après** — sinon le problème se
répète d'un cran.

## Pourquoi c'est noté maintenant

Parce que dans deux heures il y aura un verdict, et qu'une partition décidée
après un verdict n'a aucune valeur : on choisira toujours, sans même s'en rendre
compte, celle qui arrange la suite.

---

## Amendement du 03/08, 08 h 50 — après le verdict, après l'audit

Le tir de l'ADR-019 a rendu **CAS D** le 03/08 à 07 h 51. Un audit adversarial
en quatre volets a suivi. Il a confirmé le verdict (barres recomptées, seuils
exacts, aucune cellule dissimulée, empreintes reproductibles) et n'a trouvé
**aucune fuite temporelle** — mais il a trouvé **six défauts d'ingestion**, dont
deux touchent le mid, donc les labels :

* **D2** — `WARMUP_H` mangeait les 2 premières heures du JOUR COURANT : 8,33 %
  de chaque journée sans carnet, donc sans mid, donc sans label, 7 jours sur 7.
* **D3** — la branche `update` ne retirait jamais un palier tombé à taille
  nulle : 1,67 % des paliers de niveau 1 étaient fantômes, le mid était faux
  sur 3,36 % des photos (médiane 1 $, max 10,5 $).

Les deux sont corrigés le 03/08 au matin, avec quatre défauts mineurs
(colonne `action` fausse à 21,72 %, `tid` nul, rejets de bord de journée
silencieux, fusion non ordonnée sur `hl_book`/`hl_fills` des 01-03 — sans
effet, les consommateurs trient).

### Trois conséquences, décidées ici

**1. Les jours 2025-12-01 → 2025-12-07 sont désormais en LECTURE SEULE.**
`build_openbook_day._refuse_si_gele` échoue à la construction. Ces sept
journées portent le verdict rendu ; les reconstruire avec un code corrigé —
même de bonne foi — détruirait la pièce à conviction et rendrait le rapport
`jalon1-2026-08-03T052750Z-a4d558bd6072.md` invérifiable.

**2. Le 2025-12-08 devient le BANC D'INSTRUMENT.** Il sert à valider
l'ingestion (cadence, paliers fantômes, couverture horaire, taux « transaction
dans la fourchette ») et **rien d'autre** : ni certification, ni conception de
traits. Un jour dont on a mesuré la qualité d'instrument n'est plus vierge pour
un verdict.

**3. La partition devient donc :**

| jours | statut |
|---|---|
| 2025-12-01 → 07 | CERTIFICATION CONSOMMÉE — lecture seule, verdict CAS D |
| 2025-12-08 | BANC D'INSTRUMENT — validation de l'ingestion uniquement |
| 2025-12-09 → 31 | EXPLORATION — libre, 23 jours |

La tranche de la PROCHAINE certification devra être découpée dans les 09-31
**avant** de commencer à explorer, et jamais ouverte pendant l'exploration.
Non décidé ici : ça se décide quand on saura ce qu'on veut certifier.
