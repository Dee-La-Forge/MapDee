# -*- coding: utf-8 -*-
"""ÉS — campagne v5 : LE REJUGEMENT SOUS L'UNITÉ RÉELLE (ADR-005, acceptée).

PROTOCOLE PRÉ-ENREGISTRÉ, commité avant la mesure. Ce qui change par rapport
à la v4 — et RIEN d'autre :

* **la gamme d'amplitudes** est recalée sur la mesure S1 du jour de banc BTC
  (`journal/c2-mesure-20251208-BTC.json` : quantile 0,99 du ratio
  masse/voisinage = **485**). Gamme : M/8, M/4, M/2, M, 2M — soit
  {61, 121, 242, 485, 970} × la médiane de voisinage ;
* **la barre d'admission** devient : plancher ≤ **485** (= savoir voir un
  mécanisme qui atteint le quantile 0,99 réel — « être un mur au sens de
  S1 »), remplaçant la barre 2,0 d'ADR-004 ;
* **graines de nul neuves** (400-431), jamais vues par v1-v4.

Tout le reste est la composition v4 à l'identique : statistique v2 nue pour
leurre/recharge, centrée pour absorption (μ⁰ sur 16 nuls de calibration),
vérification FP sur 16 nuls jamais vus, Student 8 graines-jours, plancher
monotone, garde-fous par run.

LIMITE ÉCRITE D'AVANCE : le générateur reste zero-intelligence et HOMOGÈNE —
injecter à 485× le voisinage dans un carnet homogène est plus visible qu'au
même ratio dans le carnet réel hétérogène. Les planchers v5 restent des
bornes OPTIMISTES, doublement (lieu connu + monde homogène). L'étape
au-dessus — un générateur à hétérogénéité réaliste — est la « montée en
gamme par ADR » prévue par D3, non lancée ici.

Les planchers v4 (ancienne unité) restent au registre : on n'efface pas,
on ajoute (`05` §5).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import harnais.es_campagne as v1                                    # noqa: E402
from harnais.es_campagne import (ALPHA, FP_TOL, GRAINES, MECANISMES,  # noqa: E402
                                 MIN_RUNS, N_BOOT)
from harnais.es_campagne_v2 import _rho_run_v2                      # noqa: E402
from harnais.generateur import Injection, genere                    # noqa: E402
from harnais.stats import student_jours                             # noqa: E402

M_REEL_BTC = 485.0                       # S1, jour de banc BTC — ADR-005
AMPLITUDES_V5 = tuple(round(M_REEL_BTC * f) for f in (1 / 8, 1 / 4, 1 / 2, 1, 2))
BARRE_ADMISSION = M_REEL_BTC
GRAINES_NUL_V5 = tuple(range(400, 432))  # neuves — jamais vues par v1-v4
GRAINES_CALIB = GRAINES_NUL_V5[:16]
GRAINES_VERIF = GRAINES_NUL_V5[16:]
CENTRES = {"leurre": False, "recharge": False, "absorption": True}

OUT = Path(__file__).resolve().parent.parent / "journal" / "es-campagne-v5-20260805.json"


def _rhos_nuls(tmp, graines, log):
    chemins = []
    for g in graines:
        obs, ver = tmp / f"nul_{g}.parquet", tmp / "v.parquet"
        genere(obs, ver, graine=g, duree_s=v1.DUREE_S, pas_ms=v1.PAS_MS)
        chemins.append(obs)
    fenetre = {int(v1.T0_S * 1000) + i * v1.PAS_MS
               for i in range(int((v1.T1_S - v1.T0_S) * 1000 / v1.PAS_MS))}
    res = {mec: np.array([_rho_run_v2(p, fenetre, v1._k_pseudo(p, mec))
                          for p in chemins]) for mec in MECANISMES}
    for p in chemins:
        p.unlink()
    return res


def main() -> None:
    v1._priorite_basse()
    from harnais.preflight import run as preflight
    pf = preflight([])
    t0 = time.time()
    tmp = Path(__file__).resolve().parent / "_es_tmp"
    tmp.mkdir(exist_ok=True)

    def log(msg):
        print(f"[{time.time()-t0:7.0f}s] {msg}", flush=True)

    log(f"préflight : {pf} — v5 gelée : gamme {AMPLITUDES_V5}, barre {BARRE_ADMISSION}")
    resultats = {"protocole": "harnais/es_campagne_v5.py — rejugement ADR-005, "
                              "unité réelle S1-BTC", "preflight": pf,
                 "gamme": list(AMPLITUDES_V5), "barre": BARRE_ADMISSION}

    log("volet 1a — calibration μ⁰(absorption) : 16 nuls neufs")
    calib = _rhos_nuls(tmp, GRAINES_CALIB, log)
    mu0 = {m: (float(calib[m].mean()) if CENTRES[m] else 0.0) for m in MECANISMES}
    resultats["mu0"] = {m: round(v, 4) for m, v in mu0.items()}
    log(f"  μ⁰ : {resultats['mu0']}")

    log("volet 1b — vérification : 16 nuls neufs jamais vus")
    verif = _rhos_nuls(tmp, GRAINES_VERIF, log)
    rng = np.random.default_rng(0)
    resultats["bras_nul"] = {}
    for mec, rhos in verif.items():
        centres = rhos - mu0[mec]
        st = student_jours(centres)
        tirages = rng.choice(len(centres), size=(N_BOOT, len(GRAINES)))
        fp = sum(1 for t_ in tirages
                 if (lambda s: s["p_value"] < ALPHA and s["moyenne"] > 0)
                 (student_jours(centres[t_]))) / N_BOOT
        passe = bool(st["ic95"][0] <= 0 <= st["ic95"][1] and fp <= FP_TOL)
        resultats["bras_nul"][mec] = {"moyenne": round(float(centres.mean()), 4),
                                      "fp": fp, "passe": passe}
        log(f"  nul[{mec}] : moy={centres.mean():.4f} FP={fp:.3f} passe={passe}")

    log("volet 2 — planchers dans l'unité réelle")
    arms: dict = {}
    for mec, params in MECANISMES.items():
        if not resultats["bras_nul"][mec]["passe"]:
            arms[mec] = {"verdict": "DISQUALIFIÉ AU BRAS NUL"}
            continue
        arms[mec] = {}
        for amp in AMPLITUDES_V5:
            rhos, ecartes = [], 0
            for g in GRAINES:
                obs, ver = tmp / "i.parquet", tmp / "v.parquet"
                genere(obs, ver, graine=g, duree_s=v1.DUREE_S, pas_ms=v1.PAS_MS,
                       injections=[Injection(mec, v1.T0_S, v1.T1_S - v1.T0_S,
                                             float(amp), **params)])
                vt = pq.read_table(ver)
                if vt.num_rows == 0:
                    ecartes += 1
                    continue
                try:
                    rhos.append(_rho_run_v2(
                        obs, {int(x) for x in vt["t"].to_numpy()},
                        int(vt["k"][0].as_py())) - mu0[mec])
                except v1.GardeFouViole:
                    ecartes += 1
            if len(rhos) >= MIN_RUNS:
                st = student_jours(np.array(rhos))
                sd = float(np.std(rhos, ddof=1))
                arms[mec][str(amp)] = {
                    "moyenne": round(st["moyenne"], 4),
                    "d": round(st["moyenne"] / sd, 2) if sd > 0 else None,
                    "p": st["p_value"], "ecartes": ecartes,
                    "detecte": bool(st["p_value"] < ALPHA and st["moyenne"] > 0)}
            else:
                arms[mec][str(amp)] = {"ecartes": ecartes, "detecte": None}
            log(f"  {mec} amp={amp} : {arms[mec][str(amp)].get('moyenne')} "
                f"(d={arms[mec][str(amp)].get('d')})")
    resultats["arms"] = arms

    resultats["planchers"] = {}
    resultats["admission"] = {}
    for mec in MECANISMES:
        if "verdict" in arms[mec]:
            resultats["planchers"][mec] = None
            resultats["admission"][mec] = "REJETÉ (bras nul)"
            continue
        plancher = None
        for a in sorted(AMPLITUDES_V5, reverse=True):
            if arms[mec][str(a)].get("detecte"):
                plancher = a
            else:
                break
        resultats["planchers"][mec] = plancher
        resultats["admission"][mec] = (
            "ADMIS" if plancher is not None and plancher <= BARRE_ADMISSION
            else f"ÉCARTÉ — plancher {plancher} > {BARRE_ADMISSION} (ADR-005)")
        log(f"  PLANCHER {mec} : {plancher} → {resultats['admission'][mec]}")

    resultats["duree_totale_s"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(resultats, indent=1, ensure_ascii=False),
                   encoding="utf-8")
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    log(f"terminé — {OUT}")


if __name__ == "__main__":
    main()
