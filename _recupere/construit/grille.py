"""LA grille des paliers. Une seule implémentation, volontairement.

Porté de `gondetect/p3_target.py::_nice` et `gondetect/config.py::BIN_REL`
(04/08/2026), sans modification du calcul.

Pourquoi ce fichier existe séparément : dans l'ancien dépôt, cette fonction
existait en **deux exemplaires divergents** — une grille à quatre coefficients
{1, 2, 2,5, 5} d'un côté, trois {1, 2, 5, 10} de l'autre. Mesure du 03/08 sur
les 14 (symbole, jour) du jeu OPEN BOOK : **9 divergences sur 14**, dont 5 des
7 jours ETH.

Là où elles divergeaient, le palier auquel un événement était apparié NE
CONTENAIT PAS le prix de son étiquette — 42 % des cas BTC, **76 % des cas ETH**,
et sur ETH le décalage était systématique et signé (toujours vers le bas,
−0,10 $). Les traits servis au modèle décrivaient le mur VOISIN, pas le mur jugé.

C'est le défaut le plus lourd du 03/08. Il visait ETH trois fois plus que BTC —
ce qui compte directement ici, puisque c'est ETH qu'on fabrique.

**Ne pas réimplémenter `_nice` ailleurs. L'importer.**
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


def _selftest() -> None:
    # Les quatre coefficients, aux bornes exactes. `m < 7.5` est STRICT :
    # 7,5 pile rend 10, et c'est le cas d'ETH (voir plus bas).
    for x, attendu in ((1.0, 1), (1.49, 1), (1.51, 2), (3.49, 2), (3.51, 5),
                       (7.49, 5), (7.5, 10), (7.51, 10), (9.9, 10)):
        assert nice(x) == attendu, (x, nice(x), attendu)

    # 2,5 ne doit JAMAIS sortir : c'est le coefficient de la grille fautive
    # qui a produit 9 divergences sur 14, dont 76 % des cas ETH.
    coeffs = sorted({round(nice(v) / 10 ** math.floor(math.log10(v)), 6)
                     for v in (i / 7.0 for i in range(1, 20_000))})
    assert coeffs == [1.0, 2.0, 5.0, 10.0], coeffs

    assert nice(0.0) == 1.0 and nice(-3.0) == 1.0

    # Cas reels. BTC est verifiable contre la donnee deja construite :
    # `deep_20251209_BTC.parquet` porte bs = 2.0.
    bs_btc = nice(90_000 * BIN_REL)
    bs_eth = nice(3_000 * BIN_REL)
    assert bs_btc == 2.0, bs_btc
    print(f"construit.grille : selftest OK — coefficients {coeffs}, jamais 2,5\n"
          f"        bs(BTC ~90 000) = {bs_btc}  (concorde avec deep_*_BTC deja construit)\n"
          f"        bs(ETH ~3 000)  = {bs_eth}  "
          f"(mid*BIN_REL = {3_000 * BIN_REL:.4f}, mantisse 7,5 pile -> 10)")


if __name__ == "__main__":
    _selftest()
