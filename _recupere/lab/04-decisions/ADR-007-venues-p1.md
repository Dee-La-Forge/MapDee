# ADR-007 — Cinq venues pour le recorder P1

**Statut** : acceptée (2026-07-28, décision Meddy : « couverture max »)

## Contexte
La cohérence multi-venue est l'un des deux discriminants orthogonaux (ADR-001) :
tenir longtemps est gratuit, tenir **sur N venues** coûte N fois plus. Le nombre
de venues fixe donc directement le pouvoir de ce discriminant.

## Décision
**Binance + Bybit + OKX + Coinbase + Hyperliquid (L2)**, 2 symboles, cadence 100 ms.

## Conséquence
- Débit d'écriture ≈ **19×** l'actuel → dimensionner stockage et rotation dès le
  départ ; batcher les appends à 100 ms ; rate-limiter le REST **par venue**.
- Cinq surfaces de panne WS : reconnexion par venue, **gaps marqués honnêtement**
  (jamais maquillés).
- Hyperliquid au recorder **aligne les features live sur le L4 labellisé** de P2 —
  c'est ce qui rend le test de transfert direct.
- Alignement inter-venue = **écart RELATIF au mid**, binné sur un `bs`/mid de
  référence (Binance) ; jamais de prix absolu (tick sizes, basis, mid distincts).
- Horodatage : **réception locale** (synchro inter-venue) **+** timestamp venue.

## Conséquence MESURÉE au lancement (2026-07-28, run de vérification P1)

Les cinq venues ne publient pas la même **profondeur**, et l'écart est massif :

| venue | flux | portée autour du mid (BTC) |
|---|---|---|
| Binance | `depth@100ms`, carnet complet | ±0,40 % (toute la bande enregistrée) |
| Coinbase | `level2_batch`, carnet complet | ±0,39 % |
| OKX | `books` — 400 paliers | ±0,069 % |
| Bybit | `orderbook.200` — 200 paliers (`orderbook.500` est REFUSÉ en linear) | ±0,039 % |
| Hyperliquid | `l2Book` — **20 paliers par côté** | **±0,031 %** |

**La cohérence multi-venue ne peut donc s'évaluer que sur l'intersection** :
**±0,031 % (BTC) / ±0,101 % (ETH)** pour les 5 venues ; ±0,069 % / ±0,210 % pour
3 ; ±0,39 % pour Binance+Coinbase seules. Au-delà, la venue la moins profonde ne
dit **rien** — et **absence ≠ retrait** : confondre les deux reproduirait
exactement l'erreur que l'ADR-005 interdit.

### Ce que ça change
1. Le second discriminant (cohérence) porte sur une population **proche du mid**.
   Ce n'est pas absurde : « survivre au contact » suppose que le prix est AU
   niveau, donc dans la bande couverte. Mais les features de cohérence lues à
   l'OBSERVATION (le niveau est alors à 0,12–0,8 % du mid en P0) ne sont
   disponibles, pour BTC, sur aucune venue autre que Binance et Coinbase.
2. **ETH est trois fois mieux couvert que BTC** (±0,101 % contre ±0,031 %) —
   argument supplémentaire, non prévu, en faveur du choix de l'ADR-004.
3. Toute mesure de cohérence doit **déclarer sa portée** : un score calculé
   au-delà de la bande commune serait un artefact de profondeur, pas un fait.

### Non retenu
Approfondir les flux : Bybit plafonne à 200 en linear ; OKX `books-l2-tbt`
(400 tick-by-tick) exige VIP4+ ; Hyperliquid n'expose pas de `l2Book` plus
profond. Aucune de ces limites ne se contourne sans compte privilégié.
