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


def test_the_watchdog_stops_the_wheels_when_the_lease_lapses(drive_rig):
    r = drive_rig(time.monotonic)
    session = DriveSession(r.runner, r.lease)
    app = create_app(r.runner, session, FakeTelemetry(), TOKEN, state_period_s=0.05)
    with TestClient(app) as client, client.websocket_connect("/ws") as ws:  # runs the lifespan
        ws.send_json({"type": "hello", "token": TOKEN})
        recv(ws, "welcome")
        ws.send_json({"type": "drive", "v": 0.1, "w": 0.0, "seq": 1})
        recv(ws, "state", lambda m: m["moving"])
        # no more heartbeats: the lease lapses (0.3 s) and the watchdog halts
        recv(ws, "state", lambda m: not m["moving"])
        assert r.wheels.speeds == (0.0, 0.0)
