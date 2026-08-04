"""Fabrique `hl_fills_<jour>_<coin>.parquet` depuis le flux de transactions.

Porté de `sandbox/detect/experiments/build_openbook_fills.py` le 04/08/2026.
Seuls les chemins et les imports changent.

Le flux d'origine porte **un enregistrement par transaction** avec `side_info`
= les DEUX contreparties (wallet + oid). On écrit **deux lignes par
transaction**, une Maker et une Taker. C'est cette convention qui fait que
`hl_fills` compte double — mesuré `lignes_par_transaction = 2,0` — et toute
mesure qui somme un volume sans le savoir est fausse d'un facteur 2.

## Le seul point qui ne va pas de soi : qui est le Maker

Rien dans l'enregistrement ne le dit. L'ordre de `side_info` semble mettre
l'ordre le plus ancien en premier, mais « semble » n'est pas une mesure — et
une inversion Maker/Taker retournerait le sens de toute cible construite sur
« ce mur a-t-il été exécuté ou retiré ».

On tranche par le PRIX (voir le commentaire dans `build`), puis par le temps,
puis par l'oid. Les trois compteurs `role_par_prix` / `role_par_temps` /
`role_indecis` sont rendus : si `role_indecis` monte, l'attribution n'est pas
fiable et il faut le savoir AVANT d'en tirer quoi que ce soit.

    python construit/fills.py --day 20251208 --coin ETH
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import os
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

ICI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ICI))

from construit.jour import _refuse_si_gele                       # noqa: E402

SRC = Path(os.environ.get("GON_OPENBOOK_SRC",
                          str(ICI / "data" / "l4" / "openbook-202512")))
OUT = ICI / "data" / "openbook"
_PREFIXE_TID = {"BTC": 1, "ETH": 2, "SOL": 3}

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _cible(kind: str, day: str, coin: str) -> Path:
    d = OUT / kind / "parts"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{kind}_{day}_{coin}.parquet"


def _ts_ns(s: str) -> int:
    """`2025-12-01T08:59:59.932065631` -> nanosecondes depuis l'epoch, UTC.

    On n'utilise PAS `fromisoformat` : il tronque à la microseconde en 3.10 et
    refuse 9 décimales. Les nanosecondes sont la raison d'être de ce jeu.
    """
    d, _, frac = s.partition(".")
    base = datetime.strptime(d, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    ns = int((base - _EPOCH).total_seconds()) * 1_000_000_000
    if frac:
        ns += int(frac.ljust(9, "0")[:9])
    return ns


def read_trades(day: str, coin: str) -> list[dict]:
    """Les transactions du jour pour un symbole, depuis l'archive en flux."""
    arch = SRC / "trades_2025_12.tar"
    out: list[dict] = []
    tag = f'"{coin}"'
    pref = f"{day}/"
    seen = False
    with tarfile.open(arch, "r|") as t:
        for m in t:
            if not m.isfile():
                continue
            if not m.name.startswith(pref):
                if seen:
                    break          # les jours sont groupés : au-delà, rien
                continue
            seen = True
            raw = t.extractfile(m).read()
            with gzip.open(io.BytesIO(raw), "rt", errors="replace") as f:
                for line in f:
                    if tag not in line:
                        continue
                    try:
                        r = json.loads(line)
                    except Exception:
                        continue
                    if r.get("coin") != coin or len(r.get("side_info", [])) != 2:
                        continue
                    out.append(r)
    return out


