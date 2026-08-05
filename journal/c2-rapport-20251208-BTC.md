# C2 — le jour de banc, moitié BTC : le carnet réel n'est pas celui qu'on imaginait

> 05/08/2026, ~17 h. Protocole gelé avant la livraison
> (`chantiers/C2-observation.md`, règles de lecture pré-enregistrées).
> Chiffres : `journal/c2-mesure-20251208-BTC.json` (manifeste `deep` certifié
> `ef4ff4f6…`, hash de protocole `0531a3f` dans la sortie). La moitié ETH
> viendra avec son jour, demain.

## Les quatre sorties rendues

| sortie | règle gelée | mesuré | statut |
|---|---|---|---|
| **S1 — M du mur** | quantile 0,99 du ratio masse / médiane de voisinage (±20 paliers, même côté) | **M = 485** (préfixe 25 000 ratios) | mécaniquement valide — **conceptuellement lourd, voir §2** |
| **S2 — P du mur** | persistance médiane au-dessus de M | **6 photos = 1,5 s** (46 512 épisodes) | valide, conditionné à la lecture de S1 |
| **S4 — bande d'étude** | distance contenant 99,9 % du flux exécuté | 50,26 % | **INVALIDE — voir §3.** La règle ne bouge pas ; l'implémentation se refait |
| **S5 — paires intra-unité** | fraction de paires d'observations du jour qui se recouvrent, par fenêtre | **≤ 0,001** (1e-4 à 1e-3, fenêtres 4-64) | **valide — le préalable d'É4 (`05` §9.4) est favorable** |

## 2. Ce que S1/S2 disent vraiment — l'intuition synthétique meurt au contact du réel

Le quantile 0,99 du ratio n'est pas 2, ni 10 : **485**. Le carnet réel à
±0,5 % du mid est hétérogène sur deux à trois ordres de grandeur — des paliers
de tête énormes posés sur un voisinage de poussière. Et ces paliers extrêmes
sont **fugaces** (persistance médiane 1,5 s) — cohérent avec ce que C5 a
montré du tissu de fond (vies médianes nulles, remplissages instantanés).

**Conséquence qui dépasse C2** : l'unité « multiple de la masse médiane du
voisinage » — celle des injections d'ÉS (D4) et de l'amplitude plausible
(`ADR-004`, barre 2,0) — **ne transporte pas du générateur au réel**. Sur le
carnet ZI, homogène, 2× le voisinage est une bosse visible ; sur le carnet
réel, 1 % des paliers dépassent 485×. La clause d'errata écrite dans
`ADR-004` (« révisable quand l'observation du jour de banc aura donné les
distributions réelles ») se déclenche : c'est l'objet d'`ADR-005`,
**PROPOSÉE** — elle rejugerait les verdicts ÉS sous la nouvelle unité, comme
`05` §10 l'exige. Rien n'est changé en attendant l'arbitrage.

## 3. S4 : l'approximation déclarée a cassé, et c'est rapporté — pas maquillé

« Mid horaire = médiane des prix exécutés de l'heure » donne une bande à
50 % du mid : absurde (le prix intra-heure bouge de ~0,1-1 %). Cause
probable : des `limitPx` nuls ou sentinelles sur une partie des statuts
`FILLED` (ordres au marché), que l'approximation ne filtre pas — le quantile
99,9 % attrape les artefacts. Le protocole prévoyait exactement ce cas
(« si une distribution rend la règle absurde, on le rapporte et on corrige
par ADR — on ne choisit pas un autre quantile en silence ») ; ici la règle
n'est pas en cause, **l'implémentation l'est** : la 2ᵉ passe (déjà prévue
pour S3) fera la jointure exécution ↔ mid du `deep` au même instant, et
vérifiera l'hypothèse `limitPx = 0` en publiant la part d'exécutions
écartées et leur raison.

## 4. Ce qui est bon à prendre dès maintenant

* **S5** : avec des fenêtres jusqu'à 64 photos, moins d'une paire
  d'observations sur mille se recouvre dans un jour de 122 191 photos —
  l'unité « jour » d'É4 est saine de ce point de vue ;
* **S6** : le jour `phase=all` coûte ~80 min (posté dans `06` §8) ;
* la chaîne entière — manifeste certifié → règles gelées → mesure → rapport
  des absurdités plutôt que leur maquillage — **a tourné sur données réelles
  sans intervention**.
