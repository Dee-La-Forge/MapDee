# ADR-003 — Stack tout-Python

**Statut** : acceptée (2026-07-28)

## Contexte
Le démon existant est en Node. Écrire les features en Python pour l'analyse et
en JS pour le live créerait un **train/serve skew** : deux implémentations qui
divergent silencieusement.

## Décision
Un seul langage, Python, du recorder au modèle. L'acquisition WS multi-venue est
réimplémentée en `asyncio`/`websockets`. La logique de resync du démon Node
(`U/u/pu` Binance, `seq` Bybit, `checksum` OKX, `l2Book` Hyperliquid —
`tools/sec-recorder.js:236-311`) sert de **spec de référence** : savoir gagné à
la dure, réécrit proprement, pas redécouvert.

## Conséquence
- Les features sont **littéralement le même code** en live et en offline.
- Le démon Node de prod n'est pas touché ; il continue de tourner.
