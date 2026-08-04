# ADR-015 — Porte « VENUE ou ÉPOQUE ? » v2, sur L4 récent

**Date** : 2026-08-02, 06 h 40 · **Statut** : à valider par Meddy
· **Écrit pendant que la collecte tourne, AVANT que la moindre donnée ne soit
exploitable.** Aucun chiffre de cette porte n'existe à cette heure.

## La question, et pourquoi elle reste ouverte

S6 a rendu **NO-GO** deux fois. Mais il comparait Hyperliquid en **mai** à
Binance en **fin juillet** : venue et époque bougeaient ensemble. ADR-014 a
tenté de trancher avec le flux public d'HL et a **échoué pour une raison
matérielle** — ce flux ne publie que 20 paliers et ne produit que 6 événements
en 4 jours (`flux-public-hyperliquid-inexploitable-20260802.md`).

Le L4 récent de 0xArchive (29/07 → 01/08, BTC + ETH, collecte en cours) referme
ce trou : profondeur complète **sur les jours que le recorder a déjà**.

## Les QUATRE contrôles d'appariement — le cœur de cette porte

Trois échecs de cette nuit viennent tous de la même faute : comparer deux
grandeurs qui ne mesurent pas la même chose. Les contrôles sont donc écrits
AVANT, et chacun est vérifiable.

### C1 — BANDE. Le L4 est coupé à ±0,4 % avant tout calcul.

Le L4 donne la profondeur complète ; le recorder Binance ne garde que
`SNAP_BAND = ±0,4 %`. Sans coupure, `med` serait calculée sur deux zones
différentes — **exactement le défaut qui a faussé le premier passage de S6**.
Principe déjà appliqué le 01/08 aux 6 jours de relance : **dégrader
l'instrument, jamais les seuils**.

*Vérification publiée* : distribution de `f_dist` des deux côtés, et part des
événements HL écartés par la coupure.

### C2 — CIBLE. Le proxy continu des DEUX côtés.

`y = tradé / (tradé + retiré)`, identique à S6 et au banc. La **vérité forte**
(ordre par ordre, wallet) est calculable côté HL et **ne sera pas** la cible :
elle servira de **témoin séparé**, jamais de terme de comparaison. Mélanger
vérité d'un côté et proxy de l'autre serait le mismatch parfait.

### C3 — CADENCE. La même chaîne d'agrégation, sans réécriture.

`bn_medium` importe déjà ses constantes de `hl_weak` (`SAMPLE_MS`,
`ARCH_EVERY`, `WPEAK`/`WMEAN`, `OCC_RHO`, `CONV_RHO`, `CV_K`, `CAP_TOP`,
`CAP_NEAR`). Le L4 passe par **cette même chaîne**. Aucune logique de features
n'est réécrite pour l'occasion.

*Vérification publiée* : nombre de lignes prod-like par jour des deux côtés,
qui doit être du même ordre (~8 600 lignes/jour à 10 s).

### C4 — RECONSTRUCTION. Le mid reconstruit doit coller au mid observé.

