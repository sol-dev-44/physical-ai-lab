# Robot console, step 1: skeleton on fake devices. Implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Drive fake wheels from a phone browser through the lab's runner and safety gate, with a
hold-to-drive lease, a watchdog stop and a live (fake) sensor stream, all runnable on the Mac.

**Architecture:** The lab agent gains a `console` package: a Starlette web server with one
WebSocket per browser. Browser input becomes `Runner.request("base.drive" | "base.stop")` calls,
so every command is gated and logged. A `DriveLease` (300 ms, renewed by heartbeats) is checked by
a new `drive_lease` interlock, and a watchdog task stops the wheels when it lapses. Stop tools are
tagged `halt` and pass the STOP file and interlocks. The exp003 tool set (new workspace package)
provides `base.drive` and `base.stop` on fake wheels. A React app in `apps/robot-console` is built
to static files that the console serves.

**Tech stack:** Python 3.12, pydantic 2, Starlette and uvicorn (new optional extra), pytest;
React 19, TypeScript 5.9, zod 4, Vite, Vitest 5, Testing Library.

**Spec:** [../CONTROL_APP.md](../CONTROL_APP.md). This plan covers "Order of work", step 1 only.

**Before starting:** in a fresh worktree run `pnpm install` and `uv sync --all-packages --locked`
(AGENTS.md). Read `services/lab-agent/src/lab_agent/{runner,safety,registry,interlocks}.py` first.

---

## File map

| File | Responsibility |
|---|---|
| `docs/adr/0014-robot-console.md` (new) | The decision: LAN-only console, pairing token, halt tools, live camera never saved |
| `services/lab-agent/src/lab_agent/registry.py` | `HALT` tag constant |
| `services/lab-agent/src/lab_agent/safety.py` | `halt` tools pass STOP file, interlocks and rate limit |
| `services/lab-agent/src/lab_agent/lease.py` (new) | `DriveLease`: a renewable time window |
| `services/lab-agent/src/lab_agent/interlocks.py` | `LeaseRequired` interlock |
| `services/lab-agent/src/lab_agent/devices/base.py`, `devices/fake.py` | `Wheels` protocol, `FakeWheels` |
| `experiments/exp003-household-robot/pyproject.toml`, `src/exp003_robot/tools.py` (new) | exp003 tool set: `base.drive`, `base.stop`, lease interlock |
| `services/lab-agent/src/lab_agent/console/protocol.py` (new) | WebSocket message models |
| `packages/schema/fixtures/console/` (new) | Message fixtures shared by Python and TypeScript tests |
| `services/lab-agent/src/lab_agent/console/telemetry.py` (new) | `Telemetry` protocol and `FakeTelemetry` |
| `services/lab-agent/src/lab_agent/console/drive.py` (new) | `DriveSession`: dedupe, lease, watchdog tick, stop |
| `services/lab-agent/src/lab_agent/console/server.py` (new) | Starlette app, pairing, WebSocket loop, watchdog task, `serve()` |
| `services/lab-agent/src/lab_agent/cli.py` | `lab console` subcommand |
| `apps/robot-console/` (new) | React app: protocol, socket hook, joystick, drive controller, Drive screen |

---

### Task 1: ADR 0014 and spec touch-ups

**Files:**
- Create: `docs/adr/0014-robot-console.md`
- Modify: `docs/adr/README.md` (add the row), `experiments/exp003-household-robot/CONTROL_APP.md`

- [ ] **Step 1: Write the ADR**

```markdown
# 0014: The robot console on the home network

**Context.** The household robot (exp003) needs a control app: hold-to-drive from a phone,
live sensors, a live camera view for debugging. ADR 0003 keeps the website away from hardware
and forbids inbound ports for that path. Live driving cannot wait for a 2 s queue poll.

**Decision.**

- The lab agent on the robot serves a "robot console": a web app plus one WebSocket per browser,
  on the home network only. No port forwarding, no tunnel; remote driving (phase 4) needs its
  own decision.
- Access needs a pairing token printed when the console starts. The browser sends it in its
  first WebSocket message; anything else is closed.
- The console is a client of the runner like the CLI and the queue worker: every command goes
  through `Runner.request` and the safety gate and is logged.
- Driving is a lease: a drive command is good for 300 ms and heartbeats renew it. A
  `drive_lease` interlock refuses drive commands without a live lease, and a watchdog stops the
  wheels when it lapses.
- Tools tagged `halt` (stopping the wheels) pass the STOP file, interlocks and rate limits, so a
  stop is never refused. Their arguments are still validated and the call is still logged.
- The live camera view is allowed on the home network for debugging. Frames stay in memory and
  are never written, synced or posted (ADR 0007).

**Consequences.** The robot opens a port on the LAN; anyone on the home Wi-Fi with the token can
drive it within the gate's limits. A crash of the agent stops its watchdog too, so until the
servo's own behaviour on lost communication is known, drive only with someone at the e-stop.
```

- [ ] **Step 2: Add the ADR to the index**

Open `docs/adr/README.md`, find the table or list of ADRs, and add a line for 0014 in the same
format as 0013, titled "The robot console on the home network".

- [ ] **Step 3: Align the spec with two details settled while planning**

In `experiments/exp003-household-robot/CONTROL_APP.md`, section "Safety", replace the sentence
starting "On start the console prints a pairing link" through "every request and WebSocket must
carry it." with:

```markdown
On start the console prints a pairing link with a random token; the app stores it in the
browser's local storage and sends it in its first WebSocket message (`hello`). The page itself
holds no data, so serving it without the token is fine.
```

and add this bullet after "The physical e-stop always wins.":

```markdown
- **A stop is never refused.** `base.stop` is tagged `halt`: it passes the STOP file, interlocks
  and rate limits (its arguments are still validated and it is still logged). Otherwise a
  `touch STOP` would leave the wheels turning.
```

- [ ] **Step 4: Commit**

```bash
git add docs/adr/0014-robot-console.md docs/adr/README.md experiments/exp003-household-robot/CONTROL_APP.md
git commit -m "docs: ADR 0014, the robot console on the home network"
```

---

### Task 2: Halt tools always pass the gate

**Files:**
- Modify: `services/lab-agent/src/lab_agent/registry.py`, `services/lab-agent/src/lab_agent/safety.py`
- Test: `services/lab-agent/tests/test_safety.py`

- [ ] **Step 1: Write the failing tests** (append to `tests/test_safety.py`)

```python
from lab_agent.registry import HALT


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
```

If `Registry`, `Tool`, `SafetyGate` or `Request` are not already imported at the top of
`tests/test_safety.py`, add `from lab_agent.registry import Registry, Tool` and
`from lab_agent.safety import Request, SafetyGate`.

- [ ] **Step 2: Run them and watch them fail**

Run: `uv run pytest services/lab-agent/tests/test_safety.py -k halt -v`
Expected: FAIL with `ImportError: cannot import name 'HALT'`.

- [ ] **Step 3: Add the constant** in `registry.py`, below the imports:

```python
#: Tag for tools that stop motion. The gate never refuses them (see safety.py).
HALT = "halt"
```

- [ ] **Step 4: Let halt tools through** in `safety.py`. Change the import to
`from .registry import HALT, Registry, Tool`, and make the start of `SafetyGate.check` read:

```python
    def check(self, req: Request) -> Decision:
        tool = self.registry.get(req.tool_name)
        if tool is not None and HALT in tool.tags:
            # A stop must never be refused: not by the STOP file, an interlock or a rate limit.
            try:
                args = tool.args_model.model_validate(req.raw_args)
            except ValidationError as e:
                return Decision(False, "args", e.errors(include_url=False)[0]["msg"])
            return Decision(True, "halt", "stop commands always pass", args=args)
        if self.stop_file.exists():
            return Decision(False, "stop_file", f"{self.stop_file} exists")
        if tool is None:
            return Decision(False, "allowlist", f"unknown tool {req.tool_name}")
```

Delete the old `tool = self.registry.get(...)` line and the old `if tool is None` block that
followed the STOP check; the rest of the method stays. Add one line to the module docstring:
"Tools tagged halt (stops) skip every rule but argument validation."

- [ ] **Step 5: Run the whole agent suite**

Run: `uv run pytest services/lab-agent -q`
Expected: all pass (the existing STOP and allowlist tests still pass).

- [ ] **Step 6: Commit**

```bash
git add services/lab-agent/src/lab_agent/registry.py services/lab-agent/src/lab_agent/safety.py services/lab-agent/tests/test_safety.py
git commit -m "lab-agent: halt tools always pass the gate"
```

---

### Task 3: Drive lease and its interlock

**Files:**
- Create: `services/lab-agent/src/lab_agent/lease.py`
- Modify: `services/lab-agent/src/lab_agent/interlocks.py`
- Test: `services/lab-agent/tests/test_lease.py`

- [ ] **Step 1: Write the failing tests**

```python
from lab_agent.interlocks import LeaseRequired
from lab_agent.lease import DriveLease
from lab_agent.registry import Tool


class Clock:
    def __init__(self) -> None:
        self.t = 100.0

    def __call__(self) -> float:
        return self.t


def test_lease_lives_for_its_ttl_after_each_renewal():
    c = Clock()
    lease = DriveLease(ttl_s=0.3, clock=c)
    assert not lease.alive()
    lease.renew()
    c.t += 0.29
    assert lease.alive()
    c.t += 0.02
    assert not lease.alive()
    lease.renew()
    assert lease.alive()


def test_cancel_ends_the_lease_at_once():
    lease = DriveLease(ttl_s=0.3, clock=Clock())
    lease.renew()
    lease.cancel()
    assert not lease.alive()


def test_interlock_refuses_guarded_tools_without_a_live_lease():
    c = Clock()
    lease = DriveLease(ttl_s=0.3, clock=c)
    rule = LeaseRequired(lease, frozenset({"base.drive"}))
    drive = Tool("base.drive", "drive", lambda _a: None)
    other = Tool("base.stop", "stop", lambda _a: None)
    assert "hold the drive button" in (rule.check(drive, None) or "")
    assert rule.check(other, None) is None
    lease.renew()
    assert rule.check(drive, None) is None
    c.t += 1.0
    assert rule.check(drive, None) is not None
```

- [ ] **Step 2: Run and watch them fail**

Run: `uv run pytest services/lab-agent/tests/test_lease.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'lab_agent.lease'`.

- [ ] **Step 3: Write `lease.py`**

