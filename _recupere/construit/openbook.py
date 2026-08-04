"""Lecture du jeu OPEN BOOK (Zenodo 18184441), format brut de la bourse.

Porté de `sandbox/detect/gondetect/openbook.py` le 04/08/2026, **sans
modification du calcul** — seuls le chemin du selftest et l'en-tête changent.

Ce jeu n'est pas un instrument, c'est la **sortie brute de la bourse** :

  * statuts d'ordres — CHAQUE tentative, y compris les ~89 % rejetées qui
    n'atteignent jamais le carnet visible, horodatées à la **nanoseconde** ;
  * diffs du carnet — CHAQUE changement du carnet visible, avec wallet et oid ;
  * transactions — les DEUX contreparties de chaque exécution.

Couverture déclarée : 1er au 31 décembre 2025, 744 fichiers horaires par
archive, **aucun trou**, BTC + ETH + SOL. Mesuré sur BTC 01/12 13 h :
5 426 758 statuts, 3 634 169 diffs, et la jointure par `oid` rend
**1 805 627 / 1 805 630 = 100,00 %** (3 manquants = bord d'heure).

## Ce que le format d'origine impose

  * `limitPx`/`sz`/`origSz` sont en virgule fixe empaquetée dans un uint32 :
    3 bits de décimales en tête, 29 bits de valeur (`SCHEMA.md` §Price Encoding) ;
  * les diffs du carnet **ne portent AUCUN horodatage** — le temps vient des
    statuts, par `oid`. C'est la jointure ci-dessus, et c'est pour ça qu'elle
    est le verrou de tout le module ;
  * `userId` est un entier ; l'adresse est dans `mapdir/users.csv`
    (328 456 entrées).
"""
from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path

import numpy as np

__all__ = ["RECORD_DTYPE", "Mapdir", "decode_px", "read_statuses",
           "read_diffs", "join_report"]

# ------------------------------------------------------------ format binaire
# SCHEMA.md §1 — 54 octets par enregistrement, petit-boutiste, sans séparateur.
RECORD_DTYPE = np.dtype([
    ("ts", "<u8"), ("userId", "<u4"), ("isBuilder", "?"), ("statusId", "<u1"),
    ("isAsk", "?"), ("limitPx", "<u4"), ("sz", "<u4"), ("oid", "<u8"),
    ("timestampDiff", "<u4"), ("triggerCondition", "<i4"), ("triggered", "?"),
    ("isTrigger", "?"), ("hasChildren", "?"), ("isPositionTpsl", "?"),
    ("reduceOnly", "?"), ("orderTypeId", "<u1"), ("tifId", "<u1"),
    ("triggerPx", "<u4"), ("origSz", "<u4"),
])
assert RECORD_DTYPE.itemsize == 54, RECORD_DTYPE.itemsize

_POW = np.array([1, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7], dtype=np.float64)


def decode_px(encoded) -> np.ndarray:
    """uint32 -> float. 3 bits de décimales en tête, 29 bits de valeur.

    float64 et non float32 comme dans le lecteur fourni : un prix BTC à 5
    chiffres avec 2 décimales dépasse la précision du float32 (7 chiffres
    significatifs), et une erreur d'arrondi sur le prix déplacerait le palier.
    """
    e = np.asarray(encoded, dtype=np.uint32)
    return (e & 0x1FFFFFFF).astype(np.float64) / _POW[e >> 29]


