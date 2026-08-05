"""La statistique du banc contre scipy — la définition maison doit coïncider
avec la référence, et la partielle dégénérer proprement (`ADR-001`)."""
import numpy as np
import pytest
from scipy import stats as sps

from harnais.stats import (benjamini_hochberg, rangs, spearman,
                           spearman_partiel, student_jours)

rng = np.random.default_rng(42)


def test_spearman_egal_scipy():
    for _ in range(20):
        x, y = rng.normal(size=200), rng.normal(size=200)
        attendu = sps.spearmanr(x, y).statistic
        assert spearman(x, y) == pytest.approx(attendu, abs=1e-12)


def test_spearman_ex_aequo_rangs_moyens():
    # D9 : mid-rank. Série avec ex æquo massifs — doit rester = scipy.
    x = rng.integers(0, 5, size=300).astype(float)
    y = rng.integers(0, 5, size=300).astype(float)
    assert spearman(x, y) == pytest.approx(sps.spearmanr(x, y).statistic, abs=1e-12)
    assert list(rangs(np.array([1.0, 2.0, 2.0, 3.0]))) == [1.0, 2.5, 2.5, 4.0]


def test_serie_constante_rend_zero():
    assert spearman(np.ones(50), rng.normal(size=50)) == 0.0


def test_partielle_degenere_en_simple_sur_bloc_vide():
    x, y = rng.normal(size=100), rng.normal(size=100)
    assert spearman_partiel(x, y, None) == pytest.approx(spearman(x, y))
    assert spearman_partiel(x, y, np.empty((100, 0))) == pytest.approx(spearman(x, y))


def test_partielle_retire_le_confondant():
    # x et y ne sont liés QUE par z : la partielle doit s'effondrer vers 0
    z = rng.normal(size=2000)
    x = z + 0.1 * rng.normal(size=2000)
    y = z + 0.1 * rng.normal(size=2000)
    assert abs(spearman(x, y)) > 0.9
    assert abs(spearman_partiel(x, y, z.reshape(-1, 1))) < 0.1


def test_student_contre_scipy():
    c = rng.normal(0.3, 0.2, size=8)
    r = student_jours(c)
    attendu = sps.ttest_1samp(c, 0.0)
    assert r["p_value"] == pytest.approx(attendu.pvalue, abs=1e-12)
    lo, hi = attendu.confidence_interval(0.95)
    assert r["ic95"] == (pytest.approx(lo, abs=1e-10), pytest.approx(hi, abs=1e-10))


def test_student_refuse_un_seul_jour():
    with pytest.raises(ValueError):
        student_jours(np.array([0.5]))


def test_benjamini_hochberg_cas_connu():
    # exemple classique : 10 tests, q = 0,10
    p = {f"c{i}": v for i, v in enumerate(
        [0.001, 0.008, 0.039, 0.041, 0.042, 0.06, 0.074, 0.205, 0.212, 0.216])}
    r = benjamini_hochberg(p, q=0.10)
    # le plus grand i avec p(i) <= q·i/m est i=6 (0,06 <= 0,06) : SIX retenus,
    # y compris c2 et c3 qui rataient leur seuil individuel — c'est le step-up
    assert [r[f"c{i}"] for i in range(10)] == [True] * 6 + [False] * 4
