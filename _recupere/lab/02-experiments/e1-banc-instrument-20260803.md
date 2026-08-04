# E1 — validation de plomberie sur le banc 20251208

**03/08/2026, 20 h 52** · `experiments/e1_oracle.py --day 20251208 --coin BTC --instrument`

> **Aucune corrélation n'a été calculée.** Le mode `--instrument` exécute toute
> la chaîne — bande, murs, `flee_ratio`, `I(t)` — et **s'arrête avant la cible**.
> Découvrir un défaut après avoir vu un rho rendrait toute correction ultérieure
> suspecte d'avoir été choisie pour lui. Le jour 08 est le banc d'instrument de
> l'ADR-020 ; il ne sert qu'à ça.

## Ce que la chaîne rend

| | |
|---|---|
| photos | 8 294 |
| paliers par photo (nappe ±10 %) | 3 571 |
| photos avec une bande non vide | 8 294 (100 %) |
| murs (`mag ≥ 8× médiane de bande`) | 822 932, soit ~99 par photo |
| **murs MUETS** | **424 120 — 34,01 %** |
| instants avec `I(t)` défini | 8 294 — **couverture 100 %** |
| `flee_ratio` hors [0 ; 1] | **0** |
| `I(t)` hors [−1 ; +1] | **0** |

## Les 34 % de murs muets

Un mur est **muet** quand aucun de ses ordres ne se termine dans les 30 s qui
suivent : ni retrait, ni exécution. Son `flee_ratio` n'est pas nul, il est
**indéfini**.

L'addendum 1 de l'ADR-021 avait tranché avant de mesurer : on les écarte de
`M(t, côté)` plutôt que de les compter à 0, ce qui les déclarerait sincères sans
preuve et gonflerait le dénominateur de `I(t)` d'une masse muette. La réserve
exigeait d'en publier la proportion — la voici.

**34 % est élevé sans être disqualifiant** : `I(t)` reste défini à 100 % des
instants, donc E1 mesure bien la configuration entière, sur les deux tiers de
ses murs qui bougent.

## Ce que ça ne dit pas

* **Rien sur le signal.** Pas un rho, pas une corrélation, pas un signe.
* **Rien sur les autres symboles.** ETH et SOL n'ont pas de carnet profond.
* **Rien sur les jours d'exploration** (09-16), non construits à cette heure.

## Contrôles de bornes

`flee_ratio` est une proportion et `I(t)` un rapport normalisé : une valeur hors
bornes serait un défaut de calcul, jamais un résultat. Les deux comptes sont à
**zéro** — c'est le contrôle le plus élémentaire, et c'est précisément le genre
qu'on omet.

## Ce qui reste ouvert, et qui devra accompagner le résultat

`I(t)` porte un **cycle journalier** d'environ un écart-type (ADR-021 addendum 4,
dû à l'asymétrie des durées de vie bid/ask entre nuit et jour). Une corrélation
entre `I(t)` et le rendement pourrait donc n'être qu'un **effet d'heure de la
journée partagé par les deux**. Le contrôle correspondant — mesurer la
corrélation à heure contrôlée — est à prévoir **avant** de lire le résultat
d'E1, pas après.
