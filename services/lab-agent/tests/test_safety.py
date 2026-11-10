from pathlib import Path

from lab_agent.registry import Registry, Tool
from lab_agent.safety import Request, SafetyGate
from pydantic import BaseModel, ConfigDict


class Secs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    seconds: float


def gate(tmp_path: Path, **tool_opts) -> SafetyGate:
    reg = Registry()
    reg.add(Tool("x.go", "go", lambda _a: None, **tool_opts))
    t = [0.0]
    g = SafetyGate(reg, stop_file=tmp_path / "STOP", clock=lambda: t[0])
    g._t = t  # type: ignore[attr-defined]
    return g


def test_unknown_tool_denied(tmp_path):
    assert gate(tmp_path).check(Request("nope.go", {}, "cli")).rule == "allowlist"


def test_bad_args_denied(tmp_path):
    g = gate(tmp_path)
    assert g.check(Request("x.go", {"extra": 1}, "cli")).rule == "args"


def test_stop_file_denies_everything(tmp_path):
    g = gate(tmp_path)
    (tmp_path / "STOP").touch()
    assert g.check(Request("x.go", {}, "cli")).rule == "stop_file"


def test_duration_cap(tmp_path):
    g = gate(tmp_path, args_model=Secs, duration_arg="seconds", max_duration_s=3)
    assert g.check(Request("x.go", {"seconds": 2}, "cli")).allow
    assert g.check(Request("x.go", {"seconds": 4}, "cli")).rule == "duration_cap"
    assert g.check(Request("x.go", {"seconds": 0}, "cli")).rule == "duration_cap"


def test_rate_limit(tmp_path):
    g = gate(tmp_path, min_interval_s=1)
    assert g.check(Request("x.go", {}, "cli")).allow
    g.record_sent("x.go")
    assert g.check(Request("x.go", {}, "cli")).rule == "rate_limit"
    g._t[0] = 1.5  # type: ignore[attr-defined]
    assert g.check(Request("x.go", {}, "cli")).allow


def test_confirmation_and_manual_only(tmp_path):
    g = gate(tmp_path, requires_confirmation=True, manual_only=True)
    assert g.check(Request("x.go", {}, "human")).rule == "requires_confirmation"
    assert g.check(Request("x.go", {}, "human", confirmed=True, remote=True)).rule == "manual_only"
    assert g.check(Request("x.go", {}, "human", confirmed=True)).allow
