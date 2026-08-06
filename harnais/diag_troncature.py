# -*- coding: utf-8 -*-
"""Diagnostic PRÉ-ENREGISTRÉ (commité avant toute exécution, 06/08/2026) :
que fait une amputation type « incident 12→15 » à la statistique du jour ?

    python -m harnais.diag_troncature

LA QUESTION, posée avant de regarder : le 20251214 est plein et sain des
deux côtés (104 292 / 104 234 photos, 0 carnet croisé). On le tronque à
l'index EXACT des jours dégradés du 15 (BTC : 53 688 photos, ETH :
56 216) et on compare, pour chaque grandeur extraite, la statistique
journalière tronquée à la complète. Ça mesure, sur donnée réelle, le
déplacement qu'introduit une amputation de ce type — la démarche qui a
produit le plancher k/n : une inquiétude qualitative transformée en
nombre AVANT de devenir une garde (valeur du plancher : ADR-007, Meddy).

CE QUI EST DÉCLARÉ D'AVANCE (justification corrigée avant exécution,
audit du 06/08 — le script n'avait jamais tourné) :
* statistique du jour = MOYENNE de la série. C'est un PROXY, pas l'unité
  d'É4 : É4 agrège des COEFFICIENTS journaliers (corrélation de rang
  partielle candidat ↔ cible, un par jour) — non calculables tant que C3
  n'est pas gelé. Une amputation peut laisser la moyenne intacte et
  déplacer fortement la corrélation si la relation vit dans les heures
  perdues — précisément les heures actives : CE DIAGNOSTIC NE LE MESURE
  PAS. Il sera REFAIT sur le coefficient quand C3 sera gelé ;
* l'écart est publié en unités de l'écart-type complet du jour :
  delta = (moy_tronquée − moy_complète) / std_complète ;
* la troncature par index est équivalente à un jour amputé parce que les
  extracteurs sont CAUSAUX — propriété VÉRIFIÉE, pas affirmée : garde
  permanente (`tests/test_causalite.py`, `00` §3 zéro lookahead) ET
  contrôle en exécution ici même — un extracteur qui échouerait au
  contrôle est REFUSÉ du diagnostic, pas moyenné quand même ;
* tout est publié, y compris les écarts minuscules — pas de tri après
  coup. Sortie : impression + journal/diag-troncature-<date>.json.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from harnais.extracteurs import (EXTRACTEURS, charge,        # noqa: E402
                                 tronque_series)

DEPOT = Path(__file__).resolve().parent.parent
PARTS = DEPOT / "data" / "openbook" / "deep" / "parts"
DIST_MAX = 0.005
JOUR_PLEIN = "20251214"
#: L'index de coupe = le compte de photos RÉEL du jour dégradé homologue
#: (20251215), lu dans les manifestes le 06/08 — déclaré ici, pas ajusté.
COUPES = {"BTC": 53_688, "ETH": 56_216}


def main() -> None:
    t0 = time.time()
    sortie = {"jour_plein": JOUR_PLEIN, "coupes": COUPES, "grandeurs": {}}
    for coin, coupe in COUPES.items():
        chemin = PARTS / f"deep_{JOUR_PLEIN}_{coin}.parquet"
        print(f"[{time.time()-t0:6.0f}s] charge {JOUR_PLEIN} {coin}…", flush=True)
        s = charge(chemin, DIST_MAX)
        st = tronque_series(s, coupe)
        for nom, ext in EXTRACTEURS.items():
            x = ext(s)
            # contrôle de causalité EN EXÉCUTION : si l'extracteur regarde
            # le futur, delta ne mesure plus une amputation mais aussi la
            # déformation des valeurs conservées — REFUS, pas un chiffre
            xc = ext(st)
            if len(xc) != coupe or not np.allclose(xc, x[:coupe],
                                                   equal_nan=True):
                sortie["grandeurs"].setdefault(nom, {})[coin] = {
                    "REFUS": "extracteur NON CAUSAL — lookahead (`00` §3), "
                             "delta invalide, à corriger avant tout usage"}
                print(f"  {coin} {nom:38} REFUS : non causal", flush=True)
                continue
            fini = np.isfinite(x)
            xf = x[fini]
            xt = x[:coupe][fini[:coupe]]
            m_c, s_c = float(np.mean(xf)), float(np.std(xf))
            m_t = float(np.mean(xt))
            delta = (m_t - m_c) / s_c if s_c > 0 else float("nan")
            sortie["grandeurs"].setdefault(nom, {})[coin] = {
                "moy_complete": m_c, "moy_tronquee": m_t,
                "std_complete": s_c, "delta_std": round(delta, 4),
                "n_complet": int(fini.sum()), "n_tronque": int(fini[:coupe].sum())}
            print(f"  {coin} {nom:38} delta = {delta:+.3f} σ", flush=True)
    horodatage = time.strftime("%Y%m%d-%H%M%S")
    p = DEPOT / "journal" / f"diag-troncature-{horodatage}.json"
    p.write_text(json.dumps(sortie, ensure_ascii=False, indent=1),
                 encoding="utf-8")
    print(f"[{time.time()-t0:6.0f}s] écrit : {p.relative_to(DEPOT)}")


if __name__ == "__main__":
    main()
