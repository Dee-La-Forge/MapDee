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
from harnais.extracteurs import (ABSENTS, EXTRACTEURS, charge,      # noqa: E402
                                 tronque_series)
from harnais.fiches import FICHES, TEMOIN                           # noqa: E402
from harnais.preflight import run as preflight                      # noqa: E402

DEPOT = Path(__file__).resolve().parent.parent
PARTS = DEPOT / "data" / "openbook" / "deep" / "parts"
JOURS = {"J3": [f"202512{d:02d}" for d in range(9, 12)],
         "J8": [f"202512{d:02d}" for d in range(9, 17)]}
COINS = ("BTC", "ETH")
#: Trous d'archive DOCUMENTÉS (journal/2026-08-06_eth-20251213-*.md et
#: journal/2026-08-06_couverture-j8-*.md) : la journée du 13 est croisée
#: des DEUX côtés — ETH 0 photo (refusée par l'instrument), BTC 172 photos
#: (≈0,14 %, passée par la garde binaire : un trou de facto). J8 est
#: amendé à 14 jour-symboles — impossibilité matérielle constatée avant
#: tout calcul, jamais un périmètre ajusté après résultat. Les jours
#: DÉGRADÉS (12 et 15, ≈44-75 %) restent : dégradation documentée ≠ trou.
TROUS_ARCHIVE = {("20251213", "ETH"), ("20251213", "BTC")}
DIST_MAX = 0.005


def coupes_causalite(jour: str, coin: str, n: int) -> list[int]:
    """Quatre coupes de la garde de causalité, TIRÉES par jour-symbole à
    graine fixe (crc32 — `hash()` Python est salé par processus, il ne se
    pré-enregistre pas). Reproductibles : mêmes (jour, symbole, n), mêmes
    coupes, pour toujours.

    Pourquoi tirées et non fixes : des fractions fixes sondent 4 positions
    relatives, quatorze fois — tirées par jour-symbole, ~56 positions
    distinctes au même coût, et une branche rare a un ordre de grandeur de
    plus de chances de tomber sur un bord.

    LIMITE DE MÉTHODE, écrite : la coupe k attrape toute dépendance d'un
    indice < k à une donnée ≥ k — la garde est donc COMPLÈTE pour un
    lookahead de LONGUE portée (tout indice avant la coupe diffère) et
    pour un lookahead court PERMANENT (chaque bord le voit). Pour un
    lookahead court CONDITIONNEL à un motif rare, elle ne contrôle que le
    VOISINAGE des coupes : le motif doit tomber sur un bord. La
    randomisation élargit le filet — elle ne le ferme pas. Le test
    `test_causalite.py` rend cette limite visible plutôt que théorique."""
    import zlib
    graine = zlib.crc32(f"{jour}:{coin}".encode())
    rng = np.random.default_rng(graine)
    fracs = rng.uniform(0.05, 0.98, size=4)
    return sorted({max(1, min(n - 1, int(n * f))) for f in fracs})


def _non_causal(nom: str, x_complet: np.ndarray,
                coupes: list[tuple[int, "object"]]) -> bool:
    """La garde de causalité SUR LE RÉEL (`00` §3, préalable du tir) :
    à chaque coupe k, ext(jour tronqué) doit égaler ext(jour)[:k]. Le test
    synthétique ne suffit pas — le générateur est pauvre par construction
    (D3) : une branche non causale conditionnée à un motif réel (carnet
    croisé, palier au mid, trou de photos) n'y est jamais exercée. Ici,
    chaque extracteur est contrôlé sur CHAQUE jour-symbole qu'il va juger."""
    for k, s_tronque in coupes:
        xc = EXTRACTEURS[nom](s_tronque)
        if len(xc) != k or not np.allclose(xc, x_complet[:k], equal_nan=True):
            return True
    return False


def inventaire() -> dict:
    """Par périmètre : les jour-symboles présents (artefact + manifeste) et
    les manquants. Aucune lecture de données."""
    etat: dict = {}
    for per, jours in JOURS.items():
        presents, manquants = [], []
        for j in jours:
            for c in COINS:
                if (j, c) in TROUS_ARCHIVE:
                    continue          # trou documenté : ni présent ni manquant
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


