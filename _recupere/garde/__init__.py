"""Les garde-fous. Une mesure qui ne les passe pas ne s'exécute pas.

Ce module n'est pas une bibliothèque d'aide : c'est la **condition d'existence**
d'une mesure dans ce dépôt. Chaque fonction ici correspond à une faute commise
dans `sandbox/detect/` les 02-04/08/2026, et chacune LÈVE au lieu d'avertir —
un avertissement se lit après coup, une exception arrête avant.

    evenement_rare      quatre mesures bâties sur un « événement » à 85-100 %
    cible_utilisable    une cible à une classe, et une AUC de 0,42 puis 0,78
    fenetres_disjointes une mesure circulaire : +0,866 sur un monde nul
    unite_de_variance   un IC calculé sur des fenêtres recouvrantes, faux ×5
    controle_negatif    une bande nulle 2,5× trop étroite : 3 jours « significatifs »
                        sur 4, dont un au signe inverse ; 1 sur 4 après correction
"""
from __future__ import annotations

import numpy as np

__all__ = ["evenement_rare", "cible_utilisable", "fenetres_disjointes",
           "unite_de_variance", "controle_negatif", "EchecDeGarde"]


class EchecDeGarde(RuntimeError):
    """Une mesure a violé une condition d'existence. Elle ne rend rien."""


def evenement_rare(masque, nom: str, plafond: float = 0.60) -> dict:
    """Un « événement » qui survient tout le temps n'est pas un événement.

    Fautes qui ont motivé ce garde-fou, toutes du 03-04/08 :

        E2  encadrement           100,00 %  des instants
        D1  `flee > 0,5`           99,28 %  des murs
        D2  fuite (bug de filtre) 100,00 %  des murs approchés
        P2  ouverture d'une porte  85,09 %  des instants

    Quatre fois la mesure a été construite AVANT que sa fréquence ne soit
    regardée. `plafond` est volontairement lâche (60 %) : au-delà, ce n'est plus
    une condition, c'est une description de l'état normal du marché.
    """
    m = np.asarray(masque, dtype=bool)
    if m.size == 0:
        raise EchecDeGarde(f"{nom} : masque vide.")
    part = float(m.mean())
    if part > plafond:
        raise EchecDeGarde(
            f"{nom} : l'evenement survient dans {100*part:.2f} % des cas "
            f"(plafond {100*plafond:.0f} %). Ce n'est pas un evenement, c'est "
            f"l'etat normal. Redefinir la CONDITION, pas le modele.")
    if part < 0.001:
        raise EchecDeGarde(
            f"{nom} : l'evenement survient dans {100*part:.3f} % des cas "
            f"({int(m.sum())} occurrences). Trop rare pour etre mesure.")
    return {"n": int(m.size), "part": round(part, 5), "n_vrai": int(m.sum())}


def cible_utilisable(y, nom: str, part_min: float = 0.05,
                     n_min: int = 200) -> dict:
    """Une cible binaire dégénérée ne se mesure pas.

    Le 03/08, `flee > 0,5` valait 1 pour 99,28 % des murs. L'AUC qui en est
    sortie valait **0,42 un jour et 0,78 le lendemain** : elle se calculait sur
    quelques centaines de contre-exemples parmi 800 000.
    """
    v = np.asarray(y, dtype=float)
    v = v[np.isfinite(v)]
    if v.size == 0:
        raise EchecDeGarde(f"{nom} : aucune valeur finie.")
    if np.unique(v).size < 2:
        raise EchecDeGarde(
            f"{nom} : UNE SEULE CLASSE sur {v.size:,} points. L'evenement "
            f"mesure est universel — redefinir la condition, pas le modele.")
    part = float(min(v.mean(), 1 - v.mean()))
    n_min_obs = int(min((v > 0.5).sum(), (v <= 0.5).sum()))
    if part < part_min or n_min_obs < n_min:
        raise EchecDeGarde(
            f"{nom} : classe minoritaire a {100*part:.2f} % ({n_min_obs:,} sur "
            f"{v.size:,}). Sous {100*part_min:.0f} % ou {n_min} exemples, une "
            f"AUC n'est pas reproductible d'un jour a l'autre.")
    return {"n": int(v.size), "part_positive": round(float(v.mean()), 4),
            "part_minoritaire": round(part, 4)}


