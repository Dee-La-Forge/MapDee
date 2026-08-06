"""La garde de causalité — `00` §3 : ZÉRO lookahead, contrainte produit.

Un extracteur non causal EST du lookahead : sa valeur à la photo i dépend
du futur. L'audit F a réécrit B5 en causal, mais rien n'empêchait le
prochain extracteur de ne pas l'être — ici la propriété devient une garde
permanente : pour CHAQUE extracteur, ext(jour tronqué) == ext(jour)[:n].
(Née du diagnostic de troncature du 06/08, où la causalité rendait valide
la comparaison jour-amputé / jour-plein.)"""
from pathlib import Path

import numpy as np
import pytest

from harnais.extracteurs import EXTRACTEURS, charge, tronque_series
from harnais.generateur import genere


@pytest.fixture(scope="module")
def jour_synthetique():
    import shutil
    d = Path(__file__).resolve().parent / "_tmp_causalite"
    d.mkdir(exist_ok=True)
    try:
        genere(d / "j.parquet", d / "jv.parquet", graine=7,
               duree_s=150.0, pas_ms=250)
        yield charge(d / "j.parquet")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_chaque_extracteur_est_causal(jour_synthetique):
    s = jour_synthetique
    n = len(s.mid)
    coupe = n // 2
    st = tronque_series(s, coupe)
    non_causaux = []
    for nom, ext in EXTRACTEURS.items():
        complet = ext(s)
        tronque = ext(st)
        if len(tronque) != coupe or not np.allclose(
                tronque, complet[:coupe], equal_nan=True):
            non_causaux.append(nom)
    assert not non_causaux, (
        f"extracteur(s) NON CAUSAL(AUX) — lookahead interdit (`00` §3) : "
        f"{non_causaux}")


def test_la_garde_du_tir_attrape_les_deux_tricheurs(jour_synthetique, monkeypatch):
    """La garde d'e0_reel (préalable du tir, sur le RÉEL) attrape :
    (a) le lookahead GLOBAL — un agrégat du jour entier diffusé partout,
    le cas canonique ; (b) le lookahead LOCAL — quelques pas en avant,
    le mode de défaillance réaliste (fenêtre centrée, décalage d'indice).
    Et l'honnête passe."""
    import harnais.e0_reel as ER
    s = jour_synthetique
    n = len(s.mid)
    coupes = [(k, tronque_series(s, k)) for k in
              sorted({max(1, int(n * f)) for f in ER.FRACTIONS_CAUSALITE})]

    nom_g = "TRICHEUR · moyenne du jour (test)"
    monkeypatch.setitem(EXTRACTEURS, nom_g,
                        lambda sj: np.full(len(sj.mid), float(np.mean(sj.mid))))
    assert ER._non_causal(nom_g, EXTRACTEURS[nom_g](s), coupes)

    def espion(sj):   # x[i] = mid[i+1] — UN pas de lookahead local
        x = np.empty(len(sj.mid))
        x[:-1] = sj.mid[1:]
        x[-1] = np.nan
        return x
    nom_l = "TRICHEUR · un pas en avant (test)"
    monkeypatch.setitem(EXTRACTEURS, nom_l, espion)
    assert ER._non_causal(nom_l, EXTRACTEURS[nom_l](s), coupes)

    nom_ok = "T0 · masse brute au palier"
    assert not ER._non_causal(nom_ok, EXTRACTEURS[nom_ok](s), coupes)


def test_tronque_series_coupe_tout_ce_qui_est_indexe(jour_synthetique):
    s = jour_synthetique
    n = len(s.mid)
    st = tronque_series(s, n // 2)
    assert len(st.mid) == n // 2 and len(st.t) == n // 2
    for cote in (0, 1):
        assert len(st.m_tot[cote]) == n // 2
    assert st.profil.shape[0] == n // 2