```python
"""A drive lease: motion is allowed only inside a short, renewable window.

The robot console renews it on every heartbeat while the drive button is held. When the
heartbeats stop (button released, tab closed, Wi-Fi gone) it lapses, the drive_lease
interlock refuses further drive commands, and the console's watchdog stops the wheels.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class DriveLease:
    ttl_s: float = 0.3
    clock: Callable[[], float] = time.monotonic
    _until: float = field(default=float("-inf"), init=False)

    def renew(self) -> None:
        self._until = self.clock() + self.ttl_s

    def cancel(self) -> None:
        self._until = float("-inf")

    def alive(self) -> bool:
        return self.clock() < self._until
```

- [ ] **Step 4: Add the interlock** to `interlocks.py` (import `from .lease import DriveLease`
at the top, add the class at the end):

```python
@dataclass
class LeaseRequired:
    """Deny guarded tools unless a drive lease is live: no held button, no motion."""

    lease: DriveLease
    guarded: frozenset[str]
    name: str = "drive_lease"

    def check(self, tool: Tool, _args: BaseModel | None) -> str | None:
        if tool.name in self.guarded and not self.lease.alive():
            return "no live drive lease: hold the drive button"
        return None
```

- [ ] **Step 5: Run the tests**

Run: `uv run pytest services/lab-agent/tests/test_lease.py -v`
Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add services/lab-agent/src/lab_agent/lease.py services/lab-agent/src/lab_agent/interlocks.py services/lab-agent/tests/test_lease.py
git commit -m "lab-agent: drive lease and drive_lease interlock"
```

---

### Task 4: Wheels device and the exp003 tool set

**Files:**
- Modify: `services/lab-agent/src/lab_agent/devices/base.py`, `services/lab-agent/src/lab_agent/devices/fake.py`, root `pyproject.toml`
- Create: `experiments/exp003-household-robot/pyproject.toml`,
  `experiments/exp003-household-robot/src/exp003_robot/__init__.py`,
  `experiments/exp003-household-robot/src/exp003_robot/tools.py`
- Test: `experiments/exp003-household-robot/tests/test_exp003_tools.py`

- [ ] **Step 1: Add the device protocol** to `devices/base.py`:

```python
class Wheels(Protocol):
    """A differential drive: set each wheel's ground speed in m/s (+ is forward)."""

    id: str

    def set_speeds(self, left_m_s: float, right_m_s: float) -> None: ...
```

and the fake to `devices/fake.py`:

```python
@dataclass
class FakeWheels:
    id: str = "fake-wheels"
    speeds: tuple[float, float] = (0.0, 0.0)
    history: list[tuple[float, float]] = field(default_factory=list)

    def set_speeds(self, left_m_s: float, right_m_s: float) -> None:
        self.speeds = (left_m_s, right_m_s)
        self.history.append(self.speeds)
```

- [ ] **Step 2: Create the workspace package.** `experiments/exp003-household-robot/pyproject.toml`:

```toml
[project]
name = "exp003-household-robot"
version = "0.1.0"
description = "Experiment 3: the household robot's tool set."
requires-python = ">=3.12"
dependencies = ["lab-agent[console]"]

[tool.uv.sources]
lab-agent = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/exp003_robot"]
```

`src/exp003_robot/__init__.py`:

```python
"""Experiment 3: the household robot."""
```

In the root `pyproject.toml`, add `"experiments/exp003-household-robot"` to
`[tool.uv.workspace] members`. In `services/lab-agent/pyproject.toml`, under
`[project.optional-dependencies]`, add:

```toml
console = ["starlette>=0.41", "uvicorn>=0.32"]
```

Run: `uv lock && uv sync --all-packages`
Expected: starlette and uvicorn installed; `uv.lock` updated.

- [ ] **Step 3: Write the failing tests** `tests/test_exp003_tools.py`:

```python
from pathlib import Path

import pytest
from exp003_robot.tools import MAX_V_M_S, TRACK_M, build, wheel_speeds
from lab_agent.devices.fake import FakeWheels
from lab_agent.lease import DriveLease
from lab_agent.log import EventLog, read_log
from lab_agent.runner import Runner


class Clock:
    t = 50.0

    def __call__(self) -> float:
        return self.t


@pytest.fixture
def rig(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)  # isolate the STOP file
    clock = Clock()
    lease = DriveLease(ttl_s=0.3, clock=clock)
    wheels = FakeWheels()
    log = EventLog(tmp_path / "events" / "exp003" / "r1.jsonl", "exp003-t-r1")
    runner = Runner(build(lease=lease, wheels=wheels), log)
    runner.start("exp003-household-robot")
    return runner, lease, wheels, clock


def test_turning_left_slows_the_left_wheel():
    left, right = wheel_speeds(0.2, 1.0)
    assert left == pytest.approx(0.2 - TRACK_M / 2)
    assert right == pytest.approx(0.2 + TRACK_M / 2)


def test_drive_needs_a_live_lease(rig):
    runner, lease, wheels, _ = rig
    denied = runner.request("base.drive", {"v": 0.1, "w": 0.0}, actor="human")
    assert not denied.allowed and "drive_lease" in denied.checked.payload.reason
    lease.renew()
    ok = runner.request("base.drive", {"v": 0.1, "w": 0.0}, actor="human")
    assert ok.ok and wheels.speeds == (pytest.approx(0.1), pytest.approx(0.1))


def test_speed_over_the_cap_is_refused(rig):
    runner, lease, wheels, _ = rig
    lease.renew()
    r = runner.request("base.drive", {"v": MAX_V_M_S + 0.1, "w": 0.0}, actor="human")
    assert not r.allowed and r.checked.payload.rule == "args"
    assert wheels.history == []


def test_stop_always_works_even_with_a_stop_file(rig, tmp_path):
    runner, lease, wheels, _ = rig
    lease.renew()
    runner.request("base.drive", {"v": 0.1, "w": 0.0}, actor="human")
    (tmp_path / "STOP").touch()
    r = runner.request("base.stop", actor="system")
    assert r.ok and r.checked.payload.rule == "halt"
    assert wheels.speeds == (0.0, 0.0)


def test_every_step_is_logged_and_the_log_is_valid(rig):
    runner, lease, _, _ = rig
    lease.renew()
    runner.request("base.drive", {"v": 0.1, "w": 0.5}, actor="human")
    runner.request("base.stop", actor="human")
    runner.end()
    events = read_log(runner.log.path)
    assert [e.type for e in events].count("command.sent") == 2
```

- [ ] **Step 4: Run and watch them fail**

Run: `uv run pytest experiments/exp003-household-robot/tests/test_exp003_tools.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'exp003_robot.tools'`.

- [ ] **Step 5: Write `src/exp003_robot/tools.py`**

```python
"""Tool set for Experiment 3: the household robot's wheels.

With LAB_FAKE=1, or no EXP003_SERVO_PORT, the wheels are fake and their id starts with
"fake-", so a fake run can never be mistaken for a real one in the logs. Real STS3215
wheels arrive in step 2 of the console's order of work (CONTROL_APP.md).
"""

from __future__ import annotations

import os

from lab_agent.devices.base import Wheels
from lab_agent.devices.fake import FakeWheels
from lab_agent.interlocks import LeaseRequired
from lab_agent.lease import DriveLease
from lab_agent.registry import HALT, Registry, Tool
from pydantic import BaseModel, ConfigDict, Field

TRACK_M = 0.2976  # wheel centre to wheel centre (cad/exp003_cad/params.py, derive_base)
MAX_V_M_S = 0.3  # CONTROL_APP.md, Safety
MAX_W_RAD_S = 1.5
LEASE_S = 0.3


class Drive(BaseModel):
    """Drive for one lease: forward speed and turn rate."""

    model_config = ConfigDict(extra="forbid")
    v: float = Field(ge=-MAX_V_M_S, le=MAX_V_M_S, description="forward speed, m/s")
    w: float = Field(ge=-MAX_W_RAD_S, le=MAX_W_RAD_S, description="turn rate, rad/s, + is left")


def wheel_speeds(v: float, w: float, track_m: float = TRACK_M) -> tuple[float, float]:
    """(left, right) ground speeds for a differential drive."""
    half = w * track_m / 2
    return v - half, v + half


def _wheels() -> Wheels:
    if os.environ.get("LAB_FAKE") == "1" or not os.environ.get("EXP003_SERVO_PORT"):
        return FakeWheels(id="fake-wheels")
    raise SystemExit("real wheels are not wired yet: unset EXP003_SERVO_PORT or set LAB_FAKE=1")


def build(lease: DriveLease | None = None, wheels: Wheels | None = None) -> Registry:
    lease = lease or DriveLease(ttl_s=LEASE_S)
    wheels = wheels or _wheels()
    reg = Registry()

    def drive(args: BaseModel) -> None:
        assert isinstance(args, Drive)
        wheels.set_speeds(*wheel_speeds(args.v, args.w))

    def stop(_args: BaseModel) -> None:
        wheels.set_speeds(0.0, 0.0)

    reg.add(
        Tool(
            "base.drive",
            "Drive for one lease: forward speed v (m/s) and turn rate w (rad/s)",
            drive,
            args_model=Drive,
            device=wheels.id,
        )
    )
    reg.add(Tool("base.stop", "Stop both wheels", stop, device=wheels.id, tags=frozenset({HALT})))
    reg.add_interlock(LeaseRequired(lease, frozenset({"base.drive"})))
    return reg
```

- [ ] **Step 6: Run the tests**

Run: `uv run pytest experiments/exp003-household-robot/tests/test_exp003_tools.py -v`
Expected: 5 passed.

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml uv.lock services/lab-agent/pyproject.toml services/lab-agent/src/lab_agent/devices experiments/exp003-household-robot/pyproject.toml experiments/exp003-household-robot/src experiments/exp003-household-robot/tests
git commit -m "exp003: tool set with base.drive and base.stop on fake wheels"
```

---

### Task 5: Console protocol and shared fixtures

**Files:**
- Create: `services/lab-agent/src/lab_agent/console/__init__.py`, `services/lab-agent/src/lab_agent/console/protocol.py`
- Create: `packages/schema/fixtures/console/valid/*.json`, `packages/schema/fixtures/console/invalid/*.json`
- Test: `services/lab-agent/tests/test_console_protocol.py`

- [ ] **Step 1: Write the fixtures.** One message per file; the name's prefix says who sends
it (`client_` or `server_`).

`valid/client_hello.json`: `{"type": "hello", "token": "abc123"}`
`valid/client_drive.json`: `{"type": "drive", "v": 0.15, "w": -0.4, "seq": 7}`
`valid/client_heartbeat.json`: `{"type": "heartbeat", "seq": 8}`
`valid/client_stop.json`: `{"type": "stop"}`
`valid/server_welcome.json`:
`{"type": "welcome", "run_id": "exp003-20261121-120000-console", "max_v": 0.3, "max_w": 1.5, "lease_s": 0.3}`
`valid/server_refused.json`: `{"type": "refused", "rule": "interlock", "reason": "drive_lease: no live drive lease: hold the drive button"}`
`valid/server_state.json`:

```json
{
  "type": "state",
  "t": 1795290000.5,
  "fake": true,
  "battery": {"volts": 13.1, "amps": 0.42, "soc_pct": 88.0, "runtime_min": 310.0},
  "servos": [
    {"id": 1, "temp_c": 31.0, "load_pct": 4.0, "volts": 12.1},
    {"id": 2, "temp_c": 30.5, "load_pct": 3.5, "volts": 12.1}
  ],
  "tof": {"left_mm": 820, "center_mm": 1200, "right_mm": null},
  "cliff_mm": [42, 41, 43],
  "bumpers": [false, false],
  "wifi_dbm": -54.0,
  "pi_temp_c": 48.2,
  "lease_alive": false,
  "moving": false,
  "estop": false,
  "stop_file": false,
  "controller": {"connected": false, "battery_pct": null}
}
```

`invalid/client_drive_extra_field.json`: `{"type": "drive", "v": 0.1, "w": 0, "seq": 1, "boost": true}`
`invalid/client_drive_missing_w.json`: `{"type": "drive", "v": 0.1, "seq": 1}`
`invalid/client_heartbeat_negative_seq.json`: `{"type": "heartbeat", "seq": -1}`
`invalid/client_unknown_type.json`: `{"type": "teleport"}`
`invalid/server_state_missing_battery.json`: the valid state above with the `"battery"` key removed.

- [ ] **Step 2: Write the failing test**

```python
import json
from pathlib import Path

import pytest
from lab_agent.console.protocol import client_message, server_message
from pydantic import ValidationError

FIXTURES = Path(__file__).resolve().parents[3] / "packages" / "schema" / "fixtures" / "console"


def _adapter(path: Path):
    return client_message if path.name.startswith("client_") else server_message


VALID = sorted((FIXTURES / "valid").glob("*.json"))
INVALID = sorted((FIXTURES / "invalid").glob("*.json"))


@pytest.mark.parametrize("path", VALID, ids=lambda p: p.name)
def test_valid_messages_parse(path):
    _adapter(path).validate_python(json.loads(path.read_text()))


@pytest.mark.parametrize("path", INVALID, ids=lambda p: p.name)
def test_invalid_messages_are_rejected(path):
    with pytest.raises(ValidationError):
        _adapter(path).validate_python(json.loads(path.read_text()))


def test_there_are_fixtures_for_every_message_type():
    names = {p.stem for p in (FIXTURES / "valid").glob("*.json")}
    assert {"client_hello", "client_drive", "client_heartbeat", "client_stop"} <= names
    assert {"server_welcome", "server_state", "server_refused"} <= names
```

- [ ] **Step 3: Run and watch it fail**

Run: `uv run pytest services/lab-agent/tests/test_console_protocol.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'lab_agent.console'`.

- [ ] **Step 4: Write the protocol.** `console/__init__.py`:

```python
"""Robot console: the LAN web app's server side (docs/adr/0014-robot-console.md)."""
```

`console/protocol.py`:

```python
"""WebSocket messages between the robot console and the app.

Mirrored in apps/robot-console/src/protocol.ts; both sides test against
packages/schema/fixtures/console. Change both together.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class _Msg(BaseModel):
    model_config = ConfigDict(extra="forbid")


# Browser to robot
class Hello(_Msg):
    type: Literal["hello"]
    token: Annotated[str, Field(min_length=1)]


class DriveMsg(_Msg):
    type: Literal["drive"]
    v: float
    w: float
    seq: Annotated[int, Field(ge=0)]


class Heartbeat(_Msg):
    type: Literal["heartbeat"]
    seq: Annotated[int, Field(ge=0)]


class StopMsg(_Msg):
    type: Literal["stop"]


ClientMessage = Annotated[Hello | DriveMsg | Heartbeat | StopMsg, Field(discriminator="type")]
client_message: TypeAdapter[ClientMessage] = TypeAdapter(ClientMessage)


# Robot to browser
class Battery(_Msg):
    volts: float
    amps: float
    soc_pct: float
    runtime_min: float


class Servo(_Msg):
    id: int
    temp_c: float
    load_pct: float
    volts: float


class Tof(_Msg):
    left_mm: int | None
    center_mm: int | None
    right_mm: int | None


class Controller(_Msg):
    connected: bool
    battery_pct: float | None = None


class Welcome(_Msg):
    type: Literal["welcome"]
    run_id: str
    max_v: float
    max_w: float
    lease_s: float


class State(_Msg):
    type: Literal["state"]
    t: float
    fake: bool
    battery: Battery
    servos: list[Servo]
    tof: Tof
    cliff_mm: list[int | None]
    bumpers: list[bool]
    wifi_dbm: float | None
    pi_temp_c: float | None
    lease_alive: bool
    moving: bool
    estop: bool
    stop_file: bool
    controller: Controller


class Refused(_Msg):
    type: Literal["refused"]
    rule: str
    reason: str = ""


ServerMessage = Annotated[Welcome | State | Refused, Field(discriminator="type")]
server_message: TypeAdapter[ServerMessage] = TypeAdapter(ServerMessage)
```

> **Done 2026-11-21, then hardened after review (e254aa5):** the models are strict (no coercion)
> and every float is finite; `seq` is capped at 2^53 - 1 and the token at 256 characters; more
> invalid fixtures. The code in the repo, not this listing, is the reference for Task 10.

- [ ] **Step 5: Run the tests**

Run: `uv run pytest services/lab-agent/tests/test_console_protocol.py -v`
Expected: all pass (7 valid, 5 invalid, 1 coverage).

- [ ] **Step 6: Commit**

```bash
git add services/lab-agent/src/lab_agent/console packages/schema/fixtures/console services/lab-agent/tests/test_console_protocol.py
git commit -m "lab-agent: robot console protocol with shared fixtures"
```

---

### Task 6: Fake telemetry

**Files:**
- Create: `services/lab-agent/src/lab_agent/console/telemetry.py`
- Test: `services/lab-agent/tests/test_console_telemetry.py`

- [ ] **Step 1: Write the failing test**

```python
from lab_agent.console.protocol import State
from lab_agent.console.telemetry import FakeTelemetry


def test_fake_telemetry_fills_a_valid_state():
    reading = FakeTelemetry(clock=lambda: 12.0).read()
    state = State(
        type="state",
        t=0.0,
        lease_alive=False,
        moving=False,
        stop_file=False,
        **reading,
    )
    assert state.fake is True
    assert 12.0 < state.battery.volts < 13.6
    assert len(state.servos) == 2 and len(state.cliff_mm) == 3


def test_fake_battery_drifts_but_stays_in_range():
    volts = set()
    for t in range(0, 600, 37):
        reading = FakeTelemetry(clock=lambda t=t: float(t)).read()
        volts.add(round(reading["battery"]["volts"], 3))
    assert len(volts) > 1
    assert all(12.0 < v < 13.6 for v in volts)
```

- [ ] **Step 2: Run and watch it fail**

Run: `uv run pytest services/lab-agent/tests/test_console_telemetry.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'lab_agent.console.telemetry'`.

- [ ] **Step 3: Write `console/telemetry.py`**

```python
"""Telemetry: what the robot's sensors say, for the console's state stream.

Live only: readings are not events (CONTROL_APP.md, "What gets logged"). Anything that
matters for safety reaches the gate through an interlock instead. Real sources arrive with
the sensors (step 3 of the order of work); FakeTelemetry lets the app be built on the Mac.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol


class Telemetry(Protocol):
    def read(self) -> dict[str, Any]:
        """Every State field except type, t, lease_alive, moving and stop_file."""
        ...


@dataclass
class FakeTelemetry:
    clock: Callable[[], float] = time.monotonic

    def read(self) -> dict[str, Any]:
        t = self.clock()
        wobble = math.sin(t / 30.0)
        return {
            "fake": True,
            "battery": {
                "volts": 13.1 + 0.05 * wobble,
                "amps": 0.4 + 0.05 * wobble,
                "soc_pct": 88.0,
                "runtime_min": 310.0,
            },
            "servos": [
                {"id": 1, "temp_c": 31.0 + wobble, "load_pct": 4.0, "volts": 12.1},
                {"id": 2, "temp_c": 30.5 + wobble, "load_pct": 3.5, "volts": 12.1},
            ],
            "tof": {"left_mm": 820, "center_mm": int(1200 + 100 * wobble), "right_mm": None},
            "cliff_mm": [42, 41, 43],
            "bumpers": [False, False],
            "wifi_dbm": -54.0,
            "pi_temp_c": 48.0 + wobble,
            "estop": False,
            "controller": {"connected": False, "battery_pct": None},
        }
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest services/lab-agent/tests/test_console_telemetry.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add services/lab-agent/src/lab_agent/console/telemetry.py services/lab-agent/tests/test_console_telemetry.py
git commit -m "lab-agent: fake telemetry for the robot console"
```

---

### Task 7: Drive session (dedupe, lease, watchdog, stop)

**Files:**
- Create: `services/lab-agent/src/lab_agent/console/drive.py`
- Modify: `services/lab-agent/tests/conftest.py` (a drive rig shared by the console tests)
- Test: `services/lab-agent/tests/test_console_drive.py`

The lab agent's tests must not import an experiment's tool set, so the console tests get their
own minimal drive tools in `conftest.py`.

- [ ] **Step 1: Add the shared rig** to `services/lab-agent/tests/conftest.py`:

```python
from types import SimpleNamespace

from lab_agent.devices.fake import FakeWheels
from lab_agent.interlocks import LeaseRequired
from lab_agent.lease import DriveLease
from lab_agent.registry import HALT
from pydantic import BaseModel, ConfigDict, Field


class DriveArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    v: float = Field(ge=-0.3, le=0.3)
    w: float = Field(ge=-1.5, le=1.5)


class ManualClock:
    def __init__(self, t: float = 10.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t


@pytest.fixture
def drive_rig(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Build a runner with base.drive and base.stop on fake wheels behind a drive lease.
    Call it with a clock; the default is a ManualClock the test moves by hand."""
    monkeypatch.chdir(tmp_path)  # isolate the STOP file

    def make(clock=None):
        clock = clock or ManualClock()
        lease = DriveLease(ttl_s=0.3, clock=clock)
        wheels = FakeWheels()
        reg = Registry()

        def drive(a: DriveArgs) -> None:
            wheels.set_speeds(a.v - a.w * 0.15, a.v + a.w * 0.15)

        def stop(_a: BaseModel) -> None:
            wheels.set_speeds(0.0, 0.0)

        reg.add(Tool("base.drive", "drive", drive, args_model=DriveArgs, device=wheels.id))
        halt = frozenset({HALT})
        reg.add(Tool("base.stop", "stop", stop, device=wheels.id, tags=halt))
        reg.add_interlock(LeaseRequired(lease, frozenset({"base.drive"})))
        log = EventLog(tmp_path / "events" / "console.jsonl", "exp003-t-console")
        runner = Runner(reg, log)
        runner.start("exp003-household-robot")
        return SimpleNamespace(runner=runner, lease=lease, wheels=wheels, clock=clock)

    return make
```

