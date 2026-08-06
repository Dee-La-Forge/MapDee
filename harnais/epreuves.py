"""P3 — les épreuves. Seuils TRANSCRITS d'`05` §4 et d'`ADR-001` ; zéro
jugement, zéro paramètre libre au moment du verdict.

É3 et É4 REFUSENT de s'exécuter tant que leurs préalables manquent — le
harnais ne les simule pas (`chantiers/C9-harnais.md` §5) : un squelette qui
rendrait un verdict approximatif serait pire que pas de verdict.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from harnais.stats import spearman, spearman_partiel, student_jours

SEUIL_E0_DOUBLON = 0.90
SEUIL_E2_SURVEILLANCE = 0.50
SEUIL_E2_DOUBLON_PRESUME = 0.70
SEUIL_E3_RANG = 0.60


class RefusEpreuve(RuntimeError):
    """L'épreuve ne PEUT pas être rendue — préalable manquant. Pas un échec du
    candidat : un refus du harnais, avec sa raison."""


@dataclass
class Verdict:
    epreuve: str
    passe: bool
    chiffre: float | None
    etat_suivant: str
    detail: str = ""


# --- É0 — doublon interne ----------------------------------------------------
# UNE SEULE implémentation (audit du 06/08 : l'ancienne `e0` éliminait
# toujours le candidat testé — les jumeaux mouraient tous les deux — et
# n'était plus appelée que par ses tests pendant que la boucle réimplémentait.
# La décision pure vit ici ; la boucle l'appelle et écrit le registre.)

def e0_duel(rho: float, cout_a: float, cout_b: float,
            rang_a: int, rang_b: int) -> str | None:
    """Le duel d'É0 (`05` §4) : `|ρ| ≥ 0,90` → même objet, LE PLUS CHER meurt
    (égalité de coût : l'ordre de déclaration tranche — règle J3/boucle).
    Rend 'a' ou 'b' (le perdant), None si pas doublon. ρ non fini REFUSE."""
    if not np.isfinite(rho):
        raise RefusEpreuve("É0 : ρ non fini — un NaN ne décide pas, il refuse")
    if abs(rho) < SEUIL_E0_DOUBLON:
        return None
    return "a" if (cout_a, rang_a) > (cout_b, rang_b) else "b"


# --- É1 — admissible au produit (papier, la fiche répond) --------------------

def e1(fiche: dict) -> Verdict:
    """Quatre questions, règles cas par cas d'`05` §4. La fiche porte les
    réponses (ligne É1 remplie à la fiche, pas après)."""
    for cle in ("sans_l4", "traverse_binance", "navigateur"):
        if cle not in fiche:
            raise RefusEpreuve(f"fiche incomplète : ligne {cle!r} absente — "
                               f"pas de fiche, pas de test (`05` §1)")
    if not fiche["sans_l4"]:
        return Verdict("É1", False, None, "réorientée",
                       "exige le L4 → fabrique la vérité, sort du banc d'affichage")
    if not fiche["traverse_binance"]:
        return Verdict("É1", False, None, "éliminée", "ne traverse pas vers Binance")
    if not fiche["navigateur"] and not fiche.get("version_simplifiee_demontree", False):
        return Verdict("É1", False, None, "éliminée",
                       "ne tourne pas dans un navigateur, sans version simplifiée démontrée")
    # « survit à la dégradation » n'est pas une porte : elle EXIGE une mesure
    # avant É4 — portée au détail, jamais éliminatoire ici.
    return Verdict("É1", True, None, "É2",
                   "admissible" + ("" if fiche.get("degradation_mesuree")
                                   else " — mesure de dégradation due avant É4"))


# --- É2 — redite contre le bloc retenu (témoin inclus dès le départ) ---------

def e2(candidat: np.ndarray, bloc_retenu: dict[str, np.ndarray]) -> Verdict:
    if not bloc_retenu:
        raise RefusEpreuve("bloc de référence vide — le témoin trivial doit y "
                           "être dès le départ (`05` §4, correction I.7)")
    for nom, serie in bloc_retenu.items():
        if len(serie) != len(candidat):
            raise RefusEpreuve(
                f"É2 refusée : longueurs incompatibles — candidat "
                f"{len(candidat)} obs contre {nom} {len(serie)} (périmètres "
                f"différents, audit F1). Le bloc doit être extrait sur LE "
                f"périmètre du candidat.")
    pire, pire_nom = 0.0, ""
    for nom, serie in bloc_retenu.items():
        rho = abs(spearman(candidat, serie))
        if rho > pire:
            pire, pire_nom = rho, nom
    if pire >= SEUIL_E2_DOUBLON_PRESUME:
        return Verdict("É2", True, pire, "doublon présumé",
                       f"|ρ|={pire:.3f} ≥ 0,70 contre {pire_nom} — ne survit "
                       f"qu'en passant É4 avec un apport significatif")
    if pire >= SEUIL_E2_SURVEILLANCE:
        return Verdict("É2", True, pire, "sous surveillance",
                       f"|ρ|={pire:.3f} dans [0,50 ; 0,70) contre {pire_nom}")
    return Verdict("É2", True, pire, "É3", f"|ρ| max = {pire:.3f} < 0,50")


# --- la garde de bande É0 (post-scriptum du 06/08 au rapport du 1er tour) ----
# « Une règle en prose n'arrête personne » : la promesse de N2 (« si des
# paires siègent dans [0,70 ; 0,90), traitement par ADR avant É4 ») devient
# du code qui lève. Sans elle, BH compterait deux quasi-jumeaux à 0,85 comme
# deux tests indépendants — seuils trop laxistes, et rien ne le remarquerait.

#: Peuplé UNIQUEMENT par une ADR acceptée — chaque entrée cite son ADR en
#: commentaire. Vide tant qu'aucune paire de la bande n'a été arbitrée.
PAIRES_SOUS_ADR: set[frozenset[str]] = set()


def verifie_bande_e0(paires: list[tuple[str, str, float]]) -> None:
    """REFUSE É4 tant qu'une paire intra-périmètre siège dans
    [0,70 ; 0,90) — sous la barre de fusion d'É0, au-dessus du doublon
    présumé d'É2 — sans ADR déclarée dans PAIRES_SOUS_ADR."""
    cassees = [(a, b) for a, b, r in paires if not np.isfinite(r)]
    if cassees:
        raise RefusEpreuve(
            f"É4 refusée : {len(cassees)} paire(s) intra-périmètre à "
            f"l'alignement défaillant (|ρ| incalculable, longueurs inégales "
            f"à périmètre égal) : "
            + " ; ".join(f"({a}, {b})" for a, b in cassees)
            + " — une ADR n'exempte pas un défaut d'instrument.")
    bloquantes = [(a, b, r) for a, b, r in paires
                  if SEUIL_E2_DOUBLON_PRESUME <= r < SEUIL_E0_DOUBLON
                  and frozenset((a, b)) not in PAIRES_SOUS_ADR]
    if bloquantes:
        detail = " ; ".join(f"|ρ|({a}, {b})={r:.3f}" for a, b, r in bloquantes)
        raise RefusEpreuve(
            f"É4 refusée : {len(bloquantes)} paire(s) intra-périmètre dans "
            f"[0,70 ; 0,90) sans ADR — la multiplicité de BH serait fausse "
            f"(`05` : « quarante synonymes ne sont pas soixante tests »). "
            f"{detail}")


# --- É3 / É4 — refus tant que les préalables manquent ------------------------

def e3(*_args, **_kw) -> Verdict:
    raise RefusEpreuve(
        "É3 refusée : (1) le rejeu événementiel n'existe pas (`05` §9.1) ; "
        "(2) l'échelle la plus fine est contestée — ADR D12 requise avant le "
        "premier passage (audit I.9). Rien ici ne code 100 ms en dur.")


def e4_refus() -> None:
    raise RefusEpreuve(
        "É4 refusée : (1) la cible n'a pas de définition opératoire — C3 non "
        "gelé (`ADR-001`) ; (2) la fraction de paires intra-unité n'a jamais "
        "été mesurée (`05` §9.4) — sans elle l'IC ne vaut rien.")


def e4(candidat_par_jour: list[np.ndarray], cible_par_jour: list[np.ndarray],
       bloc_par_jour: list[np.ndarray] | None, *, prealables_leves: bool = False) -> dict:
    """La mécanique d'É4 (`ADR-001`) — exécutable sur SYNTHÉTIQUE (ÉS) où la
    vérité tient lieu de cible. Sur données réelles : refus tant que
    `prealables_leves` n'est pas démontré par le préflight.

    Rend le coefficient partiel par jour + Student (p décide via BH, IC publié).
    """
    if not prealables_leves:
        e4_refus()
    coefs = []
    for i, (x, y) in enumerate(zip(candidat_par_jour, cible_par_jour)):
        bloc = None if bloc_par_jour is None else bloc_par_jour[i]
        # Plancher d'observations, `05` §4 (ajouté le 05/08/2026 sur mesure
        # d'ÉS) : l'estimateur partiel dérive en ~k/n — à 300 obs pour 20
        # contrôles, +0,15 de biais. On refuse, on n'avertit pas.
        if bloc is not None:
            b = np.atleast_2d(np.asarray(bloc))
            k = b.shape[1] if b.shape[0] == len(x) else b.shape[0]
            if len(x) < 100 * max(k, 1):
                raise RefusEpreuve(
                    f"É4 refusée : jour {i} porte {len(x)} observations pour "
                    f"un bloc de {k} contrôles — le plancher d'`05` §4 exige "
                    f"n ≥ {100 * k} (dérive k/n mesurée à ÉS).")
        coefs.append(spearman_partiel(x, y, bloc))
    return {"coefs_jour": coefs, **student_jours(np.array(coefs))}
