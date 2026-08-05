"""D2 — l'égalité avec la production se prouve par TEST, jamais par import à
l'exécution. Trois niveaux : les cas aux bornes, la copie contre l'archive,
la copie contre un artefact `deep` RÉEL."""
import math
import sys
from pathlib import Path

import pytest

from harnais.grille import BIN_REL, nice

DEPOT = Path(__file__).resolve().parents[2]


def test_bornes_exactes():
    # `m < 7.5` est STRICT : 7,5 pile rend 10 — le cas d'ETH.
    for x, attendu in ((1.0, 1), (1.49, 1), (1.51, 2), (3.49, 2), (3.51, 5),
                       (7.49, 5), (7.5, 10), (7.51, 10), (9.9, 10)):
        assert nice(x) == attendu, (x, nice(x), attendu)
    assert nice(0.0) == 1.0 and nice(-3.0) == 1.0


def test_le_coefficient_2_5_ne_sort_jamais():
    # la grille fautive du 03/08 : 9 divergences sur 14, 76 % des cas ETH
    coeffs = sorted({round(nice(v) / 10 ** math.floor(math.log10(v)), 6)
                     for v in (i / 7.0 for i in range(1, 20_000))})
    assert coeffs == [1.0, 2.0, 5.0, 10.0], coeffs


def test_bit_a_bit_contre_l_archive():
    """La copie promue et l'original de `_recupere/construit` doivent rendre
    la MÊME valeur partout où l'un des deux existe encore."""
    sys.path.insert(0, str(DEPOT / "_recupere"))
    from construit import grille as archive
    assert archive.BIN_REL == BIN_REL
    for i in range(1, 50_000):
        x = i / 3.7
        assert nice(x) == archive.nice(x), x


def test_contre_un_artefact_deep_reel():
    """`bs` d'un artefact construit == nice(mid × BIN_REL), ligne à ligne."""
    parts = sorted((DEPOT / "data" / "openbook" / "deep" / "parts").glob("deep_*.parquet"))
    if not parts:
        pytest.skip("aucun artefact deep construit sur cette machine")
    import pyarrow.parquet as pq
    t = pq.read_table(parts[0], columns=["mid", "bs"]).slice(0, 100_000)
    mids, bss = t["mid"].to_numpy(), t["bs"].to_numpy()
    for mid, bs in zip(mids[::997], bss[::997]):
        assert nice(mid * BIN_REL) == bs, (mid, bs)
