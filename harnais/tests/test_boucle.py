"""La boucle de bout en bout — sur registre temporaire et séries synthétiques.
Le vrai registre n'est jamais touché par un test."""
import shutil

import numpy as np
import pytest

from harnais.boucle import depose_manquants, etat_courant, tour
from harnais.fiches import FICHES, TEMOIN
from harnais.registre import CHEMIN, lire


@pytest.fixture
def reg(tmp_path):
    c = tmp_path / "registre.md"
    shutil.copy(CHEMIN, c)
    return c


@pytest.fixture
def reg_vierge(tmp_path):
    """Un registre neuf : le VRAI registre porte désormais le premier tour
    réel (les candidats y sont à É3) — les tests de machine complète partent
    d'un état vierge, pas d'une copie du réel qui évolue."""
    c = tmp_path / "registre_vierge.md"
    lignes = [
        "# Registre (test)",
        "",
        "| date | nom | état | épreuve | chiffre | périmètre | proposée par |",
        "|---|---|---|---|---|---|---|",
        "| 2026-08-05 | T0 · masse brute au palier | témoin trivial | — | — "
        "| J3 | protocole |",
        "",
    ]
    c.write_text("\n".join(lignes), encoding="utf-8")
    return c


def test_depot_complete_et_idempotent(reg):
    # le vrai registre peut déjà porter des candidats (le banc est ouvert
    # depuis le 05/08) : on teste la complétude et l'idempotence, pas un
    # état daté du fichier copié
    manquaient = [n for n in FICHES if etat_courant(n, reg) is None]
    deposes = depose_manquants(reg)
    assert deposes == manquaient
    assert all(etat_courant(n, reg) is not None for n in FICHES)
    n_lignes = len(lire(reg))
    assert depose_manquants(reg) == []   # idempotent
    assert len(lire(reg)) == n_lignes    # et sans écriture fantôme


def test_sans_donnees_tout_le_monde_attend_E0(reg_vierge):
    rapport = tour(series=None, chemin=reg_vierge)
    assert len(rapport) == 16
    for nom, (etat, raison) in rapport.items():
        assert etat == "déposée"
        assert "attente des données" in raison


def test_banc_complet_sur_series_synthetiques(reg_vierge):
    reg = reg_vierge
    rng = np.random.default_rng(0)
    base = rng.normal(size=3000)
    series = {}
    for i, nom in enumerate(FICHES):
        series[nom] = rng.normal(size=3000)
    # un doublon fabriqué : A2 recopie A1 à un cheveu — É0 doit fondre
    series["A2 · OFI localisé au mur"] = (
        series["A1 · OFI"] + 0.01 * rng.normal(size=3000))
    # un candidat qui redit le témoin : corrélé ~0,9 à T0 — É2 doit le marquer
    t0 = base
    series["C1 · concentration"] = 0.9 * t0 + np.sqrt(1 - 0.81) * rng.normal(size=3000)
    bloc = {TEMOIN: t0}

    rapport = tour(series=series, bloc=bloc, chemin=reg)

    # le doublon : un des deux (A1/A2) est éliminé à É0, l'autre continue
    etats = {n: rapport[n][0] for n in rapport}
    paire = {etats["A1 · OFI"], etats["A2 · OFI localisé au mur"]}
    assert "éliminée" in paire and paire != {"éliminée"}
    # A6 tombe à É1 (ne traverse pas), comme sa fiche le déclare
    assert etats["A6 · auto-excitation (Hawkes)"] == "éliminée"
    # la redite du témoin est marquée par É2
    assert etats["C1 · concentration"] == "doublon présumé"
    # les survivants butent sur É3, avec la raison D12/rejeu — le refus, pas un verdict
    survivants = [n for n, (e, _) in rapport.items() if e == "É3"]
    assert survivants, rapport
    assert all("REFUS" in rapport[n][1] for n in survivants)
    # et chaque chute au registre porte quelque chose dans sa colonne chiffre
    for l in lire(reg):
        if l["etat"] in ("éliminée", "doublon présumé", "sous surveillance"):
            assert l["chiffre"] not in ("", "—", "-")


def test_bloc_par_perimetre_le_temoin_du_bon_perimetre(reg):
    """Dette T0-J8 fermée : un candidat J8 passe É2 contre SON témoin, plus
    de refus de longueur."""
    rng = np.random.default_rng(9)
    series = {}
    for nom, f in FICHES.items():
        n = 3000 if f["perimetre"] == "J3" else 8000
        series[nom] = rng.normal(size=n)
    blocs = {"J3": {TEMOIN: rng.normal(size=3000)},
             "J8": {TEMOIN: rng.normal(size=8000)}}
    rapport = tour(series=series, bloc_par_perimetre=blocs, chemin=reg)
    # les J8 atteignent É3 (refus rejeu) au lieu de bloquer à É2
    for nom, f in FICHES.items():
        if f["perimetre"] == "J8":
            etat, raison = rapport[nom]
            assert etat in ("É3", "éliminée"), (nom, etat, raison)
