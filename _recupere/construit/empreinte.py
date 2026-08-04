"""Manifeste d'artefact — ce qui a produit ce fichier, et sous quel reglage.

## Pourquoi ce fichier existe

`01_Cahier_des_charges.md` exige le versionnement des donnees : « un resultat
doit se reproduire exactement plusieurs mois plus tard ». Au 04/08/2026 rien de
tel n'existait — `grep -rn "hashlib|sha256|manifest"` sur `construit/` ne
rendait rien — et un lot etait sur le point de RECONSTRUIRE huit jours qui
portaient des mesures publiees. Apres ce lot, plus personne n'aurait pu dire si
`deep_20251209_BTC.parquet` etait celui sur lequel « le carnet profond couvre la
bande sur 100 % des photos » avait ete mesure.

Le programme le disait deja, piege n° 11 : la garde de gel protege l'ECRITURE,
rien ne protege la LECTURE contre le melange de generations. Un `glob` les
concatene en silence. Ce module donne de quoi le detecter.

## Ce qu'il enregistre, et pourquoi chaque champ

* **sha256 du contenu** — pas du chemin. Deux fichiers de meme nom construits a
  deux reglages ne se ressemblent pas, et c'est la seule chose qui le dit.
* **les parametres de construction** — `DEEP_MS`, `DEEP_BAND`, `WARMUP_H`,
  `BIN_REL`, `SNAP_MS`, `SNAP_MIN_MS`. Ce sont eux qui changent le SENS du
  fichier sans changer son schema. Un `deep` a +/-2 % et un `deep` a +/-10 %
  ont les memes colonnes et ne mesurent pas la meme chose.
* **le commit git, et s'il etait sale** — un artefact produit sur un arbre
  modifie n'est pas reproductible, et il faut que ca se voie.
* **les versions** — `pivot_table` et `groupby.quantile` ne se comportent pas
  pareil d'une version de pandas a l'autre.
* **les entrees** — taille et date des archives sources.

## Ce qu'il n'enregistre PAS, et c'est deliberé

Les archives sources ne sont pas hachees : `btc_orders_202512.tar.xz` pese
19 Go et `book_diffs_202512.tar` 50 Go. Les hacher a chaque jour construit
couterait plus que la construction. On enregistre taille + date de
modification, ce qui detecte un remplacement mais pas une reecriture
bit-a-bit de meme taille. **C'est une limite reelle, elle est ecrite ici pour
ne pas etre prise pour une garantie.**

Cout mesure : sha256 en flux, ~680 Mo pour la plus grosse partie `hl_orders`,
soit 1 a 2 s — contre 38 min pour construire le jour.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = 1


def _sha256(p: Path, bloc: int = 1 << 20) -> str:
    """Hache en FLUX. Une partie `hl_orders` pese 680 Mo : pas de read()."""
    h = hashlib.sha256()
    with p.open("rb") as f:
        while (b := f.read(bloc)):
            h.update(b)
    return h.hexdigest()


def _git(racine: Path) -> dict:
    """Commit courant et proprete de l'arbre. Jamais fatal : un depot absent
    n'est pas une raison de perdre le reste du manifeste."""
    def run(*a):
        return subprocess.run(a, cwd=racine, capture_output=True,
                              text=True, timeout=10).stdout.strip()
    try:
        return {"commit": run("git", "rev-parse", "HEAD"),
                "court": run("git", "rev-parse", "--short", "HEAD"),
                "sale": bool(run("git", "status", "--porcelain"))}
    except Exception as e:                       # noqa: BLE001
        return {"commit": None, "court": None, "sale": None, "erreur": str(e)}


def _versions() -> dict:
    v = {"python": platform.python_version(), "plateforme": platform.platform()}
    for nom in ("numpy", "pandas", "pyarrow", "scipy", "sortedcontainers"):
        try:
            v[nom] = __import__(nom).__version__
        except Exception:                        # noqa: BLE001
            v[nom] = None
    return v


def _entrees(chemins) -> list:
    """Taille et date des sources. PAS leur hash — voir la docstring du module."""
    out = []
    for c in chemins:
        c = Path(c)
        if not c.exists():
            out.append({"chemin": str(c), "absent": True})
            continue
        st = c.stat()
        out.append({"chemin": str(c), "octets": st.st_size,
                    "mtime_utc": datetime.fromtimestamp(
                        st.st_mtime, timezone.utc).isoformat(timespec="seconds")})
    return out


def chemin_manifeste(artefact) -> Path:
    return Path(str(artefact) + ".manifest.json")


