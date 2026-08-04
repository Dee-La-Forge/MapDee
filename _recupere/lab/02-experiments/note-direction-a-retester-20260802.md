# Note — l'hypothèse DIRECTIONNELLE mérite d'être re-testée, sur la bonne population

_02/08/2026, consignée sur demande de Meddy. **Ce n'est pas un résultat.**
C'est la trace d'une question et de ce qui la justifie, pour qu'elle ne se
perde pas et qu'elle ne soit pas rouverte en douce plus tard._

## Le raisonnement de Meddy

Le spoofing n'a de sens économique que s'il fait bouger quelqu'un : on affiche un
mur massif pour induire un flux, on le retire avant l'exécution. **La direction
n'est pas un effet secondaire du spoof, c'est sa raison d'être.** Si on sait
reconnaître un mur factice, on devrait donc savoir quelque chose de la direction.

## Ce que le dossier a déjà mesuré — et c'est négatif, deux fois

`backtest-eco-20260728T233217Z.md`, résumé dans `PROGRAMME:72-79` et
`README:168-206` :

| stratégie | BTC net | ETH net |
|---|---|---|
| fader TOUS les murs | **−10,8 bp** | **−9,6 bp** |
| filtre : 10 % les plus solides | −10,4 bp | −10,3 bp |
| contrôle aléatoire, même n | −12,0 bp | −9,4 bp |

Mouvement BRUT moyen après contact : **−1,8 bp (BTC) / −0,6 bp (ETH)**, soit un
ordre de grandeur SOUS les 9 bp de frais aller-retour. Prendre la cassure — le
miroir — perdrait aussi. Et **le filtre ne bat pas le tirage au sort** : sur
`y_flee`, le modèle n'a aucune valeur directionnelle.

C'est sur cette base que `P0-FRAG-porte-preenregistree.md:47-51` exclut
explicitement la direction de son périmètre : « Toute lecture directionnelle
d'un résultat de P0-frag est une violation du périmètre. »

## Ce qui change aujourd'hui, et seulement ça

`mesure-instrument-carnet-fin-20260802.md` établit sur BTC 2026-05-08 que
l'instrument du banc est aveugle à une population entière :

| | ordres VUS | ordres INVISIBLES |
|---|---|---|
| durée de vie médiane | 859 s | **38 s** |
| taille affichée | ×1 | **×16** |
| taux de fuite | 22,6 % | **87,5 %** |

**Le backtest directionnel a donc mesuré l'effet sur le prix des murs qui
TIENNENT** (77 % de sa population). Or un mur qui tient n'est pas un spoof et
n'a aucune raison mécanique de pousser le prix. L'archive du backtest est à
10 s — plus fine que les 62,6 s du banc, mais toujours grossière devant une
durée de vie médiane de 38 s.

## Ce que cette note NE dit PAS

- Elle **ne rouvre pas** le résultat négatif. Un négatif mesuré reste un
  négatif : fader les murs visibles perd de l'argent, c'est établi.
- Elle **n'affirme pas** que les murs invisibles portent une direction. Rien ne
  l'a mesuré.
- Elle ne dit rien du coût : les frais de 9 bp ne changent pas, et un mouvement
  brut de 1,8 bp reste très en dessous. Retrouver la bonne population ne crée
  pas d'edge par magie.

## Condition d'ouverture, posée ICI et pas après

Cette question ne devient une porte que si **l'effet d'instrument se réplique
sur les 7 jours BTC disposant du carnet à 537 ms** (mesure en cours). Un effet
vu une seule journée ne justifie rien.

Si réplication : la porte à écrire existe déjà en germe —
`note-p0bis-candidat.md` (30/07), le fade conditionné au score **en maker** avec
modèle de remplissage et gestion de sortie, plutôt qu'en taker naïf à 9 bp.
Elle est explicitement « candidate, décision APRÈS le verdict du jalon, non
planifiée, non budgétée ».

Ses seuils devront être gravés **avant** tout chiffre, comme ADR-011 et
ADR-012 — et cette fois **commités avant exécution**, conformément au garde-fou
`gondetect/provenance.py`.

## Rang dans la file

Après : (1) la réplication de l'effet d'instrument, (2) la décision sur
l'unité statistique (ADR-016 à réécrire). **Pas avant.** Un programme à la fois.
