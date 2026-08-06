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
`openbook.py` (les lecteurs), `empreinte.py` (les manifestes). La grille est
déjà sortie (`harnais/grille.py`, D2) — c'est le modèle du trajet.
**`garde/` ne se déplace PAS : il se FUSIONNE** (audit du 06/08, point 2) —
le harnais porte déjà l'implémentation testée des deux garde-fous d'`05` §3 ;
en copier une seconde recréerait mot pour mot le double É0 fermé la veille.
Une seule implémentation (`harnais/gardefous.py`), et `construit/`
l'importe.

## La méthode — caractériser d'abord, déplacer ensuite

1. **Test de reproductibilité AVANT tout déplacement** (c'est l'audit
   d'instrument minimal, et il ne touche pas au code) : reconstruire un
   jour certifié dans un bac à sable et comparer le `sha256` de l'artefact
   à celui du manifeste. **Lecture déclarée D'AVANCE** (audit du 06/08,
   point 3) : identique → déterministe et retraçable · différent →
   **comparer au niveau CONTENU** (mêmes lignes, mêmes valeurs) pour
   séparer « les octets diffèrent » (bénin — métadonnées parquet,
   row-groups ; peu probable sous versions épinglées, pas impossible) de
   « la donnée diffère » (grave). Un écart bénin ne se lira pas comme une
   catastrophe, ni l'inverse.
   Et **la circularité d'`empreinte.py` se casse une fois** : c'est lui qui
   calcule les manifestes du test — vérifier UNE fois son sha contre un
   `sha256sum` indépendant avant de lui faire confiance en boucle.
2. **Tests de caractérisation à la main** — le modèle est
   `harnais/tests/test_charge_precis.py` : de petites archives fabriquées
   ligne à ligne, chaque table attendue calculée sur papier (statuts,
   diffs → carnet, émission `deep`, chauffe, gel, manifestes).
3. **Déplacement fichier par fichier** vers `construit/` à la racine du
   dépôt, imports retournés, l'archive gardant une copie morte marquée.
3 bis. **REPOINTER LE LANCEUR DANS LA MÊME FENÊTRE** (audit du 06/08,
   point 1 — le seul trou qui mordrait en silence) :
   `construire_decembre.ps1:119` fait `Set-Location _recupere` et
   exécuterait la copie morte pendant que le neuf serait testé à la racine.
   Le repointage vit aussi dans la ligne « corrections du lanceur » du
   tableau des dettes d'ETAT — **les deux lignes se referment ensemble,
   renvoi croisé écrit des deux côtés**.
4. **Re-test de reproductibilité** après trajet : même jour, même sha —
   sinon le déplacement a changé l'instrument et ça se voit.

## Ce que ça débloque

La règle d'audit d'instrument redevient applicable partout · les défauts
connus du pipeline (taux de jointure jamais appelé, lignes illisibles sans
compteur, compteur de qualité à deux causes — ETAT §3 bis) deviennent
réparables au lieu d'être constatés · et le préflight peut enfin compter
`construit/` parmi les protocoles qu'il vérifie.
