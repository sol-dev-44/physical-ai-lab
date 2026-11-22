from pathlib import Path

import pytest
from lab_agent.registry import HALT, Registry, Tool
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


class _DenyAll:
    name = "deny_all"

    def check(self, _tool, _args):
        return "always"


def _halt_gate(tmp_path):
    reg = Registry()
    reg.add(Tool("base.stop", "stop", lambda _a: None, tags=frozenset({HALT})))
    reg.add(Tool("base.drive", "drive", lambda _a: None))
    reg.add_interlock(_DenyAll())
    return SafetyGate(reg, stop_file=tmp_path / "STOP")


def test_halt_tools_pass_the_stop_file_and_interlocks(tmp_path):
    g = _halt_gate(tmp_path)
    (tmp_path / "STOP").touch()
    d = g.check(Request("base.stop", {}, "system"))
    assert d.allow and d.rule == "halt"
    other = g.check(Request("base.drive", {}, "human"))
    assert not other.allow and other.rule == "stop_file"


def test_halt_tools_pass_interlocks_without_a_stop_file(tmp_path):
    g = _halt_gate(tmp_path)
    assert g.check(Request("base.stop", {}, "system")).allow
    d = g.check(Request("base.drive", {}, "human"))
    assert not d.allow and d.rule == "interlock"


def test_halt_tools_still_validate_their_args(tmp_path):
    g = _halt_gate(tmp_path)
    d = g.check(Request("base.stop", {"speed": 1}, "system"))
    assert not d.allow and d.rule == "args"


def test_halt_tools_pass_for_remote_automated_requests(tmp_path):
    g = _halt_gate(tmp_path)
    assert g.check(Request("base.stop", {}, "web", remote=True, automated=True)).allow


def test_halt_branch_sits_before_the_rate_limit(tmp_path):
    reg = Registry()
    reg.add(Tool("base.stop", "stop", lambda _a: None, tags=frozenset({HALT})))
    reg.add(Tool("base.drive", "drive", lambda _a: None, min_interval_s=5.0))
    g = SafetyGate(reg, stop_file=tmp_path / "STOP", clock=lambda: 0.0)
    g.record_sent("base.drive")
    g.record_sent("base.stop")
    assert g.check(Request("base.drive", {}, "human")).rule == "rate_limit"
    assert g.check(Request("base.stop", {}, "system")).allow


def test_halt_reason_notes_the_stop_file(tmp_path):
    g = _halt_gate(tmp_path)
    assert g.check(Request("base.stop", {}, "system")).reason == "stop commands always pass"
    (tmp_path / "STOP").touch()
    d = g.check(Request("base.stop", {}, "system"))
    assert d.reason == "stop commands always pass (STOP file present)"


def test_registry_rejects_non_frozenset_tags():
    with pytest.raises(TypeError):
        Registry().add(Tool("x.go", "go", lambda _a: None, tags="asphalt"))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "opts",
    [
        {"requires_confirmation": True},
        {"manual_only": True},
        {"min_interval_s": 1.0},
        {"duration_arg": "seconds", "max_duration_s": 1.0},
    ],
)
def test_registry_rejects_halt_tools_with_other_gate_rules(opts):
    with pytest.raises(ValueError, match="halt tool cannot be"):
        Registry().add(Tool("base.stop", "stop", lambda _a: None, tags=frozenset({HALT}), **opts))