def series_du_perimetre(noms: list[str], t0: float,
                        retenus: list[str] = ()) -> dict[str, np.ndarray]:
    """Extrait et concatène, par candidat, sur SON périmètre. Une passe
    `charge()` par jour-symbole, partagée entre tous les candidats du même
    périmètre."""
    par_perimetre: dict[str, list[str]] = {}
    for nom in noms:
        par_perimetre.setdefault(FICHES[nom]["perimetre"], []).append(nom)
    # le témoin s'extrait sur CHAQUE périmètre présent (dette T0-J8 fermée
    # le 06/08) : une clé par périmètre, consommée en bloc_par_perimetre.
    # Les candidats RETENUS au registre s'extraient de même : `05` —
    # « retenue » = « entre dans le bloc de référence d'É2 pour les
    # suivantes » — c'est ici que la grandeur retenue existe sur le
    # périmètre de celles qu'elle contrôlera (5e arête, 06/08).
    temoins = {per: f"_T0_{per}" for per in par_perimetre}
    cles_bloc = {(per, nom): f"_BLOC_{per}::{nom}"
                 for per in par_perimetre for nom in retenus}
    series: dict[str, list[np.ndarray]] = {
        n: [] for n in noms + list(temoins.values()) + list(cles_bloc.values())}
    diag: dict[str, list] = {"part_k0": [], "absdmid": {p: [] for p in par_perimetre}}
    for per, membres in par_perimetre.items():
        for j in JOURS[per]:
            for c in COINS:
                if (j, c) in TROUS_ARCHIVE:
                    continue
                chemin = PARTS / f"deep_{j}_{c}.parquet"
                print(f"[{time.time()-t0:6.0f}s]   extraction {j} {c} "
                      f"({chemin.stat().st_size/1e9:.2f} Go)…", flush=True)
                s = charge(chemin, DIST_MAX)
                # garde de causalité : coupe à mi-journée, contrôle de
                # CHAQUE extracteur sur CE jour réel — refus du tir AVANT
                # É0, jamais un constat après coup (les lignes du registre
                # ne se réécrivent pas)
                coupes = [(k, tronque_series(s, k)) for k in
                          coupes_causalite(j, c, len(s.mid))]
                tricheurs = []
                for nom in membres:
                    x = EXTRACTEURS[nom](s)
                    if _non_causal(nom, x, coupes):
                        tricheurs.append(nom)
                    series[nom].append(x)
                x = EXTRACTEURS[TEMOIN](s)
                if _non_causal(TEMOIN, x, coupes):
                    tricheurs.append(TEMOIN)
                series[temoins[per]].append(x)
                for nom in retenus:
                    x = EXTRACTEURS[nom](s)
                    if _non_causal(nom, x, coupes):
                        tricheurs.append(nom)
                    series[cles_bloc[(per, nom)]].append(x)
                if tricheurs:
                    raise SystemExit(
                        f"REFUS DU TIR — extracteur(s) NON CAUSAL(AUX) sur "
                        f"{j} {c} (lookahead, `00` §3, vérifié sur le "
                        f"RÉEL) : {tricheurs} — aucun verdict n'est écrit "
                        f"tant que l'instrument regarde le futur")
                # diagnostics de l'audit du 05-06/08, publiés avant tout É0 :
                # la part de masse au palier du mid (exclue des stocks/flux),
                # et |Δmid| pour la corrélation mécanique de chaque série
                tot = s.m_tot[0].sum() + s.m_tot[1].sum() + s.m_k0.sum()
                diag["part_k0"].append(
                    (f"{j} {c}", float(s.m_k0.sum() / tot) if tot else np.nan))
                dm = np.abs(np.diff(s.mid, prepend=np.nan))
                diag["absdmid"][per].append(dm)
    return ({n: np.concatenate(v) for n, v in series.items() if v}, diag)


def perimetre_d_une_cle(n: str) -> str:
    """Le périmètre déclaré d'une clé de série — candidat, témoin (_T0_)
    ou grandeur retenue au bloc (_BLOC_<per>::<nom>)."""
    if n in FICHES:
        return FICHES[n]["perimetre"]
    if n.startswith("_BLOC_"):
        return n[len("_BLOC_"):].split("::", 1)[0]
    return n.split("_T0_")[-1]


