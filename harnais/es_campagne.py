# -*- coding: utf-8 -*-
"""ÉS — la campagne du banc synthétique. PROTOCOLE PRÉ-ENREGISTRÉ.

Commité AVANT la première mesure ; les constantes ci-dessous sont les règles
du jeu et ne se renégocient pas après avoir vu un résultat (`05` §8, doctrine
générale). ÉS juge LA MÉTHODE du banc — la machinerie corrélation de rang +
Student + décision — pas une grandeur (D8, validée le 05/08/2026).

CE QUE LA CAMPAGNE REND, dans l'ordre :

1. **le bras nul** — 32 carnets sans injection, pseudo-étiquettes posées par
   la même règle de lieu et de fenêtre que les injections. Par mécanisme :
   l'IC de Student sur les 32 ρ⁰ doit contenir 0, ET le taux de fausses
   détections sur 1000 tirages bootstrap de 8 « jours » doit rester ≤ FP_TOL.
   Sinon : LA MÉTHODE EST DISQUALIFIÉE (`05` §8) ;
2. **le plancher de détection** par mécanisme — la plus petite amplitude
   (en multiples de la masse médiane locale) détectée par la règle d'arm,
   avec MONOTONIE exigée : toute amplitude supérieure doit détecter aussi,
   un plancher par accident n'est pas un plancher ;
3. **la stabilité du Spearman partiel** quand le bloc de contrôle grandit —
   l'incertitude n° 1 d'`ADR-001`, mesurée avant tout vrai candidat ;
4. **la puissance en jours** — la table effet × jours de la règle d'É4
   (Student bilatéral 5 %), et les jours requis à 80 % pour les effets
   MESURÉS au point 2. C'est le chiffre qui dit si 8 jours d'exploration
   suffisent.

LA STATISTIQUE PAR RUN (= un « jour » synthétique) : X_t = masse au palier
étiqueté k*, normalisée par la médiane de la bande à la photo t (0 si
absent) ; Y_t = présence de l'étiquette à t ; ρ_run = Spearman(X, Y) sur
toutes les photos du run. Un arm = 8 runs (8 graines) → Student sur les 8 ρ,
exactement la forme d'É4 (unité = jour).

LIMITE ÉCRITE D'AVANCE : la méthode est INFORMÉE DU LIEU (elle connaît k*).
Le plancher mesuré est donc une BORNE OPTIMISTE — un plancher déjà au-dessus
de l'amplitude plausible condamne a fortiori toute méthode aveugle. La borne
aveugle viendra avec les vrais candidats.

GARDE-FOUS (`05` §3) appliqués À CHAQUE RUN sur Y : événement < 60 %, classe
minoritaire ≥ 5 % et ≥ 200 photos. Un run qui les viole (leurre retiré trop
tôt, par exemple) est ÉCARTÉ ET COMPTÉ ; un arm avec moins de MIN_RUNS runs
valides est « non mesurable », jamais interpolé.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from harnais.gardefous import GardeFouViole, cible_binaire, evenement_rare  # noqa: E402
from harnais.generateur import Injection, genere                            # noqa: E402
from harnais.stats import spearman, spearman_partiel, student_jours         # noqa: E402

# --- LES CONSTANTES PRÉ-ENREGISTRÉES — ne bougent plus après commit ----------
DUREE_S = 150.0
PAS_MS = 250
T0_S, T1_S = 30.0, 90.0            # fenêtre d'injection : 40 % des photos
AMPLITUDES = (0.5, 1.0, 2.0, 4.0, 8.0)
GRAINES = tuple(range(100, 108))    # 8 « jours » par arm — comme l'exploration
GRAINES_NUL = tuple(range(200, 232))   # 32 bras nuls
ALPHA = 0.05
FP_TOL = 0.10                      # tolérance de fausses détections du bras nul
N_BOOT = 1000
MIN_RUNS = 6                       # en dessous : arm non mesurable
MECANISMES = {
    "leurre":     dict(cote=1, dist_paliers=12, approche_paliers=4),
    "recharge":   dict(cote=0),
    "absorption": dict(cote=1),
}
JOURS_TABLE = (3, 5, 8, 16, 24)
EFFETS_TABLE = (0.5, 1.0, 1.5, 2.0)

OUT = Path(__file__).resolve().parent.parent / "journal" / "es-campagne-20260805.json"


def _priorite_basse() -> None:
    """La campagne partage la machine avec l'enregistreur (C8.4)."""
    import ctypes
    h = ctypes.windll.kernel32.GetCurrentProcess()
    ctypes.windll.kernel32.SetPriorityClass(h, 0x4000)   # BELOW_NORMAL