def fenetres_disjointes(t_fin_traits, t_debut_cible, nom: str) -> None:
    """Les traits et la cible ne partagent AUCUN instant.

    E1 mesurait le `flee_ratio` sur `[t, t+30 s]` et la cible sur `[t, t+H]`.
    Les deux se recouvraient : le sort d'un ordre est CAUSE par le mouvement de
    prix pendant la fenetre. Sur un monde ou la verite vaut rho = 0, la mesure
    rendait **+0,866**.
    """
    a = np.asarray(t_fin_traits, dtype=float)
    b = np.asarray(t_debut_cible, dtype=float)
    if a.shape != b.shape:
        raise EchecDeGarde(f"{nom} : formes incompatibles {a.shape} {b.shape}.")
    viol = int((b < a).sum())
    if viol:
        raise EchecDeGarde(
            f"{nom} : {viol:,} observations ou la cible commence AVANT la fin "
            f"des traits. Recouvrement = circularite (E1 : +0,866 sur un monde "
            f"nul). Decaler le depart de la cible.")


def unite_de_variance(n_obs: int, recouvrement: int, nom: str) -> dict:
    """L'erreur-type naive est fausse quand les fenetres se recouvrent.

    Sur une grille de 10 s et un horizon de 300 s, 30 observations consecutives
    se recouvrent : `1/sqrt(n)` est faux d'un facteur 5,5. La regle du depot :
    **l'unite de reechantillonnage est le JOUR**, et l'IC est celui de Student
    (couverture mesuree 94-95 %, contre 80-89 % pour le bootstrap sur peu
    d'unites).
    """
    if recouvrement < 1:
        raise EchecDeGarde(f"{nom} : recouvrement invalide ({recouvrement}).")
    n_eff = n_obs / recouvrement
    return {"n_brut": int(n_obs), "n_effectif": int(n_eff),
            "erreur_type_naive": round(float(n_obs ** -0.5), 5),
            "erreur_type_corrigee": round(float(n_eff ** -0.5), 5),
            "facteur": round(float(recouvrement ** 0.5), 2)}


