"""P2 — l'interface du registre. Le fichier existe, ce module écrit dedans.

`journal/registre-des-grandeurs.md` est un RAPPORT DE MESURE : il ne se
réécrit jamais. Ce module ne sait faire qu'une chose — AJOUTER une ligne à la
table — et il refuse tout le reste : une élimination sans chiffre, un état
hors vocabulaire, une ligne au mauvais format.
"""
from __future__ import annotations

import re
from pathlib import Path

CHEMIN = Path(__file__).resolve().parent.parent / "journal" / "registre-des-grandeurs.md"

#: Le vocabulaire du registre — TRANSCRIT du fichier (décision D7), qui fait foi.
ETATS = {"déposée", "ÉS", "É0", "É1", "É2", "É3", "É4",
         "sous surveillance", "doublon présumé", "réorientée",
         "éliminée", "retenue", "témoin trivial"}

ETATS_EXIGEANT_CHIFFRE = {"éliminée", "sous surveillance", "doublon présumé", "retenue"}


class RegistreRefus(RuntimeError):
    pass


def lire(chemin: Path = CHEMIN) -> list[dict]:
    """Les lignes de la table, dans l'ordre du fichier."""
    lignes = []
    dans_table = False
    for l in chemin.read_text(encoding="utf-8").splitlines():
        if l.startswith("| date | nom |"):
            dans_table = True
            continue
        if dans_table:
            if not l.startswith("|"):
                dans_table = False
                continue
            cells = [c.strip() for c in l.strip("|").split("|")]
            if len(cells) == 7 and not set(cells[0]) <= {"-", " "}:
                lignes.append(dict(zip(
                    ("date", "nom", "etat", "epreuve", "chiffre",
                     "perimetre", "proposee_par"), cells)))
    return lignes


def ajouter(date: str, nom: str, etat: str, epreuve: str, chiffre: str,
            perimetre: str, proposee_par: str, chemin: Path = CHEMIN) -> None:
    """Ajoute UNE ligne en fin de table. C'est la seule écriture permise."""
    if etat not in ETATS:
        raise RegistreRefus(f"état inconnu : {etat!r} — le vocabulaire du "
                            f"registre fait foi (D7) : {sorted(ETATS)}")
    if etat in ETATS_EXIGEANT_CHIFFRE and chiffre.strip() in ("", "—", "-"):
        raise RegistreRefus(
            f"REFUS : passage à l'état {etat!r} sans chiffre — aucune décision "
            f"sur une opinion (`05` §5).")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise RegistreRefus(f"date au format AAAA-MM-JJ attendue, reçu {date!r}")
    for champ in (nom, etat, epreuve, chiffre, perimetre, proposee_par):
        if "|" in champ or "\n" in champ:
            raise RegistreRefus(f"champ illégal (pipe ou retour ligne) : {champ!r}")

    texte = chemin.read_text(encoding="utf-8")
    # Dernière ligne de la table du registre : on insère APRÈS elle — jamais de
    # réécriture d'une ligne existante, c'est structurellement impossible ici.
    lignes = texte.splitlines(keepends=True)
    idx_table = max(i for i, l in enumerate(lignes) if l.startswith("| date | nom |"))
    fin = idx_table + 1
    while fin < len(lignes) and lignes[fin].startswith("|"):
        fin += 1
    nouvelle = (f"| {date} | {nom} | {etat} | {epreuve} | {chiffre} "
                f"| {perimetre} | {proposee_par} |\n")
    lignes.insert(fin, nouvelle)
    # ÉCRITURE ATOMIQUE (audit du 06/08) : un kill au milieu d'un write_text
    # tronquerait le grand livre append-only — la seule chose du projet qui
    # ne doit jamais se corrompre était protégée par moins que `fusionne`.
    # tmp + os.replace : le fichier final est entier ou inchangé, jamais
    # entre les deux.
    import os
    tmp = chemin.with_suffix(".encours")
    tmp.write_text("".join(lignes), encoding="utf-8")
    os.replace(tmp, chemin)
