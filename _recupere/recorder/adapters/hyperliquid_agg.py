"""Hyperliquid AGRÉGÉ — le même `l2Book`, mais à prix regroupés.

## Pourquoi ce fichier existe

`l2Book` rend **toujours 20 paliers par côté**. À la résolution native (pas de
1 $ sur BTC) ça ne porte qu'à **±0,03 % du mid** — très en deçà de la bande
d'étude du programme, 0,12 à 0,80 %. Le recorder était donc structurellement
aveugle aux objets qu'il est censé enregistrer, et `SNAP_BAND` n'y pouvait rien :
la limite n'est pas ce qu'on garde, c'est ce que la venue envoie.

`nSigFigs` regroupe les prix. Les 20 paliers portent alors beaucoup plus loin.

## La correspondance, MESURÉE — et l'erreur qu'elle a corrigée

Premier essai, le 04/08/2026 : les cinq résolutions abonnées sur UNE connexion,
et la correspondance déduite de l'ordre des réponses. **C'était une supposition,
et elle était fausse d'un cran.** Les messages agrégés ne portent que `coin`,
`time` et `spread` — ils ne disent PAS de quelle résolution ils viennent, donc
rien ne permettait cette attribution.

Mesuré ensuite proprement, une connexion par résolution, BTC à 64 295 $ :

    nSigFigs   pas du prix   portée      couvre 0,12-0,80 % ?
    (aucun)          1 $     0,032 %     non
    5                1 $     0,032 %     non — identique au natif
    4               10 $     0,303 %     partiellement
    3              100 $     3,030 %     OUI
    2            1 000 $    30,2 %       oui, mais inexploitable

On enregistre donc **4 et 3** : le premier donne la finesse près du prix, le
second couvre la bande entière.

C'est aussi la justification du choix « une venue par résolution » : sans
connexions séparées, l'attribution reste une devinette — et elle s'est
effectivement révélée fausse.

## Ce que ça n'est pas

Ce n'est **pas** de la profondeur au sens du L4 : les paliers sont des seaux de
100 $, pas des ordres individuels. Ça sert à VOIR les murs en direct, pas à les
étudier un par un. L'étude a besoin du L4, qui ne s'obtient qu'avec un nœud.
"""
from __future__ import annotations

import orjson

from .hyperliquid import HyperliquidAdapter


class _HyperliquidAgg(HyperliquidAdapter):
    """`l2Book` avec `nSigFigs`. Une sous-classe par résolution."""

    nsigfigs: int = 4

    async def subscribe(self, ws) -> None:
        # Pas de souscription `trades` ici : elle est déjà portée par la venue
        # `hyperliquid` native. La dupliquer compterait chaque transaction deux
        # fois dans le flux, et fausserait `flow` d'un facteur 2 — c'est la même
        # faute que `hl_fills` qui compte double.
        for s in self.streams.values():
            await ws.send(orjson.dumps({
                "method": "subscribe",
                "subscription": {"type": "l2Book", "coin": s.native,
                                 "nSigFigs": self.nsigfigs},
            }).decode())


class HyperliquidFinAdapter(_HyperliquidAgg):
    """Pas de 10 $ sur BTC — portée ~0,30 %. Finesse près du prix."""
    name = "hyperliquid_fin"
    nsigfigs = 4


class HyperliquidLargeAdapter(_HyperliquidAgg):
    """Pas de 100 $ sur BTC — portée ~3,03 %. **Couvre la bande d'étude.**"""
    name = "hyperliquid_large"
    nsigfigs = 3
