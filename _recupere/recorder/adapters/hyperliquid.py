"""Hyperliquid — canal `l2Book` : PHOTO COMPLÈTE à chaque message.

Aucun chaînage, aucun resync : chaque message remplace le carnet. C'est la venue
la plus simple à enregistrer, et la plus importante du programme — c'est elle
dont on achètera le **L4** en P2, donc c'est elle qui aligne les features live
sur les labels forts (ADR-007).

Deux limites à connaître :
  * `l2Book` public ne renvoie que ~20 paliers par côté (contre 400-1000 ailleurs) :
    la profondeur enregistrée est structurellement plus fine ;
  * Hyperliquid avance par **blocs**, pas par moteur d'appariement continu — la
    microstructure sub-100 ms n'est pas comparable à celle d'un CEX (c'est un
    risque déjà identifié au programme §4, pas une surprise).
"""
from __future__ import annotations

import orjson

from .base import Adapter, touch


class HyperliquidAdapter(Adapter):
    name = "hyperliquid"
    url = "wss://api.hyperliquid.xyz/ws"
    ping_interval = 30.0

    def __init__(self, streams, log, on_trade=None):
        super().__init__(streams, log, on_trade)
        self.by_native = {s.native: k for k, s in streams.items()}

    def ping_payload(self) -> str:
        return '{"method":"ping"}'

    async def subscribe(self, ws) -> None:
        for s in self.streams.values():
            await ws.send(orjson.dumps({
                "method": "subscribe",
                "subscription": {"type": "l2Book", "coin": s.native},
            }).decode())
            # `trades` porte `users: [acheteur, vendeur]` — les SEULES identités
            # de portefeuille disponibles gratuitement, sur aucune autre venue.
            await ws.send(orjson.dumps({
                "method": "subscribe",
                "subscription": {"type": "trades", "coin": s.native},
            }).decode())

    async def on_message(self, msg) -> None:
        if not isinstance(msg, dict):
            return
        ch = msg.get("channel")
        if ch in ("subscriptionResponse", "pong"):
            return
        if ch == "trades":
            for tr in msg.get("data", []) or []:
                sym = self.by_native.get(tr.get("coin", ""))
                if sym is None:
                    continue
                # côté "B" = agresseur acheteur chez Hyperliquid
                self.on_trade(self.streams[sym], float(tr["px"]), float(tr["sz"]),
                              tr.get("side") == "B", tr.get("time"), tr.get("users"))
            return
        if ch != "l2Book":
            return
        d = msg.get("data") or {}
        sym = self.by_native.get(d.get("coin", ""))
        if sym is None:
            return
        s = self.streams[sym]
        touch(s, d.get("time"))
        levels = d.get("levels") or []
        if len(levels) != 2:
            return
        # Photo complète : on remplace, on ne fusionne pas.
        s.bids = {float(l["px"]): float(l["sz"]) for l in levels[0] if float(l["sz"]) > 0}
        s.asks = {float(l["px"]): float(l["sz"]) for l in levels[1] if float(l["sz"]) > 0}
        s.synced = True
        s.reason = ""
