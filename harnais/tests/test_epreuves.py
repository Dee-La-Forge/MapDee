"""P3 — seuils d'`05` §4 et refus explicites d'É3/É4."""
import numpy as np
import pytest

from harnais.epreuves import RefusEpreuve, e0, e1, e2, e3, e4

rng = np.random.default_rng(0)


def test_e0_elimine_le_doublon():
    x = rng.normal(size=500)
    v = e0(x + 0.01 * rng.normal(size=500), {"A1": x})
    assert not v.passe and v.etat_suivant == "éliminée" and abs(v.chiffre) >= 0.90


def test_e0_passe_l_independant():
    v = e0(rng.normal(size=500), {"A1": rng.normal(size=500)})
    assert v.passe and v.etat_suivant == "É1"


def test_e1_reoriente_le_l4():
    v = e1({"sans_l4": False, "traverse_binance": True, "navigateur": True})
    assert not v.passe and v.etat_suivant == "réorientée"


def test_e1_elimine_sans_binance():
    v = e1({"sans_l4": True, "traverse_binance": False, "navigateur": True})
    assert not v.passe and v.etat_suivant == "éliminée"


def test_e1_REFUSE_fiche_incomplete():
    with pytest.raises(RefusEpreuve, match="fiche"):
        e1({"sans_l4": True})


def test_e2_les_trois_zones():
    base = rng.normal(size=4000)

    def melange(rho):
        # mélange gaussien calibré pour viser une corrélation de rang ~rho
        return rho * base + np.sqrt(1 - rho**2) * rng.normal(size=4000)

    bloc = {"T0": base}
    assert e2(melange(0.2), bloc).etat_suivant == "É3"
    assert e2(melange(0.62), bloc).etat_suivant == "sous surveillance"
    assert e2(melange(0.9), bloc).etat_suivant == "doublon présumé"


def test_e2_REFUSE_bloc_vide():
    with pytest.raises(RefusEpreuve, match="témoin"):
        e2(rng.normal(size=100), {})


def test_e3_REFUSE_tant_que_D12_ouverte():
    with pytest.raises(RefusEpreuve, match="D12"):
        e3()


def test_e4_REFUSE_sans_prealables():
    with pytest.raises(RefusEpreuve, match="C3"):
        e4([np.zeros(3)], [np.zeros(3)], None)


def test_e4_REFUSE_sous_le_plancher_k_sur_n():
    # 05 §4, ajout du 05/08 : n_obs/jour >= 100 x taille du bloc. Ici 300 obs
    # pour 5 controles (plancher 500) : refus attendu, avec le chiffre.
    x = [np.random.default_rng(1).normal(size=300) for _ in range(3)]
    bloc = [np.random.default_rng(2).normal(size=(300, 5)) for _ in range(3)]
    with pytest.raises(RefusEpreuve, match="plancher"):
        e4(x, x, bloc, prealables_leves=True)


def test_e4_mecanique_sur_synthetique():
    """Sur synthétique (ÉS), préalables levés : la mécanique complète tourne —
    coefficients par jour, Student, IC publié."""
    jours_x, jours_y = [], []
    for j in range(8):
        r = np.random.default_rng(j)
        z = r.normal(size=300)
        jours_x.append(z + 0.5 * r.normal(size=300))
        jours_y.append(z + 0.5 * r.normal(size=300))
    r = e4(jours_x, jours_y, None, prealables_leves=True)
    assert r["n_jours"] == 8 and len(r["coefs_jour"]) == 8
    assert r["p_value"] < 0.001 and r["ic95"][0] > 0
