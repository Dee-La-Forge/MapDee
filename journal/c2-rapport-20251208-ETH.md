# C2 — le jour de banc, moitié ETH : les constantes sont par symbole

> 06/08/2026, ~03 h 40. Même protocole gelé, même script, manifeste certifié
> `7ac6ebcd…`, hash `2c8700e`. Chiffres :
> `journal/c2-mesure-20251208-ETH.json`. Complète
> `journal/c2-rapport-20251208-BTC.md`.

## Les deux symboles côte à côte

| sortie | BTC | ETH | lecture |
|---|---|---|---|
| **S1 — M du mur** (quantile 0,99 du ratio) | 485 | **175** | par symbole, facteur ~3 — réserve : la grille ETH est plus fine (`bs` 0,1 contre 2), le voisinage ±20 paliers n'y couvre pas la même distance ; la comparaison brute entre symboles est à manier avec ça en tête |
| **S2 — P** (persistance médiane) | 6 photos (1,5 s) | **4 photos (1 s)** | même monde : les murs réels sont fugaces partout |
| **S4 — bande** | 50,3 % (invalide) | **99,7 % (invalide)** | l'artefact `limitPx` est quasi certain (ETH frôle 100 %) — la règle 99,9 % ne bouge pas, la 2ᵉ passe par jointure au mid du `deep` est l'unique voie |
| **S5 — paires recouvrantes** | ≤ 0,001 | ≤ 0,001 | structurel — le préalable d'É4 est levé pour les deux symboles |

## Conséquence pour B7

Le « mur » a désormais **sa forme (C0) et ses deux constantes mesurées** —
il est techniquement fermable. Décision : **B7 se fermera d'un bloc**, les
trois définitions ensemble, après la 2ᵉ passe (S3 contact + S4 bande par
jointure) — fermer le mur seul à 3 h du matin n'apporterait rien et
fragmenterait la fermeture. La 2ᵉ passe est le dernier verrou de B7.
