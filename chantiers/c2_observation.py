# -*- coding: utf-8 -*-
"""C2 — la mesure du jour de banc. Applique `C2-observation.md` (gelé AVANT
la livraison du jour), règle de lecture par règle de lecture, rien d'autre.

    python chantiers/c2_observation.py BTC        # dès la livraison BTC
    python chantiers/c2_observation.py ETH        # quand ETH sera livré

SOURCES — certifiées toutes les deux :
* `deep_20251208_<coin>.parquet` (+ manifeste de fabrication) — S1, S2, S5 ;
* les statuts d'ordres re-extraits de l'ARCHIVE SOURCE (`<coin>_orders_202512.tar.xz`),
  comme C5 — les exécutions (statusId FILLED) donnent S3 et S4 **sans toucher
  aux `hl_fills` à manifestes non certifiés** (dette 4 ter d'ETAT : contournée
  pour C2, à trancher pour le reste).

S6 (coût du jour) est lu du journal de construction, pas mesuré ici.
"""
from __future__ import annotations

import json
import sys
import time
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
from harnais.extracteurs import charge                              # noqa: E402
from harnais.stats import spearman                                  # noqa: E402

JOUR = "20251208"
DIST_MAX = 0.005          # la même bande que les extracteurs du banc
DEMI_VOISINAGE = 20       # la localité du mur (C0 §4, ADR-004)
QUANTILE_MUR = 0.99       # S1 : ~1 palier de bande sur 100 est un mur — gelé
FRACTION_BANDE = 0.999    # S4 : la bande d'étude contient 99,9 % du flux — gelé
SEUIL_COINCIDENCE = 0.95  # S3 : au-delà, variante exécution retenue — gelé
FENETRES_S5 = (1, 4, 16, 64)   # résolutions candidates pour les paires intra-unité


