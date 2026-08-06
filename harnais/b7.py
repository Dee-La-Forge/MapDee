# -*- coding: utf-8 -*-
"""Les trois définitions de B7 — TRANSCRITES de `03` (bloc du 06/08/2026),
qui fait foi. Sources : C2 trois passes (protocoles pré-enregistrés),
ADR-009 (prix exécutés), ADR-010 (variante exécution).

Ces constantes ont été LUES au jour de banc sous des règles de lecture
gelées d'avance — elles ne se renégocient pas ici. Une révision passe par
ADR et par une relecture au jour de banc, jamais par une édition de ce
fichier au fil d'un résultat.
"""

#: Demi-largeur RELATIVE du voisinage du mur (C2 2ᵉ passe, §5) — la même
#: pour les deux symboles, c'est tout son intérêt.
DEMI_VOISINAGE_REL = 0.0005

#: Par symbole : M (ratio masse/médiane de voisinage, quantile 0,99),
#: P (persistance minimale, en photos), bande d'étude (quantile 0,999 du
#: flux exécuté, distance relative au mid).
B7 = {
    "BTC": {"M": 423.52, "P_photos": 6, "bande": 0.000925},
    "ETH": {"M": 175.36, "P_photos": 4, "bande": 0.001451},
}
