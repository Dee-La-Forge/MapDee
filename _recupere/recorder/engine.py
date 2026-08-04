"""Moteur — échantillonne les 10 flux à cadence fixe et les écrit alignés.

Trois décisions structurent ce fichier :

1. **Grille de paliers COMMUNE par symbole.** `bs = nice(mid_ref · 2,5e-5)` est
   calculée sur la venue de référence (Binance) et imposée à toutes les venues :
   le palier `k = floor(prix/bs)` devient comparable d'une venue à l'autre. Même
   règle et même granularité que la prod (`sec-recorder.js:443`), donc l'archive
   sandbox et l'archive de prod se lisent avec le même code.

2. **On stocke des paliers ABSOLUS, on aligne en RELATIF à la lecture.** Garder
   `k` absolu préserve l'identité d'un niveau dans le temps (indispensable à la
   persistance) ; l'écart relatif au mid — le seul comparable entre venues
   (tick sizes, basis et mid diffèrent) — se recalcule trivialement à l'analyse
   puisque chaque ligne porte le `mid` de SA venue.

3. **Les trous sont écrits.** Un flux désynchronisé ne produit pas de ligne de
   carnet ; il produit une ligne `gap`. Ouverture et fermeture du trou sont
   marquées, avec sa durée. Rien n'est maquillé.
"""
from __future__ import annotations

import asyncio
import math
import time

from gondetect import config as C

from .adapters.binance import BinanceAdapter
from .adapters.bybit import BybitAdapter
from .adapters.coinbase import CoinbaseAdapter
from .adapters.hyperliquid import HyperliquidAdapter
from .adapters.hyperliquid_agg import (HyperliquidFinAdapter,
                                       HyperliquidLargeAdapter)
from .adapters.okx import OkxAdapter
from .state import Stream, now_ms
from .store import Writer

ADAPTERS = {
    "binance": BinanceAdapter, "bybit": BybitAdapter, "okx": OkxAdapter,
    "coinbase": CoinbaseAdapter, "hyperliquid": HyperliquidAdapter,
    "hyperliquid_fin": HyperliquidFinAdapter,
    "hyperliquid_large": HyperliquidLargeAdapter,
}


def nice(raw: float) -> float:
    """Arrondi « joli » 1/2/5/10 — port de `sec-recorder.js:233`."""
    if raw <= 0:
        return 1.0
    e = 10 ** math.floor(math.log10(raw))
    m = raw / e
    return e * (1 if m < 1.5 else 2 if m < 3.5 else 5 if m < 7.5 else 10)


