"""Les extracteurs : fiche → série par jour, depuis un artefact `deep`.

CE QUE C'EST. É0 et É2 corrèlent des candidats entre eux : il leur faut, pour
chaque candidat, UNE série scalaire par photo, sur le périmètre de la fiche.
Ce module la fabrique. L'agrégation par photo de chaque grandeur est
**déclarée dans sa fonction** — c'est la version « série d'É0/É2 » de la
fiche, pas sa version par-palier (qui vit aux étages suivants).

CE QUE ÇA REFUSE. Quatre candidats n'ont PAS d'extracteur, avec leur raison
(`ABSENTS` en bas) : A2 et B4 attendent les définitions de B7 (« mur »,
« contact ») ; A5 attend sa calibration de noyau ; A6 son estimation Hawkes
(heures — le harnais ne paie pas ce coût en douce). La boucle les laissera
en attente, elle n'approximera pas.

PERFORMANCE, décidée d'avance : un jour réel de `deep` fait ~400 M lignes —
la lecture FILTRE à la bande utile (`dist_max`, défaut ±0,5 % du mid) via une
expression pyarrow au scan, jamais après chargement. Les séries se calculent
ensuite en numpy sur les agrégats par photo, en une passe.

EXÉCUTIONS. A3, B3 et D2 exigent le flux exécuté par palier (`execs`) — sur
données réelles il viendra des transactions agrégées (sans identité). Les
extracteurs le prennent en argument ; sans lui, ils sont absents du résultat,
comptés, jamais interpolés.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

FENETRE_BASE = 240      # photos — lignes de base glissantes (B1, C3, D1)
HORIZON_B5 = 240        # photos — plafond de l'âge de niveau (B5, version causale)
RECHARGE_W = 4          # transitions — délai exécution → recharge (B3)
NB_BINS = 16            # bins de distance du profil (C2)
MARGE_INTERIEURE = 0.9  # les FLUX ne se comptent que pour les paliers à
                        # moins de 0,9 × dist_max du mid COURANT : la bande
                        # suit le mid, et sans marge chaque déplacement
                        # fabriquait des ajouts/retraits fantômes aux bords
                        # (audits du 05-06/08, constat F9 en partie)


class SeriesJour:
    """Les agrégats par photo d'un jour-symbole — la matière des séries."""

    def __init__(self) -> None:
        self.t = self.mid = self.bs = None
        self.add = [None, None]      # [bid, ask] masse ajoutée vs photo précédente
        self.rem = [None, None]      # masse retirée
        self.m_tot = [None, None]
        self.herf = [None, None]
        self.best_k = [None, None]
        self.best_m = [None, None]
        self.disparus = None         # paliers présents à t-1, absents à t
        self.presents_prec = None
        self.recouvre = None         # masse ajoutée aux paliers en retrait net à t-1
        self.profil = None           # (n, NB_BINS) masse par bin de distance


def tronque_series(s: SeriesJour, n: int) -> SeriesJour:
    """Le même jour, coupé aux n premières photos — TOUT attribut indexé
    par photo est tranché [:n], le reste copié tel quel. Sert la garde de
    causalité (`00` §3, zéro lookahead) : pour un extracteur causal,
    ext(tronque(s, n)) == ext(s)[:n] — si l'égalité tombe, l'extracteur
    regarde le futur et le test/diagnostic REFUSE."""
    total = len(s.mid)
    out = SeriesJour()
    for att, val in vars(s).items():
        if isinstance(val, list):
            setattr(out, att, [v[:n] if hasattr(v, "__len__")
                               and len(v) == total else v for v in val])
        elif hasattr(val, "__len__") and len(val) == total:
            setattr(out, att, val[:n])
        else:
            setattr(out, att, val)
    return out


