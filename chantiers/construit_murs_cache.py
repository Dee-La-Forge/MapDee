# -*- coding: utf-8 -*-
"""Le cache des murs — `murs_light` : par jour-symbole et par photo, le MUR
LE PLUS PROCHE du mid de chaque côté (B7 : ratio ≥ M′ sur médiane de
voisinage ±0,05 %), cherché sur la PLEINE bande d'analyse ±0,5 % — fidèle à
la fiche A2, sans la borne qui a dégénéré la v1 (25 photos à mur/118 722,
mesuré le 06/08).

    python chantiers/construit_murs_cache.py

Médiane glissante EXACTE en SortedList (fenêtre entrante/sortante à deux
pointeurs, ~10× la boucle np.median) — AUTO-VÉRIFIÉE contre np.median sur
les 200 premières photos de chaque fichier : un écart = refus. Manifesté
(empreinte). Construit une fois ; `charge()` le lit à chaque tir.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from sortedcontainers import SortedList

DEPOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DEPOT))
sys.path.insert(0, str(DEPOT / "_recupere"))

from construit import empreinte                                      # noqa: E402
from harnais.b7 import B7, DEMI_VOISINAGE_REL                        # noqa: E402

PARTS = DEPOT / "data" / "openbook" / "deep" / "parts"
OUT = DEPOT / "data" / "openbook" / "murs_light" / "parts"
DIST_MAX = 0.005
JOURS = [f"202512{d:02d}" for d in range(9, 17)]
EXCLUS = {("20251213", "BTC")}
N_VERIF = 200


def _med_sl(sl: SortedList) -> float:
    m = len(sl)
    if m == 0:
        return np.nan
    return float(sl[m // 2]) if m % 2 else float((sl[m // 2 - 1] + sl[m // 2]) / 2.0)


def un_fichier(jour: str, coin: str) -> None:
    cible = OUT / f"murs_{jour}_{coin}.parquet"
    if cible.exists():
        print(f"{jour} {coin} : déjà fait, saute", flush=True)
        return
    chemin = PARTS / f"deep_{jour}_{coin}.parquet"
    t0 = time.time()
    M = B7[coin]["M"]
    cols = ["t", "k", "mag", "mid", "bs"]
    morceaux = {c: [] for c in cols}
    for lot in pq.ParquetFile(chemin).iter_batches(columns=cols,
                                                   batch_size=2_000_000):
        k = lot["k"].to_numpy(); mid = lot["mid"].to_numpy(); bs = lot["bs"].to_numpy()
        g = np.abs((k + 0.5) * bs - mid) <= mid * DIST_MAX
        for c in cols:
            morceaux[c].append(lot[c].to_numpy()[g])
    ts = np.concatenate(morceaux["t"]); ks = np.concatenate(morceaux["k"])
    mags = np.concatenate(morceaux["mag"]).astype(np.float64)
    mids = np.concatenate(morceaux["mid"]); bss = np.concatenate(morceaux["bs"])
    photos, inverse = np.unique(ts, return_inverse=True)
    ordre = np.argsort(inverse, kind="stable")
    bornes = np.searchsorted(inverse[ordre], np.arange(len(photos) + 1))
    n = len(photos)

    out = {c: np.full(n, np.nan) for c in
           ("k_mur_bid", "mag_mur_bid", "k_mur_ask", "mag_mur_ask")}
    for i in range(n):
        tr = ordre[bornes[i]:bornes[i + 1]]
        kk, mm = ks[tr], mags[tr]
        mid, bs = mids[tr[0]], bss[tr[0]]
        k0 = int(mid // bs)
        o = np.argsort(kk)
        kks, mms = kk[o], mm[o]
        demi = max(1, round(DEMI_VOISINAGE_REL * mid / bs))
        # médiane glissante exacte : fenêtre [kks[j]-demi, kks[j]+demi] sur
        # paliers OCCUPÉS, deux pointeurs, SortedList incrémentale
        m_paliers = len(kks)
        ratios = np.empty(m_paliers)
        sl = SortedList()
        a = b = 0
        for j in range(m_paliers):
            lo_k, hi_k = kks[j] - demi, kks[j] + demi
            while b < m_paliers and kks[b] <= hi_k:
                sl.add(mms[b]); b += 1
            while a < m_paliers and kks[a] < lo_k:
                sl.remove(mms[a]); a += 1
            med = _med_sl(sl)
            ratios[j] = mms[j] / med if med > 0 else np.nan
        if i < N_VERIF:   # auto-vérification contre la référence np.median
            lo = np.searchsorted(kks, kks - demi, side="left")
            hi = np.searchsorted(kks, kks + demi, side="right")
            ref = np.array([mms[x:y][0] * 0 + np.median(mms[x:y])
                            if y > x else np.nan for x, y in zip(lo, hi)])
            r_ref = np.where(ref > 0, mms / ref, np.nan)
            if not np.allclose(ratios, r_ref, equal_nan=True):
                raise SystemExit(f"REFUS : médiane glissante ≠ np.median "
                                 f"(photo {i}, {jour} {coin})")
        i0 = int(np.searchsorted(kks, k0))
        for j in range(i0 - 1, -1, -1):               # bid : le plus proche
            if ratios[j] == ratios[j] and ratios[j] >= M:
                out["k_mur_bid"][i] = kks[j]
                out["mag_mur_bid"][i] = mms[j]
                break
        dep = i0 + (1 if i0 < m_paliers and kks[i0] == k0 else 0)
        for j in range(dep, m_paliers):               # ask
            if ratios[j] == ratios[j] and ratios[j] >= M:
                out["k_mur_ask"][i] = kks[j]
                out["mag_mur_ask"][i] = mms[j]
                break
    OUT.mkdir(parents=True, exist_ok=True)
    tb = pa.table({"t": pa.array(photos, pa.int64()),
                   **{c: pa.array(v) for c, v in out.items()}})
    pq.write_table(tb, cible, compression="zstd")
    n_murs = int(np.isfinite(out["k_mur_bid"]).sum()
                 + np.isfinite(out["k_mur_ask"]).sum())
    empreinte.ecris(cible, kind="murs_light", jour=jour, coin=coin,
                    phase="murs",
                    parametres={"M": M, "demi_voisinage_rel": DEMI_VOISINAGE_REL,
                                "bande_recherche": DIST_MAX},
                    entrees=[chemin],
                    stats={"photos": n, "photos_avec_mur": n_murs})
    print(f"{jour} {coin} : {n:,} photos · {n_murs:,} côtés-photos avec mur "
          f"· {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(
        ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    for jour in JOURS:
        for coin in ("BTC", "ETH"):
            if (jour, coin) not in EXCLUS:
                un_fichier(jour, coin)
    print("terminé", flush=True)
