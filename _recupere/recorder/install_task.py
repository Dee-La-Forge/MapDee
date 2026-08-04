"""Installe (ou retire) la tâche planifiée Windows du recorder P1.

    python recorder/install_task.py            # installe et démarre
    python recorder/install_task.py --remove   # désinstalle

Choix de conception, et pourquoi :

* **`pythonw.exe`** — pas de fenêtre console qui traîne. Le journal part dans
  `recorder/recorder.log` via `--log`.
* **Deux déclencheurs** : à l'ouverture de session (donc après un redémarrage)
  ET toutes les 5 minutes. Le second n'est pas un doublon : c'est le
  **redémarrage automatique**. Le verrou d'instance unique
  (`recorder/singleton.py`) fait que la relance ne fait RIEN tant que le
  recorder tourne, et le relance dans les 5 minutes s'il est mort — crash,
  coupure réseau prolongée, arrêt manuel. Sans le verrou, ce déclencheur
  corromprait l'archive ; avec lui, il la répare.
* **`InteractiveToken`** — la tâche s'exécute sous la session ouverte, donc sans
  mot de passe stocké. Contrepartie assumée : elle ne tourne pas quand personne
  n'est connecté. Passer à `Password`/`S4U` exigerait de saisir un mot de passe,
  ce que je ne fais pas à ta place.
* **`ExecutionTimeLimit = PT0S`** — aucune limite de durée : c'est un démon.
* **`MultipleInstancesPolicy = IgnoreNew`** — deuxième garde-fou, en plus du
  verrou applicatif : le Planificateur lui-même refuse d'empiler les instances.
* **Batterie** : ni `DisallowStartIfOnBatteries` ni `StopIfGoingOnBatteries` —
  sinon l'accumulation s'arrêterait silencieusement au premier débranchement.
"""
from __future__ import annotations

import argparse
import getpass
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

TASK_NAME = "GON-detect-recorder-P1"

XML = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>GON — recorder L2 multi-venue (P1) : 5 venues x BTC/ETH @ 100 ms.
Sandbox isolee : ecrit uniquement dans sandbox/detect/recorder/store, sante sur http://127.0.0.1:8788/health.
Ne touche pas au demon de prod (:8787).</Description>
    <URI>\\{name}</URI>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <UserId>{user}</UserId>
      <Delay>PT30S</Delay>
    </LogonTrigger>
    <TimeTrigger>
      <StartBoundary>{start}</StartBoundary>
      <Enabled>true</Enabled>
      <Repetition>
        <Interval>PT5M</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{user}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>5</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{pythonw}</Command>
      <Arguments>"{script}" --log "{log}"</Arguments>
      <WorkingDirectory>{cwd}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remove", action="store_true")
    args = ap.parse_args()

    if platform.system() != "Windows":
        print("tâche planifiée Windows uniquement")
        return 1

    if args.remove:
        code, out = run(["schtasks", "/End", "/TN", TASK_NAME])
        code, out = run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"])
        print(out.strip() or ("supprimée" if code == 0 else "échec"))
        return code

    here = Path(__file__).resolve().parent
    sandbox = here.parent
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    if not pythonw.exists():
        pythonw = Path(sys.executable)      # repli : console visible
        print(f"pythonw introuvable — repli sur {pythonw}")

    domain = os.environ.get("USERDOMAIN") or platform.node()
    user = f"{domain}\\{getpass.getuser()}"
    start = (datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%S")

    xml = XML.format(name=TASK_NAME, user=user, start=start, pythonw=pythonw,
                     script=here / "run.py", log=here / "recorder.log", cwd=sandbox)

    # schtasks exige de l'UTF-16 pour /XML
    fd, tmp = tempfile.mkstemp(suffix=".xml")
    os.close(fd)
    Path(tmp).write_text(xml, encoding="utf-16")
    try:
        code, out = run(["schtasks", "/Create", "/TN", TASK_NAME, "/XML", tmp, "/F"])
        print(out.strip())
        if code != 0:
            return code
        code, out = run(["schtasks", "/Run", "/TN", TASK_NAME])
        print(out.strip())
    finally:
        os.unlink(tmp)

    print(f"\ntâche « {TASK_NAME} » installée.")
    print(f"  journal : {here / 'recorder.log'}")
    print(f"  santé   : http://127.0.0.1:8788/health")
    print(f"  état    : schtasks /Query /TN {TASK_NAME}")
    print(f"  retirer : python recorder/install_task.py --remove")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
