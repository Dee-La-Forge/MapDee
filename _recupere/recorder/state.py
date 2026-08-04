"""État d'un flux (venue × symbole) — partagé entre l'adapter et le moteur.

L'adapter ÉCRIT le carnet et le drapeau `synced` ; le moteur LIT à cadence fixe.
Aucun verrou : tout tourne dans la même boucle asyncio, les mutations sont
atomiques du point de vue du moteur (pas de `await` au milieu d'un applyDiff).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field


def now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class Stream:
    venue: str
    sym: str                       # symbole CANONIQUE (BTCUSDT / ETHUSDT)
    native: str                    # identifiant chez la venue
    bids: dict[float, float] = field(default_factory=dict)   # prix → quantité (base)
    asks: dict[float, float] = field(default_factory=dict)
    synced: bool = False
    reason: str = "démarrage"      # pourquoi non synchronisé (marqué honnêtement)
    last_msg_ms: int = 0           # dernier message reçu (santé du WS)
    venue_ts: int = 0              # horodatage FOURNI par la venue
    connects: int = 0
    resyncs: int = 0
    gaps: int = 0                  # photos manquées et ÉCRITES comme telles
    rows: int = 0
    bytes_out: int = 0
    mult: float = 1.0              # base par unité de taille (contrats OKX : ctVal)
    # Flux exécuté depuis la DERNIÈRE photo, par palier absolu :
    # k -> [notionnel acheteur agressif, notionnel vendeur agressif].
    # Vidé à chaque photo — chaque ligne porte le flux de SA fenêtre de 100 ms,
    # exactement comme la prod (`sec-recorder.js:504`).
    flow: dict = field(default_factory=dict)
    trades: int = 0                # transactions vues (santé du flux trades)
    flow_jete: int = 0             # fenêtres de flux JETÉES faute de photo valide
    trades_sans_grille: int = 0    # transactions vues AVANT que `bs` existe

    def reset(self, reason: str) -> None:
        self.bids.clear()
        self.asks.clear()
        # LE FLUX AUSSI. Sans cette ligne, le volume exécuté accumulé pendant
        # la désynchronisation survit à la reconnexion et se déverse dans la
        # première photo d'après. Mesuré le 03/08 : x100 sur `traded`, ce qui
        # transforme un RETRAIT en ABSORPTION — l'inverse exact du phénomène
        # que ce recorder existe pour mesurer.
        if self.flow:
            self.flow_jete += 1
            self.flow.clear()
        self.synced = False
        self.reason = reason

    def mid(self) -> float:
        """Mid = (meilleur bid + meilleur ask)/2, 0 si le carnet est inutilisable."""
        if not self.bids or not self.asks:
            return 0.0
        bb, ba = max(self.bids), min(self.asks)
        return (bb + ba) / 2.0 if ba > bb > 0 else 0.0

    def prune(self, band: float) -> None:
        """Élague hors de ±band autour du mid — borne la mémoire sur un flux long."""
        m = self.mid()
        if not m:
            return
        lo, hi = m * (1 - band), m * (1 + band)
        for p in [p for p in self.bids if p < lo]:
            del self.bids[p]
        for p in [p for p in self.asks if p > hi]:
            del self.asks[p]

    def health(self) -> dict:
        age = now_ms() - self.last_msg_ms if self.last_msg_ms else None
        return dict(venue=self.venue, sym=self.sym, native=self.native,
                    synced=self.synced, reason=None if self.synced else self.reason,
                    last_msg_age_ms=age, mid=round(self.mid(), 4),
                    levels=len(self.bids) + len(self.asks), connects=self.connects,
                    resyncs=self.resyncs, gaps=self.gaps, rows=self.rows,
                    bytes_out=self.bytes_out, trades=self.trades,
                    # `flow_jete` et `trades_sans_grille` DOIVENT sortir ici :
                    # un compteur qu'aucun canal n'expose est decoratif. Le
                    # commit 936045d affirmait « compte pour que ce ne soit pas
                    # silencieux » — c'etait faux, l'audit l'a releve.
                    flow_jete=self.flow_jete,
                    trades_sans_grille=self.trades_sans_grille)