# --- lecture d'un carnet -> (photos, mediane par photo, masse à k*) ----------

def _series(chemin_obs: Path, k_star: int) -> tuple[np.ndarray, np.ndarray]:
    t = pq.read_table(chemin_obs, columns=["t", "k", "mag"])
    ts, ks, mags = (t["t"].to_numpy(), t["k"].to_numpy(),
                    t["mag"].to_numpy().astype(np.float64))
    photos, inverse = np.unique(ts, return_inverse=True)
    # médiane par photo en un tri global, pas 600 masques sur 2 M de lignes
    ordre = np.argsort(inverse, kind="stable")
    inv_s, mag_s = inverse[ordre], mags[ordre]
    bornes = np.searchsorted(inv_s, np.arange(len(photos) + 1))
    med = np.array([np.median(mag_s[bornes[i]:bornes[i + 1]])
                    if bornes[i + 1] > bornes[i] else 1.0
                    for i in range(len(photos))])
    x = np.zeros(len(photos))
    sel = ks == k_star
    x[inverse[sel]] = mags[sel]
    return photos, x / med


def _k_pseudo(chemin_obs: Path, mecanisme: str) -> int:
    """La règle de lieu du mécanisme, appliquée au carnet NUL à T0 — le
    pseudo-k* du bras nul, choisi exactement comme l'injection choisit le sien."""
    t = pq.read_table(chemin_obs, columns=["t", "k", "mag", "mid", "bs"])
    ts = t["t"].to_numpy()
    t_cible = ts[np.searchsorted(ts, int(T0_S * 1000))]
    sel = ts == t_cible
    ks = t["k"].to_numpy()[sel]
    k0 = int(t["mid"].to_numpy()[sel][0] // t["bs"].to_numpy()[sel][0])
    if mecanisme == "leurre":
        return k0 + MECANISMES["leurre"]["dist_paliers"]
    asks, bids = ks[ks > k0], ks[ks < k0]
    if mecanisme == "absorption":
        return int(asks.min()) if asks.size else k0 + 1
    return int(bids.max()) if bids.size else k0 - 1


def _rho_run(chemin_obs: Path, photos_label: set[int], k_star: int) -> float:
    photos, x = _series(chemin_obs, k_star)
    y = np.array([1.0 if int(p) in photos_label else 0.0 for p in photos])
    evenement_rare(y > 0)          # lève si l'étiquette est « l'état normal »
    cible_binaire(y)               # lève si dégénérée (< 200 photos, < 5 %)
    return spearman(x, y)


# --- les quatre volets -------------------------------------------------------

def volet_injecte(tmp: Path, log) -> dict:
    arms = {}
    for mec, params in MECANISMES.items():
        arms[mec] = {}
        for amp in AMPLITUDES:
            rhos, ecartes = [], 0
            for g in GRAINES:
                obs, ver = tmp / f"i_{mec}_{amp}_{g}.parquet", tmp / "v.parquet"
                genere(obs, ver, graine=g, duree_s=DUREE_S, pas_ms=PAS_MS,
                       injections=[Injection(mec, T0_S, T1_S - T0_S, amp, **params)])
                vt = pq.read_table(ver)
                if vt.num_rows == 0:
                    ecartes += 1
                    obs.unlink()
                    continue
                k_star = int(vt["k"][0].as_py())
                labels = {int(v) for v in vt["t"].to_numpy()}
                try:
                    rhos.append(_rho_run(obs, labels, k_star))
                except GardeFouViole:
                    ecartes += 1
                obs.unlink()
            if len(rhos) >= MIN_RUNS:
                st = student_jours(np.array(rhos))
                detecte = bool(st["p_value"] < ALPHA and st["moyenne"] > 0)
                sd = float(np.std(rhos, ddof=1))
                arms[mec][str(amp)] = {
                    "rhos": [round(r, 4) for r in rhos], "ecartes": ecartes,
                    "moyenne": round(st["moyenne"], 4),
                    "d": round(st["moyenne"] / sd, 2) if sd > 0 else None,
                    "p": st["p_value"], "ic95": st["ic95"], "detecte": detecte}
            else:
                arms[mec][str(amp)] = {"ecartes": ecartes, "valides": len(rhos),
                                       "detecte": None,
                                       "verdict": "NON MESURABLE — étiquettes dégénérées"}
            log(f"  {mec} amp={amp} : "
                f"{arms[mec][str(amp)].get('moyenne', 'non mesurable')} "
                f"(écartés {ecartes})")
    return arms


def volet_nul(tmp: Path, log) -> dict:
    chemins = []
    for g in GRAINES_NUL:
        obs, ver = tmp / f"nul_{g}.parquet", tmp / "v.parquet"
        genere(obs, ver, graine=g, duree_s=DUREE_S, pas_ms=PAS_MS)
        chemins.append(obs)
    log(f"  {len(chemins)} carnets nuls fabriqués")
    fenetre = {int(T0_S * 1000) + i * PAS_MS
               for i in range(int((T1_S - T0_S) * 1000 / PAS_MS))}
    rng = np.random.default_rng(0)
    res = {}
    for mec in MECANISMES:
        rhos = np.array([_rho_run(p, fenetre, _k_pseudo(p, mec)) for p in chemins])
        st = student_jours(rhos)
        tirages = rng.choice(len(rhos), size=(N_BOOT, len(GRAINES)))
        fp = 0
        for t_ in tirages:
            s = student_jours(rhos[t_])
            fp += int(s["p_value"] < ALPHA and s["moyenne"] > 0)
        res[mec] = {"n": len(rhos), "moyenne": round(float(rhos.mean()), 4),
                    "ic95": st["ic95"], "ic_contient_zero":
                        bool(st["ic95"][0] <= 0 <= st["ic95"][1]),
                    "taux_fausses_detections": fp / N_BOOT,
                    "passe": bool(st["ic95"][0] <= 0 <= st["ic95"][1]
                                  and fp / N_BOOT <= FP_TOL)}
        log(f"  nul[{mec}] : moy={res[mec]['moyenne']} "
            f"FP={res[mec]['taux_fausses_detections']:.3f} passe={res[mec]['passe']}")
    for p in chemins:
        p.unlink()
    return res


def volet_stabilite(log) -> dict:
    """Spearman partiel quand le bloc grandit — biais et dispersion contre la
    référence sans confondant (k=0). Seuils pré-enregistrés : |biais| < 0,02,
    écart-type < 1,5× la référence, jusqu'à k=20."""
    rng = np.random.default_rng(7)
    n, reps, b = 300, 400, 0.6
    res = {}
    for k in (0, 1, 2, 5, 10, 20):
        vals = []
        for _ in range(reps):
            u = rng.normal(size=n)
            Z = rng.normal(size=(n, k)) if k else None
            gz = Z @ rng.normal(0.5, 0.1, size=k) if k else 0.0
            x = b * u + gz + rng.normal(size=n)
            y = b * u + gz + rng.normal(size=n)
            vals.append(spearman_partiel(x, y, Z))
        res[str(k)] = {"moyenne": round(float(np.mean(vals)), 4),
                       "ecart_type": round(float(np.std(vals)), 4)}
        log(f"  bloc k={k} : {res[str(k)]}")
    ref = res["0"]
    res["verdict"] = {
        "biais_max": max(abs(res[str(k)]["moyenne"] - ref["moyenne"])
                         for k in (1, 2, 5, 10, 20)),
        "ratio_ecart_type_max": max(res[str(k)]["ecart_type"] / ref["ecart_type"]
                                    for k in (1, 2, 5, 10, 20)),
        "stable": bool(
            max(abs(res[str(k)]["moyenne"] - ref["moyenne"])
                for k in (1, 2, 5, 10, 20)) < 0.02
            and max(res[str(k)]["ecart_type"] / ref["ecart_type"]
                    for k in (1, 2, 5, 10, 20)) < 1.5)}
    return res


def volet_puissance(arms: dict, log) -> dict:
    from scipy import stats as sps

    def puissance(d: float, n: int) -> float:
        tc = sps.t.ppf(1 - ALPHA / 2, df=n - 1)
        nc = d * np.sqrt(n)
        return float(1 - sps.nct.cdf(tc, df=n - 1, nc=nc)
                     + sps.nct.cdf(-tc, df=n - 1, nc=nc))

    table = {f"d={d}": {f"n={n}": round(puissance(d, n), 3) for n in JOURS_TABLE}
             for d in EFFETS_TABLE}

    def n_requis(d: float, cible: float = 0.80) -> int | None:
        for n in range(2, 201):
            if puissance(d, n) >= cible:
                return n
        return None

    requis = {f"d={d}": n_requis(d) for d in EFFETS_TABLE}
    mesures = {}
    for mec, par_amp in arms.items():
        mesures[mec] = {}
        for amp, r in par_amp.items():
            if r.get("d") and np.isfinite(r["d"]):
                mesures[mec][amp] = {"d": r["d"], "jours_requis_80pct": n_requis(r["d"])}
    log(f"  jours requis à 80 % : {requis}")
    return {"table": table, "jours_requis_80pct": requis,
            "effets_mesures": mesures}


def main() -> None:
    _priorite_basse()
    from harnais.preflight import run as preflight
    pf = preflight([])   # arbre propre, garde-fous prouvés — aucun jour de marché
    t0 = time.time()
    tmp = Path(__file__).resolve().parent / "_es_tmp"
    tmp.mkdir(exist_ok=True)

    def log(msg: str) -> None:
        print(f"[{time.time()-t0:7.0f}s] {msg}", flush=True)

    log(f"préflight : {pf} — protocole gelé, campagne lancée")
    resultats = {"protocole": "harnais/es_campagne.py, constantes pré-enregistrées",
                 "preflight": pf}
    log("volet 1/4 — bras nul (32 carnets, 3 règles de lieu)")
    resultats["bras_nul"] = volet_nul(tmp, log)
    log("volet 2/4 — plancher de détection (3 mécanismes × 5 amplitudes × 8 jours)")
    resultats["arms"] = volet_injecte(tmp, log)
    resultats["planchers"] = {}
    for mec, par_amp in resultats["arms"].items():
        plancher = None
        for a in sorted((float(a) for a in par_amp), reverse=True):
            if par_amp[str(a)].get("detecte"):   # monotonie : on descend tant que ça détecte
                plancher = a
            else:
                break
        resultats["planchers"][mec] = plancher
        log(f"  PLANCHER {mec} : {plancher}")
    log("volet 3/4 — stabilité du Spearman partiel (ADR-001, incertitude n° 1)")
    resultats["stabilite_partielle"] = volet_stabilite(log)
    log("volet 4/4 — puissance en jours")
    resultats["puissance"] = volet_puissance(resultats["arms"], log)
    resultats["duree_totale_s"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(resultats, indent=1, ensure_ascii=False),
                   encoding="utf-8")
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    log(f"terminé — {OUT}")


if __name__ == "__main__":
    main()
