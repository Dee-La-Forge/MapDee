"""Les extracteurs sur carnet synthétique — formes, finitude, et deux
comportements attendus (l'absorption injectée se voit dans T0 et C1)."""
from pathlib import Path

import numpy as np
import pytest

from harnais.extracteurs import ABSENTS, EXTRACTEURS, HORIZON_B5, series_du_jour
from harnais.fiches import FICHES, TEMOIN
from harnais.generateur import Injection, genere
from harnais.stats import spearman


@pytest.fixture(scope="module")
def jours():
    # « nul.parquet » a coûté une heure de fausse piste le 05/08 : NUL est un
    # nom de périphérique DOS réservé — même avec une extension, le stat
    # Win32 rend « Fonction incorrecte ». Ne jamais nommer un fichier
    # nul/con/prn/aux/com1…, extension ou pas.
    import shutil
    d = Path(__file__).resolve().parent / "_tmp_extracteurs"
    d.mkdir(exist_ok=True)
    try:
        genere(d / "bras_nul.parquet", d / "bras_nul_v.parquet", graine=42, duree_s=150.0, pas_ms=250)
        genere(d / "abs.parquet", d / "av.parquet", graine=42, duree_s=150.0, pas_ms=250,
               injections=[Injection("absorption", 30.0, 60.0, amplitude=8.0)])
        yield {"nul": series_du_jour(d / "bras_nul.parquet"),
               "abs": series_du_jour(d / "abs.parquet")}
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_toutes_les_series_sortent_avec_le_bon_index(jours):
    series = jours["nul"]
    n = len(series["T0 · masse brute au palier"])
    assert n == 600
    for nom, x in series.items():
        assert len(x) == n, nom
        assert np.isfinite(x).sum() > 100, f"{nom} : presque tout NaN"


def test_chaque_candidat_a_un_extracteur_ou_une_raison(jours):
    couverts = set(EXTRACTEURS) | set(ABSENTS)
    assert set(FICHES) | {TEMOIN} <= couverts
    assert not (set(EXTRACTEURS) & set(ABSENTS))


def test_bornes_elementaires(jours):
    s = jours["nul"]
    t0 = s["T0 · masse brute au palier"]
    assert (t0[np.isfinite(t0)] > 0).all()
    b5 = s["B5 · premier passage"]
    fini = b5[np.isfinite(b5)]
    # version CAUSALE (audit) : un âge, 0 juste après un déplacement
    assert fini.min() >= 0 and fini.max() <= HORIZON_B5
    assert np.isnan(b5[0]) and np.isfinite(b5[1:]).all()
    ofi = s["A1 · OFI"]
    assert (ofi[np.isfinite(ofi)] > 0).any() and (ofi[np.isfinite(ofi)] < 0).any()
    c3 = s["C3 · diffusion anormale"]
    fini = c3[np.isfinite(c3)]
    # marche aléatoire : exposant autour de 1, jamais aberrant
    assert fini.size > 50 and abs(np.median(fini) - 1.0) < 0.6


def test_l_absorption_injectee_se_voit(jours):
    """Comportement APPARIÉ : même graine, la trajectoire naturelle s'annule
    dans la différence injecté − nul ; il ne reste que la masse maintenue.
    (Un premier essai corrélait T0 seul à la fenêtre : ~2 M$ d'injection dans
    ~20 M$ de bande, noyés par la dérive — test naïf, remplacé.)"""
    diff = (jours["abs"]["T0 · masse brute au palier"]
            - jours["nul"]["T0 · masse brute au palier"])
    avant, fenetre = diff[:120], diff[120:360]
    assert np.nanmean(np.abs(avant)) < 1.0          # identiques avant T0
    assert np.nanmean(fenetre) > 100_000            # l'injection pèse pendant


def test_les_series_nul_et_injecte_different(jours):
    a, b = jours["nul"]["T0 · masse brute au palier"], jours["abs"]["T0 · masse brute au palier"]
    assert not np.allclose(np.nan_to_num(a), np.nan_to_num(b))