def ecris(artefact, *, kind: str, jour: str, coin: str, phase: str,
          parametres: dict, entrees=(), stats: dict | None = None,
          racine: Path | None = None) -> Path | None:
    """Ecrit `<artefact>.manifest.json`. Rend None si l'artefact n'existe pas.

    Appele APRES la fermeture du fichier : on hache ce qui est sur le disque,
    jamais ce qu'on croit y avoir mis.
    """
    a = Path(artefact)
    if not a.exists():
        return None
    racine = racine or Path(__file__).resolve().parent.parent

    contenu = {}
    try:
        import pyarrow.parquet as pq
        m = pq.ParquetFile(a).metadata
        contenu = {"lignes": m.num_rows, "groupes": m.num_row_groups,
                   "colonnes": [f.name for f in pq.ParquetFile(a).schema_arrow]}
    except Exception as e:                       # noqa: BLE001
        contenu = {"erreur_lecture": str(e)}

    man = {
        "schema_manifeste": SCHEMA,
        "artefact": {"nom": a.name, "octets": a.stat().st_size,
                     "sha256": _sha256(a)},
        "contenu": contenu,
        "production": {
            "horodatage_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "kind": kind, "jour": jour, "coin": coin, "phase": phase,
            "machine": platform.node(),
        },
        "code": _git(racine),
        "parametres": parametres,
        "environnement": _versions(),
        "entrees": _entrees(entrees),
        "entrees_hachees": False,      # voir la docstring : trop couteux
        "stats": stats or {},
        "argv": sys.argv,
    }
    d = chemin_manifeste(a)
    d.write_text(json.dumps(man, indent=2, ensure_ascii=False), encoding="utf-8")
    return d


def lis(artefact) -> dict | None:
    p = chemin_manifeste(artefact)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def verifie(artefact) -> dict:
    """Le fichier est-il bien celui que son manifeste decrit ?

    C'est la moitie LECTURE de la garde, celle qui manquait. Un artefact sans
    manifeste n'est pas declare bon : il est declare INCONNU, ce qui n'est pas
    la meme chose et doit se propager jusqu'au rapport.
    """
    a = Path(artefact)
    man = lis(a)
    if man is None:
        return {"etat": "INCONNU", "raison": "aucun manifeste", "chemin": str(a)}
    if not a.exists():
        return {"etat": "ABSENT", "chemin": str(a)}
    attendu = man["artefact"]["sha256"]
    obtenu = _sha256(a)
    return {"etat": "OK" if obtenu == attendu else "ALTERE",
            "chemin": str(a), "sha256_attendu": attendu, "sha256_obtenu": obtenu,
            "parametres": man.get("parametres", {}),
            "commit": man.get("code", {}).get("court"),
            "sale": man.get("code", {}).get("sale")}


def generations(dossier, motif: str = "*.parquet") -> dict:
    """Regroupe les artefacts d'un dossier par JEU DE PARAMETRES.

    Le piege n° 11 en une commande : si ce dictionnaire a plus d'une cle, un
    `glob` sur ce dossier melange deux generations. Les fichiers sans
    manifeste tombent sous la cle `"INCONNU"` — ils ne sont pas silencieux.
    """
    par: dict[str, list] = {}
    for p in sorted(Path(dossier).glob(motif)):
        man = lis(p)
        cle = ("INCONNU" if man is None
               else json.dumps(man.get("parametres", {}), sort_keys=True))
        par.setdefault(cle, []).append(p.name)
    return par


def _selftest() -> None:
    import tempfile
    import pyarrow as pa
    import pyarrow.parquet as pq
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "t_20251208_BTC.parquet"
        pq.write_table(pa.table({"k": pa.array([1, 2, 3])}), f)

        assert verifie(f)["etat"] == "INCONNU", "sans manifeste => INCONNU"

        ecris(f, kind="t", jour="20251208", coin="BTC", phase="all",
              parametres={"DEEP_MS": 10000, "DEEP_BAND": 0.10})
        v = verifie(f)
        assert v["etat"] == "OK", v
        assert lis(f)["contenu"]["lignes"] == 3

        # ALTERE : le fichier change, le manifeste ne suit pas.
        pq.write_table(pa.table({"k": pa.array([1, 2, 3, 4])}), f)
        assert verifie(f)["etat"] == "ALTERE", "reecriture non detectee"

        # Deux generations dans le meme dossier => deux cles.
        g = Path(d) / "t_20251209_BTC.parquet"
        pq.write_table(pa.table({"k": pa.array([9])}), g)
        ecris(g, kind="t", jour="20251209", coin="BTC", phase="all",
              parametres={"DEEP_MS": 250, "DEEP_BAND": 0.02})
        ecris(f, kind="t", jour="20251208", coin="BTC", phase="all",
              parametres={"DEEP_MS": 10000, "DEEP_BAND": 0.10})
        gen = generations(d)
        assert len(gen) == 2, f"melange non detecte : {gen}"
    print("empreinte : selftest OK - INCONNU, OK, ALTERE, et melange de "
          "generations detecte", flush=True)


if __name__ == "__main__":
    _selftest()
