"""La boucle de bout en bout — sur registre temporaire et séries synthétiques.
Le vrai registre n'est jamais touché par un test."""
import shutil

import numpy as np
import pytest

from harnais.boucle import depose_manquants, etat_courant, tour
from harnais.fiches import FICHES, TEMOIN
from harnais.registre import CHEMIN, lire


@pytest.fixture
def reg(tmp_path):
    c = tmp_path / "registre.md"
    shutil.copy(CHEMIN, c)
    return c


@pytest.fixture
def reg_vierge(tmp_path):
    """Un registre neuf : le VRAI registre porte désormais le premier tour
    réel (les candidats y sont à É3) — les tests de machine complète partent
    d'un état vierge, pas d'une copie du réel qui évolue."""
    c = tmp_path / "registre_vierge.md"
    lignes = [
        "# Registre (test)",
        "",
        "| date | nom | état | épreuve | chiffre | périmètre | proposée par |",
        "|---|---|---|---|---|---|---|",
        "| 2026-08-05 | T0 · masse brute au palier | témoin trivial | — | — "
        "| J3 | protocole |",
        "",
    ]
    c.write_text("\n".join(lignes), encoding="utf-8")
    return c


def test_depot_complete_et_idempotent(reg):
    # le vrai registre peut déjà porter des candidats (le banc est ouvert
    # depuis le 05/08) : on teste la complétude et l'idempotence, pas un
    # état daté du fichier copié
    manquaient = [n for n in FICHES if etat_courant(n, reg) is None]
    deposes = depose_manquants(reg)
    assert deposes == manquaient
    assert all(etat_courant(n, reg) is not None for n in FICHES)
    n_lignes = len(lire(reg))
    assert depose_manquants(reg) == []   # idempotent
    assert len(lire(reg)) == n_lignes    # et sans écriture fantôme


def test_sans_donnees_tout_le_monde_attend_E0(reg_vierge):
    rapport = tour(series=None, chemin=reg_vierge)
    assert len(rapport) == 16
    for nom, (etat, raison) in rapport.items():
        assert etat == "déposée"
        assert "attente des données" in raison


def test_banc_complet_sur_series_synthetiques(reg_vierge):
    reg = reg_vierge
    rng = np.random.default_rng(0)
    base = rng.normal(size=3000)
    series = {}
    for i, nom in enumerate(FICHES):
        series[nom] = rng.normal(size=3000)
    # un doublon fabriqué : A2 recopie A1 à un cheveu — É0 doit fondre
    series["A2 · OFI localisé au mur"] = (
        series["A1 · OFI"] + 0.01 * rng.normal(size=3000))
    # un candidat qui redit le témoin : corrélé ~0,9 à T0 — É2 doit le marquer
    t0 = base
    series["C1 · concentration"] = 0.9 * t0 + np.sqrt(1 - 0.81) * rng.normal(size=3000)
    bloc = {TEMOIN: t0}

    rapport = tour(series=series, bloc=bloc, chemin=reg)

    # le doublon : un des deux (A1/A2) est éliminé à É0, l'autre continue
    etats = {n: rapport[n][0] for n in rapport}
    paire = {etats["A1 · OFI"], etats["A2 · OFI localisé au mur"]}
    assert "éliminée" in paire and paire != {"éliminée"}
    # A6 tombe à É1 (ne traverse pas), comme sa fiche le déclare
    assert etats["A6 · auto-excitation (Hawkes)"] == "éliminée"
    # la redite du témoin est marquée par É2
    assert etats["C1 · concentration"] == "doublon présumé"
    # les survivants butent sur É3, avec la raison D12/rejeu — le refus, pas un verdict
    survivants = [n for n, (e, _) in rapport.items() if e == "É3"]
    assert survivants, rapport
    assert all("REFUS" in rapport[n][1] for n in survivants)
    # et chaque chute au registre porte quelque chose dans sa colonne chiffre
    for l in lire(reg):
        if l["etat"] in ("éliminée", "doublon présumé", "sous surveillance"):
            assert l["chiffre"] not in ("", "—", "-")