def mesure(coin: str) -> dict:
    t0 = time.time()
    chemin = DEPOT / "data" / "openbook" / "deep" / "parts" / f"deep_{JOUR}_{coin}.parquet"
    assert chemin.exists(), f"{chemin} absent — le jour de banc n'est pas livré"
    man = json.loads((chemin.parent / f"{chemin.name}.manifest.json").read_text(encoding="utf-8"))
    assert man.get("schema_manifeste", 0) >= 1 and man["artefact"]["sha256"], \
        "manifeste non certifié — refus"
    print(f"[{time.time()-t0:5.0f}s] manifeste certifié ({man['artefact']['sha256'][:12]}…), "
          f"commit {man['code']['court']}, sale={man['code']['sale']}", flush=True)

    # ---- passe deep : S1, S2, S5 -------------------------------------------
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(chemin)
    ratios: list[float] = []              # S1 : mag / médiane(voisinage ±20)
    duree_au_dessus: dict[int, int] = defaultdict(int)   # S2, par palier k
    persistances: list[int] = []
    seuil_provisoire = None
    photos_vues = 0
    masses_par_photo: list[float] = []    # S5 : masse de bande (fenêtres)
    # deux sous-passes sur le même flux : la première échantillonne les ratios
    # (1 photo sur 8) pour poser M ; la seconde mesure les persistances. Pour
    # rester en une lecture disque, M est posé sur les 25 000 premiers ratios
    # (préfixe déclaré, comme C8.2) puis appliqué au fil de l'eau.
    PREFIX = 25_000
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
            k0 = int(mids[m][0] // bss[m][0])
            photos_vues += 1
            masses_par_photo.append(float(mm.sum()))
            ordre = np.argsort(kk)
            kk, mm = kk[ordre], mm[ordre]
            # paliers triés : le voisinage ±20 est une TRANCHE — searchsorted
            # + médiane de tranche, O(n·log) par photo. La version masque
            # était en O(n²) : 25 G opérations sur la journée, invivable.
            lo = np.searchsorted(kk, kk - DEMI_VOISINAGE, side="left")
            hi = np.searchsorted(kk, kk + DEMI_VOISINAGE, side="right")
            med_vois = np.array([np.median(mm[a:b]) if b > a else np.nan
                                 for a, b in zip(lo, hi)])
            r = mm / med_vois
            if seuil_provisoire is None:
                ratios.extend(r[np.isfinite(r)].tolist())
                if len(ratios) >= PREFIX:
                    seuil_provisoire = float(np.quantile(ratios, QUANTILE_MUR))
            if seuil_provisoire is not None:
                elus = set(kk[r >= seuil_provisoire].tolist())
                for k in list(duree_au_dessus):
                    if k not in elus:
                        persistances.append(duree_au_dessus.pop(k))
                for k in elus:
                    duree_au_dessus[k] += 1
    persistances.extend(duree_au_dessus.values())
    M = seuil_provisoire
    P = float(np.median(persistances)) if persistances else None
    print(f"[{time.time()-t0:5.0f}s] S1 : M = {M:.2f} (quantile {QUANTILE_MUR} du "
          f"ratio masse/voisinage, préfixe {PREFIX}) — "
          f"S2 : P = {P} photos (médiane, {len(persistances):,} épisodes)", flush=True)

    # ---- S5 : fraction de paires intra-unité qui se recouvrent -------------
    s5 = {}
    n = len(masses_par_photo)
    for w in FENETRES_S5:
        # observations = fenêtres glissantes de w photos, unité = le jour :
        # fraction de paires d'observations du jour qui partagent ≥ 1 photo
        n_obs = n - w + 1
        if n_obs < 2:
            continue
        paires_total = n_obs * (n_obs - 1) / 2
        paires_recouvrantes = sum(n_obs - d for d in range(1, min(w, n_obs)))
        s5[f"fenetre_{w}"] = round(paires_recouvrantes / paires_total, 6)
    print(f"[{time.time()-t0:5.0f}s] S5 : {s5}", flush=True)

    # ---- passe statuts : S3, S4 (exécutions depuis l'archive certifiée) ----
    low = coin.lower()
    tmp = DEPOT / "chantiers" / "c2_work"
    tmp.mkdir(exist_ok=True)
    _extract_day(SRC / f"{low}_orders_202512.tar.xz", f"{JOUR}/", tmp, f"{low}_*.data.gz")
    dists_exec = []       # S4 : distance relative au mid des exécutions
    n_exec = 0
    for h in range(24):
        f = tmp / JOUR / f"{low}_{h:02d}.data.gz"
        if not f.exists():
            continue
        st = read_statuses(f)
        m = st["statusId"] == FILLED
        px = decode(st["limitPx"][m])
        # le mid de référence : le mid médian de l'heure lu du deep n'est pas
        # disponible ici sans jointure — approximation DÉCLARÉE : le mid de
        # l'heure = médiane des prix exécutés de l'heure (les exécutions se
        # font au contact, l'écart est < la bande par construction)
        if px.size:
            mid_h = float(np.median(px))
            dists_exec.extend((np.abs(px - mid_h) / mid_h).tolist())
            n_exec += int(px.size)
        f.unlink()
    bande = float(np.quantile(dists_exec, FRACTION_BANDE)) if dists_exec else None
    print(f"[{time.time()-t0:5.0f}s] S4 : bande d'étude = {bande:.5%} "
          f"({FRACTION_BANDE:.1%} de {n_exec:,} exécutions)", flush=True)

    resultat = {
        "jour": JOUR, "coin": coin, "photos": photos_vues,
        "manifeste_sha12": man["artefact"]["sha256"][:12],
        "S1_M": M, "S1_quantile": QUANTILE_MUR,
        "S2_P_photos": P, "S2_episodes": len(persistances),
        "S3": "PARTIEL — variante topologique et coïncidence exigent la "
              "jointure photo-à-photo deep×exécutions : 2e passe, protocole "
              "inchangé, après ETH",
        "S4_bande": bande, "S4_n_executions": n_exec,
        "S4_approximation_declaree": "mid horaire = médiane des prix exécutés "
                                     "de l'heure",
        "S5_paires_intra_unite": s5,
        "S6": "lu du journal de construction : ~80 min le jour de banc BTC, "
              "phase all — voir 06 §8",
        "duree_s": round(time.time() - t0, 1),
    }
    out = DEPOT / "journal" / f"c2-mesure-{JOUR}-{coin}.json"
    out.write_text(json.dumps(resultat, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[{time.time()-t0:5.0f}s] terminé — {out}", flush=True)
    return resultat


if __name__ == "__main__":
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(
        ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    mesure(sys.argv[1] if len(sys.argv) > 1 else "BTC")
