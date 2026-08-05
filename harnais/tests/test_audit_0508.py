"""Les régressions de l'audit du 05-06/08 — chaque constat corrigé a son
test, pour qu'aucun ne revienne en silence."""
import numpy as np
import pytest

from harnais.epreuves import RefusEpreuve, e2
from harnais.stats import benjamini_hochberg, rangs, spearman


def test_F2_rangs_REFUSENT_les_nan():
    with pytest.raises(ValueError, match="NaN"):
        rangs(np.array([1.0, np.nan, 3.0]))
    with pytest.raises(ValueError):
        spearman(np.array([1.0, np.inf]), np.array([1.0, 2.0]))


def test_F1_e2_REFUSE_les_longueurs_incompatibles():
    with pytest.raises(RefusEpreuve, match="longueurs"):
        e2(np.zeros(100), {"T0": np.zeros(80)})


def test_bh_collection_vide():
    assert benjamini_hochberg({}) == {}


def test_F1_e0_intra_perimetre_pas_de_crash(tmp_path):
    """J3 et J8 coexistent avec des longueurs différentes : le tour ne meurt
    pas, les comparaisons inter-périmètres n'existent pas."""
    import shutil

    from harnais.boucle import tour
    from harnais.fiches import FICHES, TEMOIN
    from harnais.registre import CHEMIN
    reg = tmp_path / "r.md"
    shutil.copy(CHEMIN, reg)
    rng = np.random.default_rng(3)
    series = {}
    for nom, f in FICHES.items():
        n = 3000 if f["perimetre"] == "J3" else 8000
        series[nom] = rng.normal(size=n)
    bloc = {TEMOIN: rng.normal(size=3000)}
    rapport = tour(series=series, bloc=bloc, chemin=reg, hash_protocole="abc123")
    # les J8 butent sur É2 (bloc J3) par un REFUS PROPRE, jamais un crash
    for nom, f in FICHES.items():
        etat, raison = rapport[nom]
        if f["perimetre"] == "J8" and etat == "É2":
            assert "longueurs" in raison or "REFUS" in raison


def test_F2_nan_dans_une_serie_refuse_au_lieu_d_eliminer(tmp_path):
    import shutil

    from harnais.boucle import tour
    from harnais.fiches import FICHES, TEMOIN
    from harnais.registre import CHEMIN, lire
    reg = tmp_path / "r.md"
    shutil.copy(CHEMIN, reg)
    rng = np.random.default_rng(4)
    series = {nom: rng.normal(size=500) for nom in FICHES}
    series["A1 · OFI"][10] = np.nan          # une série polluée
    bloc = {TEMOIN: rng.normal(size=500)}
    rapport = tour(series=series, bloc=bloc, chemin=reg)
    # personne n'est éliminé avec un chiffre nan, et A1 est en REFUS
    # (\bnan\b : « binance » contient « nan », leçon du premier essai)
    import re
    for l in lire(reg):
        assert not re.search(r"\bnan\b", l["chiffre"], re.IGNORECASE), l
    assert "polluée" in rapport["A1 · OFI"][1]


def test_F5_le_hash_signe_les_lignes(tmp_path):
    import shutil

    from harnais.boucle import tour
    from harnais.fiches import FICHES, TEMOIN
    from harnais.registre import CHEMIN, lire
    reg = tmp_path / "r.md"
    shutil.copy(CHEMIN, reg)
    rng = np.random.default_rng(5)
    series = {nom: rng.normal(size=400) for nom in FICHES}
    tour(series=series, bloc={TEMOIN: rng.normal(size=400)},
         chemin=reg, hash_protocole="deadbee")
    signees = [l for l in lire(reg) if "@deadbee" in l["proposee_par"]]
    assert signees, "aucune ligne signée par le hash du protocole"