def construit_blocs(series: dict[str, np.ndarray]
                    ) -> dict[str, dict[str, np.ndarray]]:
    """Le bloc de référence PAR périmètre : le témoin T0 + chaque candidat
    `retenue` extrait sur ce périmètre. C'est ICI que la phrase de `05`
    (« entre dans le bloc de référence d'É2 pour les suivantes ») se
    réalise — avant le 06/08, personne ne l'y mettait et le bloc serait
    resté le témoin seul, indéfiniment. Consomme les clés de `series`."""
    blocs: dict[str, dict[str, np.ndarray]] = {}
    for cle in [k for k in series if k.startswith("_T0_")]:
        blocs.setdefault(cle.split("_T0_")[-1], {})[TEMOIN] = series.pop(cle)
    for cle in [k for k in series if k.startswith("_BLOC_")]:
        per, nom = cle[len("_BLOC_"):].split("::", 1)
        blocs.setdefault(per, {})[nom] = series.pop(cle)
    return blocs


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

    # les retenus du registre entrent au bloc — un retenu sans extracteur
    # rendrait le bloc incomplet : refus, pas un bloc silencieusement ampute
    retenus = [n for n in FICHES if boucle.etat_courant(n) == "retenue"]
    sans_ext = [n for n in retenus if n not in EXTRACTEURS]
    if sans_ext:
        raise SystemExit(f"candidat(s) retenu(s) sans extracteur : {sans_ext}"
                         f" — le bloc d'É2 serait incomplet, refus")
    if retenus:
        print(f"  bloc retenu ({len(retenus)}) : {', '.join(retenus)} — "
              f"extraits sur chaque périmètre, entrent au bloc d'É2")

    brut, diag = series_du_perimetre(prets, t0, retenus)
    perimetre_de = {n: perimetre_d_une_cle(n) for n in brut}
    # |Δmid| entre dans l'alignement de son périmètre (même index commun),
    # puis en sort : c'est un diagnostic, jamais un candidat
    for per, morceaux in diag["absdmid"].items():
        if morceaux and any(perimetre_de.get(n) == per for n in brut):
            brut[f"_absdmid_{per}"] = np.concatenate(morceaux)
            perimetre_de[f"_absdmid_{per}"] = per
    series = aligne(brut, perimetre_de)
    dmid = {per: series.pop(f"_absdmid_{per}")
            for per in diag["absdmid"] if f"_absdmid_{per}" in series}

    if any(j in ("20251212", "20251215") for j in jours_utiles):
        print("  AVERTISSEMENT (ADR-007) : le périmètre contient des jours "
              "DÉGRADÉS (12 et/ou 15, ≈44-75 % de couverture) — tout verdict "
              "J8 de ce tir est PROVISOIRE tant qu'ADR-007 n'est pas "
              "tranchée : si le plancher accepté les exclut, les candidats "
              "jugés repassent (`05` §7).")
    print(f"[{time.time()-t0:6.0f}s] === diagnostics d'audit, publiés avant É0 ===")
    for nom_js, part in diag["part_k0"]:
        print(f"  masse au palier du mid (exclue des stocks) {nom_js} : {part:.3%}")
    from harnais.stats import spearman as _sp
    for nom, x in sorted(series.items()):
        per = perimetre_de[nom]
        if per in dmid:
            print(f"  ρ(|Δmid|, {nom}) = {_sp(x, dmid[per]):+.3f}"
                  f"   <- entanglement mécanique avec le prix, à garder pour É4")

    # É0 à ciel ouvert (note du 06/08 au rapport, N1/N2 + post-scriptum) :
    # la matrice complète des |ρ| intra-périmètre est PUBLIÉE avant tout
    # verdict — un chiffre qui fonde un verdict doit lui survivre, et en
    # JSON, pas dans une phrase de log qu'il faudrait reparser. La bande
    # 0,70-0,90 bloque É4 par code (`epreuves.verifie_bande_e0`), plus par
    # promesse. C'est LA matrice de CE tir, sur SON alignement — jamais une
    # récupération des nombres d'un tir passé.
    vivants = sorted(n for n in series if n in FICHES)
    matrice = []
    print(f"[{time.time()-t0:6.0f}s] === matrice É0 (|ρ| par paire, intra-périmètre) ===")
    for i, na in enumerate(vivants):
        for nb in vivants[i + 1:]:
            if perimetre_de[na] != perimetre_de[nb]:
                continue
            r = abs(_sp(series[na], series[nb]))
            matrice.append({"a": na, "b": nb, "perimetre": perimetre_de[na],
                            "abs_rho": round(float(r), 6),
                            "bande_0.70-0.90": bool(0.70 <= r < 0.90)})
            bande = ("   <- BANDE 0,70-0,90 : sous la barre de fusion, "
                     "au-dessus du doublon probable d'É2" if 0.70 <= r < 0.90 else "")
            print(f"  |ρ|({na.split(' ·')[0]}, {nb.split(' ·')[0]}) = {r:.3f}{bande}")
    horodatage = time.strftime("%Y%m%d-%H%M%S")
    sortie = DEPOT / "journal" / f"e0-matrice-{horodatage}.json"
    sortie.write_text(json.dumps(
        {"tir": horodatage, "protocole_hash": pf["protocole_hash"],
         "n_obs_par_perimetre": {per: int(len(next(series[n] for n in vivants
                                                   if perimetre_de[n] == per)))
                                 for per in {perimetre_de[n] for n in vivants}},
         "paires": matrice},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  matrice écrite : {sortie.relative_to(DEPOT)} ({len(matrice)} paires)")

    n_obs = {n: int(np.isfinite(x).sum()) for n, x in series.items()}
    print(f"[{time.time()-t0:6.0f}s] séries alignées : "
          f"{min(n_obs.values()):,} à {max(n_obs.values()):,} observations")
    bloc_par_perimetre = construit_blocs(series)

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
