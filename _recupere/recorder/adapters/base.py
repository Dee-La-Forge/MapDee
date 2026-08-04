"""Socle commun aux adapters de venue.

Chaque venue apporte : une URL WS, un message d'abonnement, une façon d'appliquer
ses messages au carnet, et sa propre discipline de resynchronisation. Le reste
(boucle de connexion, backoff, détection de flux mort, plafond de resyncs REST)
est mutualisé ici — c'est la partie où le démon Node s'est fait mal, et qu'on
réécrit proprement une seule fois (`tools/sec-recorder.js:236-311` = spec).
"""
from __future__ import annotations

import asyncio
import random
import time

import aiohttp
import orjson
import websockets

from gondetect import config as C

from ..state import Stream, now_ms


class Adapter:
    name = "?"
    url = ""
    ping_interval: float | None = None   # None = laisser websockets gérer le ping
    ws_kwargs: dict = {}

    def __init__(self, streams: dict[str, Stream], log, on_trade=None):
        self.streams = streams          # symbole canonique → Stream
        self.log = log
        # Callback fourni par le moteur : (stream, prix, taille_base, acheteur?,
        # ts_venue, users) — voir Engine.on_trade.
        self.on_trade = on_trade or (lambda *a, **k: None)
        self._resyncs: list[float] = []
        self.session: aiohttp.ClientSession | None = None

    # ------------------------------------------------------------- à fournir --
    async def subscribe(self, ws) -> None:
        raise NotImplementedError

    async def on_message(self, msg: dict | list) -> None:
        raise NotImplementedError

    async def prepare(self) -> None:
        """Appelé une fois avant la première connexion (métadonnées d'instrument)."""

    def extra_loops(self) -> list:
        """Connexions WS supplémentaires. Binance en a besoin : le chemin routé
        `/market/stream` est OBLIGATOIRE pour `aggTrade` et MUET pour le depth,
        et le chemin nu fait l'inverse (sondé en prod le 2026-07-25,
        `sec-recorder.js:507-509`). Deux sockets, donc."""
        return []

    # ------------------------------------------------------------- mutualisé --
    def resync_allowed(self) -> bool:
        """Plafond de snapshots REST par minute — un flap WS ne doit pas se
        transformer en rafale de requêtes (429 garanti sinon)."""
        now = time.time()
        self._resyncs = [t for t in self._resyncs if now - t < 60]
        if len(self._resyncs) >= C.RESYNC_MAX_PER_MIN:
            return False
        self._resyncs.append(now)
        return True

    async def get_json(self, url: str, **kw):
        assert self.session is not None
        async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=15), **kw) as r:
            r.raise_for_status()
            return orjson.loads(await r.read())

    def mark_all(self, reason: str) -> None:
        for s in self.streams.values():
            s.reset(reason)

    async def run(self) -> None:
        """Boucle de vie : connexion, abonnement, lecture, reconnexion à backoff."""
        # Résolveur par THREADS (getaddrinfo), pas le c-ares d'aiodns.
        # Mesuré le 02/08 : aiodns étant installé, aiohttp choisit
        # AsyncResolver, et c-ares ne trouve pas les serveurs DNS sur cette
        # machine -> « Could not contact DNS servers » sur fapi.binance.com,
        # donc AUCUNE photo REST, donc carnet Binance vide (rows=0) — alors
        # que le WS du même hôte marchait (websockets passe par getaddrinfo,
        # les trades arrivaient). Symptôme trompeur : 8 flux verts sur 10, et
        # la venue muette était justement celle du test de transfert.
        # ThreadedResolver emprunte le même chemin que le WS : ce qui résout
        # pour l'un résout pour l'autre.
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(resolver=aiohttp.ThreadedResolver()))
        try:
            await self.prepare()
        except Exception as e:
            self.log(f"[{self.name}] préparation échouée : {e!r}")
        backoff = C.WS_BACKOFF_MIN_S
        while True:
            try:
                async with websockets.connect(
                    self.url, ping_interval=20, ping_timeout=20,
                    max_size=32 * 1024 * 1024, **self.ws_kwargs
                ) as ws:
                    # Une (re)connexion = des diffs perdus : tout repart désynchronisé.
                    self.mark_all("reconnexion WS")
                    for s in self.streams.values():
                        s.connects += 1
                    await self.subscribe(ws)
                    self.log(f"[{self.name}] connecté ({len(self.streams)} flux)")
                    backoff = C.WS_BACKOFF_MIN_S
                    keepalive = (asyncio.create_task(self._keepalive(ws))
                                 if self.ping_interval else None)
                    try:
                        async for raw in ws:
                            if isinstance(raw, bytes):
                                raw = raw.decode("utf-8", "replace")
                            if raw == "pong":
                                continue
                            try:
                                await self.on_message(orjson.loads(raw))
                            except Exception as e:
                                self.log(f"[{self.name}] message ignoré : {e!r}")
                    finally:
                        if keepalive:
                            keepalive.cancel()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self.log(f"[{self.name}] WS coupé : {e!r} — retry dans {backoff:.0f}s")
            self.mark_all("WS déconnecté")
            await asyncio.sleep(backoff + random.random())
            backoff = min(C.WS_BACKOFF_MAX_S, backoff * 2)

    async def _keepalive(self, ws) -> None:
        """Ping applicatif pour les venues qui l'exigent (Bybit, OKX)."""
        while True:
            await asyncio.sleep(self.ping_interval)
            try:
                await ws.send(self.ping_payload())
            except Exception:
                return

    def ping_payload(self) -> str:
        return "ping"

    async def close(self) -> None:
        if self.session:
            await self.session.close()


def apply_side(book: dict[float, float], updates, mult: float = 1.0) -> None:
    """Applique [[prix, taille], …] : taille 0 ⇒ suppression du palier."""
    for u in updates:
        p, q = float(u[0]), float(u[1]) * mult
        if q <= 0:
            book.pop(p, None)
        else:
            book[p] = q


def touch(s: Stream, venue_ts: int | None = None) -> None:
    s.last_msg_ms = now_ms()
    if venue_ts:
        s.venue_ts = venue_ts
