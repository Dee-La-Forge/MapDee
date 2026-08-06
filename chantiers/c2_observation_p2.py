# -*- coding: utf-8 -*-
"""C2, 2ᵉ passe — applique `C2-observation.md` §5, PRÉ-ENREGISTRÉ le
06/08/2026 (commité avant tout calcul). Ferme S1′/S2′/S3/S4′ — le dernier
verrou de B7.

    python chantiers/c2_observation_p2.py BTC
    python chantiers/c2_observation_p2.py ETH

Sources certifiées : `deep_20251208_<coin>.parquet` (+ manifeste) et les
statuts re-extraits de l'archive source, comme la 1ʳᵉ passe.
"""
from __future__ import annotations

import json
import sys
import time
from bisect import bisect_left
from collections import defaultdict
from pathlib import Path

import numpy as np

DEPOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DEPOT))
sys.path.insert(0, str(DEPOT / "chantiers"))

import os                                                            # noqa: E402
os.environ.setdefault("GON_OPENBOOK_SRC", str(DEPOT / "data" / "l4" / "openbook-202512"))
os.environ.setdefault("GON_OPENBOOK_OUT", str(DEPOT / "data" / "openbook"))
sys.path.insert(0, str(DEPOT / "_recupere"))

from construit.jour import SRC, _extract_day                        # noqa: E402
from construit.openbook import read_statuses                        # noqa: E402
from c5_distributions import decode, FILLED                         # noqa: E402

JOUR = "20251208"
DIST_MAX = 0.005            # la bande d'analyse, comme partout au banc
DEMI_VOISINAGE_REL = 0.0005  # S1′ : ±0,05 % du mid — DÉCLARÉ (§5)
QUANTILE_MUR = 0.99          # inchangé
FRACTION_BANDE = 0.999       # inchangé
SEUIL_COINCIDENCE = 0.95     # inchangé
FENETRE_COINCIDENCE_MS = 1_000   # S3 — DÉCLARÉ (§5)
TOLERANCE_MID_MS = 2_000         # S4′ — DÉCLARÉ (§5)
PREFIX = 25_000              # le préfixe de pose de M, comme la 1ʳᵉ passe


