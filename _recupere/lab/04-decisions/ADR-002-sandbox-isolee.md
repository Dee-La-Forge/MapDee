# ADR-002 — Sandbox isolée, prod en lecture seule

**Statut** : acceptée (2026-07-28)

## Contexte
La chaîne de prod (démon `tools/sec-recorder.js` sur :8787, app `poi/heatmap.js`)
est opérationnelle et ne doit pas être perturbée par une exploration.

## Décision
Tout le travail de détection vit sous `sandbox/detect/`. Aucune écriture hors de
ce dossier. L'archive de prod (`%LOCALAPPDATA%\gon-sec-recorder`) est ouverte en
**lecture seule**. Le recorder de la sandbox écrira dans `recorder/store/` et
servira sur **:8788**, jamais :8787.

## Conséquence
- Vérification : `git status` ne doit montrer aucune modification hors
  `sandbox/detect/` (hors mise à jour des documents de programme).
- L'intégration (pictos 🧊👻🛡️ dans `poi/heatmap.js`) n'a lieu qu'**après la
  porte P4**, derrière un flag, réversible.
