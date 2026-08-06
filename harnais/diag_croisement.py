# -*- coding: utf-8 -*-
"""Diagnostic PRÉ-ENREGISTRÉ du croisement 12→15 — la piste de récupération.

    python -m harnais.diag_croisement --day 20251215 --coin ETH

LA QUESTION, posée avant de regarder : le carnet croisé est-il épinglé par
un PETIT ensemble d'ordres fantômes (des `remove` perdus à la capture —
récupérable par une règle d'éviction, qui passerait par ADR), ou par un
flux durablement incohérent (défaut amont de la bourse — irrécupérable) ?

LE CRITÈRE, écrit d'avance :
* RÉCUPÉRABLE : l'ensemble des oids participant au chevauchement est petit
  (≤ 100 sur la journée) et STATIQUE (Jaccard moyen entre échantillons
  consécutifs ≥ 0,8) — les mêmes fantômes épinglent pendant des heures ;
* IRRÉCUPÉRABLE : l'ensemble churne (union grande, Jaccard bas) — de
  nouveaux ordres créent le chevauchement en continu, le flux lui-même est
  incohérent ;
* entre les deux : publié tel quel, pas d'interprétation forcée.

CE QUE LE REJEU FAIT : le carnet par oid comme `construit/jour.py` (new /
remove / update-à-zéro-évince), SANS jointure de temps (l'heure du fichier
suffit pour « statique pendant des heures ») ; toutes les 20 000 lignes du
symbole, si le carnet est croisé, un échantillon : heure, profondeur du
chevauchement, oids des prix chevauchants (bid ≥ ask0, ask ≤ bid0).
Tout est publié : journal/diag-croisement-<jour>-<coin>.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from sortedcontainers import SortedList

ICI = Path(__file__).resolve().parent.parent
# `construit` vit sous `_recupere/` (dépendance d'exécution transitoire,
# `00` §7 — C10 la promeut) : c'est là qu'on l'importe, pas à la racine.
sys.path.insert(0, str(ICI / "_recupere"))

from construit.openbook import read_diffs                        # noqa: E402

SRC = Path("C:/Users/DyBoo/Desktop/-MapDee-/data/l4/openbook-202512")
DEPOT = ICI
PAS_ECHANTILLON = 20_000
MAX_PRIX_LOGGES = 50


def rejoue(day: str, coin: str) -> dict:
    t0 = time.time()
    book: dict[int, tuple[bool, float]] = {}          # oid -> (ask, px)
    oids_bid: dict[float, set] = {}
    oids_ask: dict[float, set] = {}
    bid_px, ask_px = SortedList(), SortedList()

    def _pose(o: int, ask: bool, px: float) -> None:
        d = oids_ask if ask else oids_bid
        s = d.get(px)
        if s is None:
            d[px] = {o}
            (ask_px if ask else bid_px).add(px)
        else:
            s.add(o)

    def _retire(o: int, ask: bool, px: float) -> None:
        d = oids_ask if ask else oids_bid
        s = d.get(px)
        if s is None:
            return
        s.discard(o)
        if not s:
            del d[px]
            (ask_px if ask else bid_px).remove(px)

    echantillons: list[dict] = []
    union: set[int] = set()
    n_ev = n_croise_ech = 0
    premier_croisement: str | None = None

    # les diffs du jour, ré-extraits si le lot a nettoyé work/ (le tar est
    # libre : plus aucun run de construction en cours)
    if not (SRC / "work" / day / "ex0.gz").exists():
        from construit.jour import _extract_day
        n = _extract_day(SRC / "book_diffs_202512.tar", f"{day}/",
                         SRC / "work", "ex*.gz")
        print(f"  extraction : {n} fichiers de diffs", flush=True)
    for h in range(24):
        f = SRC / "work" / day / f"ex{h}.gz"
        if not f.exists():
            print(f"  h{h:02d} : fichier absent, saute", flush=True)
            continue
        oid, _usr, side, px, kind, sz = read_diffs(f, coin)
        for i in range(len(oid)):
            o = int(oid[i])
            k = kind[i]
            if k == "new":
                a, p_ = side[i] == "A", float(px[i])
                anc = book.get(o)
                if anc is not None:
                    _retire(o, anc[0], anc[1])
                book[o] = (a, p_)
                _pose(o, a, p_)
            elif k == "remove":
                anc = book.pop(o, None)
                if anc is not None:
                    _retire(o, anc[0], anc[1])
            else:                                     # update
                if float(sz[i]) <= 1e-12:
                    anc = book.pop(o, None)
                    if anc is not None:
                        _retire(o, anc[0], anc[1])
            n_ev += 1
            if n_ev % PAS_ECHANTILLON:
                continue
            if not bid_px or not ask_px:
                continue
            b0, a0 = bid_px[-1], ask_px[0]
            if b0 < a0:
                continue
            n_croise_ech += 1
            if premier_croisement is None:
                premier_croisement = f"h{h:02d} (ligne {n_ev:,})"
            ob = [o2 for p_ in list(bid_px.irange(a0, None))[-MAX_PRIX_LOGGES:]
                  for o2 in oids_bid[p_]]
            oa = [o2 for p_ in list(ask_px.irange(None, b0))[:MAX_PRIX_LOGGES]
                  for o2 in oids_ask[p_]]
            ens = set(ob) | set(oa)
            union |= ens
            echantillons.append({
                "heure": h, "ligne": n_ev,
                "b0": b0, "a0": a0,
                "prix_bid_chevauchants": len(list(bid_px.irange(a0, None))),
                "prix_ask_chevauchants": len(list(ask_px.irange(None, b0))),
                "oids": sorted(ens)[:200]})
        print(f"  h{h:02d} : {len(oid):,} lignes {coin} · carnet {len(book):,} "
              f"ordres · échantillons croisés {n_croise_ech}", flush=True)

    jacc = []
    for e1, e2 in zip(echantillons, echantillons[1:]):
        s1, s2 = set(e1["oids"]), set(e2["oids"])
        if s1 | s2:
            jacc.append(len(s1 & s2) / len(s1 | s2))
    jaccard_moyen = round(sum(jacc) / len(jacc), 4) if jacc else None

    verdict = "AUCUN CROISEMENT ÉCHANTILLONNÉ"
    if echantillons:
        if len(union) <= 100 and (jaccard_moyen or 0) >= 0.8:
            verdict = ("RÉCUPÉRABLE (critère pré-enregistré) : ensemble petit "
                       "et statique — une éviction par ADR est plausible")
        elif len(union) > 1000 or (jaccard_moyen or 0) < 0.3:
            verdict = ("IRRÉCUPÉRABLE (critère pré-enregistré) : le "
                       "chevauchement churne — flux incohérent, défaut amont")
        else:
            verdict = "ENTRE LES DEUX — publié tel quel, à lire en table"

    out = {"jour": day, "coin": coin, "n_lignes": n_ev,
           "premier_croisement": premier_croisement,
           "n_echantillons_croises": n_croise_ech,
           "oids_union": len(union), "jaccard_moyen": jaccard_moyen,
           "verdict": verdict, "duree_s": round(time.time() - t0, 1),
           "echantillons": echantillons[:500]}
    p = DEPOT / "journal" / f"diag-croisement-{day}-{coin}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1),
                 encoding="utf-8")
    print(f"\n=== VERDICT {day} {coin} : {verdict}")
    print(f"    union oids = {len(union):,} · Jaccard moyen = {jaccard_moyen} "
          f"· premier croisement : {premier_croisement}")
    print(f"    écrit : {p.relative_to(DEPOT)}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", required=True)
    ap.add_argument("--coin", default="ETH")
    a = ap.parse_args()
    print(f"=== diag croisement {a.day} {a.coin} ===", flush=True)
    rejoue(a.day, a.coin)
