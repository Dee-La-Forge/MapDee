"""Le bloc de référence d'É2 — la 5e arête (06/08) : « retenue » = « entre
dans le bloc pour les suivantes », et c'est e0_reel qui réalise la phrase."""
import numpy as np

from harnais.e0_reel import construit_blocs, perimetre_d_une_cle
from harnais.fiches import TEMOIN


def test_construit_blocs_les_retenus_entrent():
    s = {"_T0_J3": np.arange(3.), "_T0_J8": np.arange(4.),
         "_BLOC_J3::B1 · hazard rate (version palier)": np.ones(3),
         "_BLOC_J8::B1 · hazard rate (version palier)": np.ones(4),
         "A1 · OFI": np.zeros(3)}
    blocs = construit_blocs(s)
    assert set(blocs) == {"J3", "J8"}
    assert set(blocs["J3"]) == {TEMOIN, "B1 · hazard rate (version palier)"}
    assert set(blocs["J8"]) == {TEMOIN, "B1 · hazard rate (version palier)"}
    assert len(blocs["J8"][TEMOIN]) == 4
    # les clés consommées, les candidats intacts
    assert list(s) == ["A1 · OFI"]


def test_construit_blocs_sans_retenu_le_temoin_seul():
    s = {"_T0_J3": np.arange(3.), "A1 · OFI": np.zeros(3)}
    blocs = construit_blocs(s)
    assert set(blocs["J3"]) == {TEMOIN}


def test_perimetre_d_une_cle():
    assert perimetre_d_une_cle("A1 · OFI") == "J3"
    assert perimetre_d_une_cle("_T0_J8") == "J8"
    assert perimetre_d_une_cle("_BLOC_J8::B1 · hazard rate (version palier)") == "J8"
    # un nom de candidat contenant '::' ne casse pas le découpage (split 1)
    assert perimetre_d_une_cle("_BLOC_J3::X :: Y") == "J3"
