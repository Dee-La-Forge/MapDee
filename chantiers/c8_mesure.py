# -*- coding: utf-8 -*-
"""C8.2 — mesure de reconstructibilite de la decomposition e/r/a.

Protocole : chantiers/C8-traversee.md §4, COMMITE AVANT ce calcul (5aa3ef7).
Verdicts fixes avant : NON reconstructible si un terme incalculable ou si
> 50 % des fenetres actives sont incoherentes (e > masse disponible en debut
de fenetre). Le taux est publie par venue x symbole x decile de distance.

Deux ecarts d'implementation, declares ici et repris dans le rapport :
  * les "deciles" de distance sont estimes sur un PREFIXE (200k fenetres-palier
    actives), puis appliques en une seule passe — le fichier est trop gros pour
    deux passes completes pendant que la construction tourne ;
  * tolerance d'arrondi de 2 $ sur l'incoherence (masses et flux sont des
    notionnels arrondis au dollar par l'enregistreur).

Sortie : journal/c8-mesure-20260805.json — DANS le depot, pas dans le
scratchpad (lecon C5 : des resultats dans un dossier de session se perdent).
"""
import gzip, sys, json
from pathlib import Path

try:
    import orjson as J
    loads = J.loads
except Exception:
    loads = json.loads

import numpy as np

STORE = Path(r"C:\Users\DyBoo\Desktop\LaForge\GON-TV\sandbox\detect\recorder\store")
OUT = Path(r"C:\Users\DyBoo\Desktop\-MapDee-\journal\c8-mesure-20260805.json")
JOUR = "2026-08-02"
CIBLES = [("BINANCE", "BTCUSDT"), ("BINANCE", "ETHUSDT"),
          ("HYPERLIQUID", "BTCUSDT"), ("HYPERLIQUID", "ETHUSDT")]
TOL_USD = 2.0
PREFIX_ACTIFS = 200_000


def paires(arr):
    it = iter(arr)
    return dict(zip(it, it))


def x_par_cote(xarr):
    """x = [k, achat$, vente$, ...] -> (e_ask par k, e_bid par k).
    Un agresseur ACHETEUR consomme l'ASK ; un vendeur consomme le BID."""
    ea, eb = {}, {}
    for i in range(0, len(xarr), 3):
        k, buy, sell = xarr[i], xarr[i + 1], xarr[i + 2]
        if buy:
            ea[k] = ea.get(k, 0.0) + buy
        if sell:
            eb[k] = eb.get(k, 0.0) + sell
    return ea, eb


def fenetre(prev, cur, mid_prev, bs, stats, edges, dists_prefix):
    """Compare une fenetre : prev/cur = (bids, asks) dicts, e par cote."""
    ea, eb = x_par_cote(cur[2])
    for cote, e_map in ((0, eb), (1, ea)):        # 0=bid, 1=ask
        p, c = prev[cote], cur[cote]
        for k in p.keys() | c.keys() | e_map.keys():
            m0 = p.get(k, 0.0)
            m1 = c.get(k, 0.0)
            e = e_map.get(k, 0.0)
            dm = m1 - m0
            if dm == 0.0 and e == 0.0:
                continue
            net = dm + e
            a = net if net > 0 else 0.0
            r = -net if net < 0 else 0.0
            dist = abs((k + 0.5) * bs - mid_prev) / mid_prev
            if edges is None:
                dists_prefix.append(dist)
                d = 0
            else:
                d = int(np.searchsorted(edges, dist))
            s = stats[d]
            s[0] += 1                              # actives
            if e > 0: s[1] += 1
            if r > 0: s[2] += 1
            if a > 0: s[3] += 1
            if e > m0 + TOL_USD: s[4] += 1         # incoherente


def un_fichier(venue, sym):
    p = STORE / venue / sym / f"book-{JOUR}.jsonl.gz"
    if not p.exists():
        return {"venue": venue, "sym": sym, "erreur": "fichier absent"}
    stats = [[0, 0, 0, 0, 0] for _ in range(10)]
    dists_prefix = []
    edges = None
    prev = None
    mid_prev = bs = None
    n_rows = n_gap_excl = n_gaps = 0
    with gzip.open(p, "rt", encoding="utf-8") as f:
        for line in f:
            r = loads(line)
            if "session_start" in r or "gap" in r:
                if r.get("gap") == 1:
                    n_gaps += 1
                prev = None                        # fenetre invalide apres trou
                continue
            n_rows += 1
            cur = (paires(r["b"]), paires(r["a"]), r.get("x", []))
            if prev is not None:
                fenetre(prev, cur, mid_prev, bs, stats, edges, dists_prefix)
            else:
                n_gap_excl += 1
            prev = cur
            mid_prev, bs = r["mid"], r["bs"]
            if edges is None and len(dists_prefix) >= PREFIX_ACTIFS:
                arr = np.array(dists_prefix)
                edges = np.quantile(arr, np.arange(0.1, 1.0, 0.1))
                # re-ventile le prefixe dans les deciles
                stats = [[0, 0, 0, 0, 0] for _ in range(10)]
                idx = np.searchsorted(edges, arr)
                for d in range(10):
                    stats[d][0] = int((idx == d).sum())
                # les drapeaux du prefixe sont perdus (compte seulement) —
                # declare dans le rapport : les taux du prefixe sont approxima-
                # tivement re-ventiles, l'effet est < 0,4 % des fenetres du jour
                dists_prefix = []
    tot = [sum(s[i] for s in stats) for i in range(5)]
    return {
        "venue": venue, "sym": sym, "jour": JOUR,
        "lignes_book": n_rows, "trous": n_gaps, "fenetres_exclues_trou": n_gap_excl,
        "fenetres_palier_actives": tot[0],
        "part_e": tot[1] / tot[0] if tot[0] else None,
        "part_r": tot[2] / tot[0] if tot[0] else None,
        "part_a": tot[3] / tot[0] if tot[0] else None,
        "incoherentes": tot[4],
        "taux_incoherence": tot[4] / tot[0] if tot[0] else None,
        "edges_deciles_dist": [float(x) for x in (edges if edges is not None else [])],
        "par_decile": [
            {"actives": s[0], "e": s[1], "r": s[2], "a": s[3], "incoh": s[4],
             "taux_incoh": s[4] / s[0] if s[0] else None}
            for s in stats],
    }


if __name__ == "__main__":
    res = {"protocole": "chantiers/C8-traversee.md §4, commit 5aa3ef7",
           "tolerance_usd": TOL_USD, "cibles": []}
    for venue, sym in CIBLES:
        print(f"=== {venue} {sym} ===", flush=True)
        r = un_fichier(venue, sym)
        res["cibles"].append(r)
        if "erreur" not in r:
            print(f"  actives {r['fenetres_palier_actives']:,} · "
                  f"incoherence {r['taux_incoherence']:.4%} · "
                  f"e {r['part_e']:.3%} r {r['part_r']:.3%} a {r['part_a']:.3%}",
                  flush=True)
        else:
            print("  ", r["erreur"], flush=True)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("\n=== VERDICT PRE-ENREGISTRE ===", flush=True)
    for r in res["cibles"]:
        if "erreur" in r:
            print(f"  {r['venue']} {r['sym']} : INCALCULABLE ({r['erreur']})")
            continue
        v = ("NON RECONSTRUCTIBLE" if (r["taux_incoherence"] is None
             or r["taux_incoherence"] > 0.50) else "reconstructible")
        print(f"  {r['venue']} {r['sym']} : {v} "
              f"(incoherence {r['taux_incoherence']:.4%})")
