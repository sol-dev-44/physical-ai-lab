"""The robot console's web server: pairing, one WebSocket per browser, the watchdog.

Starlette and uvicorn come from the `console` extra. It never touches a device: every
command goes through the DriveSession, which goes through Runner.request (ADR 0014).

Known limit, left for step 2: a stale buffered drive message that arrives after a watchdog
stop can renew the lease and restart motion briefly (it is bounded by the lease, but it is
not rejected by sequence number). Drive calls also run synchronously on the event loop.
"""

from __future__ import annotations

import asyncio
import contextlib
import secrets
import socket
import time
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

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

    def claim(self, who: object) -> tuple[bool, bool]:
        """Returns (granted, changed). changed means the drive passed to a different device
        (or from nobody), so the caller must bring the robot to rest first."""
        if self.holder is None or self.holder is who or not self.lease.alive():
            changed = self.holder is not who
            self.holder = who
            return True, changed
        return False, False

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


def drive_limits(registry: Registry) -> tuple[float, float]:
    """The welcome's max_v and max_w, read from base.drive's argument schema."""
    tool = registry.get("base.drive")
    if tool is None:
        raise SystemExit("this tool set has no base.drive tool; the console needs one")
    props = tool.args_schema().get("properties", {})
    try:
        return float(props["v"]["maximum"]), float(props["w"]["maximum"])
    except KeyError:
        raise SystemExit(
            "base.drive's arguments must declare a maximum for v and w (Field(le=...))"
        ) from None


def create_app(
    runner: Runner,
    session: DriveSession,
    telemetry: Telemetry,
    token: str,
    *,
    static_dir: Path | None = None,
    state_period_s: float = 0.1,
    hello_timeout_s: float = 5.0,
    max_v: float | None = None,
    max_w: float | None = None,
) -> Starlette:
    if max_v is None or max_w is None:
        max_v, max_w = drive_limits(runner.registry)

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
            first = client_message.validate_python(
                await asyncio.wait_for(ws.receive_json(), hello_timeout_s)
            )
        except (ValueError, KeyError, TimeoutError, WebSocketDisconnect):
            await ws.close(UNAUTHORISED)
            return
        if not isinstance(first, Hello) or not secrets.compare_digest(
            first.token.encode(), token.encode()
        ):
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
            try:
                while True:
                    await ws.send_json(state())
                    await asyncio.sleep(state_period_s)
            except (WebSocketDisconnect, OSError, RuntimeError):
                return  # the browser went away; the receive loop sees the disconnect
            except Exception:
                # A bug in state or telemetry: say so, and close so the endpoint's finally
                # stops a driving socket instead of leaving it blind.
                traceback.print_exc()
                with contextlib.suppress(Exception):
                    await ws.close(1011)

        async def refuse(rule: str, reason: str) -> None:
            await ws.send_json(
                Refused(type="refused", rule=rule, reason=reason).model_dump(mode="json")
            )

        def watchdog_dead() -> bool:
            task = getattr(ws.app.state, "watchdog", None)
            return task is not None and task.done()

        sender = asyncio.create_task(stream())
        me = object()
        try:
            while True:
                try:
                    msg = client_message.validate_python(await ws.receive_json())
                except (ValueError, KeyError):
                    continue  # malformed or binary input is ignored; the lease lapses on its own
                if isinstance(msg, DriveMsg | Heartbeat):
                    if watchdog_dead():
                        if session.moving:
                            session.stop(actor="system")  # nothing else will stop it now
                        await refuse("watchdog", "the safety watchdog is not running")
                        continue
                    granted, changed = driver.claim(me)
                    if not granted:
                        await refuse("driver", "another device is driving")
                        continue
                    if changed and session.moving:
                        session.stop(actor="system")  # the new driver starts from rest
                if isinstance(msg, DriveMsg):
                    result = session.drive(msg.v, msg.w)
                    # Only a drive the gate denied is a refusal; a halt result (near-zero
                    # input, or a stop after a refused drive) is allowed and is not one.
                    if result is not None and not result.allowed:
                        p = result.checked.payload
                        await refuse(p.rule or "", p.reason or "")
                elif isinstance(msg, Heartbeat):
                    session.heartbeat()
                elif isinstance(msg, StopMsg):
                    session.stop()  # any device may stop the robot
        except WebSocketDisconnect:
            pass
        finally:
            sender.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await sender
            if driver.release(me):
                session.stop(actor="system")  # a closed tab must never leave the wheels turning

    @asynccontextmanager
    async def lifespan(_app: Starlette):
        async def watchdog() -> None:
            while True:
                try:
                    session.tick()
                except Exception:
                    traceback.print_exc()  # one bad tick must not end the watchdog
                await asyncio.sleep(WATCHDOG_PERIOD_S)

        task = app.state.watchdog = asyncio.create_task(watchdog())
        try:
            yield
        finally:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    routes = [Route("/api/health", health), WebSocketRoute("/ws", ws_endpoint)]
    if static_dir is not None and static_dir.is_dir():
        routes.append(Mount("/", StaticFiles(directory=static_dir, html=True)))
    app = Starlette(routes=routes, lifespan=lifespan)
    app.state.watchdog = None  # set by the lifespan; uvicorn always runs it
    app.state.lease = session.lease
    app.state.registry = runner.registry
    return app


def pairing_url(port: int, token: str) -> str:
    host = socket.gethostname().split(".")[0]  # "Mac.lan" -> "Mac": mDNS answers Mac.local
    # In the fragment, so the token is never sent in a request line or logged by a server.
    return f"http://{host}.local:{port}/#token={token}"


def serve(runner: Runner, experiment: str, *, host: str, port: int, static_dir: Path) -> int:
    import uvicorn

    lease = find_lease(runner.registry)
    session = DriveSession(runner, lease)
    token = secrets.token_urlsafe(16)
    app = create_app(runner, session, FakeTelemetry(), token, static_dir=static_dir)
    runner.start(experiment)
    print(f"robot console: run {runner.log.run_id}", flush=True)
    print(f"open on a phone or laptop on this Wi-Fi: {pairing_url(port, token)}", flush=True)
    if not static_dir.is_dir():
        print(
            f"(no app build at {static_dir}: run `pnpm --filter robot-console build`)", flush=True
        )
    status = "completed"
    try:
        uvicorn.run(app, host=host, port=port, log_level="warning", lifespan="on")
    except KeyboardInterrupt:
        pass
    except SystemExit as e:
        if e.code not in (None, 0):
            status = "failed"
        raise
    except BaseException:
        status = "failed"
        raise
    finally:
        try:
            session.stop(actor="system")
        except Exception:
            traceback.print_exc()
        runner.end(status)
    return 0
