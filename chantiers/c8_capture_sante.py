# -*- coding: utf-8 -*-
"""C8.4 — santé de la capture de traversée (enregistreur de production).

Compte, par (venue, symbole, jour), les lignes de carnet, les trous (`gap`) et
les démarrages de session dans `book-*.jsonl.gz`. À 100 ms, un jour plein fait
864 000 lignes : la complétude se lit directement, sans interprétation.

    python chantiers/c8_capture_sante.py                    # HL + Binance, 8 jours
    python chantiers/c8_capture_sante.py --venues BINANCE   # sous-ensemble
    python chantiers/c8_capture_sante.py --days 3           # les N derniers jours

Écrit le 05/08/2026 avec le diagnostic C8.4 (`journal/c8-4-diagnostic-
enregistreur-20260805.md`). Lecture seule : cet outil ne modifie rien.
"""
from __future__ import annotations

import argparse
import gzip
from datetime import date, timedelta
from pathlib import Path

STORE = Path(r"C:\Users\DyBoo\Desktop\LaForge\GON-TV\sandbox\detect\recorder\store")
JOUR_PLEIN = 864_000  # 100 ms


def un_fichier(p: Path) -> tuple[int, int, int]:
    n = g = s = 0
    with gzip.open(p, "rt", encoding="utf-8") as f:
        for line in f:
            n += 1
            h = line[:80]
            if '"gap"' in h:
                g += 1
            if "session_start" in h:
                s += 1
    return n, g, s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--venues", default="HYPERLIQUID,BINANCE")
    ap.add_argument("--symbols", default="BTCUSDT,ETHUSDT")
    ap.add_argument("--days", type=int, default=8,
                    help="nombre de jours COMPLETS en arrière (hier inclus)")
    a = ap.parse_args()

    jours = [str(date.today() - timedelta(days=i)) for i in range(a.days, 0, -1)]
    print(f"{'venue':12} {'sym':8} {'jour':10} {'lignes':>9} {'%':>6} "
          f"{'gaps':>5} {'sessions':>8}")
    for venue in a.venues.split(","):
        for sym in a.symbols.split(","):
            for jour in jours:
                p = STORE / venue / sym / f"book-{jour}.jsonl.gz"
                if not p.exists():
                    print(f"{venue:12} {sym:8} {jour:10}    ABSENT")
                    continue
                n, g, s = un_fichier(p)
                pct = 100.0 * n / JOUR_PLEIN
                drapeau = "" if pct >= 99.0 and s <= 1 else "  ⚠️"
                print(f"{venue:12} {sym:8} {jour:10} {n:>9,} {pct:>5.1f} "
                      f"{g:>5} {s:>8}{drapeau}", flush=True)


if __name__ == "__main__":
    main()
