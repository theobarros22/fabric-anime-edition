import os, sys, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "voice"))
from job_estado import Job


def test_same_input_reuses(tmp_path):
    j = Job(str(tmp_path / "s.json")); imp = Job.impressao(text="oi", voice="v", model="m")
    assert j.feito("a", imp) is None
    j.registrar("a", imp, chars=2); assert j.feito("a", imp)["chars"] == 2
    assert j.feito("a", Job.impressao(text="oi!", voice="v", model="m")) is None   # changed text => redo


def test_preview_lock(tmp_path):
    j = Job(str(tmp_path / "s.json")); imp = Job.impressao(text="x")
    with pytest.raises(SystemExit): j.exigir_aprovacao("prev", imp)
    j.registrar("prev", imp); j.aprovar("prev"); j.exigir_aprovacao("prev", imp)
    with pytest.raises(SystemExit): j.exigir_aprovacao("prev", Job.impressao(text="y"))   # approval is per-fingerprint


def test_secrets_never_stored(tmp_path):
    j = Job(str(tmp_path / "s.json")); imp = Job.impressao(a=1)
    j.registrar("a", imp, api_key="sk-123", url="https://x?sig=abc", ok="fine")
    r = j.d["etapas"]["a"]["resultado"]; assert r["api_key"] == "***removed***" and r["url"] == "***removed***" and r["ok"] == "fine"