Rejouer les diffs pour reconstituer le carnet est l'opération qui avait
**deux défauts** trouvés le 30/07 (fichier non trié, inversions intra-ms,
+97 $ d'écart avant correctif). Les diffs de 0xArchive portent `block_number`
ET `seq` : l'ordre est déterministe, ce que le fichier Kaggle n'offrait pas.

*Porte de contrôle, PRÉ-ENREGISTRÉE ICI* : le mid reconstruit doit être à
**≤ 1 tick de l'écart médian** du mid publié par le flux Hyperliquid du
recorder sur la même fenêtre, sur **≥ 90 % des photos**. En dessous, la porte
**s'arrête** et ne rend aucun verdict de transfert — comme la porte
d'étalonnage refusée à 85,8 % le 30/07 ne s'est pas renégociée.

> **AMENDEMENT C4 (02/08, 07 h 00) — la photo de départ est ÉCARTÉE.**
> Exécuté le jour même : l'endpoint « photo L4 » de 0xArchive rend un point de
> contrôle **non avancé** jusqu'à l'instant demandé (`diffs_applied: 0`). Son
> mid était **88 $ sous** celui de quatre venues indépendantes du recorder
> (HL 64 482,50 · Binance 64 479,95 · Bybit 64 484,65 · OKX 64 487,95 contre
> **64 394,50**). Mesure et diagnostic :
> `lab/02-experiments/l4-0xarchive-photo-fausse-diffs-bons-20260802.md`.
>
> La reconstruction part donc d'un carnet **VIDE**, avec chauffe, **sans jamais
> utiliser la photo**. Vérifié : l'écart médian tombe de **35,50 $ à 0,00 $**.
> On répare l'instrument, jamais le seuil.
>
> **Le seuil de 90 % est INCHANGÉ.** À 20 min de chauffe on mesure **75,8 %** —
> insuffisant. La chauffe doit passer à **1 h** (durée du window-check du
> 30/07) et être re-mesurée. Si 1 h ne suffit pas, **C4 échoue** et cette porte
> ne rend aucun verdict.

### C5 — « RETIRÉ » ne doit pas contenir les EXÉCUTIONS

Un diff `remove` dit que l'ordre a quitté le carnet. **Il ne dit pas s'il a été
annulé ou mangé.** Compter tous les `remove` comme du retrait donnerait
`tradé / (tradé + tradé + annulé)` — une grandeur qui n'existe nulle part côté
Binance, où `traded` et la baisse de profondeur sont mesurés séparément.

*Contrôle* : jointure de chaque `remove` aux trades par **`order_id`** (champ
présent, vérifié le 02/08). Un `remove` apparié à un trade est une **exécution**,
les autres sont des **annulations**.

*Vérification publiée* : part des `remove` appariés à un trade, et volume total
des trades comparé au volume des removes appariés. Si les trades ne couvrent pas
les removes, l'écart est visible et chiffré au lieu d'être avalé.

### C6 — L'UNITÉ DE CLUSTER doit être la même des deux côtés

Côté Binance il n'y a **pas de wallet** : les clusters sont des **épisodes**.
Côté L4 les wallets existent et sont meilleurs — les utiliser serait pourtant
une faute, car les IC sont calculés **par cluster** : deux définitions
différentes rendent les barres d'erreur incomparables.

*Contrôle* : **épisodes des deux côtés**, sans exception. Les wallets HL sont
conservés en provenance, comme témoin séparé (registre des acteurs extrêmes),
et n'entrent dans aucune métrique de comparaison.

### C7 — La CHAUFFE DES FEATURES, distincte de celle du carnet

C4 réchauffe le **carnet**. Mais `build_events` a besoin d'historique pour la
persistance, l'âge et l'occupation (LOOKBACK 300 s) : `gen_prodrows` écarte
pour cela les **20 premières minutes** de chaque journée (`WARMUP_MS`).
Appliquer cette coupe d'un côté et pas de l'autre décalerait le début des deux
populations dans la journée.

*Contrôle* : **même fenêtre de chauffe écartée des deux côtés**.

*Vérification publiée* : heure de début effective et nombre d'événements de
chaque population, par jour.

### C8 — Bornes de journée

Le recorder tourne en journées **UTC** ; la collecte L4 utilise les mêmes
bornes. À vérifier plutôt qu'à supposer.

*Vérification publiée* : premier et dernier horodatage retenus de chaque côté,
par jour.

## Features — 16, celles du 2e passage de S6

`f_mult` et `f_logmag` restent exclues (elles valent `mag/med`). Même si C1
égalise la bande, la médiane reste sensible à la composition du carnet ; on ne
réintroduit pas une grandeur qui a déjà faussé une porte cette nuit.

## Le dispositif — une seule variable

| entraîné sur | évalué sur | ce que ça mesure |
|---|---|---|
| HL juillet | HL juillet (LODO par jour) | plafond intra-venue HL |
| Binance juillet | Binance juillet (LODO) | plafond intra-venue Binance |
| **HL juillet** | **Binance juillet** | **le transfert, à époque égale** |
| Binance juillet | HL juillet | symétrie |

Mêmes jours (29/07 → 01/08), mêmes heures, même bande, même cible, même
agrégation. **Seule la venue change.**

## Seuils — repris d'ADR-012, inchangés

1. AUC pairwise ≥ **0,55**, IC95 excluant 0,5.
2. `edge_transfert ≥ 0,50 × edge_plafond` de la venue cible.
3. **Les deux symboles**.
4. < 60 clusters dans une cellule → puissance insuffisante, dite comme telle.

Métrique identique au jalon et à S6 : fenêtre 300 s, décidabilité 0,10,
plafond 200 paires par couple de clusters, 400 bootstraps par clusters de
base, clusters = épisodes. p de permutation (200 tirages) publié en plus,
**informatif, jamais décisoire**.

## Les trois lectures, écrites AVANT

- **Le transfert TIENT** → la venue n'est pas la barrière. Le NO-GO de S6
  s'explique par l'époque ou par le passage vérité L4 → proxy observable. Le
  programme repart sur une fenêtre simultanée.
- **Le transfert ÉCHOUE, plafonds sains** → la venue EST la barrière. S6 est
  confirmé pour la bonne raison, et l'hypothèse du transfert direct L2 meurt
  proprement.
- **Les PLAFONDS sont bas** → ni venue ni époque : le proxy observable à 100 ms
  ne porte pas de signal exploitable, nulle part. Le plus lourd des trois.

## Ce que cette porte ne dira PAS

Elle compare **deux observables** ; la vérité forte n'entre pas dans la cible.
Elle mesure la **transférabilité entre venues**, pas la valeur économique ni la
véracité du label. Elle ne remplace ni le jalon, ni S6, ni P0-FRAG.

## Réserve d'honnêteté

Trois pièges d'appariement ont été découverts dans la seule nuit du 01→02/08,
tous après coup. Rien ne garantit qu'il n'en reste pas un quatrième. Les quatre
contrôles ci-dessus sont écrits avant les données : ils sont donc vérifiables
par un tiers, et impossibles à ajuster après lecture d'un résultat. C'est la
seule garantie qui vaille — pas la confiance dans celui qui a écrit le code.