def open_times(day: str, coin: str, oids: set[int]) -> tuple[dict, dict, dict]:
    """oid -> instant de pose, is_buy, prix limite — lu par tranches.

    116 M de lignes ne tiennent pas en mémoire sous forme de dictionnaire ; on
    ne garde que les oid qui apparaissent dans les transactions du jour.
    """
    f = OUT / "hl_orders" / "parts" / f"hl_orders_{day}_{coin}.parquet"
    if not f.exists():
        raise FileNotFoundError(
            f"{f} absent — construire d'abord les statuts :\n"
            f"    python construit/jour.py --day {day} --coin {coin} --phase orders")
    t_open: dict[int, int] = {}
    is_buy: dict[int, bool] = {}
    px_lim: dict[int, float] = {}
    # Le test d'appartenance doit être vectoriel : `int(x) in oids` sur 116 M de
    # lignes, c'est 116 M d'allers-retours Python. `np.isin` trie une fois.
    cible = np.fromiter(oids, dtype=np.int64, count=len(oids))
    cible.sort()
    pf = pq.ParquetFile(f)
    for b in pf.iter_batches(batch_size=4_000_000,
                             columns=["order_id", "timestamp_ms", "action",
                                      "is_buy", "price"]):
        o = b.column("order_id").to_numpy()
        keep = np.isin(o, cible, assume_unique=False)
        if not keep.any():
            continue
        b = b.filter(pa.array(keep))
        o = b.column("order_id").to_numpy()
        ts = b.column("timestamp_ms").to_numpy()
        ac = b.column("action").to_pylist()
        ib = b.column("is_buy").to_numpy(zero_copy_only=False)
        pxc = b.column("price").to_numpy()
        for j in range(len(o)):
            if ac[j] != "place":
                continue
            k = int(o[j])
            if k not in t_open:
                t_open[k] = int(ts[j])
                is_buy[k] = bool(ib[j])
                px_lim[k] = float(pxc[j])
    return t_open, is_buy, px_lim


