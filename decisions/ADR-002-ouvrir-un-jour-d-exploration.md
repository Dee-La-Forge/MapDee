# ADR-002 — Ce que veut dire « ouvrir un jour d'exploration »

**Date** : 2026-08-05 · **Statut** : **ACCEPTÉE le 05/08/2026** — sur
délégation explicite de Meddy (« prends les meilleures décisions pour le
projet », même jour), la décision proposée ci-dessous étant acceptée telle
quelle, sans modification. Révocable par lui comme toute ADR.
**Origine** : audit de Meddy du 05/08, constat I.1.

---

## Contexte

Deux règles du dépôt ne peuvent pas coexister :

* `06` §10 : « aucun **jour d'exploration ouvert** avant que C3 ne soit gelé et
  commité » — et `ETAT` B2 a durci : « la bonne réponse est *rien* » ;
* `06` §11 : « **C5 est lancé** » — sur les jours 08-16, avec un protocole
  pré-enregistré et commité avant le premier calcul.

Le même document déclare C5 sans verrou et interdit ce qu'il fait.

## Le point qui tranche presque seul

Lue littéralement, la règle interdit aussi **C2** — regarder les trajectoires
brutes sur le jour de banc. Or l'ordre du plan est `C2 → C3` : **on ne peut pas
écrire les définitions sans avoir regardé, et la règle littérale interdit de
regarder avant d'avoir écrit.** La lecture littérale rend le plan inexécutable
par circularité. Ce n'est donc pas une lecture possible de la règle — c'est une
formulation trop large de ce qu'elle voulait protéger.

## Ce que la règle protège réellement

La faute qu'elle existe pour empêcher est documentée quatre fois dans ce
dossier : **construire une cible après avoir vu les distributions**, puis la
« découvrir ». Le danger n'est pas de regarder un jour — c'est de regarder **la
relation à la cible** avant que la cible ne soit gelée, ou de regarder **sans
protocole écrit d'avance**.

## Décision proposée

> **« Ouvrir un jour d'exploration » est interdit dans deux cas, et deux
> seulement :**
>
> 1. **toute mesure qui référence la cible** — signe, corrélation, gain — avant
>    que C3 ne soit gelé et commité ;
> 2. **toute lecture sans protocole pré-enregistré commité avant le premier
>    calcul**, périmètre déclaré inclus.
>
> Hors ces deux cas, un jour d'exploration peut être lu. **Sa consommation
> reste actée** : un jour regardé ne peut plus entrer dans la réserve, quelle
> que soit la légitimité du regard.

Conséquences immédiates si accepté :

* **C5 est légitime** — protocole commité avant, aucun référencement de la
  cible ;
* **C2 est légitime** sur le jour de banc — c'est même sa raison d'être ;
* **É0 et É2 sont légitimes** sur périmètre minimal déclaré en fiche — ce sont
  des corrélations entre candidats, pas contre la cible ;
* **É3 et É4 restent interdits** avant C3 — ils référencent la cible ;
* `06` §10 et `ETAT` B2 sont réécrits dans ces termes.

## L'alternative écartée, et pourquoi

**La lecture littérale** — tout regard consomme, C5 s'arrête, ses distributions
sont scellées. Écartée parce qu'elle interdit C2, donc rend C3 inatteignable,
donc le plan entier inexécutable. Une règle dont l'application stricte détruit
la séquence qu'elle protège n'est pas une règle, c'est une erreur de
formulation.

## Ce que ça ne rouvre pas

L'interdit sur la **réserve** (17-23) et la **zone d'extension** (24-31) est
d'une autre nature — il ne dépend pas de la cible, il protège des jours
**jamais regardés**. Rien ici ne l'assouplit.
