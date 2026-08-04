"""Bybit v5 linear — `orderbook.500`, snapshot + deltas chaînés par `u`.

Discipline Bybit : `type="snapshot"` remet le carnet à zéro ; `type="delta"`
doit porter `u = u_précédent + 1`. Tout saut = diffs manqués → on force une
nouvelle photo en se RÉABONNANT au topic (Bybit ne propose pas de photo REST
équivalente au chaînage Binance).
"""
from __future__ import annotations

import orjson

from .base import Adapter, apply_side, touch


class BybitAdapter(Adapter):
    name = "bybit"
    url = "wss://stream.bybit.com/v5/public/linear"
    ping_interval = 20.0

    def __init__(self, streams, log, on_trade=None):
        super().__init__(streams, log, on_trade)
        # Profondeurs valides en linear : 1 / 50 / 200 / 500 selon la doc, mais
        # `orderbook.500` est REFUSÉ en pratique (« handler not found », sondé le
        # 2026-07-28). 200 est la plus profonde qui réponde, et pousse à 100 ms.
        self.depth = 200
        self.by_native = {s.native: k for k, s in streams.items()}
        self.last_u: dict[str, int] = {}
        self._ws = None

    def ping_payload(self) -> str:
        return '{"op":"ping"}'

    def topic(self, native: str) -> str:
        return f"orderbook.{self.depth}.{native}"

    async def subscribe(self, ws) -> None:
        self._ws = ws
        args = [self.topic(s.native) for s in self.streams.values()]
        args += [f"publicTrade.{s.native}" for s in self.streams.values()]
        await ws.send(orjson.dumps({"op": "subscribe", "args": args}).decode())

    async def _resubscribe(self, native: str) -> None:
        """Force une photo fraîche : Bybit ré-émet un `snapshot` à l'abonnement."""
        if self._ws is None or not self.resync_allowed():
            return
        t = [self.topic(native)]
        await self._ws.send(orjson.dumps({"op": "unsubscribe", "args": t}).decode())
        await self._ws.send(orjson.dumps({"op": "subscribe", "args": t}).decode())

    async def on_message(self, msg) -> None:
        if not isinstance(msg, dict):
            return
        if msg.get("op") in ("subscribe", "unsubscribe", "pong") or msg.get("ret_msg") == "pong":
            return
        topic = msg.get("topic", "")
        if topic.startswith("publicTrade."):
            for tr in msg.get("data", []):
                sym = self.by_native.get(tr.get("s", ""))
                if sym is None:
                    continue
                # `S` = côté de l'AGRESSEUR (taker) chez Bybit.
                self.on_trade(self.streams[sym], float(tr["p"]), float(tr["v"]),
                              tr.get("S") == "Buy", tr.get("T"))
            return
        if not topic.startswith("orderbook."):
            return
        d = msg.get("data") or {}
        native = d.get("s") or topic.rsplit(".", 1)[-1]
        sym = self.by_native.get(native)
        if sym is None:
            return
        s = self.streams[sym]
        touch(s, msg.get("cts") or msg.get("ts"))
        u = d.get("u")

        if msg.get("type") == "snapshot":
            s.bids.clear()
            s.asks.clear()
            apply_side(s.bids, d.get("b", []))
            apply_side(s.asks, d.get("a", []))
            self.last_u[sym] = u
            s.synced = True
            s.reason = ""
            s.resyncs += 1
            return

        prev = self.last_u.get(sym)
        if prev is None or u != prev + 1:
            # Trou de séquence : on ne rafistole pas, on redemande une photo.
            s.reset(f"séquence u rompue ({prev} → {u})")
            await self._resubscribe(native)
            return
        apply_side(s.bids, d.get("b", []))
        apply_side(s.asks, d.get("a", []))
        self.last_u[sym] = u
