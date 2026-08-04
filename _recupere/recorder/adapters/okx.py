"""OKX v5 — canal `books` (400 paliers, 100 ms), chaînage `prevSeqId` + CHECKSUM.

Deux garde-fous, tous deux exigés par le plan :
  * `prevSeqId` doit valoir le `seqId` précédent (sinon diffs manqués) ;
  * le **checksum CRC32** des 25 premiers paliers valide le carnet reconstruit —
    c'est la seule venue qui offre une vérification d'intégrité de bout en bout,
    on ne s'en prive pas.

Le checksum porte sur les chaînes **telles que reçues** : reformater un float
(`0.5` vs `0.50`) le casse et provoquerait un réabonnement en boucle. On maintient
donc un carnet BRUT (chaîne → chaîne) en parallèle du carnet numérique, et le
checksum se calcule sur le brut.

⚠ Les tailles OKX sont en **CONTRATS** : `ctVal` (0,01 BTC pour BTC-USDT-SWAP,
0,1 ETH pour ETH-USDT-SWAP) est lu au démarrage et appliqué au carnet numérique,
sans quoi les notionnels ne sont pas comparables aux autres venues.
"""
from __future__ import annotations

import zlib

import orjson

from .base import Adapter, touch

REST_INSTRUMENTS = "https://www.okx.com/api/v5/public/instruments"


class OkxAdapter(Adapter):
    name = "okx"
    url = "wss://ws.okx.com:8443/ws/v5/public"
    ping_interval = 25.0

    def __init__(self, streams, log, on_trade=None):
        super().__init__(streams, log, on_trade)
        self.by_native = {s.native: k for k, s in streams.items()}
        self.last_seq: dict[str, int] = {}
        self.raw: dict[str, tuple[dict, dict]] = {k: ({}, {}) for k in streams}
        self.bad_crc: dict[str, int] = {}
        self.crc_seen = False
        self._ws = None

    def ping_payload(self) -> str:
        return "ping"

    async def prepare(self) -> None:
        """Lit `ctVal` : sans lui, les tailles OKX sont incomparables."""
        o = await self.get_json(REST_INSTRUMENTS, params={"instType": "SWAP"})
        by_id = {d["instId"]: d for d in o.get("data", [])}
        for s in self.streams.values():
            info = by_id.get(s.native)
            if info and info.get("ctVal"):
                s.mult = float(info["ctVal"])
                self.log(f"[okx] {s.native} : 1 contrat = {s.mult} {info.get('ctValCcy','?')}")
            else:
                self.log(f"[okx] ctVal introuvable pour {s.native} — tailles NON converties")

    async def subscribe(self, ws) -> None:
        self._ws = ws
        args = [{"channel": "books", "instId": s.native} for s in self.streams.values()]
        args += [{"channel": "trades", "instId": s.native} for s in self.streams.values()]
        await ws.send(orjson.dumps({"op": "subscribe", "args": args}).decode())

    async def _resubscribe(self, native: str) -> None:
        if self._ws is None or not self.resync_allowed():
            return
        a = [{"channel": "books", "instId": native}]
        await self._ws.send(orjson.dumps({"op": "unsubscribe", "args": a}).decode())
        await self._ws.send(orjson.dumps({"op": "subscribe", "args": a}).decode())

    def _apply(self, sym: str, updates, is_bid: bool) -> None:
        """Applique au carnet BRUT (chaînes) et au carnet numérique en même temps."""
        s = self.streams[sym]
        raw = self.raw[sym][0 if is_bid else 1]
        num = s.bids if is_bid else s.asks
        for u in updates:
            px, sz = u[0], u[1]
            if float(sz) <= 0:
                raw.pop(px, None)
                num.pop(float(px), None)
            else:
                raw[px] = sz
                num[float(px)] = float(sz) * s.mult

    @staticmethod
    def _crc(raw_b: dict, raw_a: dict) -> int:
        """CRC32 OKX : bid0:sz0:ask0:sz0:… sur 25 paliers, chaînes d'origine."""
        bids = sorted(raw_b.items(), key=lambda kv: -float(kv[0]))[:25]
        asks = sorted(raw_a.items(), key=lambda kv: float(kv[0]))[:25]
        parts = []
        for i in range(25):
            if i < len(bids):
                parts += [bids[i][0], bids[i][1]]
            if i < len(asks):
                parts += [asks[i][0], asks[i][1]]
        crc = zlib.crc32(":".join(parts).encode()) & 0xFFFFFFFF
        return crc - 0x100000000 if crc >= 0x80000000 else crc   # entier 32 bits SIGNÉ

    async def on_message(self, msg) -> None:
        if not isinstance(msg, dict):
            return
        if msg.get("event") in ("subscribe", "unsubscribe", "channel-conn-count"):
            return
        if msg.get("event") == "error":
            self.log(f"[okx] erreur : {msg}")
            return
        arg = msg.get("arg") or {}
        if arg.get("channel") == "trades":
            sym = self.by_native.get(arg.get("instId", ""))
            if sym is None:
                return
            st = self.streams[sym]
            for tr in msg.get("data", []):
                # `sz` est en CONTRATS : on repasse en base via ctVal, comme le carnet.
                self.on_trade(st, float(tr["px"]), float(tr["sz"]) * st.mult,
                              tr.get("side") == "buy", int(tr["ts"]) if tr.get("ts") else None)
            return
        if arg.get("channel") != "books":
            return
        sym = self.by_native.get(arg.get("instId", ""))
        if sym is None:
            return
        s = self.streams[sym]
        action = msg.get("action")

        for d in msg.get("data", []):
            touch(s, int(d["ts"]) if d.get("ts") else None)
            if action == "snapshot":
                s.bids.clear()
                s.asks.clear()
                self.raw[sym] = ({}, {})
                self._apply(sym, d.get("bids", []), True)
                self._apply(sym, d.get("asks", []), False)
                s.synced = True
                s.reason = ""
                s.resyncs += 1
                self.bad_crc[sym] = 0
            else:
                prev = self.last_seq.get(sym)
                if prev is not None and d.get("prevSeqId") != prev:
                    s.reset(f"prevSeqId rompu ({prev} → {d.get('prevSeqId')})")
                    await self._resubscribe(arg["instId"])
                    return
                self._apply(sym, d.get("bids", []), True)
                self._apply(sym, d.get("asks", []), False)
            self.last_seq[sym] = d.get("seqId")

            # OKX publie `checksum: 0` sur ce canal (sondé le 2026-07-28) : le
            # champ existe mais n'est pas alimenté. On ne valide donc QUE s'il
            # est non nul — sinon on se réabonnerait en boucle sur un contrôle
            # fantôme. Conséquence assumée : l'intégrité OKX repose sur le seul
            # chaînage `prevSeqId`, comme les autres venues.
            if d.get("checksum"):
                if not self.crc_seen:
                    self.crc_seen = True
                    self.log("[okx] checksums CRC32 actifs — intégrité vérifiée de bout en bout")
                if self._crc(*self.raw[sym]) == d["checksum"]:
                    self.bad_crc[sym] = 0
                else:
                    # Un désaccord isolé peut venir d'un message hors ordre ;
                    # deux d'affilée = le carnet est faux, on redemande une photo.
                    self.bad_crc[sym] = self.bad_crc.get(sym, 0) + 1
                    if self.bad_crc[sym] >= 2:
                        s.reset("checksum CRC32 invalide ×2")
                        await self._resubscribe(arg["instId"])
                        return
