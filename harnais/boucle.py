"""La boucle — la sortie de C9 (`06` §C9) : prend une fiche, la passe par les
épreuves dans l'ordre d'`05` §4, écrit son verdict et son chiffre au registre,
et enchaîne — jusqu'à épuisement ou refus.

Ce qu'elle ne fait JAMAIS : deviner. Une épreuve dont un préalable manque
(données du périmètre, C3, D12, plancher k/n) lève `RefusEpreuve` et le
candidat reste où il est, avec la raison rapportée. Le harnais refuse, il ne
simule pas.

ÉS n'apparaît pas ici : elle juge des MÉTHODES, pas des candidats (D8), et
celle du banc est passée le 05/08/2026 — ses planchers sont au registre.

États écrits (vocabulaire du registre, D7) : au dépôt, `déposée`. Au passage
d'une épreuve, l'état est **l'épreuve suivante** et la colonne épreuve porte
celle qui vient d'être franchie, avec son chiffre. Une chute écrit `éliminée`
ou `réorientée` avec sa raison.
"""
from __future__ import annotations

import datetime as _dt
from pathlib import Path

import numpy as np

from harnais import registre
from harnais.epreuves import (SEUIL_E0_DOUBLON, RefusEpreuve, e1, e2, e3, e4)
from harnais.fiches import FICHES, TEMOIN
from harnais.stats import spearman

ORDRE = ("É0", "É1", "É2", "É3", "É4")


def _aujourdhui() -> str:
    return _dt.date.today().isoformat()


def etat_courant(nom: str, chemin: Path = registre.CHEMIN) -> str | None:
    """Le dernier état du candidat au registre, None s'il n'y est pas."""
    etat = None
    for ligne in registre.lire(chemin):
        if ligne["nom"] == nom:
            etat = ligne["etat"]
    return etat


def depose_manquants(chemin: Path = registre.CHEMIN) -> list[str]:
    """Chaque candidat déclaré sans ligne au registre y entre en `déposée`."""
    deposes = []
    for nom, f in FICHES.items():
        if etat_courant(nom, chemin) is None:
            registre.ajouter(_aujourdhui(), nom, "déposée", "—", "—",
                             f["perimetre"], "03 partie I (dépôt par la boucle)",
                             chemin)
            deposes.append(nom)
    return deposes


