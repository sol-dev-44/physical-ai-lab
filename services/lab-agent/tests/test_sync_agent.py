import json

import httpx
from lab_agent.agent import handle, register_tools
from lab_agent.supabase import Supabase
from lab_agent.sync import sync


class Recorder:
    def __init__(self, rpc_result=None):
        self.calls: list[tuple[str, str, dict, object]] = []
        self.rpc_result = rpc_result or []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content) if request.content else None
        self.calls.append((request.method, request.url.path, dict(request.url.params), body))
        if "/rpc/" in request.url.path:
            return httpx.Response(200, json=self.rpc_result)
        return httpx.Response(201)


def db(rec: Recorder) -> Supabase:
    return Supabase("https://x.supabase.co", "key", transport=httpx.MockTransport(rec))


def test_sync_uploads_valid_logs_and_skips_bad(runner, tmp_path):
    runner.start("exp000-test")
    runner.request("fan.power")
    runner.end()
    bad = tmp_path / "events" / "exp000-test" / "broken.jsonl"
    bad.write_text("{nope\n")

    rec = Recorder()
    report = sync(tmp_path / "events", db(rec))
    assert report.synced == ["exp000-t-r1"]
    assert str(bad) in report.skipped

    (m1, path1, params1, runs), (m2, path2, params2, events) = rec.calls
    assert path1.endswith("/runs") and params1["on_conflict"] == "run_id"
    assert "published" not in runs[0]  # sync never publishes
    assert path2.endswith("/events") and len(events) == 5
    assert events[0]["raw"]["type"] == "run.started"


def test_agent_registers_tools_and_handles_commands(runner):
    rec = Recorder()
    register_tools(db(rec), runner.registry, "test-agent")
    assert {t["name"] for t in rec.calls[0][3]} == {"fan.power", "heater.power"}

    runner.start("exp000-test")
    assert handle(db(rec), runner, {"id": "1", "tool": "fan.power", "args": {}}) == "done"
    assert (
        handle(db(rec), runner, {"id": "2", "tool": "heater.power", "args": {}, "confirmed": True})
        == "rejected"
    )
    patch = rec.calls[-1]
    assert patch[0] == "PATCH" and patch[2] == {"id": "eq.2"} and patch[3]["status"] == "rejected"


def test_agent_names_the_run_without_linking_an_unsynced_run(runner):
    rec = Recorder()
    runner.start("exp000-test")
    handle(db(rec), runner, {"id": "1", "tool": "fan.power", "args": {}})
    body = rec.calls[-1][3]
    assert "run_id" not in body  # FK to runs; the run exists there only after `lab sync`
    assert runner.log.run_id in body["result"]


def test_agent_survives_a_failed_status_update(runner):
    def conflict(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(409, json={"message": "violates foreign key constraint"})

    broken = Supabase("https://x.supabase.co", "key", transport=httpx.MockTransport(conflict))
    runner.start("exp000-test")
    assert handle(broken, runner, {"id": "1", "tool": "fan.power", "args": {}}) == "done"
