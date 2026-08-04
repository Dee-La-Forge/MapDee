"""Verrou d'INSTANCE UNIQUE du recorder.

Indispensable dès qu'une tâche planifiée peut relancer le recorder alors qu'il
tourne déjà : deux processus écrivant le MÊME `book-<jour>.jsonl.gz` y
entrelaceraient leurs membres gzip. Le fichier resterait décompressible (les
membres concaténés sont valides), mais les lignes seraient mélangées et les
horodatages non monotones — une corruption SILENCIEUSE, la pire espèce.

Mécanique (calquée sur `tools/lock.js` de la prod, qui a déjà servi) :
`mkdir` est atomique sous NTFS ; le PID est écrit dedans ; le mtime sert de
battement de cœur. Un verrou dont le battement date de plus de `STALE_S` est
réputé orphelin (processus tué) et peut être volé — sinon un crash brutal
interdirait tout redémarrage.
"""
from __future__ import annotations

import atexit
import os
import threading
import time
from pathlib import Path

STALE_S = 90.0        # au-delà : verrou orphelin
BEAT_S = 20.0         # battement (largement sous STALE_S)


class AlreadyRunning(RuntimeError):
    pass


def acquire(lock_dir: Path) -> None:
    """Prend le verrou ou lève `AlreadyRunning`. Libère à la sortie du process."""
    lock_dir.parent.mkdir(parents=True, exist_ok=True)
    pid_file = lock_dir / "pid"

    def make():
        lock_dir.mkdir()
        pid_file.write_text(str(os.getpid()), encoding="utf-8")

    try:
        make()
    except FileExistsError:
        try:
            age = time.time() - lock_dir.stat().st_mtime
        except OSError:
            age = STALE_S + 1
        if age < STALE_S:
            other = ""
            try:
                other = pid_file.read_text(encoding="utf-8").strip()
            except OSError:
                pass
            raise AlreadyRunning(
                f"un recorder tourne déjà (PID {other or '?'}, battement il y a "
                f"{age:.0f}s) — rien à faire")
        # Verrou orphelin : on le vole. Si DEUX processus volent en même temps,
        # un seul `mkdir` réussit ; l'autre repart en « déjà en cours ».
        try:
            pid_file.unlink(missing_ok=True)
            lock_dir.rmdir()
        except OSError:
            pass
        try:
            make()
        except FileExistsError:
            raise AlreadyRunning("course au vol du verrou — un autre process a gagné")

    def beat():
        while True:
            time.sleep(BEAT_S)
            try:
                now = time.time()
                os.utime(lock_dir, (now, now))
            except OSError:
                return

    threading.Thread(target=beat, daemon=True).start()

    def release():
        try:
            pid_file.unlink(missing_ok=True)
            lock_dir.rmdir()
        except OSError:
            pass

    atexit.register(release)