def _avance_un(nom: str, series: dict[str, "np.ndarray"] | None,
               bloc: dict[str, "np.ndarray"] | None,
               chemin: Path, signataire: str = "la boucle") -> tuple[str, str]:
    """Avance UN candidat tant que l'épreuve suivante est exécutable.
    Rend (état final, raison d'arrêt)."""
    f = FICHES[nom]
    while True:
        etat = etat_courant(nom, chemin)
        if etat in ("éliminée", "réorientée", "retenue",
                    "sous surveillance", "doublon présumé"):
            return etat, "état terminal ou en attente d'É4"
        epreuve = "É0" if etat == "déposée" else etat
        if epreuve == "É0":
            if not series or nom not in series:
                return etat, ("en attente des données du périmètre "
                              f"{f['perimetre']} (construction en cours)")
            # `05` §4 : « ils sont le même objet. On garde LE MOINS CHER ;
            # l'autre est éliminé avec son chiffre. » Le perdant n'est donc
            # pas forcément le candidat testé — et les éliminés sortent du
            # jeu de comparaison, sinon un doublon fauche les deux jumeaux
            # (bug attrapé par le test d'intégration le 05/08).
            # Égalité de coût : l'ordre de déclaration de `03` tranche.
            ordre_decl = list(FICHES)
            tombe = False
            for autre in ordre_decl:
                if (autre == nom or autre not in series
                        or etat_courant(autre, chemin) in ("éliminée", "réorientée")):
                    continue
                # É0 compare INTRA-PÉRIMÈTRE seulement (audit F1) : deux
                # périmètres différents n'ont pas le même index — corréler
                # J3 à J8 serait un non-sens et un crash. La déduplication
                # inter-périmètres, si un jour nécessaire, passera par ADR
                # (intersection des jours) — pas par un accident d'index.
                if FICHES[autre]["perimetre"] != f["perimetre"]:
                    continue
                if len(series[nom]) != len(series[autre]):
                    raise RefusEpreuve(
                        f"É0 : longueurs incompatibles à périmètre égal — "
                        f"{nom} {len(series[nom])} contre {autre} "
                        f"{len(series[autre])} : alignement défaillant en amont")
                rho = spearman(series[nom], series[autre])
                if not np.isfinite(rho):
                    raise RefusEpreuve(
                        f"É0 : ρ non fini contre {autre} — un NaN ne décide "
                        f"pas, il refuse (audit F2)")
                if abs(rho) < SEUIL_E0_DOUBLON:
                    continue
                moi = (f["cout_rang"], ordre_decl.index(nom))
                lui = (FICHES[autre]["cout_rang"], ordre_decl.index(autre))
                perdant, gagnant = (nom, autre) if moi > lui else (autre, nom)
                registre.ajouter(_aujourdhui(), perdant, "éliminée", "É0",
                                 f"ρ={abs(rho):.3f} — même objet que {gagnant}, "
                                 f"on garde le moins cher", f["perimetre"],
                                 signataire, chemin)
                if perdant == nom:
                    tombe = True
                    break
            if tombe:
                return "éliminée", "doublon interne (É0)"
            registre.ajouter(_aujourdhui(), nom, "É1", "É0", "aucun doublon "
                             "parmi les vivants", f["perimetre"], signataire,
                             chemin)
        elif epreuve == "É1":
            v = e1(f["e1"])
            registre.ajouter(_aujourdhui(), nom, v.etat_suivant, "É1",
                             v.detail or "—", f["perimetre"], signataire, chemin)
            if not v.passe:
                return v.etat_suivant, v.detail
        elif epreuve == "É2":
            if not series or nom not in series or not bloc:
                return etat, ("É2 en attente : données du périmètre et bloc "
                              "de référence (témoin T0 compris)")
            v = e2(series[nom], bloc)
            registre.ajouter(_aujourdhui(), nom, v.etat_suivant, "É2",
                             f"ρmax={v.chiffre:.3f}", f["perimetre"],
                             signataire, chemin)
            if v.etat_suivant != "É3":
                return v.etat_suivant, v.detail
        elif epreuve == "É3":
            e3()   # lève toujours à ce jour : rejeu absent, D12 ouverte
        elif epreuve == "É4":
            e4([], [], None)   # lève : C3 non gelé, paires intra-unité
        else:
            return etat or "?", f"état inattendu : {etat!r}"


def tour(series: dict | None = None, bloc: dict | None = None,
         chemin: Path = registre.CHEMIN,
         hash_protocole: str | None = None) -> dict[str, tuple[str, str]]:
    """Un tour de banc : dépose les manquants puis avance chaque candidat
    aussi loin que les préalables le permettent. Rend {nom: (état, raison)}."""
    # le hash du protocole signe CHAQUE ligne du run (audit F5 — il etait
    # promis par le preflight et jete par tous les appelants)
    signataire = f"la boucle @{hash_protocole}" if hash_protocole else "la boucle"
    # VALIDATION A L'ENTREE (audit F2) : une serie polluee (NaN/inf) ne
    # decide de rien — son candidat est REFUSE avec sa raison, les autres
    # tournent sans elle. Jamais un crash de tour, jamais un rho=nan ecrit.
    pollues = {}
    if series:
        for n in list(series):
            if not np.isfinite(series[n]).all():
                pollues[n] = ("REFUS : série polluée (NaN/inf) — corriger "
                              "l'extraction ou l'alignement en amont")
                series = {k: v for k, v in series.items() if k != n}
    if bloc:
        for n, x in bloc.items():
            if not np.isfinite(x).all():
                raise RefusEpreuve(f"bloc de référence pollué (NaN/inf) : {n}")
    depose_manquants(chemin)
    rapport = {}
    for nom in FICHES:
        if nom in pollues:
            rapport[nom] = (etat_courant(nom, chemin) or "?", pollues[nom])
            continue
        try:
            rapport[nom] = _avance_un(nom, series, bloc, chemin, signataire)
        except RefusEpreuve as e:
            rapport[nom] = (etat_courant(nom, chemin) or "?", f"REFUS : {e}")
    return rapport


if __name__ == "__main__":
    from harnais.preflight import run as preflight
    pf = preflight([])
    print(f"préflight : {pf}")
    for nom, (etat, raison) in tour().items():
        print(f"  {nom:38} {etat:16} {raison}")
