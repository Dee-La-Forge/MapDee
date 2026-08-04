"""Fabrique une PLAGE de jours, séquentiellement, sans surveillance.

Écrit le 04/08/2026. Toute l'orchestration de la première grande fabrication
vivait dans des scripts jetables hors du dépôt : la garde d'espace disque, le
nettoyage de `work/`, l'arrêt au premier échec, le refus de compter un jour
sorti sans `deep`. Un dépôt qui sait fabriquer un jour mais pas douze oblige à
réinventer tout ça, et c'est là que les périmètres deviennent flous.

    python construit/lot.py --coin BTC --jours 20251213..20251216 20251224..20251231
    python construit/lot.py --coin BTC --jours 20251201..20251207 --phase deep

## Ce que ce module refuse de faire

* **Démarrer si un seul jour demandé est gelé** pour la phase demandée. Le
  contrôle est fait AVANT la première seconde de calcul : découvrir au onzième
  jour qu'il en manquait un est le genre de perte qu'on ne rattrape pas.
* **Continuer après un échec.** Douze jours dont on ne sait plus lesquels sont
  bons ne valent pas mieux que zéro.
* **Compter un jour qui s'est terminé sans écrire son `deep`.** Le compte final
  porte sur ce qui existe sur le disque, pas sur ce que la boucle a tenté.

## Séquentiel, et pourquoi

Un rejeu tient le carnet ENTIER en mémoire — mesuré 5,6 Gio de RSS sur une
journée ETH. Deux en parallèle ne vont pas deux fois plus vite, ils se
disputent le disque et la RAM. Compter ~21 min par jour et par symbole.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ICI))

from construit.jour import (SRC, _cible, _parquet_complet,       # noqa: E402
                            _refuse_si_gele, build)

MIN_LIBRE_GIO = 25.0
# Pourquoi 25 et non 5 : l'extraction d'un jour (statuts + diffs, plus ceux de
# la veille pour la chauffe) pese ~4 Gio, et un disque plein en cours d'ecriture
# laisse un parquet tronque que la passe suivante prendrait pour un travail
# fait. On s'arrete avec de la marge, jamais au bord.


def _libre_gio() -> float:
    return shutil.disk_usage(ICI).free / 2**30


def expanse(motifs: list[str]) -> list[str]:
    """`20251213..20251216` -> les quatre jours. Un jour seul reste lui-meme."""
    out: list[str] = []
    for m in motifs:
        if ".." not in m:
            out.append(m)
            continue
        a, b = m.split("..", 1)
        d = datetime.strptime(a, "%Y%m%d")
        fin = datetime.strptime(b, "%Y%m%d")
        if fin < d:
            raise SystemExit(f"plage inversee : {m}")
        while d <= fin:
            out.append(d.strftime("%Y%m%d"))
            d += timedelta(days=1)
    vus, uniq = set(), []
    for j in out:                       # ordre conserve, doublons ecartes
        if j not in vus:
            vus.add(j); uniq.append(j)
    return uniq


def lot(jours: list[str], coin: str, phase: str = "all",
        min_libre: float = MIN_LIBRE_GIO, nettoie: bool = True) -> dict:
    ecrit = "deep" if phase == "deep" else "tout"

    # ---- controle AVANT tout calcul -------------------------------------
    bloques = []
    for j in jours:
        try:
            _refuse_si_gele(j, ecrit)
        except SystemExit as e:
            bloques.append((j, str(e).splitlines()[0]))
    if bloques:
        print("REFUS : des jours demandes sont geles pour cette phase.\n")
        for j, msg in bloques:
            print(f"  {j} : {msg}")
        raise SystemExit(1)

    work = SRC / "work"
    # On ne supprimera QUE ce que ce lot a extrait. Les repertoires deja
    # presents appartiennent a quelqu'un d'autre.
    preexistants = {p.name for p in work.iterdir()} if work.is_dir() else set()

    faits, sautes, resultats = [], [], []
    prec = None
    t0 = time.time()
    print(f"=== lot : {len(jours)} jours, {coin}, phase={phase} ===", flush=True)

    for i, j in enumerate(jours, 1):
        cible = _cible("deep", j, coin)
        if _parquet_complet(cible):
            print(f"[{i}/{len(jours)}] {j} : deja fait, saute.", flush=True)
            sautes.append(j)
            prec = j
            continue
        libre = _libre_gio()
        if libre < min_libre:
            print(f"ARRET : {libre:.1f} Gio libres, {min_libre:.0f} requis. "
                  f"{len(faits)} jours faits.", flush=True)
            break
        print(f"[{i}/{len(jours)}] === {coin} {j} "
              f"({libre:.0f} Gio libres) ===", flush=True)
        s = build(j, coin, phase)
        resultats.append(s)
        if _parquet_complet(cible):
            faits.append(j)
            print(f"[{i}/{len(jours)}] {j} OK — {len(faits)} fabriques", flush=True)
        else:
            print(f"ARRET : {j} s'est termine SANS deep complet. "
                  f"{len(faits)} jours faits.", flush=True)
            break
        # la veille a servi a la chauffe de `j` ; le jour suivant utilisera `j`
        if nettoie and prec and prec not in preexistants:
            d = work / prec
            if d.is_dir():
                shutil.rmtree(d, ignore_errors=True)
                print(f"        nettoye work/{prec}", flush=True)
        prec = j

    return {"demandes": len(jours), "fabriques": len(faits),
            "deja_faits": len(sautes), "jours_fabriques": faits,
            "minutes": round((time.time() - t0) / 60, 1),
            "detail": resultats}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--coin", default="BTC")
    ap.add_argument("--jours", nargs="+", required=True,
                    help="jours ou plages, ex. 20251213..20251216 20251224")
    ap.add_argument("--phase", default="all",
                    choices=["all", "orders", "book", "deep"])
    ap.add_argument("--min-libre-gio", type=float, default=MIN_LIBRE_GIO)
    ap.add_argument("--sans-nettoyage", action="store_true",
                    help="garder les extractions de work/ (debogage)")
    a = ap.parse_args()
    r = lot(expanse(a.jours), a.coin, a.phase, a.min_libre_gio,
            not a.sans_nettoyage)
    print(f"\n=== {r['fabriques']} fabriques, {r['deja_faits']} deja faits, "
          f"sur {r['demandes']} demandes, en {r['minutes']} min ===")
    if r["jours_fabriques"]:
        print("  " + " ".join(r["jours_fabriques"]))
    if r["fabriques"] + r["deja_faits"] < r["demandes"]:
        raise SystemExit(1)          # sortie non nulle : un lot partiel se voit
