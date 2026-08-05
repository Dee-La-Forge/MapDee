"""Les deux garde-fous d'`05` §3 — avant toute épreuve qui définit un
événement ou une cible binaire.

Ils ont attrapé les quatre fautes d'origine (quatre « événements » présents
dans la quasi-totalité des cas) plus deux autres depuis. Le symptôme est
toujours le même : une classe à 100 %.
"""
from __future__ import annotations

import numpy as np

SEUIL_RARE = 0.60        # au-delà : pas un événement, l'état normal du marché
SEUIL_CLASSE_MIN = 0.05  # classe minoritaire d'une cible binaire
N_MIN_CLASSE = 200


class GardeFouViole(RuntimeError):
    """Levée — jamais un warning. Une règle en prose n'arrête personne."""


def evenement_rare(indicateur: np.ndarray) -> float:
    """`indicateur` booléen : l'événement, observation par observation.

    Rend la fréquence si elle passe ; lève sinon.
    """
    ind = np.asarray(indicateur, dtype=bool)
    if ind.size == 0:
        raise GardeFouViole("événement : aucune observation — rien à juger")
    f = float(ind.mean())
    if f > SEUIL_RARE:
        raise GardeFouViole(
            f"événement présent dans {f:.0%} des cas (> {SEUIL_RARE:.0%}) : "
            f"ce n'est pas un événement, c'est l'état normal du marché. "
            f"On redéfinit la condition, pas le modèle.")
    return f


def cible_binaire(cible: np.ndarray) -> tuple[int, int]:
    """Cible à deux classes : minoritaire ≥ 5 % ET ≥ 200 exemples.

    Rend (n_minoritaire, n_total) si elle passe ; lève sinon.
    """
    c = np.asarray(cible)
    vals, counts = np.unique(c, return_counts=True)
    if len(vals) < 2:
        raise GardeFouViole(
            f"cible à une seule classe ({vals[0]!r}) — le symptôme classique")
    n_min, n_tot = int(counts.min()), int(counts.sum())
    if n_min < N_MIN_CLASSE:
        raise GardeFouViole(
            f"classe minoritaire à {n_min} exemples (< {N_MIN_CLASSE})")
    if n_min / n_tot < SEUIL_CLASSE_MIN:
        raise GardeFouViole(
            f"classe minoritaire à {n_min / n_tot:.1%} (< {SEUIL_CLASSE_MIN:.0%})")
    return n_min, n_tot
