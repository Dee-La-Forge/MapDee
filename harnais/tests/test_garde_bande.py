"""La garde de bande É0 (post-scriptum du 06/08) — « une règle en prose
n'arrête personne » : on prouve que celle-ci LÈVE, et quand elle se tait."""
import numpy as np
import pytest

from harnais import epreuves
from harnais.boucle import _paires_bande
from harnais.epreuves import RefusEpreuve, verifie_bande_e0
from harnais.fiches import FICHES


def test_bande_vide_ne_bloque_pas():
    verifie_bande_e0([])
    verifie_bande_e0([("a", "b", 0.30), ("a", "c", 0.69)])   # sous la bande
    verifie_bande_e0([("a", "b", 0.90)])   # 0,90 = fusion É0, pas la bande


def test_une_paire_dans_la_bande_bloque_e4():
    with pytest.raises(RefusEpreuve) as exc:
        verifie_bande_e0([("A1 · OFI", "A4 · microprice", 0.85)])
    m = str(exc.value)
    assert "É4 refusée" in m and "0.850" in m
    assert "A1 · OFI" in m and "A4 · microprice" in m


def test_les_bornes_sont_exactes():
    # [0,70 ; 0,90) : fermée à gauche, ouverte à droite
    with pytest.raises(RefusEpreuve):
        verifie_bande_e0([("a", "b", 0.70)])
    with pytest.raises(RefusEpreuve):
        verifie_bande_e0([("a", "b", 0.899999)])


def test_une_adr_declaree_leve_le_blocage(monkeypatch):
    monkeypatch.setattr(epreuves, "PAIRES_SOUS_ADR",
                        {frozenset(("a", "b"))})
    verifie_bande_e0([("a", "b", 0.85)])          # arbitrée : passe
    with pytest.raises(RefusEpreuve):
        verifie_bande_e0([("a", "b", 0.85),
                          ("a", "c", 0.85)])       # l'autre bloque toujours


def test_paires_bande_intra_perimetre_seulement():
    """Le matériau de la garde : toutes les paires intra-périmètre, jamais
    une paire inter-périmètres, jamais une clé hors fiches (_T0_*)."""
    rng = np.random.default_rng(3)
    noms = list(FICHES)
    j3 = [n for n in noms if FICHES[n]["perimetre"] == "J3"][:3]
    j8 = [n for n in noms if FICHES[n]["perimetre"] == "J8"][:1]
    series = {n: rng.normal(size=500) for n in j3}
    series.update({n: rng.normal(size=800) for n in j8})
    series["_T0_J3"] = rng.normal(size=500)
    paires = _paires_bande(series)
    assert len(paires) == 3          # C(3,2) intra-J3, rien avec J8 ni _T0_
    for a, b, r in paires:
        assert FICHES[a]["perimetre"] == FICHES[b]["perimetre"] == "J3"
        assert np.isfinite(r)
    assert _paires_bande(None) == []