class Mapdir:
    """Tables de correspondance (`mapdir/`). users.csv fait 328 456 lignes."""

    def __init__(self, root: Path):
        self.users = self._load(root / "users.csv", val_first=True)
        self.statuses = self._load(root / "statuses.csv")
        self.order_types = self._load(root / "order_types.csv")
        self.tifs = self._load(root / "tifs.csv")

    @staticmethod
    def _load(p: Path, val_first: bool = False) -> dict:
        out = {}
        with open(p, newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                if len(row) < 2:
                    continue
                label, ident = row[0], row[1]
                out[int(ident)] = label
        return out

    def wallets(self, ids: np.ndarray) -> list[str]:
        u = self.users
        return [u.get(int(i), f"?{int(i)}") for i in ids]


def read_statuses(path: Path) -> np.ndarray:
    """Un fichier horaire de statuts -> tableau structuré.

    La taille du fichier divisée par 54 donne le compte exact ; on tronque
    plutôt que d'échouer si un octet traîne (le schéma le garantit, on ne le
    suppose pas).
    """
    raw = gzip.open(path, "rb").read()
    n = len(raw) // RECORD_DTYPE.itemsize
    return np.frombuffer(raw[: n * RECORD_DTYPE.itemsize], dtype=RECORD_DTYPE)


def read_diffs(path: Path, coin: str):
    """Un fichier horaire de diffs -> listes parallèles, filtré sur `coin`.

    Les trois symboles sont entrelacés. Le pré-filtre sur la chaîne évite de
    parser ~50 % de lignes inutiles (mesuré : BTC ≈ 50 %, ETH ≈ 32 %, SOL 18 %).
    Rend (oid, user, side, px, kind, sz) où `kind` ∈ {new, remove, update} et
    `sz` vaut la taille posée (new), 0 (remove) ou la taille restante (update).
    """
    tag = f'"{coin}"'
    oid, usr, side, px, kind, sz = [], [], [], [], [], []
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if tag not in line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("coin") != coin:
                continue
            d = r["raw_book_diff"]
            if d == "remove":
                k, s = "remove", 0.0
            elif "new" in d:
                k, s = "new", float(d["new"]["sz"])
            else:
                k, s = "update", float(d["update"]["newSz"])
            oid.append(r["oid"]); usr.append(r["user"]); side.append(r["side"])
            px.append(float(r["px"])); kind.append(k); sz.append(s)
    return (np.array(oid, dtype=np.uint64), usr, side,
            np.array(px), kind, np.array(sz))


def join_report(diff_oids: np.ndarray, status_oids: np.ndarray) -> dict:
    """Taux de jointure `oid` diffs -> statuts. C'EST LE VERROU DU MODULE.

    Sans horodatage sur les diffs, un taux dégradé signifierait qu'une part du
    carnet n'est pas datable — donc pas d'événement, pas de durée de vie, pas de
    contact. Mesuré sur BTC 01/12 13 h : 100,00 % (3 manquants sur 1 805 630,
    tous explicables par le bord d'heure). À REMESURER pour chaque heure
    ingérée, jamais à supposer.
    """
    d = np.unique(diff_oids)
    s = np.unique(status_oids)
    inter = np.intersect1d(d, s, assume_unique=True)
    return {"oids_diffs": int(d.size), "oids_statuts": int(s.size),
            "apparies": int(inter.size),
            "taux": float(inter.size / max(d.size, 1)),
            "manquants": int(d.size - inter.size)}


def _selftest() -> None:
    """Vérifie le décodage sur les valeurs du SCHEMA, pas sur une intuition."""
    # exemple du schéma : BTC à 96 543,21 -> decimals=2, value=9654321
    enc = np.uint32((2 << 29) | 9654321)
    got = float(decode_px(enc))
    assert abs(got - 96543.21) < 1e-6, got
    assert RECORD_DTYPE.itemsize == 54
    p = Path(__file__).resolve().parent.parent / "data" / "l4" / "openbook-202512"
    if (p / "mapdir" / "users.csv").exists():
        m = Mapdir(p / "mapdir")
        print(f"[openbook] mapdir : {len(m.users):,} wallets · "
              f"{len(m.statuses)} statuts · {len(m.tifs)} tifs")
    else:
        print(f"[openbook] mapdir absent sous {p} — decodage seul verifie")
    print("[openbook] décodage OK (exemple du SCHEMA reproduit)")


if __name__ == "__main__":
    _selftest()
