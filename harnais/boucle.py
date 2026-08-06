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
from harnais.epreuves import (RefusEpreuve, e0_duel, e1, e2, e3, e4,
                              verifie_bande_e0)
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


def _paires_bande(series: dict[str, "np.ndarray"] | None
                  ) -> list[tuple[str, str, float]]:
    """Toutes les paires intra-périmètre avec leur |ρ| — le matériau de la
    garde de bande d'É4 (post-scriptum du 06/08). Calculé une fois par tour."""
    if not series:
        return []
    vivants = [n for n in series if n in FICHES]
    paires = []
    for i, a in enumerate(vivants):
        for b in vivants[i + 1:]:
            if FICHES[a]["perimetre"] != FICHES[b]["perimetre"]:
                continue
            if len(series[a]) != len(series[b]):
                # le MÊME défaut qu'É0 nomme « alignement défaillant en
                # amont » : la garde ne le tait pas, elle le porte — un
                # |ρ| incalculable BLOQUE É4 (une paire suspecte est ce
                # que la garde doit voir en premier, pas perdre de vue)
                paires.append((a, b, float("nan")))
                continue
            paires.append((a, b, abs(spearman(series[a], series[b]))))
    return paires


def _avance_un(nom: str, series: dict[str, "np.ndarray"] | None,
               bloc: dict[str, "np.ndarray"] | None,
               chemin: Path, signataire: str = "la boucle",
               bloc_par_perimetre: dict[str, dict] | None = None,
               paires_bande: list[tuple[str, str, float]] | None = None
               ) -> tuple[str, str]:
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
            rho_max, plus_proche = 0.0, None
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
                if abs(rho) > rho_max:
                    rho_max, plus_proche = abs(rho), autre
                # la décision est UNE fonction, testée : epreuves.e0_duel
                duel = e0_duel(rho, f["cout_rang"], FICHES[autre]["cout_rang"],
                               ordre_decl.index(nom), ordre_decl.index(autre))
                if duel is None:
                    continue
                perdant, gagnant = ((nom, autre) if duel == "a"
                                    else (autre, nom))
                registre.ajouter(_aujourdhui(), perdant, "éliminée", "É0",
                                 f"ρ={abs(rho):.3f} — même objet que {gagnant}, "
                                 f"on garde le moins cher", f["perimetre"],
                                 signataire, chemin)
                if perdant == nom:
                    tombe = True
                    break
            if tombe:
                return "éliminée", "doublon interne (É0)"
            # note du 06/08 au rapport (N1) : la ligne de passage porte SON
            # nombre — le ρ le plus haut rencontré et contre qui — plus
            # jamais un « aucun doublon » nu dont le fondement a été jeté
            registre.ajouter(_aujourdhui(), nom, "É1", "É0",
                             (f"ρmax={rho_max:.3f} contre {plus_proche}"
                              if plus_proche else "seul dans son périmètre"),
                             f["perimetre"], signataire, chemin)
        elif epreuve == "É1":
            v = e1(f["e1"])
            registre.ajouter(_aujourdhui(), nom, v.etat_suivant, "É1",
                             v.detail or "—", f["perimetre"], signataire, chemin)
            if not v.passe:
                return v.etat_suivant, v.detail
        elif epreuve == "É2":
            # le témoin doit vivre sur LE périmètre du candidat (dette T0-J8,
            # fermée le 06/08) : bloc par périmètre s'il est fourni
            if bloc_par_perimetre is not None:
                bloc = bloc_par_perimetre.get(f["perimetre"])
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
            # lève tant que rejeu absent + D12 ouverte. Le jour où É3 rend
            # un verdict, la machine ÉCRIT l'état suivant — sans cette
            # écriture, "É4" était un état inatteignable et la garde de
            # bande du dessous du code mort (2e post-scriptum du 06/08 :
            # un garde-fou doit pouvoir échouer, ÊTRE APPELÉ, et être
            # vérifié capable d'échouer — `00` §8, les trois conditions)
            v = e3()
            # la colonne chiffre reçoit LE NOMBRE d'É3 (concordance de rang
            # entre résolutions, barre 0,60) — jamais v.detail : « aucune
            # décision sur une opinion » (registre). La même correction
            # qu'É0 deux tours plus tôt, attrapée par Meddy le 06/08.
            if v.chiffre is None:
                raise RefusEpreuve(
                    "É3 a rendu un verdict sans chiffre — le registre "
                    "n'accepte pas une opinion en colonne chiffre, "
                    "l'implémentation d'É3 doit porter son nombre")
            registre.ajouter(_aujourdhui(), nom, v.etat_suivant, "É3",
                             f"rang={v.chiffre:.3f}", f["perimetre"],
                             signataire, chemin)
            if not v.passe:
                return v.etat_suivant, v.detail
        elif epreuve == "É4":
            # la garde de bande AVANT le refus C3 : placée après, elle
            # serait du code mort tant que C3 bloque — une garde qui ne
            # peut pas tirer est décorative
            verifie_bande_e0(paires_bande or [])
            e4([], [], None)   # lève : C3 non gelé, paires intra-unité
        else:
            return etat or "?", f"état inattendu : {etat!r}"


def tour(series: dict | None = None, bloc: dict | None = None,
         chemin: Path = registre.CHEMIN,
         hash_protocole: str | None = None,
         bloc_par_perimetre: dict[str, dict] | None = None
         ) -> dict[str, tuple[str, str]]:
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
    for b in ([bloc] if bloc else []) + list((bloc_par_perimetre or {}).values()):
        for n, x in b.items():
            if not np.isfinite(x).all():
                raise RefusEpreuve(f"bloc de référence pollué (NaN/inf) : {n}")
    depose_manquants(chemin)
    paires_bande = _paires_bande(series)
    rapport = {}
    for nom in FICHES:
        if nom in pollues:
            rapport[nom] = (etat_courant(nom, chemin) or "?", pollues[nom])
            continue
        try:
            rapport[nom] = _avance_un(nom, series, bloc, chemin, signataire,
                                      bloc_par_perimetre, paires_bande)
        except RefusEpreuve as e:
            rapport[nom] = (etat_courant(nom, chemin) or "?", f"REFUS : {e}")
    return rapport


if __name__ == "__main__":
    from harnais.preflight import run as preflight
    pf = preflight([])
    print(f"préflight : {pf}")
    for nom, (etat, raison) in tour().items():
        print(f"  {nom:38} {etat:16} {raison}")
