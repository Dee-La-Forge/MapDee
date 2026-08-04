"""Fabrique les parquets d'un (jour, symbole) depuis le jeu OPEN BOOK.

    hl_orders_<jour>_<coin>.parquet   <- statuts (nanoseconde, TOUTES les tentatives)
    hl_book_<jour>_<coin>.parquet     <- carnet reconstruit depuis les DIFFS
    deep_<jour>_<coin>.parquet        <- carnet PROFOND, le support des mesures

Porté de `sandbox/detect/experiments/build_openbook_day.py` le 04/08/2026.
Seuls les chemins et les imports changent ; le calcul et les commentaires sont
conservés — ils décrivent des fautes mesurées et leur coût.

## Deux pièges rencontrés à l'écriture, corrigés ici

**Le carnet ne se reconstruit PAS depuis les statuts.** Essayé, mesuré : bid
116 640 / ask 75 046 sur un marché à 85 400, soit un carnet croisé de −41 594 $.
Les statuts contiennent TOUTES les tentatives, y compris ce qui n'atteint jamais
le carnet visible. Le flux de diffs, lui, ne contient par construction que ce
qui a été accepté (`SCHEMA.md` §4). C'est donc lui la source du carnet.

**Une heure isolée part d'un carnet vide** et garde à jamais les ordres retirés
à l'heure suivante — 615 ordres aberrants mesurés sur 1,81 M. On reconstruit
donc la journée d'un trait, avec `WARMUP_H` heures de chauffe non émises.

## Le temps

Les diffs ne portent AUCUN horodatage (`SCHEMA.md` §4). Il vient des statuts par
`oid` — jointure mesurée à **100,00 %** (3 manquants sur 1 805 630, bord
d'heure). Pour un `new` on prend l'ouverture de l'oid ; pour un `remove` le
dernier statut terminal ; à défaut, la ligne est comptée dans `n_temps_approx`.

    python construit/jour.py --day 20251208 --coin ETH
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import tarfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from sortedcontainers import SortedList

ICI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ICI))

from construit.openbook import (Mapdir, decode_px,               # noqa: E402
                                read_diffs, read_statuses)
from construit.grille import BIN_REL, nice                       # noqa: E402
# `nice` vient de `construit.grille`, PAS d'une copie locale : la grille du
# carnet profond doit etre bit pour bit celle de la production. Une deuxieme
# implementation aurait rederive — c'est exactement ce qui s'est produit dans
# l'ancien depot (defaut D1, 9 divergences sur 14, dont 76 % des cas ETH).

SRC = Path(os.environ.get("GON_OPENBOOK_SRC",
                          str(ICI / "data" / "l4" / "openbook-202512")))
# Racine des archives OPEN BOOK, surchargeable. Le jeu complet pese 191,5 Gio
# (statuts acceptes ET rejetes, 3 symboles, 4 mois de transactions).
OUT = Path(os.environ.get("GON_OPENBOOK_OUT", str(ICI / "data" / "openbook")))
# Surchargeable pour ne PAS ecraser la production quand on refabrique un jour
# a des fins de controle (cf. `GON_WARMUP_H` juste en dessous).

WARMUP_H = int(os.environ.get("GON_WARMUP_H", "8"))
# Surchargeable parce que ce 8 doit pouvoir etre MIS A L EPREUVE. Il a ete
# calibre sur BTC 20251208 et sur lui seul, et la mesure du 04/08/2026 montre
# que le defaut qu'il devait corriger est toujours la sur ce meme jour :
# deficit bid 12,5 % avec 8 h, contre 11,9 % annonce avec 2 h. Un parametre
# dont on ne peut pas faire varier la valeur n'est pas un parametre, c'est une
# croyance.
#
# heures de chauffe, non émises — voir ci-dessous
# POURQUOI 8 ET NON 2. Mesure du 03/08 sur le banc 20251208 (BTC), carnet
# profond, bande 0,12-0,80 % : avec 2 h de chauffe la masse des cinq premieres
# heures vaut 6,5 % de moins que le reste de la journee (permutation sur les
# medianes horaires, p < 0,0001). Ce serait tolerable si c'etait symetrique —
# une mesure de RAPPORT annule un deficit uniforme. Il ne l'est pas :
#
#     bid   deficit 11,9 %          ask   deficit 2,5 %
#     I(t)  h00-h04 -0,0724   contre   h05-h23 -0,0117
#
# soit un ecart de -0,0606 sur `I(t)`, PLUS d'un ecart-type horaire (0,0541).
# Le demarrage a froid fabrique donc un faux desequilibre DIRECTIONNEL — c'est
# exactement la quantite que M1 correle au prix. Mesurer sur ces heures
# reviendrait a correler un artefact d'instrument avec le rendement.
#
# Le deficit disparait a partir de h05, soit 7 h apres le debut de la chauffe.
# On prend 8 h. Le cout est du TEMPS DE CALCUL (+6 h de diffs rejouees), pas de
# la donnee : l'alternative — jeter les cinq premieres heures de chaque
# journee — couterait 21 % des instants.
LEVELS = 20           # paliers par côté dans hl_book (le format en veut 20)
SNAP_MS = 1000        # battement de coeur : au moins une photo par seconde
SNAP_MIN_MS = 250     # ... et une de plus dès que le HAUT du carnet bouge
# Pourquoi les deux. Le critère « la transaction est-elle dans la fourchette »
# mesure d'abord le RETARD de la photo, pas la justesse du carnet : le banc
# officiel, jugé par ses propres transactions, n'y arrive qu'à 48,6 % avec une
# photo de 278 ms d'âge médian. À 1 s de cadence on tombait à 40,1 % ; à cadence
# événementielle on monte à 51,0 % avec 100 ms d'âge médian.

TERMINAL = {2, 4, 5, 7, 10, 11, 12, 13, 14, 16}   # statuts qui retirent du carnet
OPEN = 1

# ---- CARNET PROFOND (`deep`) ------------------------------------------------
# POURQUOI IL EXISTE. `hl_book` ne porte que 20 paliers par cote — a 1 $ le tick
# sur BTC, cela fait +/- 20 $ autour du mid. Or la bande ou les mesures cherchent
# leurs murs est 0,12 % a 0,80 % du mid, soit 108 $ a 723 $ : elle est
# ENTIEREMENT hors de `hl_book`. Rien ne peut se calculer dessus.
#
# Ici on emet ce qu'on a DEJA en memoire, sur la grille de la production,
# plutot que de le faire reconstruire en aval par un second rejeu.
#
# CE QUE CE N'EST PAS. Ce carnet n'est pas « complet » et il n'est pas exempt de
# demarrage a froid : `plan` rejoue les `WARMUP_H` dernieres heures de la VEILLE
# en partant d'un dictionnaire VIDE (`book = {}`). Un ordre pose l'avant-veille
# et jamais retouche reste invisible. L'avantage se mesure, il ne se decrete pas.
DEEP_MS = 10_000      # cadence de l'archive de production
DEEP_BAND = 0.10      # nappe +/- 10 % du mid
DEEP_LOT = 400        # photos par groupe de lignes ecrit sur disque

# ---------------------------------------------------------------- jours geles
# LE GEL A DEUX NIVEAUX, scindes le 04/08/2026. Ils protegeaient deux choses
# differentes sous un seul nom, et ca bloquait 7 jours sans raison.
#
# RESERVE (17-23) — RIEN ne s'y construit, jamais.
#   Sept jours neufs, geles AVANT d'avoir ete regardes. C'est ce qui rend une
#   future certification opposable : si on attend d'en avoir besoin pour les
#   geler, on les aura deja explores. Ce niveau ne se negocie pas.
#
# HL_FIGES (01-07) — les fichiers `hl_*` ne se REECRIVENT pas.
#   `socle/verifie_donnee.py` a passe ses cinq controles croises sur
#   `hl_book`, `hl_orders` et `hl_fills` de ces jours. Les reconstruire
#   remplacerait la donnee sur laquelle les controles ont ete rendus.
#   MAIS `deep` de ces jours n'a JAMAIS ete construit, et il vit dans
#   `deep/parts/` — un repertoire different. Le fabriquer ne remplace rien.
#   C'est autorise depuis le 04/08, via `--phase deep`, sur demande explicite.
#
#   Ce qu'on y perd, et qu'il faut assumer : le `deep` de ces sept jours n'a
#   jamais ete regarde. Les fabriquer et les mesurer les consomme — ils ne
#   pourront plus servir de jeu de controle independant plus tard.
RESERVE = {"20251217", "20251218", "20251219", "20251220",
           "20251221", "20251222", "20251223"}
HL_FIGES = {"20251201", "20251202", "20251203", "20251204",
            "20251205", "20251206", "20251207"}
JOURS_GELES = RESERVE | HL_FIGES          # compatibilite de lecture


def _refuse_si_gele(day, ecrit: str = "tout") -> None:
    """Refuse d'ECRIRE sur un jour gele. `ecrit` dit CE QU'ON VA ecrire.

        ecrit="deep"  seul `deep/parts/` sera touche
        ecrit="tout"  `hl_*` sera touche (defaut : le cas le plus restrictif)
    """
    # NORMALISATION ICI, pas chez les appelants. L'audit du 03/08 a mesure que
    # `_refuse_si_gele(20251201)` — un ENTIER — passait sans refus, et a
    # reellement demarre la reconstruction du jour gele. Une garde qui depend
    # de la discipline de ses appelants n'est pas une garde.
    day = str(day)
    if day in RESERVE:
        raise SystemExit(
            f"REFUS : {day} appartient a la RESERVE (20251217-23), gelee avant "
            f"d'avoir ete regardee. Rien ne s'y construit, aucune phase.")
    if day in HL_FIGES and ecrit != "deep":
        raise SystemExit(
            f"REFUS : {day} porte les controles croises deja passes sur hl_book, "
            f"hl_orders et hl_fills — ils ne se reecrivent pas. Son `deep`, lui, "
            f"n'a jamais ete construit et ne remplace rien :\n"
            f"    python construit/jour.py --day {day} --coin BTC --phase deep")


class _DeepWriter:
    """Ecrit `deep` par lots — 5,6 M de lignes par jour ne tiennent pas en RAM.

    Un instant, une grille (`bs`), un mid, puis un palier `k = int(px // bs)`
    par ligne avec sa masse en dollars. `mag` est une somme de `prix x taille`,
    donc des dollars.
    """

    _SCHEMA = pa.schema([
        ("t", pa.int64()), ("coin", pa.string()),
        ("mid", pa.float64()), ("bs", pa.float64()),
        ("k", pa.int32()), ("mag", pa.float32()), ("n", pa.int16()),
    ])

    def __init__(self, path: Path, coin: str) -> None:
        self.path, self.coin = path, coin
        self._w: pq.ParquetWriter | None = None
        self.n_photos = 0
        self.n_lignes = 0
        self._t: list[int] = []
        self._mid: list[float] = []
        self._bs: list[float] = []
        self._k: list[int] = []
        self._mag: list[float] = []
        self._n: list[int] = []
        self._depuis = 0

    def add(self, t: int, mid: float, bs: float,
            paliers: dict[int, list]) -> None:
        for k, (m, n) in paliers.items():
            self._t.append(t); self._mid.append(mid); self._bs.append(bs)
            self._k.append(k); self._mag.append(m); self._n.append(n)
        self.n_photos += 1
        self.n_lignes += len(paliers)
        self._depuis += 1
        if self._depuis >= DEEP_LOT:
            self.flush()

    def flush(self) -> None:
        if not self._t:
            self._depuis = 0
            return
        tab = pa.table({"t": pa.array(self._t, pa.int64()),
                        "coin": pa.array([self.coin] * len(self._t), pa.string()),
                        "mid": pa.array(self._mid, pa.float64()),
                        "bs": pa.array(self._bs, pa.float64()),
                        "k": pa.array(self._k, pa.int32()),
                        "mag": pa.array(self._mag, pa.float32()),
                        "n": pa.array(self._n, pa.int16())},
                       schema=self._SCHEMA)
        if self._w is None:
            self._w = pq.ParquetWriter(self.path, self._SCHEMA,
                                       compression="zstd")
        self._w.write_table(tab)
        self._t.clear(); self._mid.clear(); self._bs.clear()
        self._k.clear(); self._mag.clear(); self._n.clear()
        self._depuis = 0

    def close(self) -> None:
        self.flush()
        if self._w is not None:
            self._w.close()


def _cible(kind: str, day: str, coin: str) -> Path:
    """La PARTIE d'un symbole : `<racine>/<kind>/parts/<kind>_<jour>_<coin>.parquet`.

    On construit un symbole a la fois, faute de memoire pour tenir les tables
    oid -> instant des deux ensemble. D'ou les parties, puis `fusionne`.
    """
    d = OUT / kind / "parts"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{kind}_{day}_{coin}.parquet"


def fusionne(kind: str, day: str) -> dict:
    """Assemble les parties du jour en `<kind>/<kind>_<jour>.parquet`.

    Par groupe de lignes, jamais d'un bloc : `hl_orders` fait 116 M de lignes
    par symbole et par jour.
    """
    # Garde de gel : une fusion REECRIT le fichier final. Fusionner `deep` ne
    # touche que `deep/`, donc le niveau de gel depend du `kind`.
    _refuse_si_gele(str(day), "deep" if kind == "deep" else "tout")
    parts = sorted((OUT / kind / "parts").glob(f"{kind}_{day}_*.parquet"))
    if not parts:
        return {"kind": kind, "parties": 0}
    dest = OUT / kind / f"{kind}_{day}.parquet"
    tmp_ = dest.with_suffix(".encours")
    w = None
    n = 0
    for p in parts:
        f = pq.ParquetFile(p)
        for i in range(f.metadata.num_row_groups):
            tb = f.read_row_group(i)
            if w is None:
                w = pq.ParquetWriter(tmp_, tb.schema, compression="zstd")
            w.write_table(tb)
            n += tb.num_rows
    w.close()
    tmp_.replace(dest)          # jamais de fichier final à moitié écrit
    return {"kind": kind, "parties": len(parts),
            "symboles": [p.stem.split("_")[-1] for p in parts], "lignes": n}


def _extract_day(archive: Path, prefix: str, dest: Path,
                 motif: str, expected: int = 24) -> int:
    """Extrait TOUS les membres du jour en UNE passe, en FLUX.

    Corrige un défaut coûteux de la première version : ouvrir l'archive une
    fois par fichier horaire. Un `.tar.xz` ne se lit pas en accès direct — il
    se décompresse depuis le début — donc extraire le membre N coûtait N fois
    la décompression. Mesuré : 9 min pour UNE heure, soit 3 h 30 pour un jour.
    En flux (`r|xz`), une seule passe suffit.
    """
    # SORTIE ANTICIPÉE, deux niveaux. Sans elle on relit l'archive ENTIÈRE
    # (70 Go pour les deux) même quand tout est déjà extrait — mesuré ~10 min
    # perdues par jour et par symbole.
    # Le décompte doit porter sur les fichiers de CETTE archive, pas sur tout
    # le dossier du jour : BTC et les diffs y cohabitent, et compter l'ensemble
    # faisait conclure « déjà extrait » avant même de toucher l'archive ETH —
    # la journée ETH sortait vide sans une seule erreur.
    d = dest / prefix.rstrip("/")
    deja = sorted(d.glob(motif)) if d.is_dir() else []
    if len(deja) >= expected:
        return len(deja)
    mode = "r|xz" if archive.suffix == ".xz" else "r|"
    n = 0
    with tarfile.open(archive, mode) as t:
        for m in t:
            if not m.isfile():
                continue
            if not m.name.startswith(prefix):
                # les jours sont ordonnés : une fois dépassé, plus rien à voir
                if n:
                    break
                continue
            if not (dest / m.name).exists():
                t.extract(m, path=dest)
            n += 1
            if n >= expected:
                break
    return n


# Les statuts de REJET : l'ordre n'a JAMAIS atteint le carnet.
# `marginCanceled` en est EXCLU — il figure dans TERMINAL, donc l'ordre etait
# bien au carnet et en a ete retire. Le classer en rejet etait une erreur
# INTRODUITE le 03/08 par le correctif lui-meme (111 lignes mesurees sur un
# echantillon de 28 M). Les trois derniers ont ete ajoutes apres confrontation
# aux 18 statuts reels de `mapdir/statuses.csv`.
_REJETS = {"perpMarginRejected", "iocCancelRejected", "reduceOnlyRejected",
           "minTradeNtlRejected", "badAloPxRejected",
           "perpMaxPositionRejected", "oracleRejected"}


def _action(statut: str) -> str:
    """Ce que la ligne FAIT, lu du statut. Quatre valeurs, pas deux."""
    if statut == "open":
        return "place"
    if statut in _REJETS:
        return "reject"
    if statut == "filled":
        return "fill"
    return "cancel"


def _parquet_complet(p: Path) -> bool:
    """Le fichier existe ET porte son pied de page.

    Tester l'existence seule a coûté un fichier : une passe tuée en cours
    d'écriture laisse un parquet tronqué (338 Mo au lieu de 654, sans pied),
    que la passe suivante a pris pour un travail déjà fait.
    """
    if not p.exists() or p.stat().st_size < 8:
        return False
    with open(p, "rb") as f:
        if f.read(4) != b"PAR1":
            return False
        f.seek(-4, 2)
        return f.read(4) == b"PAR1"


def _hour_file(dest: Path, member: str) -> Path | None:
    p = dest / member
    return p if p.exists() else None


def build(day: str, coin: str, phase: str = "all") -> dict:
    # `--phase deep` n'ecrit QUE dans `deep/parts/`. C'est ce qui permet de
    # fabriquer le carnet profond des jours 20251201-07 sans toucher a leurs
    # `hl_*`, sur lesquels les controles croises ont ete rendus.
    _refuse_si_gele(day, "deep" if phase == "deep" else "tout")
    tmp = SRC / "work"
    tmp.mkdir(exist_ok=True)
    low = coin.lower()
    stats = {"jour": day, "coin": coin, "heures": 0, "n_temps_approx": 0}
    n_orders = 0

    # ---- 1. statuts : temps par oid + hl_orders ---------------------------
    t_open: dict[int, int] = {}
    t_term: dict[int, int] = {}
    # ÉCRITURE PAR TRANCHE HORAIRE. La première version accumulait la journée
    # entière dans des listes Python : mesuré 30,7 Go de RSS à l'heure 18 sur 24,
    # pour ~150 M de lignes, et la conversion finale en table aurait doublé.
    # Un ParquetWriter alimenté heure par heure garde la mémoire plate.
    writer = None
    refaire_orders = (phase in ("all", "orders")
                      and not _parquet_complet(_cible("hl_orders", day, coin)))
    md = Mapdir(SRC / "mapdir")
    t0 = time.time()
    ne = _extract_day(SRC / f"{low}_orders_202512.tar.xz", f"{day}/", tmp,
                      f"{low}_*.data.gz")
    nb = _extract_day(SRC / "book_diffs_202512.tar", f"{day}/", tmp, "ex*.gz")
    print(f"  extraction : {ne} fichiers de statuts, {nb} de diffs "
          f"en {time.time() - t0:.0f}s", flush=True)
    for h in range(24):
        f = _hour_file(tmp, f"{day}/{low}_{h:02d}.data.gz")
        if f is None:
            continue
        st = np.sort(read_statuses(f), order="ts")
        stats["heures"] += 1
        oid = st["oid"].astype(np.int64)
        sid = st["statusId"]
        ts_ms = (st["ts"] // 1_000_000).astype(np.int64)
        for i in np.flatnonzero(sid == OPEN):
            t_open.setdefault(int(oid[i]), int(st["ts"][i]))
        for i in np.flatnonzero(np.isin(sid, list(TERMINAL))):
            t_term[int(oid[i])] = int(st["ts"][i])
        m = len(st)
        n_orders += m
        if not refaire_orders:
            del st
            print(f"  statuts {h:02d}h : {m:,} (cumul {n_orders:,}) [table deja ecrite]",
                  flush=True)
            continue
        px, sz = decode_px(st["limitPx"]), decode_px(st["sz"])
        tb = pa.table({
            "block_height": pa.array(np.zeros(m, dtype="int64")),
            "timestamp_ms": pa.array(ts_ms),
            "wallet": pa.array(md.wallets(st["userId"]), pa.large_string()),
            "coin": pa.array([coin] * m, pa.large_string()),
            # `action` derivee du STATUT, pas d'un simple « different de open ».
            # L'audit du 03/08 a mesure 21,72 % de lignes fausses : un rejet de
            # marge (20,70 % a lui seul) etait etiquete « cancel » alors que
            # l'ordre n'a jamais atteint le carnet, et une execution aussi.
            "action": pa.array([_action(md.statuses.get(int(s), str(s)))
                                for s in sid], pa.large_string()),
            "status": pa.array([md.statuses.get(int(s), str(s)) for s in sid],
                               pa.large_string()),
            "is_buy": pa.array(~st["isAsk"]),
            "price": pa.array(px), "size": pa.array(sz),
            "order_type": pa.array([md.order_types.get(int(x), "?")
                                    for x in st["orderTypeId"]], pa.large_string()),
            "tif": pa.array([md.tifs.get(int(x), "?") for x in st["tifId"]],
                            pa.large_string()),
            "reduce_only": pa.array(st["reduceOnly"]),
            "order_id": pa.array(oid),
            "cloid": pa.array([None] * m, pa.large_string()),
        })
        if writer is None:
            writer = pq.ParquetWriter(_cible("hl_orders", day, coin),
                                      tb.schema, compression="zstd")
        writer.write_table(tb)
        del tb, px, sz, st
        print(f"  statuts {h:02d}h : {m:,} (cumul {n_orders:,})", flush=True)
    if not stats["heures"]:
        return dict(stats, erreur="aucune heure de statuts")
    if writer is not None:
        writer.close()
    stats["orders"] = n_orders
    stats["t_statuts_s"] = round(time.time() - t0, 1)
    print(f"  -> hl_orders : {n_orders:,} lignes en {stats['t_statuts_s']}s",
          flush=True)

    if phase == "orders":
        return stats

    # ---- 2. carnet depuis les DIFFS, journée d'un trait -------------------
    # AGRÉGATION PAR PRIX, PAS PAR ORDRE. La première version émettait un palier
    # par ordre : cinq ordres au meilleur bid donnaient cinq « paliers » au MÊME
    # prix. Or `hl_book` porte 20 prix DISTINCTS avec la taille cumulée et le
    # compte d'ordres (`bid_n`/`ask_n`) ; un palier par ordre aurait rendu un mid
    # faux en silence. Les paliers sont numérotés de 1 à 20, pas de 0.
    t0 = time.time()
    book: dict[int, tuple[bool, float, float]] = {}   # oid -> (ask, px, sz)
    bid_ag: dict[float, list] = {}                    # px  -> [taille, n]
    ask_ag: dict[float, list] = {}
    bid_px = SortedList()                             # prix cotés, croissants
    ask_px = SortedList()

    def _add(ask: bool, px: float, sz: float) -> None:
        ag, sl = (ask_ag, ask_px) if ask else (bid_ag, bid_px)
        e = ag.get(px)
        if e is None:
            ag[px] = [sz, 1]
            sl.add(px)
        else:
            e[0] += sz
            e[1] += 1

    def _sub(ask: bool, px: float, sz: float) -> None:
        ag, sl = (ask_ag, ask_px) if ask else (bid_ag, bid_px)
        e = ag.get(px)
        if e is None:
            return
        e[0] -= sz
        e[1] -= 1
        if e[1] <= 0 or e[0] <= 1e-12:
            del ag[px]
            sl.remove(px)

    rows_t, rows_lv = [], []
    rows_bp, rows_bs, rows_bn = [], [], []
    rows_ap, rows_as, rows_an = [], [], []
    # HORLOGE MONOTONE. Les horodatages joints ne sont PAS croissants dans
    # l'ordre du fichier : un `remove` porte l'instant de la disparition, un
    # `new` celui du placement, et le flux mêle les deux. Comparer au DERNIER
    # instant vu bloquait la cadence dès qu'un horodatage tardif passait —
    # mesuré 55 photos par heure au lieu de 3 600. On avance donc sur le
    # MAXIMUM courant, à condition de ne l'alimenter qu'avec des instants
    # CRÉDIBLES. Deux sources de bruit, mesurées :
    #   * un `update` n'a pas d'instant propre. La version précédente lui
    #     donnait `t_term`, l'instant où l'ordre DISPARAÎTRA — parfois vingt
    #     heures plus tard. Une seule ligne propulsait l'horloge en fin de
    #     journée et tuait la cadence (mesuré : 1 photo par heure). Un `update`
    #     applique donc son effet sans toucher l'heure.
    #   * un `new`/`remove` dont l'instant tombe hors de l'heure du fichier est
    #     un appariement douteux : on l'utilise pour la taille, pas pour l'heure.
    # CHAUFFE SUR LA VEILLE, PAS SUR LA JOURNEE. La version precedente sautait
    # les `WARMUP_H` premieres heures DU JOUR COURANT : mesure de l'audit du
    # 03/08, la premiere photo tombait a +2,000 h pile, 7 jours sur 7 et 2
    # symboles sur 2 — soit 8,33 % de chaque journee SANS CARNET, donc sans mid.
    # On rejoue donc les dernieres heures de la VEILLE pour remplir le carnet,
    # sans rien emettre, puis on emet la journee entiere.
    veille = (datetime.strptime(day, "%Y%m%d")
              - timedelta(days=1)).strftime("%Y%m%d")
    nv = _extract_day(SRC / "book_diffs_202512.tar", f"{veille}/", tmp, "ex*.gz")
    if nv:
        plan = ([(veille, h, False) for h in range(24 - WARMUP_H, 24)]
                + [(day, h, True) for h in range(24)])
        stats["chauffe"] = f"veille {veille} ({WARMUP_H} h)"
    else:
        # Premier jour de l'archive : la veille n'existe pas. On retombe sur
        # l'ancien comportement et on le DIT, plutot que de laisser croire a
        # une journee complete.
        plan = [(day, h, h >= WARMUP_H) for h in range(24)]
        stats["chauffe"] = f"AUCUNE veille disponible — {WARMUP_H} h du jour perdues"
    horloge = 0
    last_snap = 0
    last_deep = 0
    bs_d = 0.0
    deep = _DeepWriter(_cible("deep", day, coin), coin)
    n_croise = 0
    n_hors_heure = 0
    top = (0.0, 0.0)                      # dernier haut de carnet photographie
    for d_h, h, emet in plan:
        f = _hour_file(tmp, f"{d_h}/ex{h}.gz")
        if f is None:
            continue
        base = int(datetime.strptime(d_h, "%Y%m%d")
                   .replace(tzinfo=timezone.utc).timestamp()) * 1000
        h_lo = base + h * 3_600_000 - 300_000
        h_hi = base + (h + 1) * 3_600_000 + 300_000
        oid, usr, side, px, kind, sz = read_diffs(f, coin)
        for i in range(len(oid)):
            o = int(oid[i])
            k = kind[i]
            if k == "new":
                a, p_, z = side[i] == "A", float(px[i]), float(sz[i])
                anc = book.get(o)
                if anc is not None:                  # re-pose du même oid
                    _sub(anc[0], anc[1], anc[2])
                book[o] = (a, p_, z)
                _add(a, p_, z)
                ts = t_open.get(o)
            elif k == "remove":
                anc = book.pop(o, None)
                if anc is not None:
                    _sub(anc[0], anc[1], anc[2])
                ts = t_term.get(o)
            else:                                     # update : taille restante
                # UN PALIER VIDE DOIT QUITTER LE CARNET. La version precedente
                # ajustait la taille sans jamais tester si le total tombait a
                # zero : le prix restait dans `bid_px`/`ask_px`, occupait un
                # rang, et DEPLACAIT LE MID. Mesure de l'audit du 03/08 :
                # 1,67 % des paliers de niveau 1 (bid) et 1,69 % (ask) etaient
                # de taille nulle ou negative (jusqu'a -3e-13), le mid etait
                # faux sur 3,36 % des photos, d'un dollar en median et jusqu'a
                # 10,5 $. Le taux « transaction dans la fourchette » passe de
                # 51,03 % a 53,23 % une fois ces fantomes retires.
                anc = book.get(o)
                if anc is not None:
                    a, p_, z0 = anc
                    z = float(sz[i])
                    if z <= 1e-12:
                        # taille restante nulle : l'ordre n'est plus au carnet
                        _sub(a, p_, z0)
                        book.pop(o, None)
                    else:
                        ag = ask_ag if a else bid_ag
                        e = ag.get(p_)
                        if e is not None:
                            e[0] += z - z0
                            if e[0] <= 1e-12:
                                del ag[p_]
                                (ask_px if a else bid_px).remove(p_)
                        book[o] = (a, p_, z)
                ts = None                       # pas d'instant propre
            if ts is None:
                stats["n_temps_approx"] += 1
                continue
            ms = ts // 1_000_000
            if ms < h_lo or ms > h_hi:
                n_hors_heure += 1
            elif ms > horloge:
                horloge = ms
            if not emet or not bid_px or not ask_px:
                continue
            b0, a0 = bid_px[-1], ask_px[0]
            dt = horloge - last_snap
            if dt < SNAP_MIN_MS or (dt < SNAP_MS and (b0, a0) == top):
                continue
            if b0 >= a0:                              # carnet croisé : on saute
                n_croise += 1
                continue

            # ---- CARNET PROFOND, horloge INDEPENDANTE de celle de hl_book ---
            # `hl_book` bat a la seconde (et plus vite quand le haut bouge) ;
            # le profond bat a 10 s, la cadence d'archive. Les deux ne doivent
            # pas se partager `last_snap`, sinon la cadence rapide de l'un
            # imposerait son rythme a l'autre.
            if horloge - last_deep >= DEEP_MS:
                last_deep = horloge
                mid_d = (b0 + a0) / 2.0
                want = nice(mid_d * BIN_REL)
                if not bs_d or abs(math.log(want / bs_d)) > 0.6:
                    bs_d = want          # rebase : meme regle que la production
                lo_d, hi_d = mid_d * (1 - DEEP_BAND), mid_d * (1 + DEEP_BAND)
                pal: dict[int, list] = {}
                # `irange` evite de balayer un carnet de plusieurs centaines de
                # milliers de prix pour n'en garder qu'une nappe.
                for p_ in bid_px.irange(lo_d, None):
                    e = bid_ag[p_]
                    c = pal.get(kk := int(p_ // bs_d))
                    if c is None:
                        pal[kk] = [p_ * e[0], e[1]]
                    else:
                        c[0] += p_ * e[0]; c[1] += e[1]
                for p_ in ask_px.irange(None, hi_d):
                    e = ask_ag[p_]
                    c = pal.get(kk := int(p_ // bs_d))
                    if c is None:
                        pal[kk] = [p_ * e[0], e[1]]
                    else:
                        c[0] += p_ * e[0]; c[1] += e[1]
                deep.add(horloge, mid_d, bs_d, pal)

            nb_ = min(LEVELS, len(bid_px))
            na_ = min(LEVELS, len(ask_px))
            nlv = min(nb_, na_)
            last_snap = horloge
            top = (b0, a0)
            for lv in range(nlv):
                p_bid = bid_px[-1 - lv]
                p_ask = ask_px[lv]
                eb, ea = bid_ag[p_bid], ask_ag[p_ask]
                rows_t.append(horloge)
                rows_lv.append(lv + 1)                # 1..20
                rows_bp.append(p_bid); rows_bs.append(eb[0]); rows_bn.append(eb[1])
                rows_ap.append(p_ask); rows_as.append(ea[0]); rows_an.append(ea[1])
        print(f"  diffs {d_h[-2:]}/{h:02d}h{'' if emet else ' (chauffe)'} : "
              f"{len(oid):,} · ordres {len(book):,} · "
              f"prix {len(bid_px)}/{len(ask_px)} · photos {len(rows_t)//LEVELS:,}",
              flush=True)
    if phase == "deep":
        # On a rejoue le carnet et emis `deep`, mais on n'ecrit PAS `hl_book` :
        # celui du jour existe deja et porte les controles croises.
        stats["hl_book"] = "NON ECRIT (--phase deep)"
    else:
        bp = np.array(rows_bp); bs = np.array(rows_bs)
        ap = np.array(rows_ap); asz = np.array(rows_as)
        tot = bs + asz
        pq.write_table(pa.table({
            "timestamp_ms": pa.array(rows_t, pa.int64()),
            "coin": pa.array([coin] * len(rows_t), pa.large_string()),
            "level": pa.array(rows_lv, pa.int32()),
            "bid_price": pa.array(bp), "bid_size": pa.array(bs),
            "bid_n": pa.array(rows_bn, pa.int32()),
            "ask_price": pa.array(ap), "ask_size": pa.array(asz),
            "ask_n": pa.array(rows_an, pa.int32()),
            "obi": pa.array(np.where(tot > 0, (bs - asz) / np.maximum(tot, 1e-9), 0.0)),
        }), _cible("hl_book", day, coin), compression="zstd")
    stats["book_croise"] = n_croise
    stats["book_hors_heure"] = n_hors_heure
    stats["book_rows"] = len(rows_t)
    stats["book_snaps"] = len(set(rows_t))
    stats["t_book_s"] = round(time.time() - t0, 1)
    print(f"  -> hl_book : {len(rows_t):,} lignes · "
          f"{stats['book_snaps']:,} photos en {stats['t_book_s']}s"
          f"{' [NON ECRIT]' if phase == 'deep' else ''}", flush=True)

    deep.close()
    stats["deep_rows"] = deep.n_lignes
    stats["deep_snaps"] = deep.n_photos
    stats["deep_mo"] = (round(deep.path.stat().st_size / 2**20, 1)
                        if deep.path.exists() else 0.0)
    print(f"  -> deep : {deep.n_lignes:,} lignes · "
          f"{deep.n_photos:,} photos · {stats['deep_mo']} Mo "
          f"({deep.n_lignes / max(deep.n_photos, 1):.0f} paliers/photo)",
          flush=True)
    return stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", required=True)
    ap.add_argument("--coin", default="BTC")
    ap.add_argument("--phase", default="all",
                    choices=["all", "orders", "book", "deep"])
    a = ap.parse_args()
    print(f"=== {a.coin} {a.day} ===", flush=True)
    s = build(a.day, a.coin, a.phase)
    print("\n" + " · ".join(f"{k}={v}" for k, v in s.items()))
