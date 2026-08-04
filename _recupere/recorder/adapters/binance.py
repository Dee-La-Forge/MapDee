"""Binance USDⓈ-M futures — diffs `depth@100ms` + photo REST, chaînage U/u/pu.

Port fidèle de `tools/sec-recorder.js:243-311`. La subtilité coûteuse, apprise à
la dure côté Node et conservée ici : **le premier événement après la photo** est
valide s'il la CHEVAUCHE (`U ≤ lastUpdateId ≤ u`) ou s'il chaîne pile dessus
(`pu == lastUpdateId`). Exiger `pu` dès le premier événement fait boucler le
resync à l'infini. Ensuite seulement, `pu` doit chaîner sur le `u` précédent.
"""
from __future__ import annotations

import asyncio
import random

import orjson

from gondetect import config as C

from ..state import Stream
from .base import Adapter, apply_side, touch

REST = "https://fapi.binance.com/fapi/v1/depth"


class BinanceAdapter(Adapter):
    name = "binance"

    def __init__(self, streams, log, on_trade=None):
        super().__init__(streams, log, on_trade)
        self.url = ("wss://fstream.binance.com/stream?streams="
                    + "/".join(f"{s.native.lower()}@depth@100ms" for s in streams.values()))
        self.last_u: dict[str, int] = {}
        self.chained: dict[str, bool] = {}
        self.buf: dict[str, list[dict]] = {k: [] for k in streams}
        self.syncing: set[str] = set()
        self.by_native = {s.native: k for k, s in streams.items()}

    async def subscribe(self, ws) -> None:
        return  # les streams sont dans l'URL

    async def on_message(self, msg) -> None:
        ev = msg.get("data") if isinstance(msg, dict) else None
        if not ev or ev.get("e") != "depthUpdate":
            return
        sym = self.by_native.get(ev.get("s", ""))
        if sym is None:
            return
        s = self.streams[sym]
        touch(s, ev.get("T") or ev.get("E"))

        if not s.synced:
            b = self.buf[sym]
            b.append(ev)
            if len(b) > 4000:
                b.pop(0)
            if sym not in self.syncing:
                asyncio.create_task(self.sync(sym))
            return

        if not self.chained.get(sym):
            if ev["u"] < self.last_u[sym]:
                return                                   # antérieur à la photo
            if (ev["U"] <= self.last_u[sym] <= ev["u"]) or ev.get("pu") == self.last_u[sym]:
                self._apply(s, sym, ev)
                self.chained[sym] = True
                return
            s.reset("photo dépassée (diffs manqués)")     # photo trop vieille
            self.buf[sym] = [ev]
            if sym not in self.syncing:
                asyncio.create_task(self.sync(sym))
            return

        if ev.get("pu") != self.last_u[sym]:
            s.reset("chaînage pu rompu")
            self.chained[sym] = False
            self.buf[sym] = [ev]
            self.log(f"[binance] {sym} désynchronisé — resync")
            if sym not in self.syncing:
                asyncio.create_task(self.sync(sym))
            return

        self._apply(s, sym, ev)

    def _apply(self, s: Stream, sym: str, ev: dict) -> None:
        apply_side(s.bids, ev.get("b", []))
        apply_side(s.asks, ev.get("a", []))
        self.last_u[sym] = ev["u"]

    async def sync(self, sym: str) -> None:
        """Photo REST + rejeu du tampon selon la règle U/u/pu des futures."""
        self.syncing.add(sym)
        s = self.streams[sym]
        try:
            if not self.resync_allowed():
                await asyncio.sleep(15 + random.random() * 10)
                return
            o = await self.get_json(REST, params={"symbol": s.native, "limit": 1000})
            s.bids.clear()
            s.asks.clear()
            apply_side(s.bids, o["bids"])
            apply_side(s.asks, o["asks"])
            self.last_u[sym] = o["lastUpdateId"]

            chained, saw_newer = False, False
            for ev in self.buf[sym]:
                if ev["u"] < self.last_u[sym]:
                    continue
                if not chained:
                    if ev["U"] <= self.last_u[sym] <= ev["u"]:
                        self._apply(s, sym, ev)
                        chained = True
                    elif ev["U"] > self.last_u[sym]:
                        saw_newer = True
                    continue
                if ev.get("pu") != self.last_u[sym]:
                    raise RuntimeError("tampon discontinu")
                self._apply(s, sym, ev)
            if not chained and saw_newer:
                raise RuntimeError("photo trop vieille")

            self.buf[sym] = []
            s.synced = True
            s.reason = ""
            self.chained[sym] = chained
            s.resyncs += 1
        except Exception as e:
            self.buf[sym] = self.buf[sym][-2000:]
            s.reset(f"resync échoué : {e!r}")
            await asyncio.sleep(5 + random.random() * 5)
        finally:
            self.syncing.discard(sym)
            if not s.synced and self.buf[sym]:
                asyncio.create_task(self.sync(sym))


    # ------------------------------------------------------------- aggTrade --
    def extra_loops(self):
        return [self.run_trades()]

    async def run_trades(self) -> None:
        """Socket DÉDIÉE aux transactions, sur le chemin ROUTÉ `/market/stream`.

        Contrainte connue de la prod (sondée le 2026-07-25, `sec-recorder.js:507`) :
        le chemin routé est obligatoire pour `aggTrade` et muet pour le depth ;
        le chemin nu fait exactement l'inverse. On ne peut donc pas tout mettre
        sur une seule socket.
        """
        import asyncio
        import random

        import orjson as _oj
        import websockets

        url = ("wss://fstream.binance.com/market/stream?streams="
               + "/".join(f"{s.native.lower()}@aggTrade" for s in self.streams.values()))
        backoff = C.WS_BACKOFF_MIN_S
        while True:
            try:
                async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
                    self.log("[binance] socket transactions connectée")
                    backoff = C.WS_BACKOFF_MIN_S
                    async for raw in ws:
                        d = (_oj.loads(raw) or {}).get("data") or {}
                        if d.get("e") != "aggTrade":
                            continue
                        sym = self.by_native.get(d.get("s", ""))
                        if sym is None:
                            continue
                        # `m` = l'acheteur était MAKER ⇒ l'agresseur est VENDEUR.
                        self.on_trade(self.streams[sym], float(d["p"]), float(d["q"]),
                                      not d.get("m", False), d.get("T"))
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self.log(f"[binance] socket transactions coupée : {e!r} — retry {backoff:.0f}s")
            await asyncio.sleep(backoff + random.random())
            backoff = min(C.WS_BACKOFF_MAX_S, backoff * 2)
