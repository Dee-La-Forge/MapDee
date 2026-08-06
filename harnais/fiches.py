"""Le pont `03_EconoPhysique.md` → machine : les 16 candidats déclarés (D10),
transcrits pour la boucle.

RÈGLE DE TRANSCRIPTION : ce module ne DÉCIDE rien — chaque champ recopie une
ligne de fiche de `03`, partie I. En cas d'écart, `03` fait foi et ce fichier
se corrige. Les réponses É1 sont celles que les fiches portent (« remplie à
la fiche, pas après », `05` §1) ; la boucle ne fait que les lire à son tour.

`cout_rang` ordonne le départage d'É0 (« on garde le moins cher ») d'après la
ligne `coût` : 0 = secondes · 1 = secondes-minutes · 2 = minutes ·
3 = minutes-dizaines · 4 = dizaines de minutes · 5 = heures.
"""
from __future__ import annotations

#: nom → (e1, cout_rang, perimetre, notes)
#: e1 = dict pour `epreuves.e1` : sans_l4, traverse_binance, navigateur,
#: degradation_mesuree (False = « à mesurer avant É4 », jamais éliminatoire).
FICHES: dict[str, dict] = {
    "A1 · OFI": dict(
        e1=dict(sans_l4=True, traverse_binance=True, navigateur=True,
                degradation_mesuree=False),
        cout_rang=2, perimetre="J3", vague=1, notes=""),
    "A2 · OFI localisé au mur": dict(
        e1=dict(sans_l4=True, traverse_binance=True, navigateur=True,
                degradation_mesuree=False),
        cout_rang=2, perimetre="J3", vague=1,
        notes="sous réserve du plafonnement à 500 paliers — à mesurer"),
    "A3 · flux signé e/r/a": dict(
        e1=dict(sans_l4=True, traverse_binance=True, navigateur=True,
                degradation_mesuree=False),
        cout_rang=3, perimetre="J3", vague=1,
        notes="traversée démontrée par C8.2 (journal/c8-rapport-20260805.md)"),
    "A4 · microprice": dict(
        e1=dict(sans_l4=True, traverse_binance=True, navigateur=True,
                degradation_mesuree=False),
        cout_rang=0, perimetre="J3", vague=1, notes="le moins cher du registre"),
    "A5 · propagateur": dict(
        e1=dict(sans_l4=True, traverse_binance=True, navigateur=True,
                version_simplifiee_demontree=False, degradation_mesuree=False),
        cout_rang=4, perimetre="J3", vague=1,
        notes="⚠️ partie courte du noyau perdue à 2 500 ms — forme figée en direct"),
    "A6 · auto-excitation (Hawkes)": dict(
        e1=dict(sans_l4=True, traverse_binance=False, navigateur=False,
                degradation_mesuree=False),
        cout_rang=5, perimetre="J3", vague=1,
        notes="❌ exige l'événementiel fin ; reclassable par ADR si C7 change "
              "l'acquisition ; reste utilisable hors ligne côté vérité"),
    "B1 · hazard rate (version palier)": dict(
        e1=dict(sans_l4=True, traverse_binance=True, navigateur=True,
                degradation_mesuree=False),
        cout_rang=4, perimetre="J3", vague=1,
        notes="version PALIER seule — la version ordre est L4 ; entrée au banc "
              "en écart à sa ligne de base (correction II.2)"),
    "B2 · résilience": dict(
        e1=dict(sans_l4=True, traverse_binance=True, navigateur=True,
                degradation_mesuree=False),
        cout_rang=2, perimetre="J3", vague=1, notes=""),
    "B3 · réapprovisionnement (iceberg)": dict(
        e1=dict(sans_l4=True, traverse_binance=True, navigateur=True,
                degradation_mesuree=False),
        cout_rang=2, perimetre="J3", vague=1,
        notes="dépend d'A3 (coût porté par elle) ; traversée héritée, "
              "quantités NETTES par fenêtre"),
    "B4 · absorption au contact": dict(
        e1=dict(sans_l4=True, traverse_binance=True, navigateur=True,
                degradation_mesuree=False),
        cout_rang=2, perimetre="J8", vague=1,
        notes="INCALCULABLE tant que « contact » n'a pas de définition (B7) ; "
              "unité de sortie P8, pas une feature — piège de redite avec la "
              "cible (fiche)"),
    "B5 · premier passage": dict(
        e1=dict(sans_l4=True, traverse_binance=True, navigateur=True,
                degradation_mesuree=False),
        cout_rang=1, perimetre="J3", vague=1, notes="grandeur de calibration d'horizon"),
    "C1 · concentration": dict(
        e1=dict(sans_l4=True, traverse_binance=True, navigateur=True,
                degradation_mesuree=False),
        cout_rang=2, perimetre="J3", vague=1,
        notes="⚠️ censure du filtre v>médiane — correction F3 exigée avant "
              "interprétation"),
    "C2 · forme et courbure": dict(
        e1=dict(sans_l4=True, traverse_binance=True, navigateur=True,
                degradation_mesuree=False),
        cout_rang=2, perimetre="J3", vague=1, notes="⚠️ censure et plafond, comme C1"),
    "C3 · diffusion anormale": dict(
        e1=dict(sans_l4=True, traverse_binance=True, navigateur=True,
                degradation_mesuree=False),
        cout_rang=0, perimetre="J3", vague=1, notes="le prix seul"),
    "D1 · ralentissement critique": dict(
        e1=dict(sans_l4=True, traverse_binance=True, navigateur=True,
                degradation_mesuree=False),
        cout_rang=2, perimetre="J8", vague=1,
        notes="entrée au banc en écart à sa ligne de base (correction II.2)"),
    "D2 · cascades": dict(
        e1=dict(sans_l4=True, traverse_binance=True, navigateur=True,
                degradation_mesuree=False),
        cout_rang=4, perimetre="J8", vague=1,
        notes="dépend d'A3 ; entrée au banc en taille de grappe (II.2)"),
}

TEMOIN = "T0 · masse brute au palier"   # hors compte, jamais retenable


#: La vague 1 est GELÉE à 16 (registre, 05/08/2026) — « rien ne s'y ajoute,
#: jamais ; son BH se calcule sur 16 ». Une fiche nouvelle se déclare en
#: vague 2+ avec son propre compte (`05` protection 1). Ce garde lève à
#: l'import : le gel est du code, pas une phrase.
_V1 = sum(1 for f in FICHES.values() if f["vague"] == 1)
if _V1 != 16:
    raise AssertionError(
        f"vague 1 gelée à 16 fiches, trouvé {_V1} — une fiche nouvelle "
        f"se déclare en vague 2+, jamais dans une vague gelée")
