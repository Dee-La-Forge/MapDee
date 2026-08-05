"""P2 — le registre n'accepte que l'ajout, et jamais sans chiffre."""
import shutil
from pathlib import Path

import pytest

from harnais.registre import CHEMIN, RegistreRefus, ajouter, lire


@pytest.fixture
def copie(tmp_path):
    c = tmp_path / "registre.md"
    shutil.copy(CHEMIN, c)
    return c


def test_lit_le_vrai_registre_et_trouve_le_temoin():
    lignes = lire()
    assert any(l["etat"] == "témoin trivial" for l in lignes)


def test_ajoute_en_fin_de_table(copie):
    avant = lire(copie)
    ajouter("2026-08-05", "A1 · OFI", "déposée", "—", "—", "J3", "test", copie)
    apres = lire(copie)
    assert len(apres) == len(avant) + 1
    assert apres[-1]["nom"] == "A1 · OFI"
    # rien d'autre n'a bougé : l'ajout n'est PAS une réécriture
    assert apres[:-1] == avant


def test_REFUSE_elimination_sans_chiffre(copie):
    with pytest.raises(RegistreRefus, match="chiffre"):
        ajouter("2026-08-05", "X", "éliminée", "É0", "—", "J3", "test", copie)


def test_REFUSE_etat_inconnu(copie):
    with pytest.raises(RegistreRefus, match="vocabulaire"):
        ajouter("2026-08-05", "X", "en cours", "É0", "0.5", "J3", "test", copie)


def test_REFUSE_date_malformee_et_pipe(copie):
    with pytest.raises(RegistreRefus):
        ajouter("05/08/2026", "X", "déposée", "—", "—", "J3", "test", copie)
    with pytest.raises(RegistreRefus):
        ajouter("2026-08-05", "X|Y", "déposée", "—", "—", "J3", "test", copie)