- [ ] **Step 2: Write the failing tests** `tests/test_console_drive.py`:

```python
import pytest
from lab_agent.console.drive import DriveSession
from lab_agent.log import read_log


@pytest.fixture
def rig(drive_rig):
    r = drive_rig()
    return DriveSession(r.runner, r.lease, clock=r.clock), r.wheels, r.clock, r.runner


def sent(runner, tool):
    return [e for e in read_log(runner.log.path) if e.type == "command.sent" and e.tool == tool]


def test_first_drive_goes_through_and_renews_the_lease(rig):
    s, wheels, _, _ = rig
    r = s.drive(0.1, 0.0)
    assert r is not None and r.ok and s.moving
    assert wheels.speeds[0] == pytest.approx(0.1)


def test_small_or_fast_changes_are_not_resent(rig):
    s, _, clock, runner = rig
    s.drive(0.10, 0.0)
    clock.t += 0.05
    assert s.drive(0.20, 0.0) is None  # under 100 ms since the last send
    clock.t += 0.1
    assert s.drive(0.205, 0.0) is not None  # 100 ms passed, big change from 0.10
    clock.t += 0.1
    assert s.drive(0.21, 0.0) is None  # change too small to send
    assert len(sent(runner, "base.drive")) == 2


def test_heartbeat_keeps_the_lease_alive(rig):
    s, _, clock, _ = rig
    s.drive(0.1, 0.0)
    for _ in range(10):
        clock.t += 0.1
        s.heartbeat()
        assert s.tick() is None
    assert s.moving


def test_watchdog_stops_the_wheels_when_the_lease_lapses(rig):
    s, wheels, clock, runner = rig
    s.drive(0.1, 0.0)
    clock.t += 0.31
    r = s.tick()
    assert r is not None and r.ok
    assert wheels.speeds == (0.0, 0.0) and not s.moving
    assert s.tick() is None  # only once
    stop = sent(runner, "base.stop")
    assert len(stop) == 1 and stop[0].actor == "system"


def test_stop_cancels_the_lease_and_stops(rig):
    s, wheels, _, _ = rig
    s.drive(0.1, 0.0)
    r = s.stop()
    assert r is not None and r.ok and wheels.speeds == (0.0, 0.0) and not s.lease.alive()


def test_a_flood_of_stops_is_collapsed(rig):
    s, _, clock, runner = rig
    s.drive(0.1, 0.0)
    assert s.stop() is not None
    assert s.stop() is None  # already stopped, within 100 ms
    clock.t += 0.2
    assert s.stop() is not None  # later stops still go through
    assert len(sent(runner, "base.stop")) == 2


def test_a_refused_drive_is_returned_not_raised(rig, tmp_path):
    s, wheels, _, _ = rig
    (tmp_path / "STOP").touch()
    r = s.drive(0.1, 0.0)
    assert r is not None and not r.allowed and r.checked.payload.rule == "stop_file"
    assert wheels.history == [] and not s.moving
```

- [ ] **Step 3: Run and watch them fail**

Run: `uv run pytest services/lab-agent/tests/test_console_drive.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'lab_agent.console.drive'`.

- [ ] **Step 4: Write `console/drive.py`**

```python
"""One browser's driving: turns joystick input into gated, logged drive commands.

- drive(v, w) renews the lease and sends base.drive only on a meaningful change, at most
  every min_interval_s, so the log stays readable (CONTROL_APP.md, "What gets logged").
- heartbeat() renews the lease without logging.
- tick() is the watchdog: called often, it sends one base.stop when the lease has lapsed.
- stop() cancels the lease and stops at once.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field

from ..events import Actor
from ..lease import DriveLease
from ..runner import CommandResult, Runner


@dataclass
class DriveSession:
    runner: Runner
    lease: DriveLease
    clock: Callable[[], float] = time.monotonic
    min_interval_s: float = 0.1
    min_dv: float = 0.02
    min_dw: float = 0.05
    moving: bool = field(default=False, init=False)
    _last: tuple[float, float] | None = field(default=None, init=False)
    _last_t: float = field(default=float("-inf"), init=False)
    _stopped_t: float = field(default=float("-inf"), init=False)

    def drive(self, v: float, w: float) -> CommandResult | None:
        self.lease.renew()
        now = self.clock()
        if self._last is not None:
            if now - self._last_t < self.min_interval_s:
                return None
            lv, lw = self._last
            if abs(v - lv) < self.min_dv and abs(w - lw) < self.min_dw:
                return None
        result = self.runner.request("base.drive", {"v": v, "w": w}, actor="human")
        if result.ok:
            self._last, self._last_t = (v, w), now
            self.moving = v != 0.0 or w != 0.0
        return result

    def heartbeat(self) -> None:
        self.lease.renew()

    def tick(self) -> CommandResult | None:
        if self.moving and not self.lease.alive():
            return self._halt("system")
        return None

    def stop(self, actor: Actor = "human") -> CommandResult | None:
        """Cancel the lease and stop. A stop while already stopped within the last
        min_interval_s is collapsed (returns None), so a flood of stops cannot flood the
        log or the servo bus; a stop is never refused by the gate."""
        self.lease.cancel()
        now = self.clock()
        if not self.moving and now - self._stopped_t < self.min_interval_s:
            return None
        return self._halt(actor)

    def _halt(self, actor: Actor) -> CommandResult:
        result = self.runner.request("base.stop", actor=actor)
        self.moving = False
        self._last = None
        self._stopped_t = self.clock()
        return result
```

> **Done 2026-11-21, then hardened over two reviews (647a71a and the commit after it):** a drive
> dropped by the time dedupe is kept and sent by `tick()`; (0, 0) and near-zero halt at once; a
> drive refused or failed while moving halts; `tick()` halts on the STOP file; a failed stop stays
> owed and is retried. The code and tests in the repo, not this listing, are the reference.

- [ ] **Step 5: Run the tests**

Run: `uv run pytest services/lab-agent/tests/test_console_drive.py -v`
Expected: 7 passed.

- [ ] **Step 6: Commit**

```bash
git add services/lab-agent/src/lab_agent/console/drive.py services/lab-agent/tests/conftest.py services/lab-agent/tests/test_console_drive.py
git commit -m "lab-agent: console drive session with lease and watchdog"
```

---

### Task 8: Console server

**Files:**
- Create: `services/lab-agent/src/lab_agent/console/server.py`
- Test: `services/lab-agent/tests/test_console_server.py`

- [ ] **Step 1: Write the failing tests**

```python
import time

import pytest

pytest.importorskip("starlette")

from lab_agent.console.drive import DriveSession  # noqa: E402
from lab_agent.console.server import create_app  # noqa: E402
from lab_agent.console.telemetry import FakeTelemetry  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402
from starlette.websockets import WebSocketDisconnect  # noqa: E402

TOKEN = "test-token"


@pytest.fixture
def rig(drive_rig):
    r = drive_rig(time.monotonic)  # the server's watchdog runs in real time
    session = DriveSession(r.runner, r.lease)
    app = create_app(r.runner, session, FakeTelemetry(), TOKEN, state_period_s=0.05)
    return TestClient(app), r.wheels


def recv(ws, kind: str, ok=lambda _m: True) -> dict:
    """Read until a message of this kind that passes `ok` (states stream all the time)."""
    for _ in range(100):
        msg = ws.receive_json()
        if msg["type"] == kind and ok(msg):
            return msg
    raise AssertionError(f"no matching {kind} message")


def test_health_is_open(rig):
    client, _ = rig
    assert client.get("/api/health").json() == {"ok": True}


def test_wrong_token_is_closed(rig):
    client, _ = rig
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "hello", "token": "nope"})
        with pytest.raises(WebSocketDisconnect) as e:
            ws.receive_json()
    assert e.value.code == 4401


def test_first_message_must_be_hello(rig):
    client, _ = rig
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "drive", "v": 0.1, "w": 0, "seq": 1})
        with pytest.raises(WebSocketDisconnect) as e:
            ws.receive_json()
    assert e.value.code == 4401


def test_hello_gets_welcome_then_state(rig):
    client, _ = rig
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "hello", "token": TOKEN})
        welcome = recv(ws, "welcome")
        assert welcome["max_v"] == 0.3 and welcome["lease_s"] == 0.3
        state = recv(ws, "state")
        assert state["fake"] is True


def test_drive_moves_the_wheels_and_stop_stops_them(rig):
    client, wheels = rig
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "hello", "token": TOKEN})
        recv(ws, "welcome")
        ws.send_json({"type": "drive", "v": 0.1, "w": 0.0, "seq": 1})
        recv(ws, "state", lambda m: m["moving"])
        ws.send_json({"type": "stop"})
        recv(ws, "state", lambda m: not m["moving"])
    assert wheels.speeds == (0.0, 0.0)


def test_refusals_reach_the_browser(rig):
    client, _ = rig
    open("STOP", "w").close()  # the rig runs in tmp_path
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "hello", "token": TOKEN})
        recv(ws, "welcome")
        ws.send_json({"type": "drive", "v": 0.1, "w": 0.0, "seq": 1})
        refused = recv(ws, "refused")
        assert refused["rule"] == "stop_file"


def test_only_one_device_drives_at_a_time(rig):
    client, _ = rig
    with client.websocket_connect("/ws") as a, client.websocket_connect("/ws") as b:
        for ws in (a, b):
            ws.send_json({"type": "hello", "token": TOKEN})
            recv(ws, "welcome")
        a.send_json({"type": "drive", "v": 0.1, "w": 0.0, "seq": 1})
        recv(a, "state", lambda m: m["moving"])
        b.send_json({"type": "drive", "v": -0.1, "w": 0.0, "seq": 1})
        assert recv(b, "refused")["rule"] == "driver"
        b.send_json({"type": "stop"})  # but anyone may stop it
        recv(b, "state", lambda m: not m["moving"])


def test_closing_the_tab_stops_the_wheels(rig):
    client, wheels = rig
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "hello", "token": TOKEN})
        recv(ws, "welcome")
        ws.send_json({"type": "drive", "v": 0.1, "w": 0.0, "seq": 1})
        recv(ws, "state", lambda m: m["moving"])
    assert wheels.speeds == (0.0, 0.0)
```