def controle_negatif(stat, x, y, nom: str, recouvrement: int,
                     n_tirages: int = 200, rng=None) -> dict:
    """La bande nulle est MESURÉE, et elle préserve l'autocorrélation.

    Faute qui a motivé ce garde-fou — M1, mesurée le 04/08/2026 :

        la bande nulle était tirée par permutation i.i.d. de `y`. Une
        permutation i.i.d. détruit l'autocorrélation que les fenêtres
        recouvrantes créent (acf lag 1 = +0,96 sur le rendement, +0,73 sur
        l'asymétrie). La bande obtenue valait ±1,96/racine(n) — **exactement
        l'erreur-type naïve que `unite_de_variance` déclare fausse d'un
        facteur 5,5**, imprimée sur la même ligne que la correction.

        Mesure : bande 2,2 à 2,7 fois trop étroite. M1 déclarait 3 jours
        « hors du nul » sur 4, dont un au signe INVERSE de sa prédiction.
        Après correction : 1 sur 4.

    Le nul est ici tiré par **décalage circulaire** de `y` : l'appariement
    (x_t, y_t) est détruit, l'autocorrélation des DEUX séries reste intacte.
    Le décalage est toujours supérieur au recouvrement, sans quoi une partie
    de l'appariement d'origine survivrait dans le « nul ».

    Ne LÈVE pas quand la statistique tombe dans la bande — un résultat dans le
    nul n'est pas une faute, c'est une réponse. Lève quand la bande ne peut pas
    être construite honnêtement.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape:
        raise EchecDeGarde(f"{nom} : formes incompatibles {x.shape} {y.shape}.")
    if recouvrement < 1:
        raise EchecDeGarde(f"{nom} : recouvrement invalide ({recouvrement}).")
    n = x.size
    # Il faut au moins 20 unites independantes : sous ce seuil, la plage de
    # decalages disponibles est si courte que les tirages se ressemblent tous
    # et que les percentiles du nul ne veulent plus rien dire. Ce seuil garantit
    # aussi `n // 20 >= recouvrement`, donc un decalage TOUJOURS superieur au
    # recouvrement — sans quoi une part de l'appariement d'origine survivrait.
    if n < 20 * recouvrement:
        raise EchecDeGarde(
            f"{nom} : {n:,} observations pour un recouvrement de {recouvrement}, "
            f"soit {n // recouvrement} unites independantes (minimum 20). Trop peu "
            f"pour un nul honnete : les decalages disponibles sont trop courts.")
    marge = n // 20
    rng = np.random.default_rng(0) if rng is None else rng
    obs = float(stat(x, y))
    nul = np.array([float(stat(x, np.roll(y, int(s))))
                    for s in rng.integers(marge, n - marge, n_tirages)])
    if not np.isfinite(nul).any():
        raise EchecDeGarde(f"{nom} : la statistique ne rend que des NaN sur le nul.")
    lo, hi = (float(np.nanpercentile(nul, 2.5)),
              float(np.nanpercentile(nul, 97.5)))
    return {"observe": round(obs, 5),
            "nul_p2_5": round(lo, 5), "nul_p97_5": round(hi, 5),
            "largeur_du_nul": round(hi - lo, 5),
            "hors_du_nul": bool(obs < lo or obs > hi),
            "tirages": int(n_tirages), "decalage_minimal": int(marge),
            "methode": "decalage circulaire (autocorrelation preservee)"}


def _selftest() -> None:
    for f, args in ((evenement_rare, (np.ones(1000, bool), "tout")),
                    (evenement_rare, (np.zeros(1000, bool), "rien")),
                    (cible_utilisable, (np.ones(1000), "une classe")),
                    (cible_utilisable, ((np.arange(1000) < 5) * 1.0, "rare"))):
        try:
            f(*args)
        except EchecDeGarde:
            continue
        raise AssertionError(f"{f.__name__} n'a pas leve sur {args[1]}")
    assert evenement_rare((np.arange(1000) < 150), "ok")["part"] == 0.15
    assert cible_utilisable((np.arange(1000) < 300) * 1.0, "ok")
    try:
        fenetres_disjointes([10, 10], [5, 20], "recouvre")
        raise AssertionError("fenetres_disjointes n'a pas leve")
    except EchecDeGarde:
        pass
    fenetres_disjointes([10, 10], [10, 20], "disjoint")
    u = unite_de_variance(8640, 30, "H=300 s")
    assert u["facteur"] == 5.48, u

    # controle_negatif : DEUX MARCHES ALEATOIRES INDEPENDANTES. La verite est
    # connue — il n'y a AUCUN lien. C'est le monde nul sur lequel E1 rendait
    # +0,866. Le nul i.i.d. doit crier au signal, le nul par decalage non.
    def _rho(a, b):
        ra = np.argsort(np.argsort(a)).astype(float)
        rb = np.argsort(np.argsort(b)).astype(float)
        ra -= ra.mean(); rb -= rb.mean()
        return float((ra * rb).sum() / np.sqrt((ra * ra).sum() * (rb * rb).sum()))

    g = np.random.default_rng(7)
    x = np.cumsum(g.normal(size=4000))
    y = np.cumsum(g.normal(size=4000))
    r = controle_negatif(_rho, x, y, "marches independantes", recouvrement=42,
                         rng=np.random.default_rng(7))
    assert not r["hors_du_nul"], f"le nul par decalage a crie au signal : {r}"

    # la faute d'origine, reproduite : permutation i.i.d. sur le MEME monde nul
    h = np.random.default_rng(7)
    iid = np.array([_rho(x, h.permutation(y)) for _ in range(200)])
    lo, hi = np.percentile(iid, [2.5, 97.5])
    obs = _rho(x, y)
    assert obs < lo or obs > hi, "le nul i.i.d. aurait du crier au signal"
    assert (hi - lo) < r["largeur_du_nul"], (hi - lo, r["largeur_du_nul"])
    print(f"garde : selftest OK — 5 garde-fous, chacun leve sur sa faute d'origine\n"
          f"        controle_negatif : sur deux marches INDEPENDANTES, rho={obs:+.3f} ; "
          f"le nul i.i.d. le declare significatif (largeur {hi-lo:.4f}),\n"
          f"        le nul par decalage ne le fait pas (largeur "
          f"{r['largeur_du_nul']:.4f}, soit {r['largeur_du_nul']/(hi-lo):.1f}x plus large)")


if __name__ == "__main__":
    _selftest()
