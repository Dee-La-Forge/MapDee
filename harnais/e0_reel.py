# -*- coding: utf-8 -*-
"""Le premier É0 réel — le lanceur. PRÉ-ENREGISTRÉ, commité avant la donnée.

    python -m harnais.e0_reel --dry     # qu'est-ce qui manque ? (aucun calcul)
    python -m harnais.e0_reel           # le banc, pour de vrai

CE QU'IL FAIT, dans l'ordre, et rien d'autre :

1. inventaire du périmètre : pour chaque candidat, ses jours (J3 = 09-11
   décembre, J8 = 09-16, décision des fiches) × {BTC, ETH}, artefact `deep`
   ET manifeste exigés — un candidat dont le périmètre est incomplet ATTEND,
   il ne tourne pas sur un morceau ;
2. préflight complet : arbre propre, protocoles commités, périmètre hors
   réserve, manifestes certifiés ET homogènes (générations mélangées =
   refus), registre déclaré, garde-fous prouvés ;
3. extraction des séries (une passe par jour-symbole, bande ±0,5 %),
   CONCATÉNATION sur le périmètre — l'ordre des jours est l'ordre calendaire,
   BTC puis ETH par jour, déclaré ici ;
4. alignement : les photos où UNE série au moins est NaN (chauffe des lignes
   de base, débuts de jour) sont retirées POUR TOUT LE MONDE — même index
   pour toutes les corrélations, jamais un masquage par paire ;
5. `boucle.tour(series, bloc={T0})` — c'est la boucle commitée qui juge et
   écrit au registre, pas ce script ;
6. rapport imprimé. Le commit du registre reste un acte séparé, relu.

ADR-002 : É0 est une corrélation candidat ↔ candidat sur le périmètre de
fiche — elle ne référence PAS la cible. C3 n'est pas requis ici.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from harnais import boucle                                          # noqa: E402
from harnais.extracteurs import ABSENTS, EXTRACTEURS, charge        # noqa: E402
from harnais.fiches import FICHES, TEMOIN                           # noqa: E402
from harnais.preflight import run as preflight                      # noqa: E402

DEPOT = Path(__file__).resolve().parent.parent
PARTS = DEPOT / "data" / "openbook" / "deep" / "parts"
JOURS = {"J3": [f"202512{d:02d}" for d in range(9, 12)],
         "J8": [f"202512{d:02d}" for d in range(9, 17)]}
COINS = ("BTC", "ETH")
DIST_MAX = 0.005


def inventaire() -> dict:
    """Par périmètre : les jour-symboles présents (artefact + manifeste) et
    les manquants. Aucune lecture de données."""
    etat: dict = {}
    for per, jours in JOURS.items():
        presents, manquants = [], []
        for j in jours:
            for c in COINS:
                p = PARTS / f"deep_{j}_{c}.parquet"
                m = PARTS / f"deep_{j}_{c}.parquet.manifest.json"
                (presents if p.exists() and m.exists() else manquants).append(f"{j} {c}")
        etat[per] = {"presents": presents, "manquants": manquants,
                     "complet": not manquants}
    return etat


def candidats_prets(etat: dict) -> list[str]:
    """Ceux dont l'extracteur existe ET dont le périmètre est complet."""
    prets = []
    for nom, f in FICHES.items():
        if nom in ABSENTS or nom not in EXTRACTEURS:
            continue
        if etat[f["perimetre"]]["complet"]:
            prets.append(nom)
    return prets


def series_du_perimetre(noms: list[str], t0: float) -> dict[str, np.ndarray]:
    """Extrait et concatène, par candidat, sur SON périmètre. Une passe
    `charge()` par jour-symbole, partagée entre tous les candidats du même
    périmètre."""
    par_perimetre: dict[str, list[str]] = {}
    for nom in noms:
        par_perimetre.setdefault(FICHES[nom]["perimetre"], []).append(nom)
    # le témoin s'extrait sur CHAQUE périmètre présent (dette T0-J8 fermée
    # le 06/08) : une clé par périmètre, consommée en bloc_par_perimetre
    temoins = {per: f"_T0_{per}" for per in par_perimetre}
    series: dict[str, list[np.ndarray]] = {
        n: [] for n in noms + list(temoins.values())}
    diag: dict[str, list] = {"part_k0": [], "absdmid": {p: [] for p in par_perimetre}}
    for per, membres in par_perimetre.items():
        for j in JOURS[per]:
            for c in COINS:
                chemin = PARTS / f"deep_{j}_{c}.parquet"
                print(f"[{time.time()-t0:6.0f}s]   extraction {j} {c} "
                      f"({chemin.stat().st_size/1e9:.2f} Go)…", flush=True)
                s = charge(chemin, DIST_MAX)
                for nom in membres:
                    series[nom].append(EXTRACTEURS[nom](s))
                series[temoins[per]].append(EXTRACTEURS[TEMOIN](s))
                # diagnostics de l'audit du 05-06/08, publiés avant tout É0 :
                # la part de masse au palier du mid (exclue des stocks/flux),
                # et |Δmid| pour la corrélation mécanique de chaque série
                tot = s.m_tot[0].sum() + s.m_tot[1].sum() + s.m_k0.sum()
                diag["part_k0"].append(
                    (f"{j} {c}", float(s.m_k0.sum() / tot) if tot else np.nan))
                dm = np.abs(np.diff(s.mid, prepend=np.nan))
                diag["absdmid"][per].append(dm)
    return ({n: np.concatenate(v) for n, v in series.items() if v}, diag)


