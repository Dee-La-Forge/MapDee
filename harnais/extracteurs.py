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

import re

from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from harnais.b7 import B7, DEMI_VOISINAGE_REL

DEPOT = Path(__file__).resolve().parent.parent

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
        self.jour = self.coin = None  # parsés du nom de fichier deep_<j>_<c>
        self.k_mur = [None, None]    # palier du MUR le plus proche du mid (B7)
        self.mag_mur = [None, None]  # sa masse — NaN si aucun mur ce côté
        self.a2_devant = [None, None]  # flux net DEVANT le mur (entre mid et lui)


def tronque_series(s: SeriesJour, n: int) -> SeriesJour:
    """Le même jour, coupé aux n premières photos — TOUT attribut indexé
    par photo est tranché [:n], le reste copié tel quel. Sert la garde de
    causalité (`00` §3, zéro lookahead) : pour un extracteur causal,
    ext(tronque(s, n)) == ext(s)[:n] — si l'égalité tombe, l'extracteur
    regarde le futur et le test/diagnostic REFUSE.

    Le critère « len == len(s.mid) ⇒ indexé par photo » est une inférence
    de structure qui se trompe DU BON CÔTÉ : un attribut mal classé
    produit une fausse alerte, jamais un faux blanc-seing. NE PAS
    l'assouplir le jour où une fausse alerte apparaîtra — la corriger en
    nommant l'attribut."""
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
    # identité du jour-symbole, lue du NOM (deep_<jour>_<coin>.parquet) —
    # None sur un fichier synthétique : les extracteurs B7 rendent alors NaN
    m_nom = re.match(r"deep_(\d{8})_(BTC|ETH)\.parquet$", Path(chemin_deep).name)
    if m_nom:
        s.jour, s.coin = m_nom.group(1), m_nom.group(2)
    M_mur = B7[s.coin]["M"] if s.coin else None
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
    for cote in (0, 1):
        s.k_mur[cote] = np.full(n, np.nan)
        s.mag_mur[cote] = np.full(n, np.nan)
        s.a2_devant[cote] = np.zeros(n)
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

        # --- LE MUR LE PLUS PROCHE, par côté (B7, `03` bloc du 06/08) -------
        # ratio = mag / médiane(voisinage ±0,05 % du mid), mur si ≥ M.
        # Balayage DEPUIS le mid vers l'extérieur, arrêt au premier mur —
        # c'est ce qui rend le coût vivable (« il faut d'abord situer le
        # mur — le vrai coût est là », fiche A2). Causal : cette photo seule.
        if M_mur is not None:
            ordre_k = np.argsort(kk)
            kks, mms = kk[ordre_k], mm[ordre_k]
            demi_k = max(1, round(DEMI_VOISINAGE_REL * mid / bs))
            i0 = int(np.searchsorted(kks, k0))
            for cote, indices in ((0, range(i0 - 1, -1, -1)),
                                  (1, range(i0 + (1 if i0 < len(kks) and kks[i0] == k0 else 0), len(kks)))):
                for j in indices:
                    a = int(np.searchsorted(kks, kks[j] - demi_k, side="left"))
                    b = int(np.searchsorted(kks, kks[j] + demi_k, side="right"))
                    med = float(np.median(mms[a:b])) if b > a else np.nan
                    if med > 0 and mms[j] / med >= M_mur:
                        s.k_mur[cote][i] = kks[j]
                        s.mag_mur[cote][i] = mms[j]
                        break

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
                # A2 : flux net DEVANT le mur — paliers STRICTEMENT entre le
                # mid et le mur le plus proche de CE côté, à CETTE photo
                # (causal : mur du présent, flux présent-contre-passé)
                km = s.k_mur[cote][i]
                if km == km:          # non-NaN
                    if (cote == 0 and km < k < k0) or (cote == 1 and k0 < k < km):
                        s.a2_devant[cote][i] += d
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