def mesure(coin: str) -> dict:
    t0 = time.time()
    chemin = DEPOT / "data" / "openbook" / "deep" / "parts" / f"deep_{JOUR}_{coin}.parquet"
    man = json.loads((chemin.parent / f"{chemin.name}.manifest.json").read_text(encoding="utf-8"))
    assert man.get("schema_manifeste", 0) >= 1 and man["artefact"]["sha256"], "manifeste non certifié"
    print(f"[{time.time()-t0:5.0f}s] manifeste certifié ({man['artefact']['sha256'][:12]}…)", flush=True)

    # ---- passe deep : S1′, S2′ + le matériau de S3/S4′ ---------------------
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(chemin)
    ratios: list[float] = []
    duree: dict[int, int] = defaultdict(int)
    debut_episode: dict[int, tuple[int, str]] = {}     # k -> (t_debut, cote)
    episodes: list[tuple[int, int, str]] = []          # (k, t_debut, cote)
    persistances: list[int] = []
    M = None
    photos_t: list[int] = []
    photos_mid: list[float] = []
    photos_bs: list[float] = []
    bl_bid: dict[int, list[int]] = defaultdict(list)   # k -> temps où k est BL bid
    bl_ask: dict[int, list[int]] = defaultdict(list)
    for lot in pf.iter_batches(columns=["t", "k", "mag", "mid", "bs"],
                               batch_size=2_000_000):
        ts = lot["t"].to_numpy(); ks = lot["k"].to_numpy()
        mags = lot["mag"].to_numpy().astype(np.float64)
        mids = lot["mid"].to_numpy(); bss = lot["bs"].to_numpy()
        garde = np.abs((ks + 0.5) * bss - mids) <= mids * DIST_MAX
        ts, ks, mags, mids, bss = ts[garde], ks[garde], mags[garde], mids[garde], bss[garde]
        for t in np.unique(ts):
            m = ts == t
            kk, mm = ks[m], mags[m]
            mid, bs = float(mids[m][0]), float(bss[m][0])
            k0 = int(mid // bs)
            t = int(t)
            photos_t.append(t); photos_mid.append(mid); photos_bs.append(bs)
            ordre = np.argsort(kk)
            kk, mm = kk[ordre], mm[ordre]
            # meilleures limites du moment (matériau S3)
            bid_k = kk[kk < k0]
            ask_k = kk[kk > k0]
            if bid_k.size:
                bl_bid[int(bid_k[-1])].append(t)
            if ask_k.size:
                bl_ask[int(ask_k[0])].append(t)
            # S1′ : voisinage en DISTANCE RELATIVE, converti par photo
            demi_k = max(1, round(DEMI_VOISINAGE_REL * mid / bs))
            lo = np.searchsorted(kk, kk - demi_k, side="left")
            hi = np.searchsorted(kk, kk + demi_k, side="right")
            med = np.array([np.median(mm[a:b]) if b > a else np.nan
                            for a, b in zip(lo, hi)])
            r = mm / med
            if M is None:
                ratios.extend(r[np.isfinite(r)].tolist())
                if len(ratios) >= PREFIX:
                    M = float(np.quantile(ratios, QUANTILE_MUR))
            if M is not None:
                elus = set(kk[r >= M].tolist())
                for k in list(duree):
                    if k not in elus:
                        persistances.append(duree.pop(k))
                        episodes.append((k, *debut_episode.pop(k)))
                for k in elus:
                    if k not in duree:
                        debut_episode[k] = (t, "bid" if k < k0 else "ask")
                    duree[k] += 1
    for k, d in duree.items():
        persistances.append(d)
        episodes.append((k, *debut_episode[k]))
    P = float(np.median(persistances)) if persistances else None
    print(f"[{time.time()-t0:5.0f}s] S1′ : M′ = {M:.2f} (voisinage ±{DEMI_VOISINAGE_REL:.2%}) · "
          f"S2′ : P′ = {P} photos ({len(persistances):,} épisodes)", flush=True)

    # ---- exécutions : extraction puis jointures ----------------------------
    low = coin.lower()
    tmp = DEPOT / "chantiers" / "c2_work"
    tmp.mkdir(exist_ok=True)
    _extract_day(SRC / f"{low}_orders_202512.tar.xz", f"{JOUR}/", tmp, f"{low}_*.data.gz")
    ex_t: list[int] = []
    ex_px: list[float] = []
    n_filled = n_px_nul = 0
    for h in range(24):
        f = tmp / JOUR / f"{low}_{h:02d}.data.gz"
        if not f.exists():
            continue
        st = read_statuses(f)
        m = st["statusId"] == FILLED
        n_filled += int(m.sum())
        px = decode(st["limitPx"][m])
        tms = (st["ts"][m] // 1_000_000).astype(np.int64)
        ok = px > 0
        n_px_nul += int((~ok).sum())
        ex_t.extend(tms[ok].tolist()); ex_px.extend(px[ok].tolist())
    ordre = np.argsort(ex_t)
    ex_t = np.asarray(ex_t, dtype=np.int64)[ordre]
    ex_px = np.asarray(ex_px, dtype=np.float64)[ordre]

    # S4′ : mid asof-arrière, tolérance déclarée
    pt = np.asarray(photos_t, dtype=np.int64)
    pmid = np.asarray(photos_mid); pbs = np.asarray(photos_bs)
    idx = np.searchsorted(pt, ex_t, side="right") - 1
    valides = idx >= 0
    idx_c = np.clip(idx, 0, None)
    age = ex_t - pt[idx_c]
    valides &= age <= TOLERANCE_MID_MS
    n_sans_mid = int((~valides).sum())
    dists = np.abs(ex_px[valides] - pmid[idx_c[valides]]) / pmid[idx_c[valides]]
    quantiles = {q: float(np.quantile(dists, q))
                 for q in (0.99, 0.995, FRACTION_BANDE, 0.9999)}
    bande = quantiles[FRACTION_BANDE]
    print(f"[{time.time()-t0:5.0f}s] S4′ : bande = {bande:.4%} — {dists.size:,} exécutions "
          f"jointes ; écartées : limitPx≤0 {n_px_nul:,} ({n_px_nul/max(n_filled,1):.1%} "
          f"des FILLED), sans mid ≤{TOLERANCE_MID_MS} ms : {n_sans_mid:,}", flush=True)

    # S3 : par épisode de mur, premier contact-exécution vs première BL
    ex_k = {}                       # palier -> temps des exécutions, trié
    kx = (ex_px[valides] // pbs[idx_c[valides]]).astype(np.int64)
    tx = ex_t[valides]
    for k, t in zip(kx.tolist(), tx.tolist()):
        ex_k.setdefault(k, []).append(t)
    n_coinc = n_deux = n_ex_seul = n_bl_seul = n_aucun = 0
    delais: list[int] = []
    for k, t_deb, cote in episodes:
        src = bl_bid if cote == "bid" else bl_ask
        lb = src.get(k, [])
        i = bisect_left(lb, t_deb)
        t_bl = lb[i] if i < len(lb) else None
        le = ex_k.get(k, [])
        j = bisect_left(le, t_deb)
        t_ex = le[j] if j < len(le) else None
        if t_bl is not None and t_ex is not None:
            n_deux += 1
            d = t_ex - t_bl
            delais.append(d)
            if abs(d) <= FENETRE_COINCIDENCE_MS:
                n_coinc += 1
        elif t_ex is not None:
            n_ex_seul += 1
        elif t_bl is not None:
            n_bl_seul += 1
        else:
            n_aucun += 1
    taux = n_coinc / n_deux if n_deux else None
    print(f"[{time.time()-t0:5.0f}s] S3 : coïncidence = "
          f"{taux:.1%} sur {n_deux:,} épisodes à double événement "
          f"(ex seule {n_ex_seul:,} · BL seule {n_bl_seul:,} · aucun {n_aucun:,})"
          if taux is not None else "S3 : aucun épisode à double événement", flush=True)

    resultat = {
        "jour": JOUR, "coin": coin, "protocole": "C2-observation.md §5 (2e passe)",
        "manifeste_sha12": man["artefact"]["sha256"][:12],
        "S1p_M": M, "S1p_demi_voisinage_rel": DEMI_VOISINAGE_REL,
        "S2p_P_photos": P, "S2p_episodes": len(persistances),
        "S3_taux_coincidence": taux, "S3_episodes_double": n_deux,
        "S3_ex_seule": n_ex_seul, "S3_bl_seule": n_bl_seul, "S3_aucun": n_aucun,
        "S3_delais_ms_quantiles": ({str(q): float(np.quantile(delais, q))
                                    for q in (0.1, 0.5, 0.9)} if delais else None),
        "S4p_bande": bande, "S4p_quantiles": {str(k): v for k, v in quantiles.items()},
        "S4p_n_jointes": int(dists.size), "S4p_filled_total": n_filled,
        "S4p_ecartees_px_nul": n_px_nul, "S4p_ecartees_sans_mid": n_sans_mid,
        "duree_s": round(time.time() - t0, 1),
    }
    out = DEPOT / "journal" / f"c2-mesure-p2-{JOUR}-{coin}.json"
    out.write_text(json.dumps(resultat, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[{time.time()-t0:5.0f}s] terminé — {out}", flush=True)
    return resultat


if __name__ == "__main__":
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(
        ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    mesure(sys.argv[1] if len(sys.argv) > 1 else "BTC")
