"""Écriture de l'archive sandbox — batchée, gzippée, jamais dans la prod.

`recorder/store/<VENUE>/<SYM>/book-<jour>.jsonl.gz`

À 100 ms × 5 venues × 2 symboles = 100 lignes/s : un `append` par ligne tuerait
le disque et l'event-loop. On BATCHE (`FLUSH_MS`) et on écrit chaque lot comme un
**membre gzip indépendant** concaténé au fichier. C'est un format valide : `gzip`
et `gzip.open()` relisent les membres concaténés de façon transparente, et un
crash ne peut corrompre au pire que le dernier lot.

Un flux désynchronisé n'est PAS silencieusement sauté : on écrit une ligne
`{"t":…, "gap":1, "why":…}`. Un trou doit se voir à la relecture (contrainte
« gaps marqués honnêtement » du plan).
"""
from __future__ import annotations

import gzip
import time
from pathlib import Path

import orjson

from gondetect import config as C


class Writer:
    """Un fichier par (venue, symbole, jour UTC)."""

    def __init__(self, venue: str, sym: str, kind: str = "book"):
        self.kind = kind
        self.dir = C.STORE / venue.upper() / sym
        self.dir.mkdir(parents=True, exist_ok=True)
        self.day = ""
        self.path: Path | None = None
        self.buf: list[bytes] = []
        self.last_flush = time.time()
        self.session_marked = False

    def _rotate(self, t_ms: int) -> None:
        day = time.strftime("%Y-%m-%d", time.gmtime(t_ms / 1000))
        if day != self.day:
            self.flush()
            self.day = day
            self.path = self.dir / f"{self.kind}-{day}.jsonl.gz"
            self.session_marked = False       # chaque fichier s'ouvre sur un marqueur

    def append(self, row: dict) -> None:
        self._rotate(row["t"])
        if not self.session_marked:
            # MARQUEUR DE SESSION. Sans lui, l'arrêt-relance du recorder laisse un
            # trou qu'aucune ligne ne déclare : les `gap` ne couvrent que les
            # incidents INTERNES à une session. Avec lui, le lecteur reconstitue
            # exactement le trou = t(marqueur) − t(dernière ligne précédente),
            # et plus aucune minute non enregistrée ne peut passer pour enregistrée.
            self.buf.append(orjson.dumps({"t": row["t"], "session_start": 1}))
            self.session_marked = True
        self.buf.append(orjson.dumps(row))

    def flush(self) -> int:
        """Écrit le lot courant. Retourne le nombre d'octets écrits sur disque."""
        if not self.buf or self.path is None:
            return 0
        blob = gzip.compress(b"\n".join(self.buf) + b"\n", compresslevel=6)
        with open(self.path, "ab") as fh:      # membres gzip concaténés
            fh.write(blob)
        self.buf.clear()
        self.last_flush = time.time()
        return len(blob)

    def due(self) -> bool:
        return (time.time() - self.last_flush) * 1000 >= C.FLUSH_MS
