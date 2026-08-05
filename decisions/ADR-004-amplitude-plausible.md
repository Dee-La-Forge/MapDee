# ADR-004 — L'amplitude plausible du phénomène (D6)

**Date** : 2026-08-05 · **Statut** : **ACCEPTÉE le 05/08/2026** — sur
délégation explicite de Meddy (« prends les meilleures décisions pour le
projet », même jour). Révocable par lui comme toute ADR.
**Portée** : le seuil du critère d'arrêt d'`06` §7 (« aucune méthode ne
descend son plancher sous l'amplitude plausible → aucun jour de marché
consommé ») et la règle de sortie d'ÉS (`05` §8). Déclarée **avant** toute
mesure de plancher qui compte : la campagne v1 est annulée, la v2 n'a pas
encore tourné à cette heure.

---

## Décision

> **L'amplitude plausible du phénomène est fixée à 2,0 × la masse médiane du
> voisinage du palier** (±20 paliers, même côté — la même unité que les
> injections d'ÉS, décision D4).
>
> Une méthode dont le plancher de détection est **au-dessus de 2,0** est
> écartée : elle ne verrait pas le phénomène tel qu'il peut plausiblement
> exister. Un plancher **à 2,0 ou en dessous** admet la méthode à consommer
> des jours de marché.

## Pourquoi 2,0 — les deux appuis

* **C0 (littérature)** : un leurre doit être **vu pour agir** — sa taille
  anormale *relative à la profondeur locale* est ce qui le rend opérant. Une
  masse qui ne domine pas sa localité n'est ni un mur, ni un leurre, ni une
  absorption : en dessous de ~2× la localité, l'objet cherché n'existe pas
  conceptuellement.
* **C5 (mesuré, 18 jours-symboles, 182 381 lignes portefeuille-jour)** : le
  rapport taille p99/médiane par portefeuille atteint **7,8 au p95** — les
  acteurs réels posent couramment des ordres à plusieurs multiples de leur
  propre norme. Exiger qu'une méthode voie 2× n'exige rien d'exotique.

## Ce que ça ne fixe pas

La borne est **conservatrice et révisable par errata** quand l'observation du
jour de banc (C2) aura donné les distributions de masse par palier réelles —
dans ce cas, tout verdict d'ÉS rendu sous la borne 2,0 est **rejugé** sous la
nouvelle, comme `05` §10 l'exige pour tout changement de règle.