def charge(chemin_deep: Path, dist_max: float = 0.005) -> SeriesJour:
    """Une passe sur `deep`, filtrée à ±dist_max du mid LOT PAR LOT — un jour
    réel fait ~400 M lignes, on ne le charge jamais entier. (`pyarrow.dataset`
    échoue sur cette machine — WinError 1 — d'où le flux ParquetFile.)"""
    cols = ("t", "k", "mag", "mid", "bs")

    def _filtre(lots) -> dict[str, list]:
        m: dict[str, list] = {c: [] for c in cols}
        for lot in lots:
            k = lot["k"].to_numpy()
            mid = lot["mid"].to_numpy()
            bs = lot["bs"].to_numpy()
            garde = np.abs((k + 0.5) * bs - mid) <= mid * dist_max
            for c in cols:
                m[c].append(lot[c].to_numpy()[garde])
        return m

    morceaux = _filtre(pq.ParquetFile(chemin_deep).iter_batches(
        columns=list(cols), batch_size=2_000_000))
    ts = np.concatenate(morceaux["t"])
    ks = np.concatenate(morceaux["k"])
    mags = np.concatenate(morceaux["mag"]).astype(np.float64)
    mids = np.concatenate(morceaux["mid"])
    bss = np.concatenate(morceaux["bs"])

    photos, inverse = np.unique(ts, return_inverse=True)
    ordre = np.argsort(inverse, kind="stable")
    bornes = np.searchsorted(inverse[ordre], np.arange(len(photos) + 1))
    n = len(photos)

    s = SeriesJour()
    s.t = photos
    s.mid = np.empty(n)
    s.bs = np.empty(n)
    for cote in (0, 1):
        s.add[cote] = np.zeros(n)
        s.rem[cote] = np.zeros(n)
        s.m_tot[cote] = np.zeros(n)
        s.herf[cote] = np.full(n, np.nan)
        s.best_k[cote] = np.full(n, np.nan)
        s.best_m[cote] = np.full(n, np.nan)
    s.disparus = np.zeros(n)
    s.presents_prec = np.zeros(n)
    s.recouvre = np.zeros(n)
    s.profil = np.zeros((n, NB_BINS))
    s.m_k0 = np.zeros(n)     # masse au palier du mid — DIAGNOSTIC (audit F10) :
                             # exclue des stocks et des flux, incluse au profil

    prec: dict[int, float] | None = None
    retraits_prec: set[int] = set()
    for i in range(n):
        tr = ordre[bornes[i]:bornes[i + 1]]
        kk, mm = ks[tr], mags[tr]
        mid, bs = mids[tr[0]], bss[tr[0]]
        s.mid[i], s.bs[i] = mid, bs
        k0 = int(mid // bs)
        for cote, sel in ((0, kk < k0), (1, kk > k0)):
            km, mv = kk[sel], mm[sel]
            tot = float(mv.sum())
            s.m_tot[cote][i] = tot
            if mv.size:
                s.herf[cote][i] = float(((mv / tot) ** 2).sum()) if tot > 0 else np.nan
                j = int(np.argmax(km)) if cote == 0 else int(np.argmin(km))
                s.best_k[cote][i], s.best_m[cote][i] = km[j], mv[j]
        # profil par bins de distance relative (bande ENTIÈRE, k0 compris —
        # c'est une forme de masse, pas un flux ; documenté, audit F10)
        dist = np.abs((kk + 0.5) * bs - mid) / mid
        bins = np.minimum((dist / dist_max * NB_BINS).astype(int), NB_BINS - 1)
        np.add.at(s.profil[i], bins, mm)
        ici_k0 = mm[kk == k0]
        s.m_k0[i] = float(ici_k0[0]) if ici_k0.size else 0.0

        # transitions palier à palier contre la photo précédente — FLUX
        # comptés uniquement pour les paliers INTÉRIEURS sous le mid COURANT
        # et différents de k0 : une règle, appliquée partout (audit F9/F10)
        borne = mid * dist_max * MARGE_INTERIEURE

        def interieur(k: int) -> bool:
            return k != k0 and abs((k + 0.5) * bs - mid) <= borne

        cur = dict(zip(kk.tolist(), mm.tolist()))
        if prec is not None:
            retraits = set()
            for k, m in cur.items():
                if not interieur(k):
                    continue
                d = m - prec.get(k, 0.0)
                cote = 0 if k < k0 else 1
                if d > 0:
                    s.add[cote][i] += d
                    if k in retraits_prec:
                        s.recouvre[i] += d
                elif d < 0:
                    s.rem[cote][i] += -d
                    retraits.add(k)
            for k, m in prec.items():
                if k not in cur and interieur(k):
                    s.rem[0 if k < k0 else 1][i] += m
                    s.disparus[i] += 1
                    retraits.add(k)
            s.presents_prec[i] = sum(1 for k in prec if interieur(k))
            retraits_prec = retraits
        prec = cur
    return s


# --- outils ------------------------------------------------------------------

def _base_glissante(x: np.ndarray, w: int = FENETRE_BASE) -> np.ndarray:
    """Médiane glissante causale — la « ligne de base » des fiches B1/D1."""
    out = np.full(len(x), np.nan)
    for i in range(w, len(x)):
        out[i] = np.nanmedian(x[i - w:i])
    return out


# --- les séries, une fonction par fiche --------------------------------------

def a1_ofi(s: SeriesJour) -> np.ndarray:
    """OFI agrégé par photo : (ajouts − retraits) bid − (ajouts − retraits) ask."""
    x = (s.add[0] - s.rem[0]) - (s.add[1] - s.rem[1])
    x[0] = np.nan
    return x

def a4_microprice(s: SeriesJour) -> np.ndarray:
    """Microprice − mid, en paliers. Pondération par les volumes OPPOSÉS."""
    pb = (s.best_k[0] + 0.5) * s.bs
    pa = (s.best_k[1] + 0.5) * s.bs
    micro = (pb * s.best_m[1] + pa * s.best_m[0]) / (s.best_m[0] + s.best_m[1])
    return (micro - s.mid) / s.bs

def b1_hazard(s: SeriesJour) -> np.ndarray:
    """Taux de disparition de paliers par photo, en ÉCART à sa ligne de base
    (entrée au banc, correction II.2)."""
    h = np.divide(s.disparus, s.presents_prec,
                  out=np.full(len(s.t), np.nan), where=s.presents_prec > 0)
    return h - _base_glissante(h)

def b2_resilience(s: SeriesJour) -> np.ndarray:
    """Masse recouvrée aux paliers en retrait à la transition précédente,
    rapportée au retrait — la reformation, agrégée au pas 1."""
    r_tot = s.rem[0] + s.rem[1]
    r_prec = np.roll(r_tot, 1)
    r_prec[0] = np.nan
    return np.divide(s.recouvre, r_prec, out=np.full(len(s.t), np.nan),
                     where=r_prec > 0)

def b5_premier_passage(s: SeriesJour) -> np.ndarray:
    """L'ÂGE du niveau : photos écoulées depuis le dernier déplacement du mid
    d'au moins un palier, plafonné à HORIZON_B5.

    ⚠️ CORRIGÉ À L'AUDIT DU 05/08 : la première version mesurait le délai
    JUSQU'AU prochain déplacement — une feature qui regarde le futur, donc
    qui aurait fui la cible à É4. Celle-ci est strictement causale : même
    grandeur (premier passage), lue vers l'arrière."""
    out = np.full(len(s.t), np.nan)
    ref, age = s.mid[0], 0
    for i in range(1, len(s.t)):
        if abs(s.mid[i] - ref) >= s.bs[i]:
            ref, age = s.mid[i], 0
        else:
            age += 1
        out[i] = min(age, HORIZON_B5)
    return out

def c1_concentration(s: SeriesJour) -> np.ndarray:
    """Herfindahl de la bande, moyenne des deux côtés — le représentant le
    moins cher de la famille (fiche C1)."""
    return (s.herf[0] + s.herf[1]) / 2

def c2_courbure(s: SeriesJour) -> np.ndarray:
    """Convexité du profil cumulé : 2·cum(milieu) − cum(proche) − cum(loin),
    normalisée par la masse totale — POSITIF = le cumul bombe au-dessus de la
    corde = masse au contact ; négatif = masse au large.

    ⚠️ CORRIGÉ À L'AUDIT DU 05-06/08 (constat F4) : la première version
    prenait la moyenne des différences secondes d'une somme cumulée — qui
    TÉLESCOPE algébriquement en (dernier bin − premier bin)/14, jetant les
    quatorze bins intermédiaires, c'est-à-dire toute la forme."""
    cum = np.cumsum(s.profil, axis=1)
    tot = cum[:, -1]
    m = NB_BINS // 2
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(tot > 0,
                        (2 * cum[:, m] - cum[:, 0] - cum[:, -1]) / tot, np.nan)

def c3_diffusion(s: SeriesJour) -> np.ndarray:
    """Exposant de diffusion glissant, par rapport des déplacements quadratiques
    à lag 16 et lag 1 (simplification déclarée : 2 lags, pas 5)."""
    x = s.mid
    out = np.full(len(x), np.nan)
    w = FENETRE_BASE
    d1 = np.diff(x) ** 2
    d16 = (x[16:] - x[:-16]) ** 2
    for i in range(w + 16, len(x)):
        m1 = d1[i - w:i].mean()
        m16 = d16[i - w - 16:i - 16].mean()
        if m1 > 0 and m16 > 0:
            out[i] = np.log2(m16 / (16 * m1)) / np.log2(16) + 1
    return out

def d1_ralentissement(s: SeriesJour) -> np.ndarray:
    """Autocorrélation lag-1 glissante de la masse de bande, en écart à sa
    ligne de base (correction II.2)."""
    m = s.m_tot[0] + s.m_tot[1]
    w = FENETRE_BASE
    ac = np.full(len(m), np.nan)
    for i in range(w, len(m)):
        seg = m[i - w:i]
        a, b = seg[:-1], seg[1:]
        sa, sb = a.std(), b.std()
        if sa > 0 and sb > 0:
            ac[i] = float(np.corrcoef(a, b)[0, 1])
    return ac - _base_glissante(ac)

def t0_temoin(s: SeriesJour) -> np.ndarray:
    """Le témoin trivial : la masse brute de la bande, telle quelle."""
    return s.m_tot[0] + s.m_tot[1]


# --- avec exécutions (A3, B3, D2) — l'interface, réelle plus tard ------------

def a3_era(s: SeriesJour, e_par_photo: np.ndarray) -> np.ndarray:
    """Part MANGÉE du flux sortant : e / (e + retraits). La décomposition
    par palier vit aux étages suivants ; ceci est sa série d'É0/É2."""
    sortant = e_par_photo + s.rem[0] + s.rem[1]
    return np.divide(e_par_photo, sortant, out=np.full(len(s.t), np.nan),
                     where=sortant > 0)


EXTRACTEURS = {
    "A1 · OFI": a1_ofi,
    "A4 · microprice": a4_microprice,
    "B1 · hazard rate (version palier)": b1_hazard,
    "B2 · résilience": b2_resilience,
    "B5 · premier passage": b5_premier_passage,
    "C1 · concentration": c1_concentration,
    "C2 · forme et courbure": c2_courbure,
    "C3 · diffusion anormale": c3_diffusion,
    "D1 · ralentissement critique": d1_ralentissement,
    "T0 · masse brute au palier": t0_temoin,
}

#: Sans extracteur, avec leur raison — la boucle les laisse en attente.
ABSENTS = {
    "A2 · OFI localisé au mur": "attend la définition de « mur » (B7)",
    "A3 · flux signé e/r/a": "attend le flux exécuté par palier (transactions "
                             "agrégées) — interface `a3_era` prête",
    "A5 · propagateur": "attend la calibration hors ligne du noyau",
    "A6 · auto-excitation (Hawkes)": "série = estimation Hawkes (heures) — "
                                     "coût non payé en douce",
    "B3 · réapprovisionnement (iceberg)": "dépend d'A3 (flux exécuté)",
    "B4 · absorption au contact": "attend la définition de « contact » (B7)",
    "D2 · cascades": "dépend d'A3 (flux exécuté)",
}


def series_du_jour(chemin_deep: Path, dist_max: float = 0.005) -> dict[str, np.ndarray]:
    """Toutes les séries extractibles d'un jour-symbole, index commun (photos)."""
    s = charge(chemin_deep, dist_max)
    return {nom: fn(s) for nom, fn in EXTRACTEURS.items()}
