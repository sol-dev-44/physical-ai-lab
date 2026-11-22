import asyncio
import json
import socket
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

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
    # TestClient(app) without `with` does not run the lifespan, so the watchdog is off here:
    # these tests move time by hand (cancelling the lease) and must not race a background
    # tick. Tests of the watchdog itself use `with TestClient(app)`.
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


from lab_agent.console.server import find_lease, pairing_url  # noqa: E402
from lab_agent.registry import Registry  # noqa: E402


def test_console_refuses_a_tool_set_without_a_lease():
    with pytest.raises(SystemExit, match="drive_lease"):
        find_lease(Registry())


def test_pairing_url_names_a_local_host_and_the_token():
    url = pairing_url(8080, "abc")
    assert url.startswith("http://") and ".local:8080/#token=abc" in url


def lifespan_app(drive_rig, **kw):
    r = drive_rig(time.monotonic)
    session = DriveSession(r.runner, r.lease)
    telemetry = kw.pop("telemetry", None) or FakeTelemetry()
    app = create_app(r.runner, session, telemetry, TOKEN, state_period_s=0.05, **kw)
    return r, session, app


def hello(ws):
    ws.send_json({"type": "hello", "token": TOKEN})
    recv(ws, "welcome")


def _ts(s: str) -> float:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC).timestamp()


def test_watchdog_stop_is_logged_promptly_by_the_system(drive_rig):
    r, _session, app = lifespan_app(drive_rig)
    with TestClient(app) as client, client.websocket_connect("/ws") as ws:
        hello(ws)
        ws.send_json({"type": "drive", "v": 0.1, "w": 0.0, "seq": 1})
        recv(ws, "state", lambda m: m["moving"])
        recv(ws, "state", lambda m: not m["moving"])
    events = [json.loads(line) for line in r.runner.log.path.read_text().splitlines()]
    sent = next(e for e in events if e["type"] == "command.sent" and e["tool"] == "base.drive")
    stops = [
        e
        for e in events
        if e["type"] == "command.requested" and e["tool"] == "base.stop" and e["actor"] == "system"
    ]
    assert stops, "the watchdog's stop is logged with actor system"
    assert 0 <= _ts(stops[0]["ts"]) - _ts(sent["ts"]) < 0.45


def test_watchdog_survives_a_bad_tick(drive_rig):
    r, session, app = lifespan_app(drive_rig)
    real_tick, calls = session.tick, [0]

    def flaky():
        calls[0] += 1
        if calls[0] == 1:
            raise RuntimeError("boom")
        return real_tick()

    session.tick = flaky
    with TestClient(app) as client, client.websocket_connect("/ws") as ws:
        hello(ws)
        ws.send_json({"type": "drive", "v": 0.1, "w": 0.0, "seq": 1})
        recv(ws, "state", lambda m: m["moving"])
        recv(ws, "state", lambda m: not m["moving"])
    assert r.wheels.speeds == (0.0, 0.0) and calls[0] > 1


def test_a_dead_watchdog_refuses_drive_and_heartbeat(drive_rig):
    r, session, app = lifespan_app(drive_rig)

    def die():
        raise asyncio.CancelledError  # not an Exception: ends the watchdog task

    session.tick = die
    with TestClient(app) as client, client.websocket_connect("/ws") as ws:
        hello(ws)
        time.sleep(0.3)  # let the watchdog task end
        ws.send_json({"type": "drive", "v": 0.1, "w": 0.0, "seq": 1})
        assert recv(ws, "refused")["rule"] == "watchdog"
        ws.send_json({"type": "heartbeat", "seq": 2})
        assert recv(ws, "refused")["rule"] == "watchdog"
    assert r.wheels.speeds == (0.0, 0.0)


def test_a_new_driver_starts_from_rest(rig):
    client, wheels = rig
    with client.websocket_connect("/ws") as a, client.websocket_connect("/ws") as b:
        hello(a)
        hello(b)
        a.send_json({"type": "drive", "v": 0.2, "w": 0.0, "seq": 1})
        recv(a, "state", lambda m: m["moving"])
        assert wheels.speeds != (0.0, 0.0)
        client.app.state.lease.cancel()  # A goes quiet; B takes over with one heartbeat
        b.send_json({"type": "heartbeat", "seq": 1})
        recv(b, "state", lambda m: not m["moving"] and m["lease_alive"])
        assert wheels.speeds == (0.0, 0.0)


def test_a_non_driver_heartbeat_is_refused_while_the_lease_is_alive(rig):
    client, _ = rig
    with client.websocket_connect("/ws") as a, client.websocket_connect("/ws") as b:
        hello(a)
        hello(b)
        a.send_json({"type": "drive", "v": 0.1, "w": 0.0, "seq": 1})
        recv(a, "state", lambda m: m["moving"])
        b.send_json({"type": "heartbeat", "seq": 1})
        assert recv(b, "refused")["rule"] == "driver"


