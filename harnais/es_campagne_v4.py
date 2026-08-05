# -*- coding: utf-8 -*-
"""ÉS — campagne v4, LA COMPOSITION FINALE. PROTOCOLE PRÉ-ENREGISTRÉ.

Ce que les trois itérations ont appris, chacune par son bras nul :

* v1 — artefact d'ANCRAGE (lieu choisi à T0, gonflé pendant la fenêtre) :
  ρ⁰ jusqu'à 0,57, FP 100 %. Disqualifiée.
* v2 — normalisation par voisins à même distance du mid courant : tue
  l'ancrage. Leurre et recharge passent (ρ⁰ −0,03/−0,05, FP 2 %/0,8 %) ;
  absorption garde l'artefact du CONTACT (le palier au contact est appauvri
  par les exécutions relativement à ses voisins) : ρ⁰ = −0,38. Disqualifiée.
* v3 — centrage sur nul appris : répare absorption (vérifié sur 16 graines
  jamais vues : FP 0,4 %) mais CASSE leurre et recharge — ils n'avaient pas
  de biais, soustraire un μ⁰ bruité leur a ajouté de la variance (FP 27 %,
  13 %). Disqualifiés sous centrage.

LA COMPOSITION v4, qui en découle mécaniquement :

* **leurre, recharge** : statistique v2, NON centrée ;
* **absorption** : statistique v2, centrée par μ⁰ estimé sur calibration.

Et pour que cette composition ne soit pas un choix après coup : elle est
validée ici sur **32 graines de nul entièrement neuves (300-331), jamais vues
par v1, v2 ni v3** — 16 pour calibrer μ⁰(absorption), 16 pour vérifier le FP
de chaque mécanisme sous SA statistique assignée. Puis les planchers des
trois mécanismes sont remesurés sous ce protocole unique, et confrontés à
l'amplitude plausible d'ADR-004 (2,0).

Tout le reste (durées, fenêtre, amplitudes, graines d'arms, α, FP_TOL,
bootstraps, MIN_RUNS, garde-fous, monotonie du plancher) : inchangé depuis v1.

LIMITES ÉCRITES D'AVANCE, pour le rapport : (1) la méthode est informée du
lieu — borne optimiste ; (2) trois itérations de méthode ont précédé — le
risque résiduel de sur-ajustement méthodologique est réel, borné par le fait
que chaque verdict de nul a été rendu sur des graines non réutilisées, et que
celui-ci l'est sur des graines neuves.
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
from harnais.es_campagne import (ALPHA, AMPLITUDES, FP_TOL, GRAINES,  # noqa: E402
                                 MECANISMES, MIN_RUNS, N_BOOT)
from harnais.es_campagne_v2 import _rho_run_v2                      # noqa: E402
from harnais.generateur import Injection, genere                    # noqa: E402
from harnais.stats import student_jours                             # noqa: E402

AMPLITUDE_PLAUSIBLE = 2.0                    # ADR-004
GRAINES_NUL_V4 = tuple(range(300, 332))      # NEUVES — jamais vues avant
GRAINES_CALIB = GRAINES_NUL_V4[:16]          # μ⁰(absorption) seulement
GRAINES_VERIF = GRAINES_NUL_V4[16:]
CENTRES = {"leurre": False, "recharge": False, "absorption": True}

OUT = Path(__file__).resolve().parent.parent / "journal" / "es-campagne-v4-20260805.json"


def _rhos_nuls(tmp: Path, graines, log) -> dict[str, np.ndarray]:
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

    def log(msg: str) -> None:
        print(f"[{time.time()-t0:7.0f}s] {msg}", flush=True)

    log(f"préflight : {pf} — protocole v4 gelé (composition finale)")
    resultats = {"protocole": "harnais/es_campagne_v4.py — composition par "
                              "mécanisme, nuls neufs 300-331",
                 "preflight": pf, "amplitude_plausible": AMPLITUDE_PLAUSIBLE,
                 "centrage": CENTRES}

    log("volet 1a — calibration μ⁰(absorption) : 16 nuls neufs")
    calib = _rhos_nuls(tmp, GRAINES_CALIB, log)
    mu0 = {mec: (float(calib[mec].mean()) if CENTRES[mec] else 0.0)
           for mec in MECANISMES}
    resultats["mu0"] = {m: round(v, 4) for m, v in mu0.items()}
    log(f"  μ⁰ appliqués : {resultats['mu0']}")

    log("volet 1b — vérification finale : 16 nuls neufs, statistique assignée")
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
        resultats["bras_nul"][mec] = {
            "moyenne": round(float(centres.mean()), 4), "ic95": st["ic95"],
            "taux_fausses_detections": fp, "passe": passe}
        log(f"  nul[{mec}] : moy={centres.mean():.4f} FP={fp:.3f} passe={passe}")

    log("volet 2 — planchers, protocole unique")
    arms: dict = {}
    for mec, params in MECANISMES.items():
        if not resultats["bras_nul"][mec]["passe"]:
            arms[mec] = {"verdict": "DISQUALIFIÉ AU BRAS NUL"}
            log(f"  {mec} : disqualifié, arms non mesurés")
            continue
        arms[mec] = {}
        for amp in AMPLITUDES:
            rhos, ecartes = [], 0
            for g in GRAINES:
                obs, ver = tmp / "i.parquet", tmp / "v.parquet"
                genere(obs, ver, graine=g, duree_s=v1.DUREE_S, pas_ms=v1.PAS_MS,
                       injections=[Injection(mec, v1.T0_S, v1.T1_S - v1.T0_S,
                                             amp, **params)])
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
                    "p": st["p_value"], "ic95": st["ic95"], "ecartes": ecartes,
                    "detecte": bool(st["p_value"] < ALPHA and st["moyenne"] > 0)}
            else:
                arms[mec][str(amp)] = {"ecartes": ecartes, "detecte": None,
                                       "verdict": "NON MESURABLE"}
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
        for a in sorted(AMPLITUDES, reverse=True):
            if arms[mec][str(a)].get("detecte"):
                plancher = a
            else:
                break
        resultats["planchers"][mec] = plancher
        resultats["admission"][mec] = (
            "ADMIS" if plancher is not None and plancher <= AMPLITUDE_PLAUSIBLE
            else f"ÉCARTÉ — plancher {plancher} > {AMPLITUDE_PLAUSIBLE} (ADR-004)")
        log(f"  PLANCHER {mec} : {plancher} → {resultats['admission'][mec]}")

    resultats["duree_totale_s"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(resultats, indent=1, ensure_ascii=False),
                   encoding="utf-8")
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    log(f"terminé — {OUT}")


if __name__ == "__main__":
    main()
