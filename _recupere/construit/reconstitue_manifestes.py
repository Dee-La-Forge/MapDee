"""Manifeste RECONSTITUE pour les artefacts anterieurs a l'empreinte.

## Ce que ce script fait, et surtout ce qu'il ne fait PAS

Les parquets deja sur disque ont ete construits avant l'existence de
`empreinte.py`. On ne peut pas savoir avec certitude sous quel commit ni sous
quelles versions — cette information n'a jamais ete ecrite, et l'inventer
serait pire que de ne rien avoir.

Ce script fait donc UNE chose : il fige leur etat actuel (hash du contenu) pour
que toute alteration ULTERIEURE soit detectable. Il marque explicitement les
manifestes ainsi produits :

    "reconstitue": true
    "provenance_certifiee": false

Un consommateur qui lit `provenance_certifiee: false` sait qu'il tient une
photo, pas un acte de naissance.

Les parametres inscrits sont ceux qui etaient EN DUR dans le code au moment ou
ces fichiers ont ete produits — DEEP_MS = 10 000, DEEP_BAND = 0,10 — soit les
defauts actuels. C'est verifiable sur la donnee elle-meme : un `deep` a
+/-10 % porte des paliers jusqu'a 10 % du mid, un `deep` a +/-2 % non. Le
script le VERIFIE au lieu de le supposer, et refuse d'ecrire si la donnee
contredit le parametre suppose.

Usage :
    python construit/reconstitue_manifestes.py            # verifie, n'ecrit pas
    python construit/reconstitue_manifestes.py --ecris
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

ICI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ICI))

from construit import empreinte                              # noqa: E402
from construit.jour import OUT                               # noqa: E402

SUPPOSE = {"DEEP_MS": 10000, "DEEP_BAND": 0.10, "WARMUP_H": 8,
           "BIN_REL": 2.5e-05, "SNAP_MS": 1000, "SNAP_MIN_MS": 250,
           "LEVELS": 20, "DEEP_LOT": 400}


def portee_deep(p: Path, groupes: int = 2) -> float:
    """Portee relative maximale observee dans un `deep` — sur quelques groupes.

    C'est le temoin qui distingue un artefact +/-10 % d'un artefact +/-2 %.
    """
    f = pq.ParquetFile(p)
    n = min(groupes, f.metadata.num_row_groups)
    t = f.read_row_groups(list(range(n)), columns=["mid", "bs", "k"])
    k = t["k"].to_numpy(); mid = t["mid"].to_numpy(); bs = t["bs"].to_numpy()
    return float(np.abs(k * bs - mid).max() / mid.max())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ecris", action="store_true",
                    help="ecrit les manifestes (sinon : verification seule)")
    a = ap.parse_args()

    n_ok = n_ecrit = n_deja = n_refus = 0
    for kind in ("deep", "hl_book", "hl_orders", "hl_fills"):
        d = OUT / kind / "parts"
        if not d.exists():
            continue
        for p in sorted(d.glob("*.parquet")):
            if empreinte.lis(p) is not None:
                n_deja += 1
                continue
            jour, coin = p.stem.split("_")[-2], p.stem.split("_")[-1]

            # CONTROLE : la donnee contredit-elle le parametre suppose ?
            note = None
            if kind == "deep":
                try:
                    pr = portee_deep(p)
                except Exception as e:                        # noqa: BLE001
                    print(f"  ILLISIBLE {p.name} : {e}")
                    n_refus += 1
                    continue
                # +/-10 % attendu : on doit voir des paliers nettement au-dela
                # de 2 %. Sinon le fichier n'a pas ete produit sous SUPPOSE.
                if pr < 0.05:
                    print(f"  REFUS {p.name} : portee max {pr:.3%} — "
                          f"incompatible avec DEEP_BAND=0,10 suppose")
                    n_refus += 1
                    continue
                note = f"portee max observee {pr:.2%} (coherent avec DEEP_BAND=0,10)"

            n_ok += 1
            if not a.ecris:
                continue
            m = empreinte.ecris(p, kind=kind, jour=jour, coin=coin,
                                phase="INCONNUE", parametres=SUPPOSE,
                                stats={"note": note} if note else {})
            if m:
                # marquage : ce manifeste est une PHOTO, pas un acte de naissance
                man = json.loads(m.read_text(encoding="utf-8"))
                man["reconstitue"] = True
                man["provenance_certifiee"] = False
                man["avertissement"] = (
                    "Manifeste ecrit APRES coup, le 04/08/2026. Le commit, les "
                    "versions et la phase inscrits sont ceux de la MACHINE AU "
                    "MOMENT DE LA RECONSTITUTION, pas ceux de la construction. "
                    "Les parametres sont SUPPOSES (defauts du code) et "
                    "controles contre la donnee quand c'est possible. Ce "
                    "manifeste sert a detecter une alteration future, il ne "
                    "certifie pas l'origine.")
                man["code"] = {"commit": None, "court": None, "sale": None,
                               "note": "inconnu — anterieur a l'empreinte"}
                man["environnement"] = {
                    "note": "inconnu — anterieur a l'empreinte"}
                m.write_text(json.dumps(man, indent=2, ensure_ascii=False),
                             encoding="utf-8")
                n_ecrit += 1

    print(f"\neligibles {n_ok} · deja manifestes {n_deja} · "
          f"refuses {n_refus} · ecrits {n_ecrit}")
    if not a.ecris:
        print("(verification seule — relancer avec --ecris)")
    return 1 if n_refus else 0


if __name__ == "__main__":
    sys.exit(main())
