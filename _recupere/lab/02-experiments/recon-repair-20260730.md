# Réparation de la reconstruction — deux défauts du producteur, mesurés puis corrigés

_30/07 · scripts : `experiments/export_mid.py`, `diag_recon_sides.py`, `diag_recon_vs_trades.py`,
`diag_recon_zombies.py`, `diag_disorder.py` · correctifs dans `gondetect/hl_book_reconstruct.py`
(`_reorder_stream` + clef secondaire, `reorder_ms=90 000` par défaut dans `l2_snapshots`)_

## Symptôme

Export du mid jour entier (nécessaire car le book perps10 à ~15 s ne retient que 27,5 % des
ordres) : mid reconstruit à **+97 $** du book officiel canonique après 1 h de rejeu, carnet
**croisé** (bids fantômes jusqu'à 312 $ au-dessus du vrai marché). La « validation 100 % » du
module n'avait jamais exercé un rejeu long (15 min max) — instrument sous-testé.

## Diagnostic (trois témoins)

- book officiel vs prix de transaction : **±0,50 $** → la référence est innocente ;
- reconstruction vs transactions : **+96,5 $** → la reconstruction est coupable ;
- autopsie des oid fantômes dans le fichier brut → **deux défauts distincts du producteur** :

1. **Fichier non trié dans le temps** — ~3-4 % des lignes en retard de 1 à 60 s
   (pire mesuré : **63 858 ms**, identique dans les DEUX datasets : BTC-only et perps10).
   Des annulations sont écrites physiquement avant leur placement → la machine à états
   jette l'annulation (oid inconnu) puis pose l'ordre pour toujours.
2. **Inversion INTRA-milliseconde** — des paires Place/Cancel du même oid au même
   timestamp, écrites Cancel d'abord. Un tri stable ne peut pas les réparer.

## Correctifs (dans `_reorder_stream`)

1. **Tampon de réordonnancement borné** : on ne livre que les lignes plus vieilles que
   `max_ts_vu − 90 s` (> pire retard), tri vectorisé par lots pyarrow — pas de tas Python
   à 1,36 milliard d'opérations.
2. **Clef secondaire** : à timestamp égal, les statuts qui POSENT (k=1 : open/triggered)
   passent avant ceux qui RETIRENT. Un oid ne peut pas être retiré avant d'exister, et les
   oid Hyperliquid ne sont pas réutilisés.

## Résultat

Window-check canonique (1 113 photos, 10 min, chauffe 1 h) :

| état | écart médian | photos au mid exact |
|---|---|---|
| avant | **+97,00 $** | 0,0 % |
| tampon seul | +97 → toujours faux (les paires intra-ms survivent au tri stable) | 0,0 % |
| tampon + clef secondaire | **+0,00 $** (p90 = 0,00, max 12 $) | **92,5 %** |

Résidu : 7,5 % des photos à ≤ 12 $ — compatible avec le jeu d'horloge du book de référence
(`server_time − timestamp_ms` ≈ −330 ms) pendant les mouvements rapides.

## Conséquences

- Les labels déjà produits (dict par oid, sans machine à états) sont **peu sensibles** à ces
  défauts — l'accord vérité-contre-vérité de 94,3 % le confirmait — mais la **porte
  d'étalonnage** (export jour entier 05-08 → labels sur mid reconstruit → seuils gelés :
  population ≥ 90 % du canonique, accord y_flee ≥ 98 %, Δt_contact p90 ≤ 2 s, fuite ±3 pts
  de 69,7 %) reste l'arbitre final avant de reconstruire les 5 jours.
- Leçon d'instrument, la troisième du projet : une validation qui ne couvre pas le régime
  d'usage réel (ici : rejeu LONG) ne valide rien. Toujours tester dans les conditions de
  l'usage, pas dans celles du confort.
