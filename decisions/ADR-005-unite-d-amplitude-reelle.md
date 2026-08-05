# ADR-005 — L'unité d'amplitude ne transporte pas du synthétique au réel

**Date** : 2026-08-05 · **Statut** : **PROPOSÉE — à trancher par Meddy.**
Pas d'auto-acceptation par délégation ici : cette décision **rejuge des
verdicts ÉS** (`05` §10) et touche un seuil (`06` §5 : les seuils
t'appartiennent).
**Origine** : la mesure S1 du jour de banc
(`journal/c2-rapport-20251208-BTC.md`), qui déclenche la clause d'errata
écrite dans `ADR-004`.

---

## Le constat mesuré

L'unité commune aux injections d'ÉS (D4) et à l'amplitude plausible
(`ADR-004` : barre à **2,0 × la masse médiane du voisinage ±20**) supposait
un voisinage homogène — vrai sur le générateur zero-intelligence, faux sur
le carnet réel : au jour de banc BTC, **le quantile 0,99 du ratio
masse/voisinage vaut 485**, pas 2-10. Sur données réelles, « 2× le
voisinage » ne décrit pas un mur : il décrit la poussière ordinaire.

## Décision proposée

> **L'amplitude s'exprime désormais en quantile de la distribution réelle
> des ratios du jour de banc, pas en multiple fixe.**
>
> * un « mécanisme plausible » est un palier qui **atteint le quantile 0,99**
>   du ratio masse/voisinage de son côté (= être un mur au sens de S1) ;
> * la barre d'admission d'ÉS devient : *le détecteur doit voir un mécanisme
>   dont l'amplitude est au quantile 0,99 réel* — le générateur devra donc
>   injecter à des ratios calés sur la distribution S1 du jour de banc
>   (BTC : 485 ; ETH : à mesurer demain), pas à 0,5-8× ;
> * conformément à `05` §10, **les verdicts ÉS sont rejugés** sous cette
>   unité : une campagne v5 avec la gamme d'amplitudes recalée, mêmes règles
>   par ailleurs. Les planchers actuels (0,5×/1,0×/8,0×) restent au registre
>   comme mesures de l'ancienne unité — on n'efface pas, on ajoute.

## L'alternative écartée, et pourquoi

Garder 2,0× et « laisser ÉS conservateur » : écartée — une barre que 1 % du
carnet ordinaire franchit en permanence ne sépare plus un mécanisme du bruit,
elle ne dit littéralement rien. Une admission rendue contre une barre vide
de sens n'est pas conservatrice, elle est décorative.

## Ce que ça ne change pas

S1/S2 (les définitions du mur pour B7) : leur règle de lecture a fonctionné —
M et P sont mesurés, la moitié ETH manque encore, et la fermeture de B7 suit
son chemin propre (forme C0 + constantes des deux symboles + ligne dans `03`).
