@echo off
REM ============================================================
REM  GON detect — installe la tache planifiee du recorder P1.
REM  5 venues x BTC/ETH @ 100 ms, archive dans recorder\store\.
REM  Relance auto a l'ouverture de session ET toutes les 5 min
REM  (sans effet tant qu'il tourne : verrou d'instance unique).
REM  Desinstaller : install-p1-task.cmd --remove
REM ============================================================
cd /d "%~dp0.."
python recorder\install_task.py %*
pause
