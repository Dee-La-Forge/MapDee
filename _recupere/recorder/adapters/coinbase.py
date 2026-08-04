"""Coinbase Exchange — canal `level2_batch` (SPOT BTC-USD / ETH-USD).

⚠ **Spot, pas perp** : les perpétuels Coinbase sont sur Coinbase International,
inaccessible sans compte/clé. Le flux public de Coinbase Exchange ne donne que le
spot. C'est assumé (ADR-007) : l'alignement inter-venue se fait en écart RELATIF
au mid de chaque venue, donc le basis spot/perp ne fausse pas la cohérence — il
faudra simplement ne jamais comparer des prix absolus.

`level2_batch` est la variante publique agrégée (~50 ms côté Coinbase) ; `level2`
exige une authentification. Protocole : une photo `snapshot` puis des `l2update`
sans numéro de séquence — il n'y a donc **rien à chaîner** : on fait confiance au
transport, et toute coupure WS repart d'une photo neuve.
"""
from __future__ import annotations

import orjson

from .base import Adapter, touch


class CoinbaseAdapter(Adapter):
    name = "coinbase"
    url = "wss://ws-feed.exchange.coinbase.com"

    def __init__(self, streams, log, on_trade=None):
        super().__init__(streams, log, on_trade)
        self.by_native = {s.native: k for k, s in streams.items()}

    async def subscribe(self, ws) -> None:
        await ws.send(orjson.dumps({
            "type": "subscribe",
            "product_ids": [s.native for s in self.streams.values()],
            "channels": ["level2_batch", "matches"],
        }).decode())

    async def on_message(self, msg) -> None:
        if not isinstance(msg, dict):
            return
        typ = msg.get("type")
        if typ == "error":
            self.log(f"[coinbase] erreur : {msg.get('message')} — {msg.get('reason')}")
            for s in self.streams.values():
                s.reset(f"refus Coinbase : {msg.get('message')}")
            return
        if typ in ("subscriptions", "heartbeat"):
            return
        if typ in ("match", "last_match"):
            sym = self.by_native.get(msg.get("product_id", ""))
            if sym is not None:
                # ⚠ Chez Coinbase, `side` est le côté du MAKER : l'agresseur est
                # l'inverse. Se tromper ici inverserait tout le flux acheteur/vendeur.
                self.on_trade(self.streams[sym], float(msg["price"]), float(msg["size"]),
                              msg.get("side") == "sell", None)
            return
        sym = self.by_native.get(msg.get("product_id", ""))
        if sym is None:
            return
        s = self.streams[sym]
        touch(s)

        if typ == "snapshot":
            s.bids.clear()
            s.asks.clear()
            for p, q in msg.get("bids", []):
                if float(q) > 0:
                    s.bids[float(p)] = float(q)
            for p, q in msg.get("asks", []):
                if float(q) > 0:
                    s.asks[float(p)] = float(q)
            s.synced = True
            s.reason = ""
            s.resyncs += 1
        elif typ == "l2update":
            for side, p, q in msg.get("changes", []):
                book = s.bids if side == "buy" else s.asks
                px, qty = float(p), float(q)
                if qty <= 0:
                    book.pop(px, None)
                else:
                    book[px] = qty
