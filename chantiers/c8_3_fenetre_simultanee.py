# -*- coding: utf-8 -*-
"""C8.3 — la fenêtre simultanée. PROTOCOLE PRÉ-ENREGISTRÉ, commité avant.

`chantiers/C8-traversee.md` §5 : « le même estimateur sur les jours où les
deux places sont captées ensemble ». C8.2 a rendu le verdict de
reconstructibilité sur UN jour (2026-08-02) ; C8.3 étend la mesure aux jours
de capture simultanée COMPLETS et publie la stabilité inter-jours de la
décomposition e/r/a des deux côtés. **Aucun verdict nouveau** : la
comparaison s'ajoute au dossier de traversée, elle ne juge pas (`C8` §6 —
pas de seuil pré-enregistré pour la comparaison, donc elle ne peut rien
trancher).

PÉRIMÈTRE, déclaré avant le calcul — les cinq jours ≥ 99,8 % du diagnostic
C8.4 (`journal/c8-4-diagnostic-enregistreur-20260805.md` §2), le jour de
C8.2 étant déjà mesuré :

    2026-07-29 · 2026-07-30 · 2026-07-31 · 2026-08-01 · 2026-08-03

× {BINANCE, HYPERLIQUID} × {BTCUSDT, ETHUSDT} = 20 cibles. Estimateur,
tolérance (2 $) et exclusion des trous : STRICTEMENT ceux de
`chantiers/c8_mesure.py` (commit `0d574b6`), importés — pas recopiés.

CE QUI EST PUBLIÉ : par cible, le taux d'incohérence et les parts e/r/a ;
par (venue, symbole), la fourchette inter-jours — c'est elle qui dit si la
mesure du 02/08 était un jour ordinaire ou une exception.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import c8_mesure as m                                               # noqa: E402

JOURS = ("2026-07-29", "2026-07-30", "2026-07-31", "2026-08-01", "2026-08-03")
CIBLES = [("BINANCE", "BTCUSDT"), ("BINANCE", "ETHUSDT"),
          ("HYPERLIQUID", "BTCUSDT"), ("HYPERLIQUID", "ETHUSDT")]
OUT = Path(__file__).resolve().parent.parent / "journal" / "c8-3-mesure-20260805.json"


def main() -> None:
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(
        ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)  # le recorder d'abord
    t0 = time.time()
    res = {"protocole": "chantiers/c8_3_fenetre_simultanee.py — estimateur de "
                        "c8_mesure.py (0d574b6), 5 jours pleins",
           "tolerance_usd": m.TOL_USD, "jours": list(JOURS), "cibles": []}
    for jour in JOURS:
        m.JOUR = jour                      # le module mesure « son » jour
        for venue, sym in CIBLES:
            r = m.un_fichier(venue, sym)
            res["cibles"].append(r)
            if "erreur" in r:
                print(f"[{time.time()-t0:6.0f}s] {jour} {venue} {sym} : "
                      f"{r['erreur']}", flush=True)
            else:
                print(f"[{time.time()-t0:6.0f}s] {jour} {venue} {sym} : "
                      f"incoh {r['taux_incoherence']:.4%} · e {r['part_e']:.2%}",
                      flush=True)
    # fourchettes inter-jours, par (venue, symbole)
    res["fourchettes"] = {}
    for venue, sym in CIBLES:
        vals = [c["taux_incoherence"] for c in res["cibles"]
                if c.get("venue") == venue and c.get("sym") == sym
                and "taux_incoherence" in c]
        if vals:
            res["fourchettes"][f"{venue} {sym}"] = {
                "n_jours": len(vals), "min": min(vals), "max": max(vals)}
    res["duree_totale_s"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"[{time.time()-t0:6.0f}s] terminé — {OUT}", flush=True)


if __name__ == "__main__":
    main()
