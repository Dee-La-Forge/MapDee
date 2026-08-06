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


def test_alignement_defaillant_bloque_et_aucune_adr_n_exempte(monkeypatch):
    """Une paire à périmètre égal et longueurs inégales est un défaut
    d'instrument : |ρ| incalculable BLOQUE É4 — il ne disparaît pas de la
    garde au moment précis où la donnée est suspecte."""
    with pytest.raises(RefusEpreuve) as exc:
        verifie_bande_e0([("a", "b", float("nan"))])
    assert "alignement défaillant" in str(exc.value)
    # une ADR arbitre une corrélation, jamais un instrument cassé
    monkeypatch.setattr(epreuves, "PAIRES_SOUS_ADR", {frozenset(("a", "b"))})
    with pytest.raises(RefusEpreuve):
        verifie_bande_e0([("a", "b", float("nan"))])


def test_paires_bande_porte_le_defaut_d_alignement():
    """Longueurs inégales à périmètre égal : la paire entre dans le matériau
    de la garde avec |ρ|=NaN, elle n'est pas tue par un continue."""
    rng = np.random.default_rng(7)
    j3 = [n for n in FICHES if FICHES[n]["perimetre"] == "J3"][:2]
    series = {j3[0]: rng.normal(size=500), j3[1]: rng.normal(size=400)}
    paires = _paires_bande(series)
    assert len(paires) == 1
    a, b, r = paires[0]
    assert {a, b} == set(j3) and not np.isfinite(r)


def test_e4_refuse_de_juger_sans_le_bloc_retenu():
    """La dégénérescence de spearman_partiel (bloc None → Spearman simple)
    est réservée au bloc VIDE. Si le registre compte un bloc retenu et
    qu'on ne le passe pas, un doublon présumé serait jugé sans pénalité —
    e4 refuse : la garantie, pas l'argument."""
    from harnais.epreuves import e4
    with pytest.raises(RefusEpreuve) as exc:
        e4([np.arange(300.)], [np.arange(300.)], None,
           prealables_leves=True, n_bloc_retenu=2)
    assert "sans pénalité" in str(exc.value)
    # bloc vide déclaré vide : la dégénérescence est LÉGITIME (1er candidat)
    r = e4([np.random.default_rng(0).normal(size=300) for _ in range(3)],
           [np.random.default_rng(1).normal(size=300) for _ in range(3)],
           None, prealables_leves=True, n_bloc_retenu=0)
    assert "p_value" in r


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
