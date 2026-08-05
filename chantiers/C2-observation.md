# C2 — L'observation du jour de banc : protocole, ÉCRIT AVANT DE REGARDER

> **Pré-enregistré le 05/08/2026, avant que le jour de banc n'existe** — le
> `20251208` se construit en ce moment. `05` §9.3 impose l'ordre : littérature
> (C0, fait) **puis** observation, **jamais** de définition posée après avoir
> vu la relation à une cible. Ce protocole dit ce qui sera regardé et ce qui
> en sortira ; il ne se renégocie pas après ouverture du jour.
>
> **Ce que C2 ne regarde JAMAIS** (`ADR-002`) : aucune relation à la cible,
> aucun classement de candidat. C2 produit des **distributions d'instrument**
> et les **constantes des définitions** — rien d'autre.

## 1. Le périmètre, fermé

Le jour de banc d'instrument : **`20251208`**, BTC et ETH (`ADR-000`,
addendum du 05/08). Artefacts : `deep` (+ `hl_orders` pour le typage par
`oid`, côté vérité). Aucun jour d'exploration n'est touché. Un jour regardé
est consommé — le 08 l'est déjà par destination : c'est le banc.

## 2. Les sorties, énumérées d'avance — six, pas une de plus

| # | sortie | ce qu'elle ferme |
|---|---|---|
| **S1** | distribution des masses par palier, par côté et par distance au mid (quantiles publiés) | la constante **M** du « mur » (`C0` §4 : `mag ≥ M × médiane_locale`) — proposée = le quantile tel que ~1 palier de bande sur 100 est un mur ; **la valeur exacte se lit, la règle de lecture est celle-ci** |
| **S2** | distribution des durées de persistance des paliers anormaux (au-dessus du M de S1) | la constante **P** (persistance minimale du mur, en photos) — proposée = la médiane des persistances au-dessus de M |
| **S3** | comparaison des deux variantes de « contact » (`C0` §4) : première exécution au palier CONTRE palier devient meilleure limite — taux de coïncidence, délai entre les deux | **le choix de la variante** : si coïncidence > 95 %, variante exécution (la moins chère) ; sinon les deux distributions sont publiées et le choix est un ADR |
| **S4** | distribution des distances au mid du flux exécuté (par transaction, quantiles fins en queue) | la **bande d'étude** = distance contenant 99,9 % du flux exécuté (`C0` §4), par symbole |
| **S5** | fraction de paires d'observations intra-unité qui se recouvrent (fenêtres des grandeurs A1/B2/C3 aux résolutions candidates) | le préalable d'É4 (`05` §9.4) — l'IC de Student vaut-il quelque chose |
| **S6** | coût de la journée `phase all`, poste par poste, chauffe comprise | le trou restant de `06` §8 |

## 3. La règle de fermeture de B7

Chaque définition de B7 se ferme par : **forme de C0** (commitée avant) +
**constante de S1-S4** (lue au jour de banc, règle de lecture pré-enregistrée
ci-dessus) + **ligne écrite dans `03`** avec la source des deux. Si une
distribution rend la règle de lecture absurde (par exemple S1 dégénérée), on
ne « choisit » pas un autre quantile : on le rapporte, et la règle se corrige
**par ADR** avant toute lecture supplémentaire.

## 4. Ce que ça n'ouvre pas

Le typage annulé/mangé/rechargé (`05` §9.3, table de contingence par strate)
exige la **vérité** (`oid`, côté L4) et vient APRÈS les définitions de B7 —
deuxième passe sur le même jour, protocole séparé. L'amplitude plausible
(`ADR-004`) reste à 2,0× tant que S1 n'a pas motivé un errata.
