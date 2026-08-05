# -*- coding: utf-8 -*-
"""ÉS — campagne v3. PROTOCOLE PRÉ-ENREGISTRÉ, commité avant la mesure.

Historique, en deux lignes : la v1 est tombée sur l'artefact d'ANCRAGE
(le lieu choisi à T0 est mécaniquement gonflé pendant la fenêtre — ρ⁰ jusqu'à
0,57, FP 100 %). La v2 (normalisation par voisins à même distance du mid
courant) a tué cet artefact pour leurre et recharge (ρ⁰ = −0,03/−0,05, FP
2 %/0,8 %) mais pas l'artefact du CONTACT pour absorption (ρ⁰ = −0,38) : le
palier au contact est systématiquement appauvri par les exécutions
relativement à ses voisins — c'est une propriété du marché, pas du mécanisme.

CE QUE LA v3 CHANGE — deux choses, et rien d'autre :

1. **le centrage sur le nul appris, en coupe franche.** Un biais de lieu
   mesurable se soustrait ; il ne se nie pas. Les 32 bras nuls sont coupés en
   deux : les 16 premiers (graines 200-215) SERVENT À ESTIMER μ⁰ par
   mécanisme ; les 16 autres (216-231), jamais utilisés pour l'estimation,
   vérifient le taux de fausses détections de la statistique CENTRÉE
   ρ' = ρ − μ⁰. Les arms injectés sont jugés sur ρ' avec les règles v1
   inchangées (Student 8 jours, p < 0,05, moyenne > 0, plancher monotone) ;
2. **le verdict d'admission est PAR MÉCANISME.** Une méthode peut savoir voir
   la recharge et ne pas savoir voir l'absorption ; l'écrire est plus
   informatif qu'un tout-ou-rien, et `05` §8 n'exige rien d'autre que le
   plancher inscrit au registre par méthode jugée.

Tout le reste — durées, fenêtre, amplitudes, graines d'arms, α, FP_TOL,
bootstraps, MIN_RUNS, garde-fous, mécanismes, statistique X de la v2,
stabilité, puissance — est IMPORTÉ à l'identique de v1/v2.

L'admission finale confronte le plancher à l'amplitude plausible d'ADR-004
(2,0 × la médiane du voisinage) : plancher ≤ 2,0 → le détecteur est admis ;
au-dessus → écarté, il ne consommera aucun jour de marché.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import harnais.es_campagne as v1                                    # noqa: E402
from harnais.es_campagne import (ALPHA, AMPLITUDES, FP_TOL, GRAINES,  # noqa: E402
                                 GRAINES_NUL, MECANISMES, MIN_RUNS, N_BOOT)
from harnais.es_campagne_v2 import _rho_run_v2                      # noqa: E402
from harnais.generateur import genere                               # noqa: E402
from harnais.stats import student_jours                             # noqa: E402

AMPLITUDE_PLAUSIBLE = 2.0        # ADR-004, déclarée avant cette campagne
GRAINES_CALIBRATION = GRAINES_NUL[:16]    # estiment mu0 — jamais réutilisées
GRAINES_VERIF = GRAINES_NUL[16:]          # vérifient le FP — jamais vues avant

OUT = Path(__file__).resolve().parent.parent / "journal" / "es-campagne-v3-20260805.json"


def _rhos_nuls(tmp: Path, graines, log) -> dict[str, np.ndarray]:
    chemins = []
    for g in graines:
        obs, ver = tmp / f"nul_{g}.parquet", tmp / "v.parquet"
        genere(obs, ver, graine=g, duree_s=v1.DUREE_S, pas_ms=v1.PAS_MS)
        chemins.append(obs)
    fenetre = {int(v1.T0_S * 1000) + i * v1.PAS_MS
               for i in range(int((v1.T1_S - v1.T0_S) * 1000 / v1.PAS_MS))}
    res = {}
    for mec in MECANISMES:
        res[mec] = np.array([_rho_run_v2(p, fenetre, v1._k_pseudo(p, mec))
                             for p in chemins])
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

    log(f"préflight : {pf} — protocole v3 gelé, campagne lancée")
    resultats = {"protocole": "harnais/es_campagne_v3.py — statistique v2 + "
                              "centrage sur nul appris (coupe 16/16), verdict "
                              "par mécanisme", "preflight": pf,
                 "amplitude_plausible": AMPLITUDE_PLAUSIBLE}

    log("volet 1a — calibration : 16 nuls, estimation de μ⁰ par mécanisme")
    calib = _rhos_nuls(tmp, GRAINES_CALIBRATION, log)
    mu0 = {mec: float(r.mean()) for mec, r in calib.items()}
    resultats["mu0"] = {m: round(v, 4) for m, v in mu0.items()}
    log(f"  μ⁰ : {resultats['mu0']}")

    log("volet 1b — vérification : 16 nuls JAMAIS VUS, FP de la statistique centrée")
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
            "moyenne_centree": round(float(centres.mean()), 4),
            "ic95": st["ic95"], "taux_fausses_detections": fp, "passe": passe}
        log(f"  nul[{mec}] centré : moy={centres.mean():.4f} FP={fp:.3f} passe={passe}")

    log("volet 2 — plancher de détection (statistique centrée), par mécanisme")
    arms = {}
    for mec, params in MECANISMES.items():
        if not resultats["bras_nul"][mec]["passe"]:
            arms[mec] = {"verdict": "DISQUALIFIÉ AU BRAS NUL — pas de plancher"}
            log(f"  {mec} : disqualifié au nul, arms non mesurés")
            continue
        arms[mec] = {}
        for amp in AMPLITUDES:
            rhos, ecartes = [], 0
            for g in GRAINES:
                obs, ver = tmp / "i.parquet", tmp / "v.parquet"
                genere(obs, ver, graine=g, duree_s=v1.DUREE_S, pas_ms=v1.PAS_MS,
                       injections=[v1.Injection(mec, v1.T0_S, v1.T1_S - v1.T0_S,
                                                amp, **params)])
                import pyarrow.parquet as pq
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
                    "moyenne_centree": round(st["moyenne"], 4),
                    "d": round(st["moyenne"] / sd, 2) if sd > 0 else None,
                    "p": st["p_value"], "ic95": st["ic95"], "ecartes": ecartes,
                    "detecte": bool(st["p_value"] < ALPHA and st["moyenne"] > 0)}
            else:
                arms[mec][str(amp)] = {"ecartes": ecartes, "detecte": None,
                                       "verdict": "NON MESURABLE"}
            log(f"  {mec} amp={amp} : {arms[mec][str(amp)].get('moyenne_centree')}")
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
            else f"ÉCARTÉ — plancher {plancher} > amplitude plausible "
                 f"{AMPLITUDE_PLAUSIBLE} (ADR-004)")
        log(f"  PLANCHER {mec} : {plancher} → {resultats['admission'][mec]}")

    resultats["duree_totale_s"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(resultats, indent=1, ensure_ascii=False),
                   encoding="utf-8")
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    log(f"terminé — {OUT}")


if __name__ == "__main__":
    main()
