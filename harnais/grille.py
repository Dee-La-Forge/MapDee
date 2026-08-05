"""LA grille des paliers — copie versionnée dans le harnais (décision D2).

Promue depuis `_recupere/construit/grille.py` le 05/08/2026 : l'archive ne
doit pas être une dépendance d'exécution du harnais. L'égalité avec la
production ne se vérifie PAS par un import — elle se vérifie par
`tests/test_grille.py`, qui compare cette copie à `construit.grille` ET à un
artefact `deep` réel, bit à bit.

Histoire, à ne pas perdre : dans l'ancien dépôt cette fonction existait en deux
exemplaires divergents ({1, 2, 2.5, 5} contre {1, 2, 5, 10}) — 9 divergences
sur 14 (symbole, jour), et sur ETH le palier étiqueté NE CONTENAIT PAS son
prix dans 76 % des cas. Le coefficient 2,5 ne doit jamais sortir.
"""
from __future__ import annotations

import math

__all__ = ["BIN_REL", "nice"]

#: Granularité relative de palier, identique à la production
#: (`sec-recorder.js:443`). `bs = nice(mid * BIN_REL)`.
BIN_REL = 2.5e-5


def nice(x: float) -> float:
    """Arrondi 1/2/5/10 — `sec-recorder.js:233`. LA GRILLE DE LA PRODUCTION."""
    if x <= 0:
        return 1.0
    e = 10 ** math.floor(math.log10(x))
    m = x / e
    return e * (1 if m < 1.5 else 2 if m < 3.5 else 5 if m < 7.5 else 10)
