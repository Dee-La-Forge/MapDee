# ADR — décisions figées de la sandbox de détection

Format court volontaire (contexte / décision / conséquence). Écrits à la main
plutôt que via `ruflo-adr` : le plan le prévoyait, mais l'outil crée son propre
index hors de la sandbox et la contrainte d'isolation prime. L'indexation
`ruflo-adr` / `ruflo-agentdb` reste possible plus tard sur ce dossier.

| # | décision | statut |
|---|---|---|
| [001](ADR-001-pivot-supervise.md) | Détection = apprentissage SUPERVISÉ, pas débruitage | acceptée |
| [002](ADR-002-sandbox-isolee.md) | Sandbox isolée `sandbox/detect/`, prod en lecture seule | acceptée |
| [003](ADR-003-tout-python.md) | Stack tout-Python (features live = offline) | acceptée |
| [004](ADR-004-deux-symboles.md) | 2 symboles : BTC + ETH | acceptée |
| [005](ADR-005-label-immunise-churn.md) | Label immunisé au churn via `peak/traded` | acceptée |
| [006](ADR-006-gpu-sans-rapids.md) | GPU sans RAPIDS (GTX 1060 = Pascal) | acceptée — **révise le plan** |
| [007](ADR-007-venues-p1.md) | 5 venues pour le recorder P1 | acceptée |
| [008](ADR-008-souverainete-des-labels.md) | **Souveraineté des labels** : nœud d'abord, achat en secours | acceptée — **révise le plan** |
| [009](ADR-009-noeud-generateur-de-labels.md) | Le nœud est un **générateur de labels**, pas une infra (frontière = `gondetect/labelsource.py`) | acceptée |
| [010](ADR-010-gel-du-banc-p2a5.md) | Gel du banc P2a.5 : cible `y_post`, cadrage par RANG, instrument 15 s + barres pré-enregistrées du jalon 1 | acceptée |
| [011](ADR-011-grille-de-decision-jalon-1.md) | Grille de décision du jalon 1 (D → A → B → C) + relance unique pré-engagée | acceptée |
| [012](ADR-012-seuil-transfert-hl-binance.md) | Seuil pré-enregistré du transfert HL→Binance (porte S6) | acceptée |
| [013](ADR-013-barres-en-proportion-et-symbole-temoin.md) | Barres en **proportion** des folds (invariantes à la taille du banc) + symbole **témoin** vs **certifiant** | acceptée — **corrige l'implémentation d'ADR-010/011** |
| [014](ADR-014-porte-venue-ou-epoque.md) | Porte « venue ou époque ? » — **close, infaisable** : le flux L2 public d'Hyperliquid ne produit pas d'événements | close |
| [015](ADR-015-porte-venue-ou-epoque-v2.md) | Porte « venue ou époque ? » v2 sur L4 récent — 4 contrôles d'appariement pré-enregistrés (bande, cible, cadence, reconstruction) | proposée |
| [016](ADR-016-reparation-du-clustering.md) | Réparation de l'unité statistique (v2) — la percolation vient à 100 % de l'arête wallet ; bootstrap hiérarchique retenu | **appliquée** (décision 2), le reste en attente |
| [017](ADR-017-unite-de-plafonnement.md) | Séparer l'unité de **plafonnement** (`palier_ep`) de l'unité de **variance** (hiérarchique) — le régime précédent FABRIQUAIT +0,07 d'AUC sur un trait nul | appliquée — **voir l'addendum du 03/08 : 3 affirmations fausses** |
| [018](ADR-018-purge-du-cote-entrainement.md) | Purger du côté **entraînement**, pas du côté test — même invariant, test intact | **acceptée** — le « ~100× » tient ; l'addendum qui le corrigeait à ~3× est retiré (03/08 19 h) |
| [019](ADR-019-preenregistrement-certification-openbook.md) | Pré-enregistrement de la certification OPEN BOOK — unité de pli = le JOUR, barres 6/7 et 5/7, **un seul tir** | **consommée** le 03/08 → **CAS D** · voir l'addendum : §6.2 violé |
| [020](ADR-020-partition-certification-exploration.md) | Partition des jours : 01-07 certification (gelée), 08 banc d'instrument, 09-31 exploration | acceptée |
| [021](ADR-021-unite-configuration-et-impact.md) | Changer d'unité : la **configuration**, pas le mur. Cible = déplacement du prix, direction intrinsèque | **gelée**, non commencée |
