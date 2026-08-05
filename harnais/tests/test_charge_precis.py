"""LA PRÉCISION DE `charge()`, VÉRIFIÉE À L'UNITÉ — audit du 05/08/2026.

Un parquet fabriqué à la main, trois photos, chaque agrégat attendu calculé
sur papier. C'est ce test qui définit la sémantique :

* les flux (ajouts/retraits/disparitions/recouvrement) ne se comptent que
  pour les paliers INTÉRIEURS à la photo courante (marge 0,9 × dist_max) —
  la bande suit le mid, et sans marge chaque déplacement fabriquait des
  flux fantômes aux bords ;
* le palier k == k0 (celui du mid) est exclu des stocks ET des flux —
  l'ancienne version l'excluait des stocks mais le comptait côté ask ;
* les stocks (masses, Herfindahl, meilleurs) se calculent sur la bande
  entière, côté par côté.
"""
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from harnais.extracteurs import charge
from harnais.generateur import SCHEMA_DEEP

BS, MID12, MID3 = 2.0, 1000.0, 1002.0   # k0 = 500 puis 501
DIST = 0.01                              # bande ±10 $, intérieur ±9 $

# (t, k, mag) — n=1 partout, coin SYN
PHOTOS = [
    # photo 1 : bids 497/498/499, asks 501/502
    (0,   [(497, 100.0), (498, 200.0), (499, 300.0), (501, 300.0), (502, 150.0)], MID12),
    # photo 2 : 498 -> 150 (retrait 50) · 499 disparu (retrait 300, disparition)
    #           496 nouveau (ajout 80) · 501 -> 400 (ajout 100)
    (250, [(496, 80.0), (497, 100.0), (498, 150.0), (501, 400.0), (502, 150.0)], MID12),
    # photo 3 : mid 1002, k0 = 501 — 501 devient LE palier du mid : exclu des
    #           stocks et des flux (sa variation 400 -> 300 ne compte pas) ·
    #           499 revient a 120 : ajout ET recouvrement (retrait en photo 2)
    (500, [(496, 80.0), (497, 100.0), (498, 150.0), (499, 120.0),
           (501, 300.0), (502, 150.0)], MID3),
]


@pytest.fixture(scope="module")
def s(tmp_path_factory):
    lignes = {c: [] for c in ("t", "coin", "mid", "bs", "k", "mag", "n")}
    for t, paliers, mid in PHOTOS:
        for k, m in paliers:
            lignes["t"].append(t); lignes["coin"].append("SYN")
            lignes["mid"].append(mid); lignes["bs"].append(BS)
            lignes["k"].append(k); lignes["mag"].append(m); lignes["n"].append(1)
    p = tmp_path_factory.mktemp("precis") / "main.parquet"
    pq.write_table(pa.table(
        {"t": pa.array(lignes["t"], pa.int64()),
         "coin": pa.array(lignes["coin"], pa.string()),
         "mid": pa.array(lignes["mid"], pa.float64()),
         "bs": pa.array(lignes["bs"], pa.float64()),
         "k": pa.array(lignes["k"], pa.int32()),
         "mag": pa.array(lignes["mag"], pa.float32()),
         "n": pa.array(lignes["n"], pa.int16())}, schema=SCHEMA_DEEP), p)
    return charge(p, DIST)


def test_stocks_photo1(s):
    assert s.m_tot[0][0] == pytest.approx(600.0)     # 100+200+300
    assert s.m_tot[1][0] == pytest.approx(450.0)     # 300+150
    assert s.best_k[0][0] == 499 and s.best_m[0][0] == pytest.approx(300.0)
    assert s.best_k[1][0] == 501 and s.best_m[1][0] == pytest.approx(300.0)
    herf_attendu = (100/600)**2 + (200/600)**2 + (300/600)**2
    assert s.herf[0][0] == pytest.approx(herf_attendu)


def test_flux_photo2(s):
    assert s.add[0][1] == pytest.approx(80.0)        # 496, intérieur
    assert s.rem[0][1] == pytest.approx(350.0)       # 50 (498) + 300 (499)
    assert s.add[1][1] == pytest.approx(100.0)       # 501
    assert s.rem[1][1] == pytest.approx(0.0)
    assert s.disparus[1] == 1                        # 499 seul
    assert s.presents_prec[1] == 5
    assert s.recouvre[1] == pytest.approx(0.0)


def test_photo3_k0_exclu_et_recouvrement(s):
    # k0 = 501 : sa variation 400->300 ne compte NI en flux NI en stocks
    assert s.m_tot[1][2] == pytest.approx(150.0)     # 502 seul côté ask
    assert s.add[1][2] == pytest.approx(0.0)
    assert s.rem[1][2] == pytest.approx(0.0)
    # 499 revient : ajout bid 120, ET recouvrement (retiré à la photo 2)
    assert s.add[0][2] == pytest.approx(120.0)
    assert s.recouvre[2] == pytest.approx(120.0)
    assert s.disparus[2] == 0
    # les stocks bid : 80+100+150+120
    assert s.m_tot[0][2] == pytest.approx(450.0)


def test_profil_conserve_la_masse(s):
    for i, (_, paliers, _) in enumerate(PHOTOS):
        assert s.profil[i].sum() == pytest.approx(sum(m for _, m in paliers))
