# ADR-006 — GPU sans RAPIDS ; pas de WSL2

**Statut** : acceptée (2026-07-28) — **révise le plan approuvé**

## Contexte
Le plan prévoyait « FULL GPU » pour l'analytique via **RAPIDS cuDF/cuML**, avec
un caveat : « à trancher au setup selon la carte ». Carte constatée :
**NVIDIA GeForce GTX 1060 6 Go**, architecture **Pascal (sm_61)**.

## Décision
- **Pas de RAPIDS** : les versions actuelles de cuDF/cuML exigent Volta (7.0+).
  Monter WSL2 pour un RAPIDS qui ne supporte pas la carte serait du temps perdu.
- **Pas de WSL2** pour la sandbox : tout tourne en Python natif Windows.
- GPU réservé aux modèles quand le volume le justifiera (**P3**) : XGBoost /
  LightGBM GPU et PyTorch CUDA fonctionnent sur Pascal (`torch 2.5.1+cu121` déjà
  installé).
- **P0 tourne en CPU** : pandas/numpy/scikit-learn suffisent largement.

## Conséquence
Aucune perte : le run P0 complet (2 symboles × 3 jours, ~82 000 événements,
14 features, ablation sur 2 échelles) prend **~90 s en CPU**. Le GPU n'aurait
rien accéléré d'observable. La contrainte réapparaîtra à P3 avec le L4 (millions
d'ordres) — 6 Go de VRAM seront alors la vraie limite à surveiller.
