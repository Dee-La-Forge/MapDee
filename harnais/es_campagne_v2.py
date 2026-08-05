# -*- coding: utf-8 -*-
"""ÉS — campagne v2. PROTOCOLE PRÉ-ENREGISTRÉ, commité avant la mesure.

La v1 (`harnais/es_campagne.py`) a été DISQUALIFIÉE PAR SON PROPRE BRAS NUL
le 05/08/2026 : ρ⁰ = 0,44-0,57, 100 % de fausses détections. Cause identifiée,
l'ARTEFACT D'ANCRAGE — le palier visé est choisi au début de la fenêtre, à
distance fixe du mid de cet instant ; or la masse d'un palier s'accumule tant
que le mid est proche : un palier ancré à T0 est mécaniquement gonflé pendant
la fenêtre, injection ou pas.

SEUL CHANGEMENT v1 → v2, et il est ici : la statistique X.

    v1 : X_t = mag(k*, t) / médiane(toute la bande à t)
    v2 : X_t = mag(k*, t) / médiane(des paliers du MÊME CÔTÉ dont la distance
         au mid COURANT est à ±3 paliers de celle de k*, k* exclu)

Les voisins à même distance du mid courant subissent le même artefact
d'ancrage et la même accumulation de proximité : le rapport les annule et ne
laisse que l'excès propre au palier visé. Si k* n'a pas de voisin valide à la
photo t (côté vide), X_t = 0 — compté, jamais interpolé.

TOUT LE RESTE EST IMPORTÉ DE v1 À L'IDENTIQUE : durées, fenêtre, amplitudes,
graines, α, tolérance FP, bootstraps, MIN_RUNS, mécanismes, garde-fous,
volets. La substitution de la statistique est faite par remplacement explicite
de `_rho_run` dans le module v1 avant d'appeler ses volets — le diff entier
de la méthode tient dans `_series_v2` ci-dessous, il n'y a rien d'autre à
auditer.

Le verdict du bras nul reste souverain : si la v2 détecte aussi dans le nul,
elle est disqualifiée pareil.
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
from harnais.gardefous import cible_binaire, evenement_rare         # noqa: E402
from harnais.stats import spearman                                  # noqa: E402

DEMI_VOISINAGE = 3
OUT = Path(__file__).resolve().parent.parent / "journal" / "es-campagne-v2-20260805.json"


def _series_v2(chemin_obs: Path, k_star: int) -> tuple[np.ndarray, np.ndarray]:
    """X_t = mag(k*, t) / médiane des voisins à MÊME distance du mid courant."""
    t = pq.read_table(chemin_obs, columns=["t", "k", "mag", "mid", "bs"])
    ts = t["t"].to_numpy()
    ks = t["k"].to_numpy()
    mags = t["mag"].to_numpy().astype(np.float64)
    mids = t["mid"].to_numpy()
    bss = t["bs"].to_numpy()
    photos, inverse = np.unique(ts, return_inverse=True)
    ordre = np.argsort(inverse, kind="stable")
    bornes = np.searchsorted(inverse[ordre], np.arange(len(photos) + 1))
    x = np.zeros(len(photos))
    for i in range(len(photos)):
        tr = ordre[bornes[i]:bornes[i + 1]]
        if tr.size == 0:
            continue
        k0 = int(mids[tr[0]] // bss[tr[0]])
        cote_star = np.sign(k_star - k0)
        if cote_star == 0:
            continue                      # mid SUR k* : côté indéfini, X_t = 0
        d_star = abs(k_star - k0)
        kk, mm = ks[tr], mags[tr]
        meme_cote = np.sign(kk - k0) == cote_star
        voisins = meme_cote & (np.abs(np.abs(kk - k0) - d_star) <= DEMI_VOISINAGE) \
            & (kk != k_star)
        ref = np.median(mm[voisins]) if voisins.any() else 0.0
        if ref <= 0:
            continue
        ici = mm[kk == k_star]
        x[i] = float(ici[0]) / ref if ici.size else 0.0
    return photos, x


def _rho_run_v2(chemin_obs: Path, photos_label: set[int], k_star: int) -> float:
    photos, x = _series_v2(chemin_obs, k_star)
    y = np.array([1.0 if int(p) in photos_label else 0.0 for p in photos])
    evenement_rare(y > 0)
    cible_binaire(y)
    return spearman(x, y)


def main() -> None:
    v1._priorite_basse()
    from harnais.preflight import run as preflight
    pf = preflight([])
    t0 = time.time()
    tmp = Path(__file__).resolve().parent / "_es_tmp"
    tmp.mkdir(exist_ok=True)

    def log(msg: str) -> None:
        print(f"[{time.time()-t0:7.0f}s] {msg}", flush=True)

    # LA substitution — tout le protocole v1 tourne avec la statistique v2.
    v1._rho_run = _rho_run_v2

    log(f"préflight : {pf} — protocole v2 gelé, campagne lancée")
    resultats = {"protocole": "harnais/es_campagne_v2.py — v1 + statistique "
                              "normalisée par voisins à même distance",
                 "preflight": pf}
    log("volet 1/4 — bras nul (32 carnets, statistique v2) — verdict souverain")
    resultats["bras_nul"] = v1.volet_nul(tmp, log)
    disqualifiee = not all(r["passe"] for r in resultats["bras_nul"].values())
    resultats["methode_disqualifiee"] = disqualifiee
    if disqualifiee:
        log("BRAS NUL DÉTECTE : méthode v2 DISQUALIFIÉE — on n'ira pas plus loin")
    else:
        log("volet 2/4 — plancher de détection")
        resultats["arms"] = v1.volet_injecte(tmp, log)
        resultats["planchers"] = {}
        for mec, par_amp in resultats["arms"].items():
            plancher = None
            for a in sorted((float(x) for x in par_amp), reverse=True):
                if par_amp[str(a)].get("detecte"):
                    plancher = a
                else:
                    break
            resultats["planchers"][mec] = plancher
            log(f"  PLANCHER {mec} : {plancher}")
        log("volet 3/4 — stabilité du Spearman partiel")
        resultats["stabilite_partielle"] = v1.volet_stabilite(log)
        log("volet 4/4 — puissance en jours")
        resultats["puissance"] = v1.volet_puissance(resultats["arms"], log)
    resultats["duree_totale_s"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(resultats, indent=1, ensure_ascii=False),
                   encoding="utf-8")
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    log(f"terminé — {OUT}")


if __name__ == "__main__":
    main()
