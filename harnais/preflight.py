"""P0 — le préflight. EN TÊTE des quatre pièces (audit I.5, `06` corrigé).

Il ne prévient pas, il bloque : chaque contrôle lève `PreflightError`. La seule
construction jamais lancée l'a été avec `sale=True`, consigné et non bloqué —
ce module existe pour que ça ne se reproduise pas.

Chaque contrôle est une fonction PURE sur ses entrées, pour que la suite de
tests prouve qu'il PEUT échouer sans avoir à salir le vrai dépôt. `run()` les
câble sur le dépôt réel.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

DEPOT = Path(__file__).resolve().parent.parent

#: `decisions/ADR-000` : 17-23 = RÉSERVE, jamais construite ni regardée ;
#: 08 = banc d'instrument ; 09-16 = exploration (tranche 1).
RESERVE = {f"202512{d}" for d in range(17, 24)}
EXPLORATION = {f"202512{d:02d}" for d in range(9, 17)}

#: Chemins de sortie déclarés — s'écrivent PENDANT un run, exclus du contrôle
#: d'arbre propre, sinon le préflight s'interbloque (audit I.5).
SORTIES_DECLAREES = ("journal/construction/", "journal/registre-des-grandeurs.md",
                    "journal/c5/", "chantiers/c5_",   # C5 écrit à côté de sa recette (ETAT §3)
                    "journal/es-campagne-",           # la campagne ÉS écrit son log et son JSON
                    "journal/c8-3-")                  # C8.3 écrit le sien pendant sa mesure

PROTOCOLES = ("05_Protocole_de_selection.md", "03_EconoPhysique.md",
              "decisions/ADR-001-la-metrique-de-E4.md")


class PreflightError(RuntimeError):
    """Refus de démarrer. Le message dit quoi et pourquoi — jamais silencieux."""


# --- les contrôles, purs -----------------------------------------------------

def check_arbre_propre(porcelain: list[str],
                       exclus: tuple[str, ...] = SORTIES_DECLAREES) -> None:
    """`porcelain` : lignes de `git status --porcelain`."""
    sales = []
    for ligne in porcelain:
        if not ligne.strip():
            continue
        chemin = ligne[3:].strip().strip('"').replace("\\", "/")
        if not any(chemin.startswith(e) for e in exclus):
            sales.append(chemin)
    if sales:
        raise PreflightError(
            f"REFUS : arbre git sale hors chemins de sortie déclarés — "
            f"{sales[:5]}{' …' if len(sales) > 5 else ''}. Commiter avant de mesurer.")


def check_protocoles_commites(porcelain: list[str]) -> None:
    """Les documents qui font foi ne doivent porter aucune modification locale."""
    for ligne in porcelain:
        chemin = ligne[3:].strip().strip('"').replace("\\", "/")
        if chemin in PROTOCOLES:
            raise PreflightError(
                f"REFUS : {chemin} est modifié et non commité — le banc jugerait "
                f"contre un protocole que git ne connaît pas.")


def check_perimetre(jours: list[str]) -> None:
    for j in jours:
        if j in RESERVE:
            raise PreflightError(
                f"REFUS : {j} est dans la RÉSERVE (17-23, ADR-000) — elle ne se "
                f"construit pas, ne se regarde pas, ne se consomme pas.")
        if j not in EXPLORATION:
            raise PreflightError(
                f"REFUS : {j} n'est pas un jour d'exploration (09-16). Le banc ne "
                f"tourne que sur l'exploration de la tranche 1.")


def check_manifestes(manifestes: list[dict], chemins: list[str] | None = None) -> None:
    """Provenance certifiée ET génération homogène sur tout le périmètre.

    Deux générations de manifestes coexistent : l'ancienne porte un drapeau
    `provenance_certifiee` (les mesures de la nuit du 04→05/08 reposaient sur
    des `false` — plus jamais sans refus) ; la nouvelle (`schema_manifeste` ≥ 1,
    écrite par `empreinte.py` à la fabrication) EST la certification — sha256
    de l'artefact, commit du code, paramètres. On exige l'une ou l'autre.
    """
    noms = chemins or [f"manifeste[{i}]" for i in range(len(manifestes))]
    if not manifestes:
        raise PreflightError("REFUS : aucun manifeste sur le périmètre — "
                             "une donnée sans manifeste n'a pas de provenance.")
    for m, nom in zip(manifestes, noms):
        nouveau = (m.get("schema_manifeste", 0) >= 1
                   and bool(m.get("artefact", {}).get("sha256"))
                   and "parametres" in m)
        if not nouveau and not m.get("provenance_certifiee", False):
            raise PreflightError(
                f"REFUS : {nom} n'est certifié par aucune génération — ni "
                f"drapeau provenance_certifiee, ni manifeste de fabrication "
                f"(sha256 + paramètres).")
    params = [json.dumps(m.get("parametres", {}), sort_keys=True) for m in manifestes]
    if len(set(params)) > 1:
        raise PreflightError(
            "REFUS : deux générations coexistent sur le périmètre (paramètres de "
            "manifeste hétérogènes) — un mélange est inexploitable.")


def check_fichiers_obligatoires(registre_texte: str, fiche_presente: bool) -> None:
    if "à remplir avant le premier calcul" in registre_texte:
        raise PreflightError(
            "REFUS : le nombre de candidats n'est pas déclaré au registre — "
            "première protection contre la multiplicité (`05` §4).")
    if "| témoin trivial |" not in registre_texte.replace("`", ""):
        raise PreflightError(
            "REFUS : le témoin trivial n'a pas sa ligne au registre — le premier "
            "candidat serait jugé contre le vide (`05` §4).")
    if not fiche_presente:
        raise PreflightError("REFUS : pas de fiche, pas de test (`05` §1).")


def check_gardefous_peuvent_lever() -> None:
    """Un garde-fou dont on n'a pas prouvé qu'il peut échouer est décoratif —
    le préflight le prouve à CHAQUE run, pas seulement dans la suite de tests."""
    import numpy as np

    from harnais.gardefous import GardeFouViole, cible_binaire, evenement_rare
    try:
        evenement_rare(np.ones(100, dtype=bool))
    except GardeFouViole:
        pass
    else:
        raise PreflightError("REFUS : evenement_rare n'a pas levé sur 100 % — "
                             "le garde-fou est décoratif.")
    try:
        cible_binaire(np.zeros(300))
    except GardeFouViole:
        pass
    else:
        raise PreflightError("REFUS : cible_binaire n'a pas levé sur une classe "
                             "unique — le garde-fou est décoratif.")


# --- le câblage sur le dépôt réel -------------------------------------------

def _git(depot: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(depot), *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise PreflightError(f"REFUS : git {' '.join(args)} a échoué — {r.stderr.strip()}")
    return r.stdout


def run(jours: list[str], fiche_presente: bool = True,
        manifestes: list[dict] | None = None,
        chemins_manifestes: list[str] | None = None,
        depot: Path = DEPOT) -> dict:
    """Tous les contrôles, dans l'ordre. Rend le hash du protocole à inscrire
    dans chaque ligne de registre du run."""
    porcelain = _git(depot, "status", "--porcelain").splitlines()
    check_arbre_propre(porcelain)
    check_protocoles_commites(porcelain)
    check_perimetre(jours)
    if manifestes is not None:
        check_manifestes(manifestes, chemins_manifestes)
    registre = (depot / "journal" / "registre-des-grandeurs.md").read_text(encoding="utf-8")
    check_fichiers_obligatoires(registre, fiche_presente)
    check_gardefous_peuvent_lever()
    return {"protocole_hash": _git(depot, "rev-parse", "--short", "HEAD").strip()}