def test_a_displaced_driver_disconnecting_does_not_stop_the_new_one(rig):
    client, wheels = rig
    with client.websocket_connect("/ws") as b:
        hello(b)
        with client.websocket_connect("/ws") as a:
            hello(a)
            a.send_json({"type": "drive", "v": 0.1, "w": 0.0, "seq": 1})
            recv(a, "state", lambda m: m["moving"])
            client.app.state.lease.cancel()
            b.send_json({"type": "drive", "v": -0.1, "w": 0.0, "seq": 1})
            recv(b, "state", lambda m: m["moving"] and m["lease_alive"])
        # A has left (the exit waits for the server to finish with it); B still drives
        assert wheels.speeds != (0.0, 0.0)


def test_binary_first_frame_is_closed(rig):
    client, _ = rig
    with client.websocket_connect("/ws") as ws:
        ws.send_bytes(b"\x00\x01")
        with pytest.raises(WebSocketDisconnect) as e:
            ws.receive_json()
    assert e.value.code == 4401


def test_non_ascii_token_is_closed(rig):
    client, _ = rig
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "hello", "token": "t\u00e9st"})
        with pytest.raises(WebSocketDisconnect) as e:
            ws.receive_json()
    assert e.value.code == 4401


def test_silence_before_hello_times_out(drive_rig):
    _r, _s, app = lifespan_app(drive_rig, hello_timeout_s=0.1)
    with TestClient(app).websocket_connect("/ws") as ws, pytest.raises(WebSocketDisconnect) as e:
        ws.receive_json()
    assert e.value.code == 4401


def test_malformed_and_binary_frames_after_hello_are_ignored(rig):
    client, _ = rig
    with client.websocket_connect("/ws") as ws:
        hello(ws)
        ws.send_text("not json")
        ws.send_bytes(b"\xff")
        ws.send_json({"type": "nope"})
        ws.send_json({"type": "drive", "v": "fast", "w": 0, "seq": 1})
        ws.send_json({"type": "drive", "v": 0.1, "w": 0.0, "seq": 1})
        recv(ws, "state", lambda m: m["moving"])


class ExplodingTelemetry:
    def __init__(self) -> None:
        self.armed = False
        self.inner = FakeTelemetry()

    def read(self):
        if self.armed:
            raise ValueError("sensor bug")
        return self.inner.read()


def test_a_telemetry_failure_closes_the_socket_and_stops_the_wheels(drive_rig):
    tel = ExplodingTelemetry()
    r = drive_rig(time.monotonic)
    session = DriveSession(r.runner, r.lease)
    client = TestClient(create_app(r.runner, session, tel, TOKEN, state_period_s=0.05))
    with client.websocket_connect("/ws") as ws:
        hello(ws)
        ws.send_json({"type": "drive", "v": 0.1, "w": 0.0, "seq": 1})
        recv(ws, "state", lambda m: m["moving"])
        tel.armed = True
        with pytest.raises(WebSocketDisconnect) as e:
            for _ in range(100):
                ws.receive_json()
    assert e.value.code == 1011
    assert r.wheels.speeds == (0.0, 0.0)


def test_welcome_limits_come_from_the_drive_tool(rig):
    from lab_agent.console.server import drive_limits

    client, _ = rig
    assert drive_limits(client.app.state.registry) == (0.3, 1.5)
    with pytest.raises(SystemExit, match="base.drive"):
        drive_limits(Registry())


def test_a_failing_run_is_ended_failed(drive_rig, monkeypatch):
    import uvicorn
    from lab_agent.console.server import serve

    r = drive_rig(time.monotonic)
    monkeypatch.setattr(r.runner, "start", lambda *a, **k: None)  # drive_rig already started

    def boom(*_a, **_k):
        raise RuntimeError("port in use")

    monkeypatch.setattr(uvicorn, "run", boom)
    with pytest.raises(RuntimeError):
        serve(r.runner, "exp003-household-robot", host="127.0.0.1", port=0, static_dir=Path("x"))
    last = json.loads(r.runner.log.path.read_text().splitlines()[-1])
    assert last["type"] == "run.ended" and last["payload"]["status"] == "failed"


def test_real_uvicorn_serves_the_websocket(drive_rig):
    uvicorn = pytest.importorskip("uvicorn")
    ws_sync = pytest.importorskip("websockets.sync.client")
    r = drive_rig(time.monotonic)
    session = DriveSession(r.runner, r.lease)
    app = create_app(r.runner, session, FakeTelemetry(), TOKEN, state_period_s=0.05)
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, log_level="warning", lifespan="on"))
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
    thread.start()
    try:
        for _ in range(200):
            if server.started:
                break
            time.sleep(0.05)
        assert server.started
        with ws_sync.connect(f"ws://127.0.0.1:{port}/ws", open_timeout=5) as ws:

            def get(kind, ok=lambda _m: True):
                for _ in range(100):
                    msg = json.loads(ws.recv(timeout=5))
                    if msg["type"] == kind and ok(msg):
                        return msg
                raise AssertionError(kind)

            ws.send(json.dumps({"type": "hello", "token": TOKEN}))
            get("welcome")
            ws.send(json.dumps({"type": "drive", "v": 0.1, "w": 0.0, "seq": 1}))
            get("state", lambda m: m["moving"])
            ws.send(json.dumps({"type": "stop"}))
            get("state", lambda m: not m["moving"])
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        sock.close()
    assert not thread.is_alive()
    assert r.wheels.speeds == (0.0, 0.0)
