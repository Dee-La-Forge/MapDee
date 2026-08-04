"""Point d'entrée du recorder P1.

    python recorder/run.py                       # les 5 venues, BTC + ETH
    python recorder/run.py --venues binance,okx  # sous-ensemble (mise au point)
    python recorder/run.py --duration 60         # arrêt propre après 60 s (test)
    python recorder/run.py --log <fichier>       # journal sur disque (tâche planifiée)

N'écrit QUE dans `recorder/store/` (+ le journal demandé). Ne touche ni au démon
de prod (:8787) ni à son archive : celle-ci n'est même pas ouverte ici.

**Instance unique** : un verrou (`recorder/.recorder.lock`) empêche deux
processus d'écrire les mêmes fichiers. Une relance alors qu'il tourne déjà sort
proprement — c'est ce qui rend la tâche planifiée « toutes les 5 min »
inoffensive ET auto-réparatrice : elle ne fait rien tant qu'il tourne, et le
relance dans les 5 minutes s'il est mort.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gondetect import config as C            # noqa: E402
from recorder.engine import Engine           # noqa: E402
from recorder.server import serve            # noqa: E402
from recorder.singleton import AlreadyRunning, acquire   # noqa: E402

LOG_MAX_BYTES = 10 * 1024 * 1024


def setup_log(path: str) -> None:
    """Journal sur disque, tronqué au-delà de 10 Mo. Pas de rotation savante :
    ce fichier sert au diagnostic, l'archive c'est `store/`."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and p.stat().st_size > LOG_MAX_BYTES:
        p.unlink()
    fh = open(p, "a", encoding="utf-8", errors="replace", buffering=1)
    sys.stdout = fh
    sys.stderr = fh


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--venues", default=",".join(C.VENUES))
    ap.add_argument("--symbols", default=",".join(C.SYMBOLS))
    ap.add_argument("--duration", type=float, default=0, help="secondes puis arrêt (0 = infini)")
    ap.add_argument("--no-server", action="store_true")
    ap.add_argument("--log", default="")
    args = ap.parse_args()

    if args.log:
        setup_log(args.log)
    try:
        acquire(C.SANDBOX / "recorder" / ".recorder.lock")
    except AlreadyRunning as e:
        print(f"[singleton] {e}", flush=True)
        return

    venues = [v.strip() for v in args.venues.split(",") if v.strip()]
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    eng = Engine(venues=venues, symbols=symbols)
    eng.log(f"recorder P1 — {len(venues)} venues × {len(symbols)} symboles @ {C.SNAP_MS} ms")
    eng.log(f"store : {C.STORE}")

    tasks = [asyncio.create_task(eng.run())]
    if not args.no_server:
        tasks.append(asyncio.create_task(serve(eng)))
    if args.duration:
        tasks.append(asyncio.create_task(asyncio.sleep(args.duration)))
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for t in pending:
            t.cancel()
        for key, w in eng.writers.items():
            eng.streams[key].bytes_out += w.flush()
        import orjson
        print(orjson.dumps(eng.health(), option=orjson.OPT_INDENT_2).decode())
    else:
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("arrêt demandé")