- [ ] **Step 2: Run and watch them fail**

Run: `uv run pytest services/lab-agent/tests/test_console_server.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'lab_agent.console.server'`.

- [ ] **Step 3: Write `console/server.py`**

```python
"""The robot console's web server: pairing, one WebSocket per browser, the watchdog.

Starlette and uvicorn come from the `console` extra. It never touches a device: every
command goes through the DriveSession, which goes through Runner.request (ADR 0014).
"""

from __future__ import annotations

import asyncio
import contextlib
import secrets
import socket
import time
from contextlib import asynccontextmanager
from pathlib import Path

from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket, WebSocketDisconnect

from ..interlocks import LeaseRequired
from ..lease import DriveLease
from ..registry import Registry
from ..runner import Runner
from .drive import DriveSession
from .protocol import DriveMsg, Heartbeat, Hello, Refused, State, StopMsg, Welcome, client_message
from .telemetry import FakeTelemetry, Telemetry

UNAUTHORISED = 4401
WATCHDOG_PERIOD_S = 0.05


class Driver:
    """One device drives at a time. The first to send drive or heartbeat holds the drive
    until it disconnects or the lease lapses; others are refused with rule "driver". Any
    device may stop the robot."""

    def __init__(self, lease: DriveLease) -> None:
        self.lease = lease
        self.holder: object | None = None

    def claim(self, who: object) -> bool:
        if self.holder is None or self.holder is who or not self.lease.alive():
            self.holder = who
            return True
        return False

    def release(self, who: object) -> bool:
        if self.holder is who:
            self.holder = None
            return True
        return False


def find_lease(registry: Registry) -> DriveLease:
    for interlock in registry.interlocks:
        if isinstance(interlock, LeaseRequired):
            return interlock.lease
    raise SystemExit("this tool set has no drive_lease interlock; the console needs one")


def create_app(
    runner: Runner,
    session: DriveSession,
    telemetry: Telemetry,
    token: str,
    *,
    static_dir: Path | None = None,
    state_period_s: float = 0.1,
    max_v: float = 0.3,
    max_w: float = 1.5,
) -> Starlette:
    def state() -> dict:
        return State(
            type="state",
            t=time.time(),
            lease_alive=session.lease.alive(),
            moving=session.moving,
            stop_file=runner.gate.stop_file.exists(),
            **telemetry.read(),
        ).model_dump(mode="json")

    driver = Driver(session.lease)

    async def health(_request) -> JSONResponse:
        return JSONResponse({"ok": True})

    async def ws_endpoint(ws: WebSocket) -> None:
        await ws.accept()
        try:
            first = client_message.validate_python(await ws.receive_json())
        except (ValidationError, WebSocketDisconnect, ValueError):
            await ws.close(UNAUTHORISED)
            return
        if not isinstance(first, Hello) or not secrets.compare_digest(first.token, token):
            await ws.close(UNAUTHORISED)
            return
        await ws.send_json(
            Welcome(
                type="welcome",
                run_id=runner.log.run_id,
                max_v=max_v,
                max_w=max_w,
                lease_s=session.lease.ttl_s,
            ).model_dump(mode="json")
        )

        async def stream() -> None:
            while True:
                await ws.send_json(state())
                await asyncio.sleep(state_period_s)

        sender = asyncio.create_task(stream())
        me = object()
        try:
            while True:
                try:
                    msg = client_message.validate_python(await ws.receive_json())
                except ValidationError:
                    continue  # ignore malformed input; the lease still lapses on its own
                result = None
                if isinstance(msg, DriveMsg | Heartbeat) and not driver.claim(me):
                    await ws.send_json(
                        Refused(
                            type="refused", rule="driver", reason="another device is driving"
                        ).model_dump(mode="json")
                    )
                    continue
                if isinstance(msg, DriveMsg):
                    result = session.drive(msg.v, msg.w)
                elif isinstance(msg, Heartbeat):
                    session.heartbeat()
                elif isinstance(msg, StopMsg):
                    result = session.stop()  # any device may stop the robot
                if result is not None and not result.allowed:
                    p = result.checked.payload
                    await ws.send_json(
                        Refused(
                            type="refused", rule=p.rule or "", reason=p.reason or ""
                        ).model_dump(mode="json")
                    )
        except WebSocketDisconnect:
            pass
        finally:
            sender.cancel()
            if driver.release(me):
                session.stop(actor="system")  # a closed tab must never leave the wheels turning

    @asynccontextmanager
    async def lifespan(_app: Starlette):
        async def watchdog() -> None:
            while True:
                session.tick()
                await asyncio.sleep(WATCHDOG_PERIOD_S)

        task = asyncio.create_task(watchdog())
        try:
            yield
        finally:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    routes = [Route("/api/health", health), WebSocketRoute("/ws", ws_endpoint)]
    if static_dir is not None and static_dir.is_dir():
        routes.append(Mount("/", StaticFiles(directory=static_dir, html=True)))
    return Starlette(routes=routes, lifespan=lifespan)


def pairing_url(port: int, token: str) -> str:
    host = socket.gethostname()
    if not host.endswith(".local"):
        host += ".local"
    return f"http://{host}:{port}/?token={token}"


def serve(runner: Runner, experiment: str, *, host: str, port: int, static_dir: Path) -> int:
    import uvicorn

    lease = find_lease(runner.registry)
    session = DriveSession(runner, lease)
    token = secrets.token_urlsafe(16)
    app = create_app(runner, session, FakeTelemetry(), token, static_dir=static_dir)
    runner.start(experiment)
    print(f"robot console: run {runner.log.run_id}")
    print(f"open on a phone or laptop on this Wi-Fi: {pairing_url(port, token)}")
    if not static_dir.is_dir():
        print(f"(no app build at {static_dir}: run `pnpm --filter robot-console build`)")
    try:
        uvicorn.run(app, host=host, port=port, log_level="warning")
    finally:
        session.stop(actor="system")
        runner.end("completed")
    return 0
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest services/lab-agent/tests/test_console_server.py -v`
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add services/lab-agent/src/lab_agent/console/server.py services/lab-agent/tests/test_console_server.py
git commit -m "lab-agent: robot console server with pairing and watchdog"
```

---

### Task 9: `lab console` command

**Files:**
- Modify: `services/lab-agent/src/lab_agent/cli.py`
- Test: `services/lab-agent/tests/test_console_server.py` (append)

- [ ] **Step 1: Write the failing test** (append)

```python
from lab_agent.console.server import find_lease, pairing_url  # noqa: E402
from lab_agent.registry import Registry  # noqa: E402


def test_console_refuses_a_tool_set_without_a_lease():
    with pytest.raises(SystemExit, match="drive_lease"):
        find_lease(Registry())


def test_pairing_url_names_a_local_host_and_the_token():
    url = pairing_url(8080, "abc")
    assert url.startswith("http://") and ".local:8080/?token=abc" in url
```

- [ ] **Step 2: Run them**

Run: `uv run pytest services/lab-agent/tests/test_console_server.py -k "lease or pairing" -v`
Expected: 2 passed (the functions exist since Task 8; these pin their behaviour).

- [ ] **Step 3: Add the subcommand** to `cli.py`. Add the function next to `cmd_agent`:

```python
def cmd_console(s: Settings, a: argparse.Namespace) -> int:
    from .console.server import serve

    registry = load_tools(a.tools or s.tools)
    runner = make_runner(s, a, registry, "console")
    return serve(runner, a.experiment, host=a.host, port=a.port, static_dir=Path(a.static))
```

and register it in `main()` after the `agent` parser:

```python
    sp = sub.add_parser("console", help="serve the robot console on the home network")
    sp.add_argument("experiment")
    sp.add_argument("--host", default="0.0.0.0", help="bind address (LAN only; never forward it)")
    sp.add_argument("--port", type=int, default=8080)
    sp.add_argument("--static", default="apps/robot-console/dist", help="built app directory")
    sp.set_defaults(fn=cmd_console)
```

Make sure `from pathlib import Path` is imported at the top of `cli.py`.

- [ ] **Step 4: Try it by hand (fake wheels)**

Run: `LAB_FAKE=1 uv run lab --tools exp003_robot.tools:build console exp003-household-robot`
Expected: prints the run id and a `http://<host>.local:8080/?token=...` link, plus the note that
there is no app build yet. `curl -s localhost:8080/api/health` prints `{"ok":true}`. Ctrl-C ends
the run; `uv run lab validate events/exp003-household-robot/*.jsonl` reports the log valid.

- [ ] **Step 5: Commit**

```bash
git add services/lab-agent/src/lab_agent/cli.py services/lab-agent/tests/test_console_server.py
git commit -m "lab-agent: lab console subcommand"
```

---

### Task 10: The app's scaffold and protocol

**Files:**
- Create: `apps/robot-console/package.json`, `tsconfig.json`, `vite.config.ts`, `eslint.config.js`,
  `index.html`, `src/main.tsx`, `src/protocol.ts`, `src/protocol.test.ts`, `src/test-setup.ts`

- [ ] **Step 1: Create `package.json`**

```json
{
  "name": "robot-console",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc --noEmit && vite build",
    "typecheck": "tsc --noEmit",
    "lint": "eslint .",
    "test": "vitest run"
  },
  "dependencies": {
    "react": "19.3.0",
    "react-dom": "19.3.0",
    "zod": "4.6.7"
  },
  "devDependencies": {
    "typescript": "5.9.3",
    "vitest": "5.1.0"
  }
}
```

Then add the rest at their current versions (pnpm pins them in the lockfile):

```bash
pnpm --filter robot-console add -D vite @vitejs/plugin-react @types/react @types/react-dom jsdom @testing-library/react @testing-library/jest-dom eslint @eslint/js typescript-eslint eslint-plugin-react-hooks globals @types/node
```

If pnpm warns that the installed `vite` does not satisfy `vitest@5.1.0`'s peer range, install the
newest `vite` major that does (`pnpm --filter robot-console add -D vite@<major>`).

- [ ] **Step 2: Config files.** `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noEmit": true,
    "resolveJsonModule": true,
    "skipLibCheck": true,
    "types": ["vitest/globals", "@testing-library/jest-dom", "node"]
  },
  "include": ["src", "vite.config.ts"]
}
```

`vite.config.ts`:

```ts
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// In dev, the page comes from Vite and the WebSocket from `lab console` on :8080.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/ws": { target: "ws://localhost:8080", ws: true } } },
  test: { environment: "jsdom", globals: true, setupFiles: ["src/test-setup.ts"] },
});
```

`src/test-setup.ts`:

```ts
import "@testing-library/jest-dom/vitest";
```

`eslint.config.js`:

```js
import js from "@eslint/js";
import reactHooks from "eslint-plugin-react-hooks";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist"] },
  js.configs.recommended,
  ...tseslint.configs.strict,
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: { globals: globals.browser },
    plugins: { "react-hooks": reactHooks },
    rules: reactHooks.configs.recommended.rules,
  },
);
```

`index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <title>Robot console</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

`src/main.tsx` (the App comes in Task 13; this keeps the build green until then):

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

const root = document.getElementById("root");
if (root) createRoot(root).render(<StrictMode><p>Robot console</p></StrictMode>);
```

- [ ] **Step 3: Write the failing protocol test** `src/protocol.test.ts`:

```ts
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { ClientMessage, ServerMessage } from "./protocol";

const dir = fileURLToPath(new URL("../../../packages/schema/fixtures/console", import.meta.url));
const files = (kind: string) => readdirSync(join(dir, kind)).filter((f) => f.endsWith(".json"));
const parse = (kind: string, f: string) => {
  const data: unknown = JSON.parse(readFileSync(join(dir, kind, f), "utf8"));
  return (f.startsWith("client_") ? ClientMessage : ServerMessage).safeParse(data);
};

describe("console protocol fixtures (shared with the Python server)", () => {
  it.each(files("valid"))("accepts %s", (f) => {
    expect(parse("valid", f).success).toBe(true);
  });
  it.each(files("invalid"))("rejects %s", (f) => {
    expect(parse("invalid", f).success).toBe(false);
  });
});
```

Run: `pnpm --filter robot-console test`
Expected: FAIL, cannot resolve `./protocol`.

- [ ] **Step 4: Write `src/protocol.ts`**

```ts
// Mirror of services/lab-agent/src/lab_agent/console/protocol.py. Change both together;
// both test against packages/schema/fixtures/console.
import { z } from "zod";

// z.number() already rejects NaN and Infinity and never coerces strings, matching the strict,
// finite Python models.
const seq = z.number().int().min(0).max(2 ** 53 - 1);

export const ClientMessage = z.discriminatedUnion("type", [
  z.strictObject({ type: z.literal("hello"), token: z.string().min(1).max(256) }),
  z.strictObject({ type: z.literal("drive"), v: z.number(), w: z.number(), seq }),
  z.strictObject({ type: z.literal("heartbeat"), seq }),
  z.strictObject({ type: z.literal("stop") }),
]);
export type ClientMessage = z.infer<typeof ClientMessage>;

const nullableInt = z.number().int().nullable();

export const State = z.strictObject({
  type: z.literal("state"),
  t: z.number(),
  fake: z.boolean(),
  battery: z.strictObject({
    volts: z.number(),
    amps: z.number(),
    soc_pct: z.number(),
    runtime_min: z.number(),
  }),
  servos: z.array(
    z.strictObject({ id: z.number().int(), temp_c: z.number(), load_pct: z.number(), volts: z.number() }),
  ),
  tof: z.strictObject({ left_mm: nullableInt, center_mm: nullableInt, right_mm: nullableInt }),
  cliff_mm: z.array(nullableInt),
  bumpers: z.array(z.boolean()),
  wifi_dbm: z.number().nullable(),
  pi_temp_c: z.number().nullable(),
  lease_alive: z.boolean(),
  moving: z.boolean(),
  estop: z.boolean(),
  stop_file: z.boolean(),
  controller: z.strictObject({ connected: z.boolean(), battery_pct: z.number().nullable().optional() }),
});
export type State = z.infer<typeof State>;

export const Welcome = z.strictObject({
  type: z.literal("welcome"),
  run_id: z.string(),
  max_v: z.number(),
  max_w: z.number(),
  lease_s: z.number(),
});
export type Welcome = z.infer<typeof Welcome>;

export const Refused = z.strictObject({
  type: z.literal("refused"),
  rule: z.string(),
  reason: z.string().optional(),
});
export type Refused = z.infer<typeof Refused>;

export const ServerMessage = z.discriminatedUnion("type", [Welcome, State, Refused]);
export type ServerMessage = z.infer<typeof ServerMessage>;
```

- [ ] **Step 5: Run the checks**

Run: `pnpm --filter robot-console test && pnpm --filter robot-console typecheck && pnpm --filter robot-console lint && pnpm --filter robot-console build`
Expected: all fixtures pass; typecheck, lint and build succeed; `apps/robot-console/dist/index.html` exists.

- [ ] **Step 6: Ignore the build output and commit.** Add `apps/robot-console/dist/` to the root
`.gitignore` (next to the other build outputs), then:

```bash
git add .gitignore apps/robot-console pnpm-lock.yaml
git commit -m "robot-console: app scaffold and protocol"
```

---

### Task 11: Drive controller (hold-to-drive logic)

**Files:**
- Create: `apps/robot-console/src/driveController.ts`, `apps/robot-console/src/driveController.test.ts`

- [ ] **Step 1: Write the failing test**

```ts
import { DriveController } from "./driveController";
import type { ClientMessage } from "./protocol";

function rig() {
  const sent: ClientMessage[] = [];
  const c = new DriveController((m) => sent.push(m), { maxW: 1.5, speedLimit: 0.2 });
  return { c, sent, types: () => sent.map((m) => m.type) };
}

describe("DriveController", () => {
  it("maps the stick to speed and turn rate: up is forward, right turns right", () => {
    const { c, sent } = rig();
    c.hold(0.5, 1, 0);
    expect(sent[0]).toMatchObject({ type: "drive", v: 0.2, w: -0.75 });
  });

  it("sends drive at most every 100 ms, and only on a real change", () => {
    const { c, types } = rig();
    c.hold(0, 0.5, 0);
    c.hold(0, 1, 50); // too soon
    c.hold(0, 1, 120); // sent
    c.hold(0, 1.01, 250); // too small a change
    expect(types().filter((t) => t === "drive")).toHaveLength(2);
  });

  it("sends a heartbeat every 100 ms while held, and none after release", () => {
    const { c, types } = rig();
    c.hold(0, 0.5, 0);
    c.tick(100);
    c.tick(200);
    c.release();
    c.tick(300);
    expect(types()).toEqual(["drive", "heartbeat", "heartbeat", "stop"]);
  });

  it("numbers every message so the robot can spot gaps", () => {
    const { c, sent } = rig();
    c.hold(0, 0.5, 0);
    c.tick(100);
    const seqs = sent.flatMap((m) => ("seq" in m ? [m.seq] : []));
    expect(seqs).toEqual([0, 1]);
  });
});
```

Run: `pnpm --filter robot-console test`
Expected: FAIL, cannot resolve `./driveController`.

- [ ] **Step 2: Write `src/driveController.ts`**

```ts
import type { ClientMessage } from "./protocol";

export type Send = (msg: ClientMessage) => void;

const HEARTBEAT_MS = 100;
const MIN_SEND_MS = 100;
const MIN_DV = 0.02;
const MIN_DW = 0.05;

/** Turns a held joystick into drive, heartbeat and stop messages (CONTROL_APP.md, Safety).
 * Pure logic with an injected clock, so it is tested without timers or a socket. */
export class DriveController {
  private seq = 0;
  private held = false;
  private last: { v: number; w: number; at: number } | null = null;
  private lastBeat = 0;

  constructor(
    private readonly send: Send,
    private readonly limits: { maxW: number; speedLimit: number },
  ) {}

  /** x and y in [-1, 1]: y up is forward, x right is a right turn (negative w). */
  hold(x: number, y: number, now: number): void {
    const v = round(y * this.limits.speedLimit);
    const w = round(-x * this.limits.maxW);
    this.held = true;
    const l = this.last;
    if (l && (now - l.at < MIN_SEND_MS || (Math.abs(v - l.v) < MIN_DV && Math.abs(w - l.w) < MIN_DW))) {
      return;
    }
    this.send({ type: "drive", v, w, seq: this.seq++ });
    this.last = { v, w, at: now };
    this.lastBeat = now;
  }

  tick(now: number): void {
    if (this.held && now - this.lastBeat >= HEARTBEAT_MS) {
      this.send({ type: "heartbeat", seq: this.seq++ });
      this.lastBeat = now;
    }
  }

  release(): void {
    if (!this.held) return;
    this.held = false;
    this.last = null;
    this.send({ type: "stop" });
  }

  setSpeedLimit(speedLimit: number): void {
    this.limits.speedLimit = speedLimit;
  }
}

const round = (n: number) => Math.round(n * 1000) / 1000 + 0; // + 0 turns -0 into 0
```

> **Done 2026-11-21, then hardened after review:** like the server, the client snaps near-zero to
> (0, 0), sends a move to centre at once, keeps a change dropped for timing as pending and sends it
> on the next tick, re-sends after a speed-limit change while held, and ignores non-finite input.
> The repo code is the reference.

- [ ] **Step 3: Run the tests**

Run: `pnpm --filter robot-console test`
Expected: all pass.

- [ ] **Step 4: Commit**

```bash
git add apps/robot-console/src/driveController.ts apps/robot-console/src/driveController.test.ts
git commit -m "robot-console: hold-to-drive controller"
```

---

### Task 12: Socket hook and joystick

**Files:**
- Create: `apps/robot-console/src/useRobot.ts`, `apps/robot-console/src/useRobot.test.ts`,
  `apps/robot-console/src/Joystick.tsx`, `apps/robot-console/src/stick.ts`, `apps/robot-console/src/stick.test.ts`

- [ ] **Step 1: Write the failing tests.** `src/stick.test.ts`:

```ts
import { stickVector } from "./stick";

const rect = { left: 0, top: 0, width: 200, height: 200 };

describe("stickVector", () => {
  it("is zero at the centre", () => {
    expect(stickVector(rect, 100, 100)).toEqual({ x: 0, y: 0 });
  });
  it("points up as +y and right as +x", () => {
    expect(stickVector(rect, 100, 0)).toEqual({ x: 0, y: 1 });
    expect(stickVector(rect, 200, 100)).toEqual({ x: 1, y: 0 });
  });
  it("clamps to the unit circle", () => {
    const v = stickVector(rect, 400, 400);
    expect(Math.hypot(v.x, v.y)).toBeCloseTo(1);
  });
});
```

`src/useRobot.test.ts`:

```ts
import { act, renderHook } from "@testing-library/react";
import { useRobot } from "./useRobot";

class FakeSocket {
  static last: FakeSocket;
  sent: string[] = [];
  onopen: (() => void) | null = null;
  onmessage: ((e: { data: string }) => void) | null = null;
  onclose: ((e: { code: number }) => void) | null = null;
  readyState = 0;
  constructor(public url: string) {
    FakeSocket.last = this;
  }
  send(data: string) {
    this.sent.push(data);
  }
  close() {}
}

const make = (url: string) => new FakeSocket(url) as unknown as WebSocket;

describe("useRobot", () => {
  it("says hello with the token when the socket opens", () => {
    renderHook(() => useRobot("ws://robot/ws", "tok", make));
    act(() => FakeSocket.last.onopen?.());
    expect(JSON.parse(FakeSocket.last.sent[0] ?? "{}")).toEqual({ type: "hello", token: "tok" });
  });

  it("keeps the latest welcome and state, and ignores malformed messages", () => {
    const { result } = renderHook(() => useRobot("ws://robot/ws", "tok", make));
    act(() => {
      FakeSocket.last.onopen?.();
      FakeSocket.last.onmessage?.({ data: JSON.stringify({ type: "welcome", run_id: "r", max_v: 0.3, max_w: 1.5, lease_s: 0.3 }) });
      FakeSocket.last.onmessage?.({ data: "{not json" });
    });
    expect(result.current.status).toBe("open");
    expect(result.current.welcome?.max_v).toBe(0.3);
  });

  it("reports a bad token instead of reconnecting", () => {
    const { result } = renderHook(() => useRobot("ws://robot/ws", "bad", make));
    act(() => FakeSocket.last.onclose?.({ code: 4401 }));
    expect(result.current.status).toBe("unauthorised");
  });
});
```

Run: `pnpm --filter robot-console test`
Expected: FAIL, cannot resolve `./stick` and `./useRobot`.

- [ ] **Step 2: Write `src/stick.ts`**

```ts
export type Rect = { left: number; top: number; width: number; height: number };

/** Pointer position to a stick vector in the unit circle: +x right, +y up. */
export function stickVector(rect: Rect, clientX: number, clientY: number): { x: number; y: number } {
  const r = rect.width / 2;
  let x = (clientX - (rect.left + r)) / r;
  let y = -(clientY - (rect.top + rect.height / 2)) / (rect.height / 2);
  const len = Math.hypot(x, y);
  if (len > 1) {
    x /= len;
    y /= len;
  }
  return { x: x + 0, y: y + 0 };
}
```

- [ ] **Step 3: Write `src/useRobot.ts`**

```ts
import { useCallback, useEffect, useRef, useState } from "react";
import { type ClientMessage, type Refused, ServerMessage, type State, type Welcome } from "./protocol";

export type Status = "connecting" | "open" | "closed" | "unauthorised";
const UNAUTHORISED = 4401;
const RETRY_MS = 1000;

/** One WebSocket to the robot console: says hello, keeps the latest state, reconnects. */
export function useRobot(
  url: string,
  token: string,
  makeSocket: (url: string) => WebSocket = (u) => new WebSocket(u),
) {
  const [status, setStatus] = useState<Status>("connecting");
  const [welcome, setWelcome] = useState<Welcome | null>(null);
  const [state, setState] = useState<State | null>(null);
  const [refused, setRefused] = useState<Refused | null>(null);
  const socket = useRef<WebSocket | null>(null);

  useEffect(() => {
    let stopped = false;
    let retry: ReturnType<typeof setTimeout> | undefined;
    const connect = () => {
      const ws = makeSocket(url);
      socket.current = ws;
      setStatus("connecting");
      ws.onopen = () => {
        ws.send(JSON.stringify({ type: "hello", token }));
        setStatus("open");
      };
      ws.onmessage = (e: MessageEvent<string> | { data: string }) => {
        let data: unknown;
        try {
          data = JSON.parse(e.data);
        } catch {
          return;
        }
        const msg = ServerMessage.safeParse(data);
        if (!msg.success) return;
        if (msg.data.type === "welcome") setWelcome(msg.data);
        else if (msg.data.type === "state") setState(msg.data);
        else setRefused(msg.data);
      };
      ws.onclose = (e: CloseEvent | { code: number }) => {
        if (e.code === UNAUTHORISED) {
          setStatus("unauthorised");
          return;
        }
        setStatus("closed");
        if (!stopped) retry = setTimeout(connect, RETRY_MS);
      };
    };
    connect();
    return () => {
      stopped = true;
      clearTimeout(retry);
      socket.current?.close();
    };
  }, [url, token, makeSocket]);

  const send = useCallback((msg: ClientMessage) => {
    if (socket.current?.readyState === WebSocket.OPEN) socket.current.send(JSON.stringify(msg));
  }, []);

  return { status, welcome, state, refused, send };
}
```

Note for the test's fake socket: `send` only sends when `readyState` is `WebSocket.OPEN`; the
hello in `onopen` is sent directly, so the first test passes without touching `readyState`.

- [ ] **Step 4: Write `src/Joystick.tsx`**

```tsx
import { type PointerEvent, useCallback, useEffect, useRef, useState } from "react";
import { stickVector } from "./stick";

type Props = { onMove: (x: number, y: number) => void; onRelease: () => void; size?: number };

/** A touch joystick: drag to drive, lift to stop. Pointer capture keeps the drag even when
 * the finger leaves the circle. */
export function Joystick({ onMove, onRelease, size = 220 }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  // The pointer that is driving, in a ref so a late pointermove after pointerup can never
  // restart driving (a dead-man path must not depend on React flushing state).
  const pointer = useRef<number | null>(null);
  const [knob, setKnob] = useState({ x: 0, y: 0 });

  const move = (e: PointerEvent) => {
    if (!ref.current) return;
    const v = stickVector(ref.current.getBoundingClientRect(), e.clientX, e.clientY);
    setKnob(v);
    onMove(v.x, v.y);
  };
  const end = useCallback(() => {
    if (pointer.current === null) return;
    pointer.current = null;
    setKnob({ x: 0, y: 0 });
    onRelease();
  }, [onRelease]);

  // Hiding the tab or leaving the window releases the stick.
  useEffect(() => {
    const hidden = () => document.visibilityState === "hidden" && end();
    document.addEventListener("visibilitychange", hidden);
    window.addEventListener("blur", end);
    return () => {
      document.removeEventListener("visibilitychange", hidden);
      window.removeEventListener("blur", end);
    };
  }, [end]);

  return (
    <div
      ref={ref}
      role="slider"
      aria-label="Drive joystick: drag to drive, release to stop"
      aria-valuetext={knob.x || knob.y ? `forward ${knob.y.toFixed(2)}, turn ${knob.x.toFixed(2)}` : "released"}
      tabIndex={0}
      className="joystick"
      style={{ width: size, height: size }}
      onPointerDown={(e) => {
        e.currentTarget.setPointerCapture(e.pointerId);
        pointer.current = e.pointerId;
        move(e);
      }}
      onPointerMove={(e) => {
        if (e.pointerId === pointer.current && e.buttons !== 0) move(e);
      }}
      onPointerUp={end}
      onPointerCancel={end}
      onLostPointerCapture={end}
    >
      <div
        className="knob"
        style={{ transform: `translate(${knob.x * size * 0.35}px, ${-knob.y * size * 0.35}px)` }}
      />
    </div>
  );
}
```

- [ ] **Step 5: Test the joystick's release paths** `src/Joystick.test.tsx` (jsdom has no layout, so
stub `getBoundingClientRect` to a 200 x 200 box; `setPointerCapture` may need a no-op stub on
`HTMLElement.prototype`):

```tsx
import { fireEvent, render, screen } from "@testing-library/react";
import { Joystick } from "./Joystick";

function setup() {
  const onMove = vi.fn();
  const onRelease = vi.fn();
  render(<Joystick onMove={onMove} onRelease={onRelease} />);
  const el = screen.getByRole("slider");
  el.getBoundingClientRect = () => ({ left: 0, top: 0, width: 200, height: 200, right: 200, bottom: 200, x: 0, y: 0, toJSON: () => ({}) });
  HTMLElement.prototype.setPointerCapture = () => {};
  return { el, onMove, onRelease };
}

describe("Joystick", () => {
  it("a move after release never drives", () => {
    const { el, onMove, onRelease } = setup();
    fireEvent.pointerDown(el, { pointerId: 1, buttons: 1, clientX: 100, clientY: 0 });
    fireEvent.pointerUp(el, { pointerId: 1 });
    onMove.mockClear();
    fireEvent.pointerMove(el, { pointerId: 1, buttons: 1, clientX: 100, clientY: 0 });
    expect(onMove).not.toHaveBeenCalled();
    expect(onRelease).toHaveBeenCalledTimes(1);
  });

  it("hiding the tab releases a held stick", () => {
    const { el, onRelease } = setup();
    fireEvent.pointerDown(el, { pointerId: 1, buttons: 1, clientX: 100, clientY: 0 });
    Object.defineProperty(document, "visibilityState", { value: "hidden", configurable: true });
    fireEvent(document, new Event("visibilitychange"));
    expect(onRelease).toHaveBeenCalledTimes(1);
  });
});
```

If jsdom drops `pointerId` or `buttons` from `fireEvent.pointerDown`, build the events with
`new MouseEvent(...)` plus `Object.defineProperty` for those two fields, and say so in the report.

- [ ] **Step 6: Run the checks**

Run: `pnpm --filter robot-console test && pnpm --filter robot-console typecheck && pnpm --filter robot-console lint`
Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add apps/robot-console/src
git commit -m "robot-console: socket hook and joystick"
```

---

### Task 13: Drive screen and app shell

**Files:**
- Create: `apps/robot-console/src/DriveScreen.tsx`, `apps/robot-console/src/DriveScreen.test.tsx`,
  `apps/robot-console/src/App.tsx`, `apps/robot-console/src/token.ts`, `apps/robot-console/src/token.test.ts`,
  `apps/robot-console/src/styles.css`
- Modify: `apps/robot-console/src/main.tsx`

- [ ] **Step 1: Write the failing tests.** `src/token.test.ts`:

```ts
import { takeToken } from "./token";

