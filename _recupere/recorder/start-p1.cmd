@echo off
REM Recorder P1 — 5 venues x 2 symboles @ 100 ms, archive dans recorder\store\.
REM N'ecrit RIEN hors de la sandbox et ne touche pas au demon de prod (:8787).
REM Sante : http://127.0.0.1:8788/health
cd /d "%~dp0.."
set PYTHONIOENCODING=utf-8
python recorder\run.py %*
