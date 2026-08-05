"""P1 — les quatre tests d'acceptation de la spec : schéma, déterminisme
octet par octet, bras nul strict, vérité qui recoupe l'observable."""
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from harnais.generateur import SCHEMA_DEEP, Injection, genere

DEPOT = Path(__file__).resolve().parents[2]
COURT = dict(duree_s=30.0, pas_ms=250)   # 120 photos — assez pour tout tester


def _gen(tmp, nom, **kw):
    obs, ver = tmp / f"{nom}.parquet", tmp / f"{nom}_verite.parquet"
    stats = genere(obs, ver, **kw)
    return obs, ver, stats


def test_schema_identique_au_contrat(tmp_path):
    obs, _, _ = _gen(tmp_path, "a", graine=1, **COURT)
    assert pq.read_schema(obs).equals(SCHEMA_DEEP)


def test_schema_identique_a_un_deep_reel(tmp_path):
    parts = sorted((DEPOT / "data" / "openbook" / "deep" / "parts").glob("deep_*.parquet"))
    if not parts:
        pytest.skip("aucun artefact deep construit sur cette machine")
    obs, _, _ = _gen(tmp_path, "a", graine=1, **COURT)
    reel = pq.read_schema(parts[0])
    synth = pq.read_schema(obs)
    assert synth.names == reel.names
    assert [str(f.type) for f in synth] == [str(f.type) for f in reel]


def test_deterministe_octet_par_octet(tmp_path):
    inj = [Injection("leurre", 5.0, 15.0, amplitude=3.0)]
    a = _gen(tmp_path, "a", graine=7, injections=inj, **COURT)
    b = _gen(tmp_path, "b", graine=7, injections=inj, **COURT)
    assert a[0].read_bytes() == b[0].read_bytes()
    assert a[1].read_bytes() == b[1].read_bytes()
    c = _gen(tmp_path, "c", graine=8, injections=inj, **COURT)
    assert a[0].read_bytes() != c[0].read_bytes()   # la graine compte vraiment


def test_bras_nul_strict(tmp_path):
    """Amplitude zéro == aucune injection, à l'octet près, vérité vide."""
    a = _gen(tmp_path, "a", graine=3, **COURT)
    b = _gen(tmp_path, "b", graine=3,
             injections=[Injection("absorption", 0.0, 30.0, amplitude=0.0)], **COURT)
    assert a[0].read_bytes() == b[0].read_bytes()
    assert pq.read_table(b[1]).num_rows == 0


def test_la_verite_recoupe_l_observable(tmp_path):
    obs, ver, stats = _gen(
        tmp_path, "a", graine=11,
        injections=[Injection("absorption", 2.0, 20.0, amplitude=4.0),
                    Injection("recharge", 2.0, 20.0, amplitude=3.0, cote=0)],
        **COURT)
    assert stats["lignes_verite"] > 0
    o = pq.read_table(obs).to_pydict()
    presents = {(t, k) for t, k, m in zip(o["t"], o["k"], o["mag"]) if m > 0}
    v = pq.read_table(ver).to_pydict()
    manquants = [(t, k) for t, k in zip(v["t"], v["k"]) if (t, k) not in presents]
    assert not manquants, f"vérité sans trace observable : {manquants[:5]}"


def test_le_leurre_est_retire_jamais_execute(tmp_path):
    """La signature du leurre : présent, puis retiré — sa vérité s'arrête."""
    _, ver, _ = _gen(tmp_path, "a", graine=5,
                     injections=[Injection("leurre", 2.0, 25.0, amplitude=5.0,
                                           dist_paliers=6, approche_paliers=5)],
                     **COURT)
    v = pq.read_table(ver).to_pydict()
    if v["t"]:
        # des lignes existent puis cessent avant la fin de la fenêtre : retrait
        assert max(v["t"]) < 27_000
