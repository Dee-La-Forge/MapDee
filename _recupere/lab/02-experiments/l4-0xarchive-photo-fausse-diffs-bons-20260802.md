# L4 0xArchive — la PHOTO est fausse, les DIFFS sont bons · 2026-08-02

_Contrôle C4 d'ADR-015, exécuté AVANT tout verdict de transfert. Script :
`experiments/check_l4_reconstruction.py`. Découvert en vérifiant, pas après coup._

## Le symptôme

Rejeu « photo L4 à T, puis diffs » sur BTC, 2026-07-29 12:00Z + 3 min, comparé
au mid observé par le recorder (flux Hyperliquid, 100 ms) :

```
écart médian 35,50 $ · p90 44,00 $ · max 87,00 $
photos à <= 1 tick (2 $) : 0,0 %
>>> C4 : ÉCHEC
```

## Le diagnostic — quatre venues mettent la photo en minorité

Le carnet reconstruit n'était **pas** croisé (bid 64 394,0 / ask 64 395,0,
spread 1 $) : le rejeu n'était pas en cause. Comparaison des mids au même
instant (2026-07-29 12:00:00Z), toutes sources de l'archive du recorder :

| source | mid |
|---|---|
| HYPERLIQUID (recorder) | 64 482,50 |
| BINANCE | 64 479,95 |
| BYBIT | 64 484,65 |
| OKX | 64 487,95 |
| **0xArchive, photo L4** | **64 394,50** |

**Quatre venues indépendantes s'accordent à 8 $ près ; la photo est 88 $ en
dessous.** Ce n'est pas un décalage temporel : un balayage de −40 s à +40 s ne
trouve aucun minimum (l'écart reste entre 26 et 43 $). Et le marché n'a valu
64 394,50 qu'à 06:33 et 19:16 ce jour-là, pas autour de midi.

Cause probable, avouée par la réponse elle-même : le champ **`diffs_applied: 0`**.
L'endpoint rend un point de contrôle **non avancé** jusqu'à l'instant demandé.

## La vérification qui tranche — reconstruire SANS la photo

Rejeu depuis un carnet **vide**, 20 min de chauffe, aucune photo utilisée :

```
bid 64 482,0  ask 64 483,0  ->  mid 64 482,50
référence recorder                    64 482,50      (identique)

écart médian 0,00 $ · p90 8,00 $ · max 21,00 $
photos à <= 1 tick (2 $) : 75,8 %
```

**L'écart médian passe de 35,50 $ à 0,00 $.** Les diffs sont fidèles ; c'est la
photo, et elle seule, qui était fausse.

## Conséquences

1. **La collecte en cours reste valide** — elle récupère les diffs et les
   trades, pas les photos.
2. **C4 est amendé** : reconstruction depuis les **diffs seuls, avec chauffe**,
   la photo n'est plus utilisée nulle part. Même esprit que le 30/07 : on
   répare l'instrument, jamais le seuil.
3. **Le seuil de 90 % NE BOUGE PAS.** À 20 min de chauffe on est à **75,8 %** —
   en dessous. Des ordres anciens manquent encore au carnet (2 149 ordres
   reconstruits). Il faut tester une chauffe d'**1 h**, comme le window-check
   du 30/07, avant de dire si C4 passe. Si 1 h ne suffit pas, C4 échoue et la
   porte ADR-015 ne rendra aucun verdict.

## Leçon, la quatrième de la nuit

Trois pièges d'appariement trouvés le 01→02/08, tous après coup. Celui-ci a été
trouvé **avant** — parce que le contrôle était écrit avant les données, et
qu'une source de référence indépendante existait (les 4 venues du recorder).
C'est ce que le pré-enregistrement achète, concrètement.