def test_garde_bande_atteinte_et_avant_le_refus_C3(reg_vierge, monkeypatch):
    """`00` §8, les trois conditions : la garde de bande peut échouer (ses
    tests unitaires), est vérifiée capable d'échouer (idem) — ici on prouve
    la troisième : elle est APPELÉE. Avant le 2e post-scriptum du 06/08,
    aucun `registre.ajouter` n'écrivait "É4" : la branche était
    inatteignable et la garde du code mort. On stubbe É3 (rejeu fictif de
    test) pour conduire les candidats jusqu'à la branche É4, et on vérifie
    l'ordre : la garde lève AVANT le refus C3 d'e4 — l'ordre n'est plus un
    commentaire, il est vérifié."""
    from harnais import boucle as B
    from harnais.epreuves import Verdict
    monkeypatch.setattr(B, "e3", lambda *a, **k: Verdict(
        "É3", True, 0.99, "É4", "stub de test : rejeu fictif"))
    a1, a4 = "A1 · OFI", "A4 · microprice"

    def jeu(avec_bande: bool, graine: int, chemin):
        rng = np.random.default_rng(graine)
        series = {n: rng.normal(size=3000) for n in FICHES}
        if avec_bande:   # ρ de Spearman ~0,86 : dans [0,70 ; 0,90)
            series[a4] = (0.87 * series[a1]
                          + np.sqrt(1 - 0.87 ** 2) * rng.normal(size=3000))
        return tour(series=series, bloc={TEMOIN: rng.normal(size=3000)},
                    chemin=chemin)

    # 1) une paire dans la bande : c'est la GARDE qui refuse É4, pas C3
    rapport = jeu(True, 11, reg_vierge)
    etat, raison = rapport[a1]
    assert etat == "É4" and "0,70 ; 0,90" in raison and "C3" not in raison
    # et la ligne d'É3 au registre porte SON NOMBRE, jamais du texte
    # (« aucune décision sur une opinion » — correction du 06/08, la même
    # qu'É0 deux tours plus tôt)
    lignes_e3 = [l for l in lire(reg_vierge) if l["epreuve"] == "É3"]
    assert lignes_e3
    assert all(l["chiffre"] == "rang=0.990" for l in lignes_e3)
    # 2) sans paire en bande : la garde se tait, e4 refuse sur C3 —
    #    la garde est donc bien passée en premier
    reg2 = reg_vierge.parent / "registre_vierge_2.md"
    shutil.copy(reg_vierge, reg2)   # copie AVANT usage : reg_vierge a évolué
    # (on repart d'un registre neuf, pas de celui où tout le monde est à É4)
    reg2.write_text(reg_vierge.read_text(encoding="utf-8").split("| 2026")[0]
                    + "| 2026-08-05 | T0 · masse brute au palier | témoin "
                    "trivial | — | — | J3 | protocole |\n", encoding="utf-8")
    rapport2 = jeu(False, 12, reg2)
    etat2, raison2 = rapport2[a1]
    assert etat2 == "É4" and "REFUS" in raison2 and "C3 non gelé" in raison2


def test_bh_refuse_la_vague_partielle(reg_vierge, monkeypatch):
    """`05` §multiplicité, protection 1 : le compte est déclaré AVANT. Si
    seuls les J3 sont mesurables, BH ne tourne PAS sur eux — deux familles
    de 8 à q=10 % au lieu d'une de 16 seraient la fuite exacte que les
    vagues empêchent, produite toute seule au rythme des tours."""
    from harnais import boucle as B
    from harnais.epreuves import Verdict
    monkeypatch.setattr(B, "e3", lambda *a, **k: Verdict(
        "É3", True, 0.99, "É4", "stub de test : rejeu fictif"))
    rng = np.random.default_rng(31)
    series = {n: rng.normal(size=3000)
              for n in FICHES if FICHES[n]["perimetre"] == "J3"}
    rapport = tour(series=series, bloc={TEMOIN: rng.normal(size=3000)},
                   chemin=reg_vierge)
    arrives = [n for n, (e, _) in rapport.items() if e == "É4"]
    assert arrives, rapport
    for n in arrives:
        assert "VAGUE COMPLÈTE" in rapport[n][1]
    # et rien n'est écrit : pas une seule ligne É4 au registre
    assert not [l for l in lire(reg_vierge) if l["epreuve"] == "É4"]


