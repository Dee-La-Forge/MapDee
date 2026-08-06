# Couverture J8 : la garde binaire a laissé passer un trou — 20251213 BTC n'a que 172 photos

> 06/08/2026. Déclenché par l'audit du log de construction (compteur de
> photos ETH gelé à 13 h le 15). La table complète des manifestes révèle
> plus grave que le point signalé.

## La table — photos valides (`deep_snaps`) et carnets croisés, J8 entier

| jour | BTC snaps | BTC croisés | ETH snaps | ETH croisés |
|---|---|---|---|---|
| 20251209 | 118 722 | 56 704 | 121 548 | 0 |
| 20251210 | 117 154 | 0 | 123 091 | 0 |
| 20251211 | 123 215 | 0 | 125 527 | 0 |
| 20251212 | 82 447 (≈69 %) | 12 961 287 | 86 339 (≈75 %) | 8 476 949 |
| **20251213** | **172 (≈0,14 %)** | **28 056 154** | ABSENT (trou acté) | 15 191 426 |
| 20251214 | 104 292 | 0 | 104 234 | 0 |
| 20251215 | 53 688 (≈44 %) | 41 653 597 | 56 216 (≈54 %) | 33 748 052 |
| 20251216 | 120 433 | 0 | (en construction) | — |

Référence de journée pleine : ~104 000-125 000 photos (le 14, mesuré sain
des deux côtés).

## Les quatre constats

1. **20251213 BTC est un trou de facto** : 172 photos, 28 M de carnets
   croisés. La garde de `construit/` teste l'intégrité du fichier
   (`_parquet_complet` : existence + pied de page PAR1) et le refus d'un
   jour sorti **sans** `deep` — jamais la couverture. 0 photo (13 ETH) a
   été refusé ; 172 photos (13 BTC) est passé. **Vérifié par lecture de
   `jour.py`/`lot.py`, pas déduit d'un log.**
2. **La note du 06/08 (« ETH 20251213 irréconstructible ») affirmait
   « BTC 20251213 se reconstruit normalement — le défaut est côté ETH
   seulement ». C'est FAUX** — constat tiré du non-échec du lot, pas d'une
   mesure. Corrigé par addendum daté sur la note même.
3. **L'incident d'archive couvre LES DEUX symboles, du 12 au 15**, avec le
   14 épargné : 12 au soir (69/75 %), 13 en entier (0,14 %/0 %), 15 à
   partir de 13 h (44/54 %). C'est un défaut de la capture Hyperliquid,
   pas d'un symbole. Le 16 BTC est plein ; le 16 ETH dira au manifeste.
4. **Les jours partiels sont biaisés vers le calme** : les heures perdues
   (après-midi/soir) portent 3 à 5 fois plus de flux que le matin. Deux
   jours amputés dans le même sens déplacent toute statistique à l'unité
   jour — c'est É3/É4 que ça mordra (toutes deux REFUSÉES à ce jour), et
   σ inter-journalier (C6) qui dimensionnera la réserve.

## Les décisions

1. **J8 est ré-amendé : « 09-16, moins 20251213 BTC ET ETH » = 14
   jour-symboles.** Même fondement que le 13 ETH : impossibilité
   matérielle — 172 photos n'est pas une journée, par aucune lecture
   honnête, et aucun seuil subtil n'est requis pour le dire (0,14 % contre
   44 % au pire des jours dégradés : trois ordres de grandeur). Constaté
   AVANT tout calcul de J8. `03` et `e0_reel.TROUS_ARCHIVE` portent
   l'amendement.
2. **20251212 et 20251215 (les deux symboles) RESTENT dans J8** comme
   jours dégradés documentés — les exclure au vu des compteurs serait de
   la chirurgie de périmètre post-hoc. Leur couverture est publiée ici,
   AVANT le tir.
3. **Un plancher de couverture est une barre nouvelle → ADR** :
   `ADR-007` (EN RÉDACTION) propose le mécanisme — la valeur appartient à
   Meddy. En attendant, défense existante : le plancher k/n d'É4 refuse
   déjà un jour à 172 observations pour tout bloc non trivial.
4. **Corrections en file pour `construit/`** (jamais sous un run) : le
   manifeste porte déjà `deep_snaps` et `book_croise` par jour — il
   manque `heures_a_zero_photo` et un refus à plancher dans `lot.py`,
   plus le préflight qui refuse un périmètre contenant un jour sous
   plancher. S'ajoute à la file du lanceur (ETAT §4 ter).

## La leçon

La même qu'hier, au carré : une garde binaire (vide/plein) laisse passer
tout ce qui est presque vide. Et un jour « vérifié sain » par le non-échec
d'un instrument n'a été vérifié par personne — **le non-échec n'est pas
une mesure.** Les compteurs des manifestes, eux, l'étaient depuis le
début : il suffisait de les ouvrir en table.
