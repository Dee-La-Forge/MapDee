"""P0 — la suite qui prouve que chaque contrôle PEUT lever (spec §2/P0.7).
Les contrôles sont purs : on les frappe sans salir le vrai dépôt."""
import pytest

from harnais.preflight import (PreflightError, check_arbre_propre,
                               check_fichiers_obligatoires,
                               check_gardefous_peuvent_lever,
                               check_manifestes, check_perimetre,
                               check_protocoles_commites)


def test_arbre_propre_passe_sur_sorties_declarees():
    check_arbre_propre([" M journal/construction/x.log",
                        " M journal/registre-des-grandeurs.md"])


def test_arbre_propre_LEVE_sur_fichier_quelconque():
    with pytest.raises(PreflightError):
        check_arbre_propre([" M harnais/epreuves.py"])


def test_protocoles_LEVE_si_05_modifie():
    with pytest.raises(PreflightError):
        check_protocoles_commites([" M 05_Protocole_de_selection.md"])
    check_protocoles_commites([" M autre_fichier.md"])  # ne lève pas


def test_perimetre_passe_sur_exploration():
    check_perimetre(["20251209", "20251210", "20251211"])


def test_perimetre_LEVE_sur_reserve():
    with pytest.raises(PreflightError, match="RÉSERVE"):
        check_perimetre(["20251218"])


def test_perimetre_LEVE_hors_exploration():
    with pytest.raises(PreflightError):
        check_perimetre(["20251201"])   # certification, pas exploration
    with pytest.raises(PreflightError):
        check_perimetre(["20251208"])   # banc d'instrument, pas exploration


def test_manifestes_passent_certifies_homogenes():
    m = {"provenance_certifiee": True, "parametres": {"DEEP_MS": 250}}
    check_manifestes([m, dict(m)])


def test_manifestes_nouvelle_generation_passent():
    # le format d'empreinte.py : la certification EST le manifeste
    m = {"schema_manifeste": 1, "artefact": {"sha256": "9bb3b0..."},
         "parametres": {"DEEP_MS": 250, "DEEP_BAND": 0.1}}
    check_manifestes([m, dict(m)])


def test_manifeste_nouvelle_generation_sans_sha_LEVE():
    with pytest.raises(PreflightError, match="certifié"):
        check_manifestes([{"schema_manifeste": 1, "artefact": {},
                           "parametres": {}}])


def test_manifestes_LEVENT_non_certifies():
    # la faute de la nuit du 04→05/08 : 93 manifestes false, blanchis par un script
    with pytest.raises(PreflightError, match="provenance"):
        check_manifestes([{"provenance_certifiee": False}])


def test_manifestes_LEVENT_deux_generations():
    with pytest.raises(PreflightError, match="générations"):
        check_manifestes([
            {"provenance_certifiee": True, "parametres": {"DEEP_MS": 250}},
            {"provenance_certifiee": True, "parametres": {"DEEP_MS": 10_000}}])


def test_manifestes_LEVENT_sur_vide():
    with pytest.raises(PreflightError):
        check_manifestes([])


def test_fichiers_LEVENT_sans_declaration():
    with pytest.raises(PreflightError, match="multiplicité"):
        check_fichiers_obligatoires(
            "| **candidats déclarés** | *à remplir avant le premier calcul* |", True)


def test_fichiers_LEVENT_sans_temoin():
    with pytest.raises(PreflightError, match="témoin"):
        check_fichiers_obligatoires("candidats déclarés : 16", True)


def test_fichiers_LEVENT_sans_fiche():
    with pytest.raises(PreflightError, match="fiche"):
        check_fichiers_obligatoires(
            "16 | témoin trivial | dans la table", False)


def test_les_gardefous_prouvent_leur_levee():
    check_gardefous_peuvent_lever()   # lèverait PreflightError s'ils étaient décoratifs


def test_le_vrai_registre_passe_le_controle():
    from harnais.preflight import DEPOT
    texte = (DEPOT / "journal" / "registre-des-grandeurs.md").read_text(encoding="utf-8")
    check_fichiers_obligatoires(texte, True)