def test_les_vagues_sont_jugees_separement(reg_vierge, monkeypatch):
    """Le champ `vague` porte le mécanisme : une fiche de vague 2 encore en
    chemin ne gèle PAS le BH de la vague 1 — et le BH de la vague 1 se
    calcule sur SES membres, jamais sur la fusion des familles déclarées."""
    from harnais import boucle as B
    from harnais.epreuves import Verdict
    monkeypatch.setattr(B, "FICHES", {
        **FICHES, "Z1 · fiche de vague 2 (test)":
        dict(perimetre="J3", vague=2, cout_rang=99)})
    monkeypatch.setattr(B, "e3", lambda *a, **k: Verdict(
        "É3", True, 0.99, "É4", "stub de test : rejeu fictif"))
    appels = iter(range(100))
    monkeypatch.setattr(B, "e4", lambda *a, **k: (
        lambda i: {"n_jours": 3, "moyenne": 0.5 if i == 0 else 0.01,
                   "p_value": 0.001 if i == 0 else 0.9,
                   "ic95": (0.1, 0.9)})(next(appels)))
    rng = np.random.default_rng(41)
    series = {n: rng.normal(size=3000) for n in FICHES}   # Z1 : pas de série
    rapport = B.tour(series=series, bloc={TEMOIN: rng.normal(size=3000)},
                     chemin=reg_vierge)
    # la vague 1 est jugée malgré Z1 (vague 2) en attente de données
    assert any(e == "retenue" for e, _ in rapport.values())
    lignes_e4 = [l for l in lire(reg_vierge) if l["epreuve"] == "É4"]
    assert lignes_e4
    for l in lignes_e4:
        assert "vague 1, 16 déclarés" in l["chiffre"]
    # et Z1 n'a pas été jugée : elle attend, dans sa vague à elle
    assert rapport["Z1 · fiche de vague 2 (test)"][0] == "déposée"


def test_n_bloc_se_recalcule_entre_les_vagues(reg_vierge, monkeypatch):
    """Figé avant la boucle des vagues, n_bloc aurait donné à la vague 2 le
    compte d'AVANT la vague 1 — et la garde n_bloc_retenu>0 n'aurait rien
    vu : Spearman simple avec un bloc de deux grandeurs, en silence. On
    capture ce que e4 reçoit : 0 pour la vague 1, 1 pour la vague 2 (jugée
    après qu'une retenue de vague 1 est écrite)."""
    from harnais import boucle as B
    from harnais.epreuves import Verdict
    z1 = "Z1 · fiche de vague 2 (test)"
    monkeypatch.setattr(B, "FICHES", {
        **FICHES, z1: dict(perimetre="J3", vague=2, cout_rang=99,
                           e1=dict(sans_l4=True, traverse_binance=True,
                                   navigateur=True))})
    monkeypatch.setattr(B, "e3", lambda *a, **k: Verdict(
        "É3", True, 0.99, "É4", "stub de test : rejeu fictif"))
    recus, appels = [], iter(range(100))
    def e4_stub(*a, **k):
        recus.append(k.get("n_bloc_retenu"))
        i = next(appels)
        return {"n_jours": 3, "moyenne": 0.5 if i == 0 else 0.01,
                "p_value": 0.001 if i == 0 else 0.9, "ic95": (0.1, 0.9)}
    monkeypatch.setattr(B, "e4", e4_stub)
    rng = np.random.default_rng(51)
    series = {n: rng.normal(size=3000) for n in FICHES}
    series[z1] = rng.normal(size=3000)
    rapport = B.tour(series=series, bloc={TEMOIN: rng.normal(size=3000)},
                     chemin=reg_vierge)
    assert any(e == "retenue" for e, _ in rapport.values())
    assert rapport[z1][0] == "éliminée" and "BH" in rapport[z1][1]
    # la vague 1 a été jugée à bloc 0 ; la vague 2 au compte D'APRÈS
    assert recus[:-1] == [0] * (len(recus) - 1)
    assert recus[-1] == 1


def test_e3_sans_chiffre_est_refuse_jamais_enregistre(reg_vierge, monkeypatch):
    """Un É3 qui rendrait un verdict sans nombre est REFUSÉ — pas écrit au
    registre avec une opinion en colonne chiffre."""
    from harnais import boucle as B
    from harnais.epreuves import Verdict
    monkeypatch.setattr(B, "e3", lambda *a, **k: Verdict(
        "É3", True, None, "É4", "opinion sans nombre"))
    rng = np.random.default_rng(2)
    series = {n: rng.normal(size=3000) for n in FICHES}
    rapport = tour(series=series, bloc={TEMOIN: rng.normal(size=3000)},
                   chemin=reg_vierge)
    assert any("sans chiffre" in raison for _, raison in rapport.values())
    assert not [l for l in lire(reg_vierge) if l["epreuve"] == "É3"]