def build(day: str, coin: str) -> dict:
    _refuse_si_gele(day)
    t0 = time.time()
    tr = read_trades(day, coin)
    if not tr:
        return {"jour": day, "coin": coin, "erreur": "aucune transaction"}
    oids = {int(si["oid"]) for r in tr for si in r["side_info"]}
    print(f"  transactions : {len(tr):,} · oids distincts {len(oids):,} "
          f"en {time.time() - t0:.0f}s", flush=True)

    t1 = time.time()
    t_open, is_buy, px_lim = open_times(day, coin, oids)
    print(f"  statuts appariés : {len(t_open):,}/{len(oids):,} "
          f"({len(t_open) / len(oids):.2%}) en {time.time() - t1:.0f}s", flush=True)

    ts_l, wal, sid, rol, prx, szl, oid_l, tid_l = ([] for _ in range(8))
    ec_mk, ec_tk = [], []
    n_accord = n_side = n_indecis = n_par_prix = n_par_temps = 0
    for r in tr:
        ns = _ts_ns(r["time"])
        ms = ns // 1_000_000
        px, sz = float(r["px"]), float(r["sz"])
        a, b = r["side_info"]
        oa, ob = int(a["oid"]), int(b["oid"])
        ta, tb = t_open.get(oa), t_open.get(ob)
        # LE MAKER EST CELUI DONT LE PRIX LIMITE EST CELUI DE LA TRANSACTION.
        # C'est la définition du Maker dans un carnet : l'exécution se fait à
        # SON prix. La règle naïve « le dernier posé est l'agresseur » s'inverse
        # sur les ordres à DÉCLENCHEMENT (stops, TP/SL, liquidations) : posés
        # longtemps avant, ils dorment hors du carnet visible puis agressent.
        # Mesuré sur BTC 01/12 : 4,68 % des transactions, toutes de ce type —
        # exemple relevé, un stop posé 142 s avant, prix limite 79 994 alors que
        # la transaction se fait à 86 932, soit son prix de DÉCLENCHEMENT.
        pa_, pb_ = px_lim.get(oa), px_lim.get(ob)
        ma = pa_ is not None and abs(pa_ - px) <= 1e-9
        mb = pb_ is not None and abs(pb_ - px) <= 1e-9
        if ma != mb:                                   # un seul au prix du trade
            mk, tk = (a, b) if ma else (b, a)
            n_par_prix += 1
        elif ta is not None and tb is not None and ta != tb:
            mk, tk = (a, b) if ta < tb else (b, a)
            n_par_temps += 1
        else:                       # à défaut : l'oid le plus petit est le plus ancien
            mk, tk = (a, b) if oa < ob else (b, a)
            n_indecis += 1
        if ta is not None and tb is not None:
            ec_mk.append(ms - t_open[int(mk["oid"])])
            ec_tk.append(ms - t_open[int(tk["oid"])])
        # `side` de la transaction = côté de l'AGRESSEUR (le Taker).
        tk_buy = r["side"] == "B"
        mesure = is_buy.get(int(tk["oid"]))
        if mesure is not None:
            n_side += 1
            n_accord += int(bool(mesure) == tk_buy)
        # tid UNIQUE ENTRE SYMBOLES. Un compteur qui repart a 1 par (jour,
        # coin) collisionne des la fusion : l'audit du 03/08 a mesure
        # 1 609 932 lignes sur 2 379 596 (67,7 %) ou un tid designait DEUX
        # transactions differentes, une BTC et une ETH.
        tid = _PREFIXE_TID.get(coin, 9) * 10 ** 12 + len(ts_l) // 2 + 1
        for who, role, buy in ((mk, "Maker", not tk_buy), (tk, "Taker", tk_buy)):
            tid_l.append(tid)
            ts_l.append(ms); wal.append(who["user"]); sid.append("Buy" if buy else "Sell")
            rol.append(role); prx.append(px); szl.append(sz)
            oid_l.append(int(who["oid"]))

    n = len(ts_l)
    pq.write_table(pa.table({
        "block_height": pa.array(np.zeros(n, dtype="int64")),
        "timestamp_ms": pa.array(ts_l, pa.int64()),
        "wallet": pa.array(wal, pa.large_string()),
        "coin": pa.array([coin] * n, pa.large_string()),
        "side": pa.array(sid, pa.large_string()),
        "role": pa.array(rol, pa.large_string()),
        "price": pa.array(prx, pa.float64()),
        "size": pa.array(szl, pa.float64()),
        "fee": pa.array(np.zeros(n)),
        "is_liquidation": pa.array(np.zeros(n, dtype=bool)),
        # `tid` : identifiant de transaction. Les DEUX lignes d'une transaction
        # partagent leur tid : c'est ce qui les relie, et ce qui permet de
        # compter les transactions REELLES (`tid.nunique()`) plutot que les
        # lignes.
        "tid": pa.array(tid_l, pa.int64()),
        "oid": pa.array(oid_l, pa.int64()),
    }), _cible("hl_fills", day, coin), compression="zstd")

    # Manifeste : meme regle que `jour.py`. Un artefact sans manifeste est
    # indistinguable d'un artefact d'une autre generation.
    from construit import empreinte
    from construit.jour import parametres_courants
    empreinte.ecris(_cible("hl_fills", day, coin), kind="hl_fills", jour=day,
                    coin=coin, phase="fills",
                    parametres=parametres_courants(),
                    entrees=[SRC / "trades_2025_12.tar"])

    mk_a, tk_a = np.array(ec_mk), np.array(ec_tk)
    return {
        "jour": day, "coin": coin, "trades": len(tr), "lignes": n,
        "role_par_prix": n_par_prix, "role_par_temps": n_par_temps,
        "role_indecis": n_indecis,
        "ecart_maker_ms_median": float(np.median(mk_a)) if mk_a.size else None,
        "ecart_taker_ms_median": float(np.median(tk_a)) if tk_a.size else None,
        "taker_pose_sous_100ms": (float((tk_a < 100).mean()) if tk_a.size else None),
        "maker_pose_sous_100ms": (float((mk_a < 100).mean()) if mk_a.size else None),
        "accord_side": (n_accord / n_side) if n_side else None,
        "t_s": round(time.time() - t0, 1),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", required=True)
    ap.add_argument("--coin", default="BTC")
    a = ap.parse_args()
    print(f"=== fills {a.coin} {a.day} ===", flush=True)
    s = build(a.day, a.coin)
    print("\n" + " · ".join(f"{k}={v}" for k, v in s.items()))
