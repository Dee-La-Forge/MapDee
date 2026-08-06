# C10 — Sortir l'instrument de l'archive

> **Décidé le 06/08/2026** sous la délégation de Meddy, sur l'argument de
> l'audit : tout chiffre du projet sort de `_recupere/construit/` — le seul
> code que la règle « on n'audite pas l'archive » rendait inauditable. La
> nuit du 4-5 août a payé la démonstration : des mesures invalidées non pas
> pour leurs calculs, mais pour leur instrument non vérifié. La règle n° 1
> du projet (« toute conclusion négative passe par un audit d'instrument »)
> doit être applicable à l'instrument principal.
>
> `00` §7 est corrigé le même jour : l'état transitoire est dit, et la règle
> d'inauditabilité ne s'applique plus à `construit/`.

## La contrainte absolue

**JAMAIS sous un run.** Aucun fichier de `construit/` ne se déplace ni ne
s'édite tant qu'une construction tourne — règle payée 10 heures le 05/08
(un script modifié sous exécution a sauté deux lots en silence). C10 ne
commence qu'après la fin de la tranche 1, arbre au repos.

## Le périmètre

`construit/` : `jour.py` (le rejeu — le cœur), `lot.py` (l'orchestration),
`openbook.py` (les lecteurs), `empreinte.py` (les manifestes), `garde/`
(les garde-fous d'`05` §3, dont le harnais porte déjà sa version). La grille
est déjà sortie (`harnais/grille.py`, D2) — c'est le modèle du trajet.

## La méthode — caractériser d'abord, déplacer ensuite

1. **Test de reproductibilité AVANT tout déplacement** (c'est l'audit
   d'instrument minimal, et il ne touche pas au code) : reconstruire un
   jour certifié dans un bac à sable et comparer le `sha256` de l'artefact
   à celui du manifeste. Identique → l'instrument est déterministe et ses
   artefacts retraçables ; différent → on a appris quelque chose de grave
   AVANT de bouger quoi que ce soit.
2. **Tests de caractérisation à la main** — le modèle est
   `harnais/tests/test_charge_precis.py` : de petites archives fabriquées
   ligne à ligne, chaque table attendue calculée sur papier (statuts,
   diffs → carnet, émission `deep`, chauffe, gel, manifestes).
3. **Déplacement fichier par fichier** vers `construit/` à la racine du
   dépôt, imports retournés, l'archive gardant une copie morte marquée.
4. **Re-test de reproductibilité** après trajet : même jour, même sha —
   sinon le déplacement a changé l'instrument et ça se voit.

## Ce que ça débloque

La règle d'audit d'instrument redevient applicable partout · les défauts
connus du pipeline (taux de jointure jamais appelé, lignes illisibles sans
compteur, compteur de qualité à deux causes — ETAT §3 bis) deviennent
réparables au lieu d'être constatés · et le préflight peut enfin compter
`construit/` parmi les protocoles qu'il vérifie.
