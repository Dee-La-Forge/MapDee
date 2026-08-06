# -*- coding: utf-8 -*-
"""Le cache léger des transactions — `trades_light` : (t_ms, px, sz) par
jour-symbole, MANIFESTÉ (empreinte), construit UNE fois. Écrit le 06/08/2026
pour B4 (contact = première transaction au palier du mur, ADR-009/010).

    python chantiers/construit_trades_cache.py

Un flux tar par JOUR (les deux symboles séparés en une passe — read_trades
en aurait fait deux). 20251213 BTC est sauté : hors J8 (bande ADR-008).
"""
from __future__ import annotations

import gzip
import io
import json
import sys
import tarfile
import time
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

DEPOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DEPOT))
sys.path.insert(0, str(DEPOT / "_recupere"))

import os                                                            # noqa: E402
os.environ.setdefault("GON_OPENBOOK_SRC", str(DEPOT / "data" / "l4" / "openbook-202512"))

from construit import empreinte                                      # noqa: E402
from construit.fills import _ts_ns                                   # noqa: E402

SRC = Path(os.environ["GON_OPENBOOK_SRC"])
OUT = DEPOT / "data" / "openbook" / "trades_light" / "parts"
JOURS = [f"202512{d:02d}" for d in range(9, 17)]
EXCLUS = {("20251213", "BTC")}          # hors J8, bande ADR-008


def un_jour(day: str) -> None:
    t0 = time.time()
    cibles = [(c, OUT / f"trades_{day}_{c}.parquet") for c in ("BTC", "ETH")
              if (day, c) not in EXCLUS]
    cibles = [(c, p) for c, p in cibles if not p.exists()]
    if not cibles:
        print(f"{day} : déjà fait, saute", flush=True)
        return
    par_coin = {c: {"t": [], "px": [], "sz": []} for c, _ in cibles}
    seen = False
    with tarfile.open(SRC / "trades_2025_12.tar", "r|") as t:
        for m in t:
            if not m.isfile():
                continue
            if not m.name.startswith(f"{day}/"):
                if seen:
                    break
                continue
            seen = True
            raw = t.extractfile(m).read()
            with gzip.open(io.BytesIO(raw), "rt", errors="replace") as f:
                for line in f:
                    for c in par_coin:
                        if f'"{c}"' in line:
                            try:
                                r = json.loads(line)
                            except Exception:
                                continue
                            if r.get("coin") == c:
                                d = par_coin[c]
                                d["t"].append(_ts_ns(r["time"]) // 1_000_000)
                                d["px"].append(float(r["px"]))
                                d["sz"].append(float(r["sz"]))
                            break
    OUT.mkdir(parents=True, exist_ok=True)
    for c, p in cibles:
        d = par_coin[c]
        ordre = np.argsort(np.asarray(d["t"], dtype=np.int64), kind="stable")
        tb = pa.table({
            "t_ms": pa.array(np.asarray(d["t"], dtype=np.int64)[ordre]),
            "px": pa.array(np.asarray(d["px"])[ordre]),
            "sz": pa.array(np.asarray(d["sz"])[ordre])})
        pq.write_table(tb, p, compression="zstd")
        empreinte.ecris(p, kind="trades_light", jour=day, coin=c, phase="trades",
                        parametres={"colonnes": "t_ms/px/sz",
                                    "source": "trades_2025_12.tar"},
                        entrees=[SRC / "trades_2025_12.tar"],
                        stats={"transactions": len(d["t"])})
        print(f"{day} {c} : {len(d['t']):,} transactions "
              f"({time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(
        ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    for day in JOURS:
        un_jour(day)
    print("terminé", flush=True)
