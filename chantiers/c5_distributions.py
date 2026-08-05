"""C5 étape 1 — LES DISTRIBUTIONS, rien d'autre.

Protocole : `chantiers/C5-protagonistes.md`, commité AVANT ce calcul.

Ce script ne classe rien, ne compare rien, ne conclut rien. Il produit les
distributions des grandeurs du §4 par portefeuille et par jour, et il applique
les garde-fous du §6. C'est la seule chose autorisée à ce stade : le protocole
interdit tout classement avant que les distributions n'aient été regardées.

SOURCE : les statuts d'ordres du L4. Ils portent `userId`, `oid`, `statusId`,
`isAsk`, `origSz`, et surtout **`timestampDiff`** — la durée de vie exacte de
l'ordre en millisecondes, sans reconstruction de carnet. C'est ce champ qui rend
ce chantier indépendant de tout verrou.

CE QUI N'EST PAS CALCULÉ ICI, ET POURQUOI : la distance au mid à la pose exige
un carnet reconstruit. Elle est déclarée au §4 du protocole et reportée à
l'étape suivante. Ne pas la calculer n'est pas un oubli, c'est une dépendance.

PÉRIMÈTRE : déclaré au §8 du protocole — jours 08 à 16, BTC et ETH. Ce script
refuse tout autre jour.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

DEPOT = Path(r"C:\Users\DyBoo\Desktop\-MapDee-")

# PIEGE DOCUMENTE (FAITS.md §10) : `construit/` calcule ses chemins par rapport
# a son propre dossier parent. Sans ces deux variables il cherche la donnee la
# ou elle n'est pas — il echoue, ou il ecrit au mauvais endroit. Ce script est
# tombe dedans a son premier lancement. On les pose AVANT l'import.
os.environ.setdefault("GON_OPENBOOK_SRC",
                      str(DEPOT / "data" / "l4" / "openbook-202512"))
os.environ.setdefault("GON_OPENBOOK_OUT", str(Path(__file__).resolve().parent))
sys.path.insert(0, str(DEPOT / "_recupere"))

from construit.jour import _extract_day, SRC                    # noqa: E402
from construit.openbook import read_statuses, Mapdir            # noqa: E402

ICI = Path(__file__).resolve().parent
TMP = ICI / "c5_work"

# --- PÉRIMÈTRE, §8 du protocole. Le script REFUSE d'en sortir. ---------------
JOURS_AUTORISES = {f"202512{d:02d}" for d in range(8, 17)}

# --- statuts, depuis mapdir/statuses.csv ------------------------------------
OPEN = 1
FILLED = 5
# tout ce qui retire l'ordre du carnet sans exécution complète
ANNULATIONS = {2, 7, 11, 12, 13, 14, 16}
TERMINAUX = ANNULATIONS | {FILLED}


def decode(enc: np.ndarray) -> np.ndarray:
    """Décodage fixe-point du schéma : 3 bits de décimales, 29 bits de valeur."""
    p = np.array([1, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7], dtype=np.float64)
    return (enc & 0x1FFFFFFF) / p[enc >> 29]


def un_jour(day: str, coin: str) -> dict:
    if day not in JOURS_AUTORISES:
        raise SystemExit(f"REFUS : {day} est hors du perimetre declare au §8 "
                         f"du protocole C5 (08-16 decembre). Le perimetre ne "
                         f"s'etend pas apres avoir vu un resultat.")
    t0 = time.time()
    low = coin.lower()
    TMP.mkdir(parents=True, exist_ok=True)
    n = _extract_day(SRC / f"{low}_orders_202512.tar.xz", f"{day}/", TMP,
                     f"{low}_*.data.gz")
    print(f"  {day} {coin} : {n} fichiers horaires en {time.time()-t0:.0f}s",
          flush=True)

    # accumulateurs par portefeuille
    n_open = defaultdict(int)       # ordres posés
    n_fill = defaultdict(int)       # exécutés
    n_canc = defaultdict(int)       # annulés
    n_ask = defaultdict(int)        # posés côté ask
    vies = defaultdict(list)        # durées de vie (ms), sur les terminaux
    tailles = defaultdict(list)     # tailles posées
    px_par_w = defaultdict(lambda: defaultdict(int))   # replacements par palier

    n_rec = 0
    for h in range(24):
        f = TMP / day / f"{low}_{h:02d}.data.gz"
        if not f.exists():
            continue
        st = read_statuses(f)
        n_rec += len(st)
        uid, sid = st["userId"], st["statusId"]

        m = sid == OPEN
        for u, a, s, p in zip(uid[m], st["isAsk"][m],
                              decode(st["origSz"][m]), decode(st["limitPx"][m])):
            n_open[u] += 1
            n_ask[u] += int(a)
            tailles[u].append(float(s))
            px_par_w[u][round(float(p), 4)] += 1

        m = sid == FILLED
        for u in uid[m]:
            n_fill[u] += 1
        m = np.isin(sid, list(ANNULATIONS))
        for u in uid[m]:
            n_canc[u] += 1

        m = np.isin(sid, list(TERMINAUX))
        for u, d in zip(uid[m], st["timestampDiff"][m]):
            vies[u].append(int(d))

        for p in (TMP / day).glob(f"{low}_{h:02d}.data.gz"):
            p.unlink()

    # --- une ligne par portefeuille ------------------------------------------
    out = []
    for u in n_open:
        v = np.array(vies[u]) if vies[u] else np.array([])
        t = np.array(tailles[u]) if tailles[u] else np.array([])
        pal = px_par_w[u]
        nf, nc = n_fill[u], n_canc[u]
        out.append({
            "userId": int(u),
            "n_open": n_open[u], "n_fill": nf, "n_canc": nc,
            # §4 — durée de vie médiane des ordres au repos
            "vie_med_ms": float(np.median(v)) if v.size else None,
            "vie_p90_ms": float(np.percentile(v, 90)) if v.size else None,
            # §4 — taille relative à SA PROPRE norme, pas la taille absolue
            "taille_med": float(np.median(t)) if t.size else None,
            "taille_p99_sur_med": (float(np.percentile(t, 99) / np.median(t))
                                   if t.size and np.median(t) > 0 else None),
            # §4 — asymétrie de côté
            "part_ask": n_ask[u] / n_open[u] if n_open[u] else None,
            # §4 — engagement : posé contre exécuté
            "ratio_fill": nf / n_open[u] if n_open[u] else None,
            # §4 — cadence de replacement au même palier
            "paliers_distincts": len(pal),
            "replacements_par_palier": n_open[u] / len(pal) if pal else None,
            # §3 — MESURÉ ET RAPPORTÉ, INTERDIT COMME DISCRIMINANT
            "taux_annulation": nc / (nf + nc) if (nf + nc) else None,
        })

    return {"jour": day, "coin": coin, "n_records": n_rec,
            "n_portefeuilles": len(out), "t_s": round(time.time() - t0, 1),
            "lignes": out}


def gardefous(lignes: list, champ: str) -> dict:
    """§6 du protocole. Appliqué AVANT tout classement."""
    v = np.array([l[champ] for l in lignes if l[champ] is not None], dtype=float)
    if v.size < 200:
        return {"champ": champ, "verdict": "ECHANTILLON INSUFFISANT",
                "n": int(v.size), "requis": 200}
    # classe majoritaire = plus gros décile-bloc autour de la valeur modale
    q = np.quantile(v, [0, .05, .25, .5, .75, .95, 1])
    part_mode = float(np.mean(np.isclose(v, np.median(v))))
    return {
        "champ": champ, "n": int(v.size),
        "min": q[0], "p05": q[1], "p25": q[2], "med": q[3],
        "p75": q[4], "p95": q[5], "max": q[6],
        "part_a_la_mediane": part_mode,
        "verdict": ("DEGENERE — plus de 60 % a une seule valeur"
                    if part_mode > 0.60 else "utilisable"),
    }


if __name__ == "__main__":
    jours = sys.argv[1].split(",") if len(sys.argv) > 1 else ["20251208"]
    coins = sys.argv[2].split(",") if len(sys.argv) > 2 else ["BTC"]
    # §8 — la garde du perimetre passe AVANT toute lecture, pas au milieu.
    for d in jours:
        if d not in JOURS_AUTORISES:
            raise SystemExit(
                f"REFUS : {d} est hors du perimetre declare au §8 du protocole "
                f"C5 (08-16 decembre). Le perimetre ne s'etend pas apres avoir "
                f"vu un resultat.")
    tout = []
    for d in jours:
        for c in coins:
            r = un_jour(d, c)
            print(f"  -> {r['n_records']:,} enregistrements, "
                  f"{r['n_portefeuilles']:,} portefeuilles, {r['t_s']}s",
                  flush=True)
            (ICI / f"c5_{d}_{c}.json").write_text(
                json.dumps(r, indent=1), encoding="utf-8")
            tout.extend(r["lignes"])

    print("\n=== GARDE-FOUS §6 — avant tout classement ===", flush=True)
    for champ in ("vie_med_ms", "taille_p99_sur_med", "part_ask", "ratio_fill",
                  "replacements_par_palier", "taux_annulation"):
        g = gardefous(tout, champ)
        if "med" in g:
            print(f"  {champ:26} n={g['n']:>6}  p05={g['p05']:>12.4g}  "
                  f"med={g['med']:>12.4g}  p95={g['p95']:>12.4g}   {g['verdict']}")
        else:
            print(f"  {champ:26} {g['verdict']} (n={g['n']})")
    print("\nAUCUN CLASSEMENT N'EST PRODUIT ICI — protocole C5 §6.", flush=True)
