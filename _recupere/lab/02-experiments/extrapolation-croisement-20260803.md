# Extrapolation du croisement pose/agression — et sa condition de validité

**03/08/2026, 23 h 50** · demandé par Meddy · BTC, jour 20251209
**RÉPLICATION FAITE — elle CONFIRME.** Jours 09, 10 et 11 :

| jour | écart pondéré | déciles gagnants |
|---|---|---|
| 09/12 | **+0,766 bp** | 9/10 |
| 10/12 | **+0,654 bp** | 8/10 |
| 11/12 | **+0,456 bp** | 9/10 |
| **moyenne** | **+0,625 bp** | **26/30** |

Écart-type entre jours 0,157, erreur-type de la moyenne 0,091 → **t = 6,9**.
Le document tient donc. À noter tout de même : le point estimé **décroît** sur
les trois jours (0,77 → 0,65 → 0,46). Trois jours ne permettent pas de dire si
c'est du bruit ou une décroissance.

---

## Le fait mesuré

| | |
|---|---|
| couples (seau, portefeuille) avec pose ET agression | 102 195 / jour |
| dont **croisés** (pose d'un côté, agression de l'autre) | **14,1 %** |
| rendement 60 s après croisement, sens de l'agression | **+1,156 bp** |
| idem sans croisement | +0,344 bp |
| **à taille d'agression égale** (moyenne pondérée sur 10 déciles) | **+0,766 bp** |
| déciles où le croisement gagne | **9 / 10** |

## Ce qui devrait tenir en s'étendant

**La puissance.** 102 000 couples par jour, ~800 000 sur les huit jours
d'exploration. On peut découper par taille, par heure, par portefeuille sans
épuiser l'échantillon.

**La stabilité temporelle.** Le classement des portefeuilles par impact persiste
déjà à **+0,85** d'une semaine à l'autre (mesuré). Rien ne suggère que le
croisement soit moins stable que l'impact dont il est une composante.

## Ce qui ne tiendra pas

**L'argent, sous cette forme.** +0,77 bp contre **7 bp de frais** preneur : il
manque un facteur neuf. Même en ne gardant que les meilleurs déciles (+2,1 bp),
il manque un facteur trois.

Et ce n'est pas un problème de sélection : **le plafond mesuré n'a jamais
dépassé 2,5 bp**, à aucun des cinq horizons testés (60 s à 1 h). Affiner la
sélection ne peut pas franchir un plafond qui n'existe pas.

**Le transfert vers Binance.** Le signal repose entièrement sur l'identité, que
Binance ne publie pas. Il restera hyperliquid-natif.

## Où ça pourrait valoir quelque chose — le retournement

**Ce n'est pas un signal directionnel, c'est un signal de SÉLECTION ADVERSE.**

Un teneur de marché paie 1 bp, pas 3,5. Sa perte ne vient pas de se tromper de
direction : elle vient d'**être servi juste avant que le prix parte**. Savoir
qu'un mur va disparaître, ou qu'un acteur pose devant vous en agressant
derrière, ne vaut pas 0,77 bp d'alpha — ça vaut de **ne pas prendre le mauvais
fill**, ce qui se chiffre en plusieurs bp par occurrence évitée.

Cohérent avec tout le reste de la soirée : les **gros** teneurs ont une
corrélation **négative** (−0,074) — ils se font systématiquement traverser. Le
signal ne sert pas à parier, il sert à **ne pas être de l'autre côté**.

## Ce qui changerait la réponse, par ordre de coût

1. **Mesurer le gain ÉVITÉ plutôt que le gain réalisé.** Même donnée, question
   renversée. Quelques heures.
2. **Étendre à ETH et SOL** : frais identiques, fourchettes relativement plus
   larges — le rapport signal/coût peut différer.
3. **Remplacer le proxy grossier par la vraie configuration** : empilement,
   rafraîchissement, dynamique à l'approche. **Deux des sept éléments
   disponibles ont été utilisés.** Le +0,77 bp est un plancher obtenu avec
   l'instrument le plus pauvre possible.

## La réserve, écrite avant de connaître la suite

Un jour, un symbole. La réplication sur les jours 10 et 11 tourne au moment où
ces lignes sont écrites. **Si elle ne confirme pas, ce document est retiré, pas
réinterprété** — c'est la règle qu'on s'est donnée après E1.

Et une limite qui ne bougera pas quelle que soit la réplication : poser d'un
côté et se rééquilibrer de l'autre est **aussi** le comportement banal d'un
teneur de marché gérant son inventaire. La mesure établit une **structure**, pas
une **intention**. Appeler ça « spoofing » va au-delà de ce qui est montré.