def a2_ofi_mur(s: SeriesJour) -> np.ndarray:
    """OFI localisé DEVANT le mur (fiche A2, définitions B7 du 06/08) : flux
    net des paliers STRICTEMENT entre le mid et le mur le plus proche, bid −
    ask — le discriminant de la fiche (« celui devant lequel le flux se vide
    cède le premier »). Choix déclarés : le mur jugé = le plus proche du mid
    par côté ; photo sans mur d'un côté = contribution 0. Sans identité de
    symbole (jour synthétique) : NaN — les constantes B7 sont par symbole."""
    if s.coin is None:
        return np.full(len(s.t), np.nan)
    x = s.a2_devant[0] - s.a2_devant[1]
    x[0] = np.nan
    return x


def b4_absorption(s: SeriesJour) -> np.ndarray:
    """Absorption au contact (fiche B4 ; contact = première transaction au
    palier du mur, ADR-010) : masse exécutée sur le mur le plus proche entre
    deux photos, rapportée à la masse du mur à la photo PRÉCÉDENTE — max des
    deux côtés, 0 sans contact (série dense, événements rares = pics ;
    déclaré). Causal : mur et masse de i−1, transactions dans (t[i−1], t[i]].
    Source : cache certifié `trades_light` (les prix touchés, ADR-009)."""
    n = len(s.t)
    if s.coin is None:
        return np.full(n, np.nan)
    cache = (DEPOT / "data" / "openbook" / "trades_light" / "parts"
             / f"trades_{s.jour}_{s.coin}.parquet")
    if not cache.exists():
        raise FileNotFoundError(
            f"cache trades absent : {cache.name} — construire d'abord "
            f"chantiers/construit_trades_cache.py (B4 exige les prix "
            f"touchés, ADR-009/010)")
    tb = pq.read_table(cache, columns=["t_ms", "px", "sz"])
    tt = tb["t_ms"].to_numpy()
    px = tb["px"].to_numpy().astype(np.float64)
    sz = tb["sz"].to_numpy().astype(np.float64)
    lo = np.searchsorted(tt, s.t[:-1], side="right")
    hi = np.searchsorted(tt, s.t[1:], side="right")
    out = np.full(n, np.nan)
    if n > 1:
        out[1:] = 0.0
    for i in range(1, n):
        a, b = lo[i - 1], hi[i - 1]
        if a >= b:
            continue
        val = 0.0
        kk_tr = (px[a:b] // s.bs[i - 1]).astype(np.int64)
        dollars = px[a:b] * sz[a:b]
        for cote in (0, 1):
            km, mg = s.k_mur[cote][i - 1], s.mag_mur[cote][i - 1]
            if km == km and mg > 0:
                masse = float(dollars[kk_tr == int(km)].sum())
                if masse > 0:
                    val = max(val, masse / mg)
        out[i] = val
    return out


EXTRACTEURS = {
    "A1 · OFI": a1_ofi,
    "A2 · OFI localisé au mur": a2_ofi_mur,
    "B4 · absorption au contact": b4_absorption,
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
    "A3 · flux signé e/r/a": "attend le flux exécuté par palier (transactions "
                             "agrégées) — interface `a3_era` prête",
    "A5 · propagateur": "attend la calibration hors ligne du noyau",
    "A6 · auto-excitation (Hawkes)": "série = estimation Hawkes (heures) — "
                                     "coût non payé en douce",
    "B3 · réapprovisionnement (iceberg)": "dépend d'A3 (flux exécuté)",
    "D2 · cascades": "dépend d'A3 (flux exécuté)",
}


def series_du_jour(chemin_deep: Path, dist_max: float = 0.005) -> dict[str, np.ndarray]:
    """Toutes les séries extractibles d'un jour-symbole, index commun (photos)."""
    s = charge(chemin_deep, dist_max)
    return {nom: fn(s) for nom, fn in EXTRACTEURS.items()}