class Engine:
    def __init__(self, venues=C.VENUES, symbols=C.SYMBOLS, verbose=True):
        self.verbose = verbose
        self.started = now_ms()
        self.symbols = list(symbols)
        self.streams: dict[tuple[str, str], Stream] = {}
        self.writers: dict[tuple[str, str], Writer] = {}
        self.twriters: dict[tuple[str, str], Writer] = {}
        self.in_gap: dict[tuple[str, str], int] = {}     # début du trou (ms) ou 0
        self.bs: dict[str, float] = {}
        self.adapters = []
        self.ticks = 0

        for venue in venues:
            per_sym = {}
            for sym in self.symbols:
                native = C.VENUE_SYMBOLS[sym][venue]
                st = Stream(venue=venue, sym=sym, native=native)
                self.streams[(venue, sym)] = st
                self.writers[(venue, sym)] = Writer(venue, sym)
                self.twriters[(venue, sym)] = Writer(venue, sym, kind="trade")
                self.in_gap[(venue, sym)] = 0
                per_sym[sym] = st
            self.adapters.append(ADAPTERS[venue](per_sym, self.log, self.on_trade))

    def log(self, m: str) -> None:
        if self.verbose:
            print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

    # ---------------------------------------------------------- transactions --
    def on_trade(self, s: Stream, price: float, qty: float, is_buy: bool,
                 venue_ts=None, users=None) -> None:
        """Reçoit une transaction d'un adapter. Deux usages, deux destinations.

        1. **Agrégée par palier** dans `s.flow`, vidée à chaque photo : c'est ce
           qui permet de distinguer une profondeur MANGÉE d'une profondeur
           RETIRÉE. À 100 ms on peut faire mieux que la prod : la baisse de
           profondeur entre deux photos, moins le volume exécuté, EST le retrait
           — plus besoin du proxy `peak − v − traded` qui m'a déjà piégé.
        2. **Brute** dans `trade-<jour>.jsonl.gz`, avec `users` quand la venue le
           donne : Hyperliquid est la seule à publier les adresses des deux
           contreparties, et ça ne se retrouve nulle part ailleurs.
        """
        bs = self.bs.get(s.sym)
        if bs and price > 0:
            k = int(price // bs)
            f = s.flow.get(k)
            if f is None:
                f = s.flow[k] = [0.0, 0.0]
            f[0 if is_buy else 1] += price * qty
        else:
            # Avant le premier `update_bs`, la grille n'existe pas : la
            # transaction ne peut etre rattachee a aucun palier. Elle etait
            # PERDUE sans trace ; on la compte desormais (audit du 03/08).
            # Borne a quelques ticks au demarrage, mais un silence reste un
            # silence.
            s.trades_sans_grille += 1
        s.trades += 1
        row = {"t": now_ms(), "tv": venue_ts, "p": price, "q": qty, "s": 1 if is_buy else 0}
        if users:
            row["u"] = users
        self.twriters[(s.venue, s.sym)].append(row)

    # ------------------------------------------------------------ grille bs --
    def update_bs(self) -> None:
        for sym in self.symbols:
            mid = 0.0
            ref = self.streams.get((C.REF_VENUE, sym))
            if ref and ref.synced:
                mid = ref.mid()
            if not mid:      # référence absente : on prend la première venue prête
                for v in C.VENUES:
                    s = self.streams.get((v, sym))
                    if s and s.synced and s.mid():
                        mid = s.mid()
                        break
            if not mid:
                continue
            want = nice(mid * C.BIN_REL)
            cur = self.bs.get(sym)
            # Rebase seulement sur une vraie dérive (même seuil que la prod) :
            # changer `bs` invalide la comparabilité des `k` dans le temps.
            if not cur or abs(math.log(want / cur)) > 0.6:
                if cur:
                    self.log(f"grille {sym} rebasée : bs {cur} → {want}")
                    # LE FLUX EN ATTENTE EST SUR L'ANCIENNE GRILLE. `update_bs`
                    # tourne AVANT `snapshot` dans le même tick : sans ce
                    # vidage, la photo suivante publierait des paliers `k`
                    # calculés avec l'ancien `bs` sous une en-tête qui annonce
                    # le nouveau — un prix implicite faux d'un facteur 10.
                    # C'est le seul cas ou le flux etait MAL ATTRIBUE plutot
                    # que jete (audit du 03/08). Rare (dérive log > 0,6), mais
                    # silencieux et faux, donc pire qu'un trou déclaré.
                    for s_ in self.streams.values():
                        if s_.sym == sym and s_.flow:
                            s_.flow_jete += 1
                            s_.flow.clear()
                self.bs[sym] = want

    # ------------------------------------------------------------- snapshot --
    def snapshot(self, key: tuple[str, str]) -> dict | None:
        venue, sym = key
        s = self.streams[key]
        bs = self.bs.get(sym)
        mid = s.mid()
        if not bs or not mid or not s.synced:
            # LE FLUX NE DOIT PAS TRAVERSER UN TROU. `on_trade` continue de
            # l'alimenter pendant toute la désynchronisation ; sans ce vidage
            # il se déverse dans la première photo valide d'après. Mesuré le
            # 03/08 : une fenêtre normale à 100 000 $ devenait 10 000 000 $
            # après 10 s de trou. La docstring de `x` promettait déjà « chaque
            # ligne porte le flux de SA fenêtre » — elle était fausse.
            # On JETTE plutôt que d'attribuer à la mauvaise fenêtre, et on
            # compte : `flow_jete` dit combien de fois c'est arrivé.
            if s.flow:
                s.flow_jete += 1
                s.flow.clear()
            return None
        lo, hi = mid * (1 - C.SNAP_BAND), mid * (1 + C.SNAP_BAND)
        bids: dict[int, float] = {}
        asks: dict[int, float] = {}
        for p, q in s.bids.items():
            if p >= lo:
                k = int(p // bs)
                bids[k] = bids.get(k, 0.0) + p * q      # notionnel en USD
        for p, q in s.asks.items():
            if p <= hi:
                k = int(p // bs)
                asks[k] = asks.get(k, 0.0) + p * q
        if not bids and not asks:
            # Carnet vide DANS LA BANDE : le flux est réel mais n'a aucune
            # photo à laquelle s'attacher. Même règle — jeté et compté, jamais
            # reporté sur la fenêtre suivante.
            if s.flow:
                s.flow_jete += 1
                s.flow.clear()
            return None
        flat = lambda d: [x for k in sorted(d) for x in (k, round(d[k]))]
        # `x` = flux exécuté depuis la photo précédente : [palier, achat$, vente$].
        # Vidé après lecture : chaque ligne porte le flux de SA fenêtre.
        x = [v for k in sorted(s.flow) for v in (k, round(s.flow[k][0]), round(s.flow[k][1]))]
        s.flow.clear()
        return {"t": now_ms(), "tv": s.venue_ts or None, "mid": round(mid, 6),
                "bs": bs, "b": flat(bids), "a": flat(asks), "x": x}

    # ----------------------------------------------------------- boucle 100ms --
    async def sample_loop(self) -> None:
        period = C.SNAP_MS / 1000.0
        nxt = time.perf_counter()
        while True:
            nxt += period
            await asyncio.sleep(max(0.0, nxt - time.perf_counter()))
            self.ticks += 1
            self.update_bs()
            t = now_ms()
            for key, s in self.streams.items():
                # Flux muet trop longtemps = mort, même si le WS croit vivre.
                if s.synced and s.last_msg_ms and t - s.last_msg_ms > C.STALE_MS:
                    s.reset(f"muet depuis {t - s.last_msg_ms} ms")
                row = self.snapshot(key)
                w = self.writers[key]
                if row is None:
                    if not self.in_gap[key]:
                        self.in_gap[key] = t
                        s.gaps += 1
                        w.append({"t": t, "gap": 1, "why": s.reason or "carnet vide"})
                    continue
                if self.in_gap[key]:
                    w.append({"t": t, "gap": 0, "ms": t - self.in_gap[key]})
                    self.in_gap[key] = 0
                w.append(row)
                s.rows += 1
                s.prune(C.BOOK_KEEP)

    async def flush_loop(self) -> None:
        while True:
            await asyncio.sleep(C.FLUSH_MS / 1000.0)
            for key, w in self.writers.items():
                if w.due():
                    self.streams[key].bytes_out += w.flush()
            for key, w in self.twriters.items():
                if w.due():
                    self.streams[key].bytes_out += w.flush()

    def health(self) -> dict:
        up = (now_ms() - self.started) / 1000
        streams = [s.health() for s in self.streams.values()]
        return {
            "uptime_s": round(up, 1), "ticks": self.ticks, "port": C.RECORDER_PORT,
            "snap_ms": C.SNAP_MS, "band": C.SNAP_BAND, "bs": self.bs,
            "store": str(C.STORE),
            "synced": sum(1 for s in streams if s["synced"]), "streams_total": len(streams),
            "rows": sum(s["rows"] for s in streams),
            "bytes_out": sum(s["bytes_out"] for s in streams),
            "gaps": sum(s["gaps"] for s in streams),
            "trades": sum(s["trades"] for s in streams),
            "streams": streams,
        }

    async def run(self) -> None:
        tasks = [asyncio.create_task(a.run()) for a in self.adapters]
        for a in self.adapters:
            tasks += [asyncio.create_task(c) for c in a.extra_loops()]
        tasks += [asyncio.create_task(self.sample_loop()),
                  asyncio.create_task(self.flush_loop())]
        try:
            await asyncio.gather(*tasks)
        finally:
            for w in list(self.writers.values()) + list(self.twriters.values()):
                w.flush()
            for a in self.adapters:
                await a.close()