describe("takeToken", () => {
  beforeEach(() => localStorage.clear());

  it("moves the token from the pairing link into local storage", () => {
    const replace = vi.fn();
    expect(takeToken("http://robot.local:8080/#token=abc", replace)).toBe("abc");
    expect(localStorage.getItem("robot-token")).toBe("abc");
    expect(replace).toHaveBeenCalledWith("http://robot.local:8080/");
  });

  it("falls back to the stored token", () => {
    localStorage.setItem("robot-token", "kept");
    expect(takeToken("http://robot.local:8080/", vi.fn())).toBe("kept");
  });

  it("is null when the browser was never paired", () => {
    expect(takeToken("http://robot.local:8080/", vi.fn())).toBeNull();
  });
});
```

`src/DriveScreen.test.tsx`:

```tsx
import { fireEvent, render, screen } from "@testing-library/react";
import stateJson from "../../../packages/schema/fixtures/console/valid/server_state.json";
import { DriveScreen } from "./DriveScreen";
import { State } from "./protocol";

const state = State.parse(stateJson);

describe("DriveScreen", () => {
  it("sends stop from the big stop button", () => {
    const send = vi.fn();
    render(<DriveScreen send={send} status="open" state={state} refused={null} maxV={0.3} maxW={1.5} />);
    fireEvent.click(screen.getByRole("button", { name: /stop/i }));
    expect(send).toHaveBeenCalledWith({ type: "stop" });
  });

  it("never shows a fake e-stop reading as real", () => {
    render(<DriveScreen send={vi.fn()} status="open" state={state} refused={null} maxV={0.3} maxW={1.5} />);
    expect(screen.getByText(/e-stop: no sensor/i)).toBeInTheDocument();
    expect(screen.queryByText(/e-stop clear/i)).not.toBeInTheDocument();
  });

  it("shows when the robot is fake and when the connection is down", () => {
    render(<DriveScreen send={vi.fn()} status="closed" state={state} refused={null} maxV={0.3} maxW={1.5} />);
    expect(screen.getByText(/fake devices/i)).toBeInTheDocument();
    expect(screen.getByText(/reconnecting/i)).toBeInTheDocument();
  });

  it("shows the last refusal with its rule", () => {
    render(
      <DriveScreen send={vi.fn()} status="open" state={state} refused={{ type: "refused", rule: "stop_file", reason: "STOP exists" }} maxV={0.3} maxW={1.5} />,
    );
    expect(screen.getByText(/stop_file/)).toBeInTheDocument();
  });
});
```

Run: `pnpm --filter robot-console test`
Expected: FAIL, cannot resolve `./token` and `./DriveScreen`.

- [ ] **Step 2: Write `src/token.ts`**

```ts
const KEY = "robot-token";

/** The pairing token: from the link `lab console` printed (in the URL fragment, so it never
 * reaches a server log; then stored and stripped from the address bar), or from local storage on
 * later visits. Null if never paired. */
export function takeToken(href: string, replace: (url: string) => void): string | null {
  const url = new URL(href);
  const fromLink = new URLSearchParams(url.hash.slice(1)).get("token");
  if (fromLink) {
    localStorage.setItem(KEY, fromLink);
    url.hash = "";
    replace(url.toString().replace(/#$/, ""));
    return fromLink;
  }
  return localStorage.getItem(KEY);
}
```

- [ ] **Step 3: Write `src/DriveScreen.tsx`**

```tsx
import { useEffect, useMemo, useState } from "react";
import { DriveController } from "./driveController";
import { Joystick } from "./Joystick";
import type { ClientMessage, Refused, State } from "./protocol";
import type { Status } from "./useRobot";

type Props = {
  send: (m: ClientMessage) => void;
  status: Status;
  state: State | null;
  refused: Refused | null;
  maxV: number;
  maxW: number;
};

export function DriveScreen({ send, status, state, refused, maxV, maxW }: Props) {
  const [speed, setSpeed] = useState(Math.min(0.15, maxV));
  // One controller per connection (send changes only on reconnect), so seq keeps rising on a
  // socket; the welcome's limits are applied in place.
  const controller = useMemo(() => new DriveController(send, { maxW, speedLimit: speed }), [send]); // eslint-disable-line react-hooks/exhaustive-deps -- limits are applied below, not by rebuilding
  useEffect(() => controller.setLimits({ maxW, speedLimit: Math.min(speed, maxV) }), [controller, maxW, maxV, speed]);
  useEffect(() => {
    const id = setInterval(() => controller.tick(performance.now()), 50);
    return () => clearInterval(id);
  }, [controller]);

  return (
    <main className="drive">
      <header className="pills">
        <span className={`pill ${status === "open" ? "ok" : "warn"}`}>
          {status === "open" ? "Connected" : status === "unauthorised" ? "Pair again" : "Reconnecting"}
        </span>
        {state?.fake && <span className="pill warn">Fake devices</span>}
        {state && <span className={`pill ${state.lease_alive ? "ok" : ""}`}>{state.lease_alive ? "Driving" : "Idle"}</span>}
        {state && <span className="pill">{state.battery.volts.toFixed(1)} V</span>}
        {state?.stop_file && <span className="pill bad">STOP file</span>}
        {state && (
          <span className={`pill ${state.fake ? "muted" : state.estop ? "bad" : "ok"}`}>
            {state.fake ? "E-stop: no sensor" : state.estop ? "E-stop pressed" : "E-stop clear"}
          </span>
        )}
      </header>

      <Joystick onMove={(x, y) => controller.hold(x, y, performance.now())} onRelease={() => controller.release()} />

      <label className="speed">
        Top speed {speed.toFixed(2)} m/s
        <input type="range" min={0.05} max={maxV} step={0.01} value={speed} onChange={(e) => setSpeed(Number(e.target.value))} />
      </label>

      <button type="button" className="stop" onClick={() => send({ type: "stop" })}>
        Stop
      </button>

      {refused && (
        <p className="refused" role="status">
          Refused by <code>{refused.rule}</code>
          {refused.reason ? `: ${refused.reason}` : ""}
        </p>
      )}
    </main>
  );
}
```

- [ ] **Step 4: Write `src/App.tsx`, `src/styles.css` and update `src/main.tsx`.** `App.tsx`:

```tsx
import { DriveScreen } from "./DriveScreen";
import { takeToken } from "./token";
import { useRobot } from "./useRobot";

const token = takeToken(window.location.href, (u) => window.history.replaceState(null, "", u));
const wsUrl = `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/ws`;

export function App() {
  if (!token) {
    return (
      <main className="drive">
        <p>Open the pairing link that <code>lab console</code> printed on the robot.</p>
      </main>
    );
  }
  return <Connected token={token} />;
}

function Connected({ token }: { token: string }) {
  const robot = useRobot(wsUrl, token);
  return (
    <DriveScreen
      send={robot.send}
      status={robot.status}
      state={robot.state}
      refused={robot.refused}
      maxV={robot.welcome?.max_v ?? 0.3}
      maxW={robot.welcome?.max_w ?? 1.5}
    />
  );
}
```

`styles.css`:

```css
:root { color-scheme: light dark; --bg: #fafaf7; --fg: #1d1d1b; --muted: #6b6b66; --ok: #2f7d4f; --warn: #b26b00; --bad: #b3261e; }
@media (prefers-color-scheme: dark) { :root { --bg: #151513; --fg: #ecece6; --muted: #a3a39b; } }
body { margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.4 system-ui, sans-serif; }
.drive { display: flex; flex-direction: column; align-items: center; gap: 20px; padding: 16px; touch-action: none; }
.pills { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.pill { border: 1px solid var(--muted); border-radius: 999px; padding: 2px 10px; font-size: 14px; }
.pill.ok { border-color: var(--ok); color: var(--ok); }
.pill.warn { border-color: var(--warn); color: var(--warn); }
.pill.bad { border-color: var(--bad); color: var(--bad); }
.pill.muted { opacity: 0.5; border-style: dashed; }
.joystick { border-radius: 50%; border: 2px solid var(--muted); display: grid; place-items: center; touch-action: none; user-select: none; }
.knob { width: 30%; height: 30%; border-radius: 50%; background: var(--fg); opacity: 0.8; }
.speed { display: flex; flex-direction: column; align-items: center; gap: 4px; color: var(--muted); }
.stop { width: min(320px, 90vw); padding: 18px; font-size: 22px; font-weight: 600; border: 0; border-radius: 14px; background: var(--bad); color: #fff; }
.refused { color: var(--bad); text-align: center; }
```

`main.tsx`:

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./styles.css";

const root = document.getElementById("root");
if (root) createRoot(root).render(<StrictMode><App /></StrictMode>);
```

- [ ] **Step 5: Run the checks**

Run: `pnpm --filter robot-console test && pnpm --filter robot-console typecheck && pnpm --filter robot-console lint && pnpm --filter robot-console build`
Expected: all pass; `dist/` rebuilt.

- [ ] **Step 6: Commit**

```bash
git add apps/robot-console/src
git commit -m "robot-console: drive screen, pairing and app shell"
```

---

### Task 14: Try it end to end on the Mac, then docs

**Files:**
- Modify: `AGENTS.md`, `experiments/exp003-household-robot/CONTROL_APP.md`,
  `experiments/exp003-household-robot/README.md`

- [ ] **Step 1: Run it**

```bash
pnpm --filter robot-console build
LAB_FAKE=1 uv run lab --tools exp003_robot.tools:build console exp003-household-robot
```

Open the printed link on a phone on the same Wi-Fi (or on the Mac). Check, and note each result:
1. The pills show Connected, Fake devices, Idle and a battery voltage.
2. Dragging the joystick shows Driving; releasing returns to Idle within half a second.
3. Holding the stick, then closing the tab: the terminal run keeps going, and the log shows a
   `base.stop` by `system`.
4. `touch STOP` while holding: the screen shows "Refused by stop_file"; the Stop button still
   works (`rule: halt` in the log). Remove `STOP`.
5. Ctrl-C, then `uv run lab validate events/exp003-household-robot/*.jsonl`: valid.

- [ ] **Step 2: Docs.** In `AGENTS.md`, under the hardware rules, add:

```markdown
- The exp003 robot console (`lab console`, `apps/robot-console`, ADR 0014) is LAN only: never
  forward its port. Drive is a lease; `base.stop` is a halt tool the gate never refuses.
```

In `CONTROL_APP.md`, under "Order of work", mark step 1 done with the date and link this plan.
In the exp003 README's progress log, add a dated line: the robot console runs on fake wheels
from a phone, with hold-to-drive, the watchdog stop and the STOP file checked by hand.

- [ ] **Step 3: Full checks**

Run: `pnpm check`, `uv run pytest`, `cargo test` (prepend the rustup toolchain to PATH if needed),
and the CadQuery tests are unaffected.
Expected: all pass.

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md experiments/exp003-household-robot/CONTROL_APP.md experiments/exp003-household-robot/README.md
git commit -m "exp003: robot console step 1 done on fake wheels"
```
