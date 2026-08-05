"""P1 — le générateur synthétique. Carnet fabriqué, vérité connue.

Contrat (`chantiers/C9-harnais.md` §2/P1) :

* l'observable émet EXACTEMENT le schéma de `deep` — transcrit ici de
  `_recupere/construit/jour.py::_DeepWriter._SCHEMA`, vérifié par test contre
  un artefact réel, jamais par import de l'archive ;
* la vérité (quel mécanisme, où, quand, à quelle amplitude) part dans une
  table SÉPARÉE : la méthode ne la voit jamais, seul le banc compare ;
* déterministe à graine fixée — deux runs à même graine sont identiques
  octet par octet, sans quoi le bras nul n'est pas comparable au bras injecté.

Modèle génératif (D3, validé le 05/08/2026) : flux sans intelligence —
arrivées et annulations en Poisson par palier, intensités décroissantes avec
la distance au mid, exécutions au contact. Volontairement pauvre : ÉS teste
« la méthode retrouve-t-elle une injection », pas « le générateur imite-t-il
le marché ». Montée en gamme queue-réactive : par ADR, pas en silence.

Mécanismes injectables (D4, validés le 05/08/2026) — amplitude en MULTIPLE de
la masse médiane locale, l'axe du plancher de détection :

* `leurre`     — masse posée hors contact, retirée quand le prix s'approche,
                 jamais exécutée ;
* `recharge`   — masse ré-approvisionnée au même palier après consommation ;
* `absorption` — masse tenue sous exécutions répétées au contact.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from harnais.grille import BIN_REL, nice

#: TRANSCRIT de `_DeepWriter._SCHEMA` — ne pas « améliorer » : une méthode
#: validée ici doit tourner telle quelle sur décembre.
SCHEMA_DEEP = pa.schema([
    ("t", pa.int64()), ("coin", pa.string()),
    ("mid", pa.float64()), ("bs", pa.float64()),
    ("k", pa.int32()), ("mag", pa.float32()), ("n", pa.int16()),
])

SCHEMA_VERITE = pa.schema([
    ("t", pa.int64()), ("k", pa.int32()),
    ("mecanisme", pa.string()), ("amplitude", pa.float64()),
])

DEEP_BAND = 0.10   # nappe large — le réglage arrêté de la construction
DEEP_LOT = 400     # photos par groupe de lignes, comme la production


@dataclass
class Injection:
    mecanisme: str          # 'leurre' | 'recharge' | 'absorption'
    t_debut_s: float
    duree_s: float
    amplitude: float        # multiple de la masse médiane locale au déclenchement
    cote: int = 1           # 0 = bid, 1 = ask
    dist_paliers: int = 12  # leurre : distance de pose ; ignoré au contact
    approche_paliers: int = 4   # leurre : seuil de retrait
    # état interne, jamais fourni par l'appelant
    _k: int | None = field(default=None, repr=False)
    _masse: float = field(default=0.0, repr=False)
    _retire: bool = field(default=False, repr=False)


class _Livre:
    """Deux côtés, masse et compte d'ordres par palier. Zero-intelligence."""

    def __init__(self, rng: np.random.Generator, mid0: float) -> None:
        self.rng = rng
        self.mid = mid0
        self.mag: list[dict[int, float]] = [{}, {}]   # [bid, ask]
        self.n: list[dict[int, int]] = [{}, {}]
        bs = self.bs
        k0 = int(mid0 // bs)
        # état initial : profil décroissant avec la distance, des deux côtés
        for d in range(1, int(mid0 * DEEP_BAND / bs)):
            for cote, k in ((0, k0 - d), (1, k0 + d)):
                m = float(rng.lognormal(mean=np.log(50_000 / (1 + 0.15 * d)), sigma=0.6))
                self.mag[cote][k] = m
                self.n[cote][k] = 1 + int(rng.poisson(2))

    @property
    def bs(self) -> float:
        return nice(self.mid * BIN_REL)

    def _bornes_bande(self) -> tuple[int, int]:
        bs = self.bs
        return (int(self.mid * (1 - DEEP_BAND) // bs),
                int(self.mid * (1 + DEEP_BAND) // bs))

    def mediane_locale(self, cote: int) -> float:
        v = [m for m in self.mag[cote].values() if m > 0]
        return float(np.median(v)) if v else 50_000.0

    def _depose(self, cote: int, k: int, m: float, n_ordres: int = 1) -> None:
        self.mag[cote][k] = self.mag[cote].get(k, 0.0) + m
        self.n[cote][k] = self.n[cote].get(k, 0) + n_ordres

    def _retire_tout(self, cote: int, k: int) -> None:
        self.mag[cote].pop(k, None)
        self.n[cote].pop(k, None)

    def meilleurs(self) -> tuple[int | None, int | None]:
        bid = max(self.mag[0]) if self.mag[0] else None
        ask = min(self.mag[1]) if self.mag[1] else None
        return bid, ask

    def pas(self) -> None:
        """Un pas de temps : arrivées, annulations, exécutions, mid."""
        rng = self.rng
        lo, hi = self._bornes_bande()
        k0 = int(self.mid // self.bs)
        # arrivées — intensité décroissante avec la distance
        for _ in range(int(rng.poisson(12))):
            cote = int(rng.integers(2))
            d = 1 + int(rng.exponential(6))
            k = k0 - d if cote == 0 else k0 + d
            if lo <= k <= hi:
                self._depose(cote, k, float(rng.lognormal(np.log(20_000), 0.8)))
        # annulations — proportionnelles, uniformes en palier
        for cote in (0, 1):
            for k in list(self.mag[cote]):
                if rng.random() < 0.03:
                    self.mag[cote][k] *= float(rng.uniform(0.2, 0.8))
                    if self.mag[cote][k] < 1.0:
                        self._retire_tout(cote, k)
        # exécutions — au contact, côté tiré au sort
        for _ in range(int(rng.poisson(3))):
            cote = int(rng.integers(2))          # côté CONSOMMÉ
            bid, ask = self.meilleurs()
            k = bid if cote == 0 else ask
            if k is None:
                continue
            vol = float(rng.exponential(15_000))
            self.mag[cote][k] -= vol
            if self.mag[cote][k] <= 1.0:
                self._retire_tout(cote, k)
        # mid depuis les meilleures limites
        bid, ask = self.meilleurs()
        if bid is not None and ask is not None:
            bs = self.bs
            self.mid = ((bid + 0.5) + (ask + 0.5)) / 2 * bs


def _applique_injections(livre: _Livre, injections: list[Injection],
                         t_s: float, verite: list) -> None:
    for inj in injections:
        # Amplitude nulle = BRAS NUL STRICT : aucune mutation du livre, aucune
        # ligne de vérité. Même toucher un dict changerait la consommation du
        # générateur aléatoire et rendrait le bras nul incomparable.
        if inj.amplitude <= 0:
            continue
        if not (inj.t_debut_s <= t_s < inj.t_debut_s + inj.duree_s):
            continue
        k0 = int(livre.mid // livre.bs)
        cible = inj._k
        if inj.mecanisme == "leurre":
            if inj._retire:
                continue
            if cible is None:
                cible = inj._k = (k0 + inj.dist_paliers if inj.cote == 1
                                  else k0 - inj.dist_paliers)
                inj._masse = inj.amplitude * livre.mediane_locale(inj.cote)
                livre._depose(inj.cote, cible, inj._masse)
            # le prix s'approche -> retrait TOTAL, jamais exécuté
            if abs(cible - k0) <= inj.approche_paliers:
                livre.mag[inj.cote][cible] = max(
                    0.0, livre.mag[inj.cote].get(cible, 0.0) - inj._masse)
                if livre.mag[inj.cote].get(cible, 0.0) <= 1.0:
                    livre._retire_tout(inj.cote, cible)
                inj._retire = True
                continue
        elif inj.mecanisme in ("recharge", "absorption"):
            if cible is None:
                bid, ask = livre.meilleurs()
                cible = inj._k = (ask if inj.cote == 1 else bid) or k0
                inj._masse = inj.amplitude * livre.mediane_locale(inj.cote)
            # tenue/re-approvisionnement : la masse revient à son niveau
            actuel = livre.mag[inj.cote].get(cible, 0.0)
            if actuel < inj._masse:
                livre._depose(inj.cote, cible, inj._masse - actuel)
        if not inj._retire:
            verite.append((cible, inj.mecanisme, inj.amplitude))


def genere(chemin_obs: Path, chemin_verite: Path, *, graine: int,
           duree_s: float = 600.0, pas_ms: int = 250, mid0: float = 90_000.0,
           coin: str = "SYN", injections: list[Injection] | None = None) -> dict:
    """Fabrique un carnet et l'écrit en deux tables. Rend les compteurs."""
    # Copie à état neuf : les Injection portent un état interne, et réutiliser
    # les objets de l'appelant d'un run à l'autre casserait le déterminisme.
    injections = [Injection(i.mecanisme, i.t_debut_s, i.duree_s, i.amplitude,
                            i.cote, i.dist_paliers, i.approche_paliers)
                  for i in (injections or [])]
    rng = np.random.Generator(np.random.PCG64(graine))
    livre = _Livre(rng, mid0)
    cols = {c: [] for c in ("t", "coin", "mid", "bs", "k", "mag", "n")}
    vcols = {c: [] for c in ("t", "k", "mecanisme", "amplitude")}
    w = pq.ParquetWriter(chemin_obs, SCHEMA_DEEP, compression="zstd")
    n_photos = n_lignes = 0
    depuis = 0

    def flush() -> None:
        nonlocal depuis
        if not cols["t"]:
            return
        w.write_table(pa.table(
            {"t": pa.array(cols["t"], pa.int64()),
             "coin": pa.array(cols["coin"], pa.string()),
             "mid": pa.array(cols["mid"], pa.float64()),
             "bs": pa.array(cols["bs"], pa.float64()),
             "k": pa.array(cols["k"], pa.int32()),
             "mag": pa.array(cols["mag"], pa.float32()),
             "n": pa.array(cols["n"], pa.int16())}, schema=SCHEMA_DEEP))
        for c in cols.values():
            c.clear()
        depuis = 0

    n_pas = int(duree_s * 1000 / pas_ms)
    for i in range(n_pas):
        t = i * pas_ms
        livre.pas()
        v_photo: list = []
        _applique_injections(livre, injections, t / 1000.0, v_photo)
        lo, hi = livre._bornes_bande()
        mid, bs = livre.mid, livre.bs
        for cote in (0, 1):
            for k, m in sorted(livre.mag[cote].items()):
                if lo <= k <= hi and m > 0:
                    cols["t"].append(t); cols["coin"].append(coin)
                    cols["mid"].append(mid); cols["bs"].append(bs)
                    cols["k"].append(k); cols["mag"].append(m)
                    cols["n"].append(min(livre.n[cote].get(k, 1), 32_000))
                    n_lignes += 1
        for k, mec, amp in v_photo:
            vcols["t"].append(t); vcols["k"].append(k)
            vcols["mecanisme"].append(mec); vcols["amplitude"].append(amp)
        n_photos += 1
        depuis += 1
        if depuis >= DEEP_LOT:
            flush()
    flush()
    w.close()
    pq.write_table(pa.table(
        {"t": pa.array(vcols["t"], pa.int64()),
         "k": pa.array(vcols["k"], pa.int32()),
         "mecanisme": pa.array(vcols["mecanisme"], pa.string()),
         "amplitude": pa.array(vcols["amplitude"], pa.float64())},
        schema=SCHEMA_VERITE), chemin_verite, compression="zstd")
    return {"photos": n_photos, "lignes": n_lignes,
            "lignes_verite": len(vcols["t"]), "graine": graine}
