"""Chaque garde-fou passe sur le sain ET lève sur le malade — les deux moitiés
sont obligatoires : un garde-fou qui ne peut pas échouer est décoratif."""
import numpy as np
import pytest

from harnais.gardefous import GardeFouViole, cible_binaire, evenement_rare


def test_evenement_rare_passe():
    ind = np.zeros(1000, dtype=bool)
    ind[:100] = True
    assert evenement_rare(ind) == pytest.approx(0.10)


def test_evenement_rare_LEVE_sur_etat_normal():
    ind = np.ones(1000, dtype=bool)
    ind[:100] = False  # 90 % : « l'état normal du marché »
    with pytest.raises(GardeFouViole):
        evenement_rare(ind)


def test_evenement_rare_LEVE_sur_vide():
    with pytest.raises(GardeFouViole):
        evenement_rare(np.array([], dtype=bool))


def test_cible_binaire_passe():
    c = np.array([0] * 800 + [1] * 200)
    assert cible_binaire(c) == (200, 1000)


def test_cible_binaire_LEVE_classe_unique():
    with pytest.raises(GardeFouViole):
        cible_binaire(np.zeros(500))


def test_cible_binaire_LEVE_minoritaire_trop_petite():
    with pytest.raises(GardeFouViole):
        cible_binaire(np.array([0] * 10_000 + [1] * 199))   # < 200 exemples
    with pytest.raises(GardeFouViole):
        cible_binaire(np.array([0] * 10_000 + [1] * 400))   # 3,8 % < 5 %