def aligne(series: dict[str, np.ndarray],
           perimetre_de: dict[str, str]) -> dict[str, np.ndarray]:
    """Retire, PAR PÉRIMÈTRE DÉCLARÉ, les photos où quiconque du périmètre
    est NaN — un seul index commun par périmètre, jamais de masquage par
    paire. (Corrigé à l'audit F1 : la version précédente groupait par
    LONGUEUR de série — une coïncidence de tailles aurait co-masqué deux
    périmètres étrangers.)"""
    from collections import defaultdict
    groupes = defaultdict(list)
    for n in series:
        groupes[perimetre_de[n]].append(n)
    out = {}
    for _, noms in groupes.items():
        bloc = np.vstack([series[n] for n in noms])
        garde = np.isfinite(bloc).all(axis=0)
        for n in noms:
            out[n] = series[n][garde]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    t0 = time.time()

    etat = inventaire()
    prets = candidats_prets(etat)
    print("=== inventaire du périmètre ===")
    for per, e in etat.items():
        print(f"  {per} : {len(e['presents'])}/{len(e['presents'])+len(e['manquants'])} "
              f"jour-symboles — manquants : {e['manquants'] or 'aucun'}")
    print(f"  candidats prêts ({len(prets)}) : {', '.join(prets) or '—'}")
    print(f"  sans extracteur ({len(ABSENTS)}) : attente motivée, voir ABSENTS")
    if a.dry or not prets:
        print("--dry ou rien de prêt : aucun calcul." if a.dry or not prets else "")
        return

    jours_utiles = sorted({j for f in (FICHES[n] for n in prets)
                           for j in JOURS[f["perimetre"]]})
    manifestes, chemins = [], []
    for j in jours_utiles:
        for c in COINS:
            m = PARTS / f"deep_{j}_{c}.parquet.manifest.json"
            manifestes.append(json.loads(m.read_text(encoding="utf-8")))
            chemins.append(m.name)
    pf = preflight(jours_utiles, manifestes=manifestes,
                   chemins_manifestes=chemins)
    print(f"[{time.time()-t0:6.0f}s] préflight : {pf}")

    brut, diag = series_du_perimetre(prets, t0)
    perimetre_de = {n: (FICHES[n]["perimetre"] if n in FICHES
                        else n.split("_T0_")[-1])
                    for n in brut}
    # |Δmid| entre dans l'alignement de son périmètre (même index commun),
    # puis en sort : c'est un diagnostic, jamais un candidat
    for per, morceaux in diag["absdmid"].items():
        if morceaux and any(perimetre_de.get(n) == per for n in brut):
            brut[f"_absdmid_{per}"] = np.concatenate(morceaux)
            perimetre_de[f"_absdmid_{per}"] = per
    series = aligne(brut, perimetre_de)
    dmid = {per: series.pop(f"_absdmid_{per}")
            for per in diag["absdmid"] if f"_absdmid_{per}" in series}

    print(f"[{time.time()-t0:6.0f}s] === diagnostics d'audit, publiés avant É0 ===")
    for nom_js, part in diag["part_k0"]:
        print(f"  masse au palier du mid (exclue des stocks) {nom_js} : {part:.3%}")
    from harnais.stats import spearman as _sp
    for nom, x in sorted(series.items()):
        per = perimetre_de[nom]
        if per in dmid:
            print(f"  ρ(|Δmid|, {nom}) = {_sp(x, dmid[per]):+.3f}"
                  f"   <- entanglement mécanique avec le prix, à garder pour É4")

    n_obs = {n: int(np.isfinite(x).sum()) for n, x in series.items()}
    print(f"[{time.time()-t0:6.0f}s] séries alignées : "
          f"{min(n_obs.values()):,} à {max(n_obs.values()):,} observations")
    bloc_par_perimetre = {per: {TEMOIN: series.pop(cle)}
                          for per, cle in
                          {n.split("_T0_")[-1]: n for n in list(series)
                           if n.startswith("_T0_")}.items()}

    # LIMITE CONNUE, écrite d'avance : le témoin T0 est extrait sur J3 — les
    # candidats J8 (D1) auront besoin d'un T0 sur J8 pour LEUR É2 ; la garde
    # de longueur d'É2 les laissera en attente propre d'ici là (audit F1).
    rapport = boucle.tour(series=series,
                          bloc_par_perimetre=bloc_par_perimetre,
                          hash_protocole=pf["protocole_hash"])
    print(f"[{time.time()-t0:6.0f}s] === LE PREMIER TOUR DE BANC RÉEL ===")
    for nom, (etat_f, raison) in rapport.items():
        print(f"  {nom:38} {etat_f:16} {raison}")


if __name__ == "__main__":
    main()