def test_retenue_est_atteignable_et_bh_tranche_la_vague(reg_vierge, monkeypatch):
    """La 3e arête manquante (06/08) : « retenue » — la porte de sortie du
    banc, celle qui fait grandir le bloc d'É2. On stubbe É3 et É4 (rejeu et
    cible fictifs) : la phase collective applique BH sur la vague, écrit
    `retenue` pour le p qui passe et `éliminée` pour les autres, chaque
    ligne portant son chiffre complet (coef, p, IC, taille de vague)."""
    from harnais import boucle as B
    from harnais.epreuves import Verdict
    monkeypatch.setattr(B, "e3", lambda *a, **k: Verdict(
        "É3", True, 0.99, "É4", "stub de test : rejeu fictif"))
    appels = iter(range(100))
    monkeypatch.setattr(B, "e4", lambda *a, **k: (
        lambda i: {"n_jours": 3, "moyenne": 0.5 if i == 0 else 0.01,
                   "p_value": 0.001 if i == 0 else 0.9,
                   "ic95": (0.1, 0.9)})(next(appels)))
    rng = np.random.default_rng(21)
    t0 = rng.normal(size=3000)
    series = {n: rng.normal(size=3000) for n in FICHES}
    # un doublon présumé fabriqué : C1 à ρ≈0,73 du témoin — `05` É2 : « une
    # barre, pas une porte fermée » — il doit TRAVERSER jusqu'à É4, pas
    # rester garé (4e arête, attrapée le 06/08)
    c1 = "C1 · concentration"
    series[c1] = 0.75 * t0 + np.sqrt(1 - 0.75 ** 2) * rng.normal(size=3000)
    rapport = tour(series=series, bloc={TEMOIN: t0}, chemin=reg_vierge)

    etats = [e for e, _ in rapport.values()]
    assert "retenue" in etats           # la porte de sortie EXISTE
    assert etats.count("retenue") == 1  # BH : seul p=0,001 passe à q=0,10
    retenue = next(n for n, (e, _) in rapport.items() if e == "retenue")
    assert "bloc de référence" in rapport[retenue][1]
    # le doublon présumé a bien été JUGÉ à É4 (par BH), pas garé à É2
    assert rapport[c1][0] in ("retenue", "éliminée") and "BH" in rapport[c1][1]
    historique = [l["etat"] for l in lire(reg_vierge) if l["nom"] == c1]
    assert "doublon présumé" in historique   # le drapeau d'É2 reste écrit
    # chaque ligne d'É4 au registre porte son chiffre complet, jamais du texte
    lignes_e4 = [l for l in lire(reg_vierge) if l["epreuve"] == "É4"]
    assert lignes_e4
    for l in lignes_e4:
        assert l["chiffre"].startswith("coef=") and "p=" in l["chiffre"]
        assert l["etat"] in ("retenue", "éliminée")
    # et les éliminés de la vague le sont par BH, pas par une épreuve ratée
    assert any(e == "éliminée" and "BH" in r for e, r in rapport.values())


def test_bloc_par_perimetre_le_temoin_du_bon_perimetre(reg):
    """Dette T0-J8 fermée : un candidat J8 passe É2 contre SON témoin, plus
    de refus de longueur."""
    rng = np.random.default_rng(9)
    series = {}
    for nom, f in FICHES.items():
        n = 3000 if f["perimetre"] == "J3" else 8000
        series[nom] = rng.normal(size=n)
    blocs = {"J3": {TEMOIN: rng.normal(size=3000)},
             "J8": {TEMOIN: rng.normal(size=8000)}}
    rapport = tour(series=series, bloc_par_perimetre=blocs, chemin=reg)
    # les J8 atteignent É3 (refus rejeu) au lieu de bloquer à É2
    for nom, f in FICHES.items():
        if f["perimetre"] == "J8":
            etat, raison = rapport[nom]
            assert etat in ("É3", "éliminée"), (nom, etat, raison)
