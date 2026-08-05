"""La statistique du banc — une seule, appliquée à trois questions (`ADR-001`).

É0 : Spearman candidat ↔ candidat. É2 : candidat ↔ bloc retenu.
É4 : Spearman PARTIEL candidat ↔ cible, contrôlé sur le bloc gelé du tour.

Ex æquo : rangs moyens (mid-rank) partout — décision D9, validée le
05/08/2026. Trois épreuves, une seule définition du rang, sinon elles ne
calculent pas la même statistique.
"""
from __future__ import annotations

import numpy as np
from scipy import stats as sps


def rangs(x: np.ndarray) -> np.ndarray:
    """Rangs moyens (D9). REFUSE les NaN/inf : `rankdata` les classerait en
    silence comme les plus grands, et un ρ pollué a déjà failli écrire une
    élimination `ρ=nan` au registre (audit du 05-06/08, constats F2/F3) —
    l'alignement des séries se fait AVANT la corrélation, jamais dedans."""
    a = np.asarray(x, dtype=float)
    if not np.isfinite(a).all():
        raise ValueError("série avec NaN/inf — aligner (index commun) avant "
                         "toute corrélation de rang")
    return sps.rankdata(a, method="average")


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Pearson sur rangs moyens — identique à scipy.spearmanr, réécrit ici
    pour que la définition du banc soit UN endroit, pas une dépendance."""
    rx, ry = rangs(x), rangs(y)
    sx, sy = rx.std(), ry.std()
    if sx == 0 or sy == 0:
        return 0.0  # série constante : aucun ordre à corréler
    return float(np.corrcoef(rx, ry)[0, 1])


def spearman_partiel(x: np.ndarray, y: np.ndarray,
                     bloc: np.ndarray | None) -> float:
    """Corrélation de rang partielle : Spearman des résidus de x et y après
    régression linéaire sur les RANGS du bloc de contrôle.

    `bloc` : matrice (n, k) des candidats retenus (+ témoin), ou None/vide —
    auquel cas elle DÉGÉNÈRE en Spearman simple, le cas prévu par `ADR-001`
    pour le premier candidat.
    """
    if bloc is None or (hasattr(bloc, "size") and bloc.size == 0):
        return spearman(x, y)
    b = np.atleast_2d(np.asarray(bloc, dtype=float))
    if b.shape[0] != len(x):
        b = b.T
    rb = np.column_stack([rangs(b[:, j]) for j in range(b.shape[1])])
    z = np.column_stack([np.ones(len(x)), rb])
    rx, ry = rangs(x), rangs(y)
    res_x = rx - z @ np.linalg.lstsq(z, rx, rcond=None)[0]
    res_y = ry - z @ np.linalg.lstsq(z, ry, rcond=None)[0]
    sx, sy = res_x.std(), res_y.std()
    if sx == 0 or sy == 0:
        return 0.0
    return float(np.corrcoef(res_x, res_y)[0, 1])


def student_jours(coefs: np.ndarray) -> dict:
    """É4, unité = le JOUR : un coefficient par jour, Student bilatéral.

    Rend la p-value (elle DÉCIDE, via BH) et l'IC 95 % (il est PUBLIÉ, il ne
    décide pas) — `ADR-001`, correction II.4.
    """
    c = np.asarray(coefs, dtype=float)
    n = len(c)
    if n < 2:
        raise ValueError(f"{n} coefficient(s) journalier(s) : Student exige n >= 2")
    m, s = c.mean(), c.std(ddof=1)
    if s == 0:
        # coefficients identiques : p-value dégénérée, IC ponctuel
        return {"n_jours": n, "moyenne": float(m), "p_value": 0.0 if m != 0 else 1.0,
                "ic95": (float(m), float(m))}
    t = m / (s / np.sqrt(n))
    p = 2.0 * sps.t.sf(abs(t), df=n - 1)
    demi = sps.t.ppf(0.975, df=n - 1) * s / np.sqrt(n)
    return {"n_jours": n, "moyenne": float(m), "p_value": float(p),
            "ic95": (float(m - demi), float(m + demi))}


def benjamini_hochberg(p_values: dict[str, float], q: float = 0.10) -> dict[str, bool]:
    """BH sur la collection des CANDIDATS jugés à É4 — et eux seuls
    (`ADR-001`, II.3). Résolutions et symboles sont des conjonctions internes.

    Rend {nom: retenu_par_BH}.
    """
    if not p_values:
        return {}
    noms = sorted(p_values, key=p_values.get)
    m = len(noms)
    seuil_atteint = 0
    for i, nom in enumerate(noms, start=1):
        if p_values[nom] <= q * i / m:
            seuil_atteint = i
    return {nom: (i <= seuil_atteint) for i, nom in enumerate(noms, start=1)}
