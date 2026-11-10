from lab_agent.log import read_log
from lab_agent.registry import Tool
from lab_agent.runner import Runner
from lab_agent.summary import summarize_run


def test_full_flow_is_logged_with_causal_links(runner, blaster):
    runner.start("exp000-test")
    r = runner.request("fan.power", actor="human")
    runner.observe(r, True)
    denied = runner.request("heater.power", actor="human")
    runner.end()

    events = read_log(runner.log.path)  # read_log validates every rule
    assert [e.type for e in events] == [
        "run.started",
        "command.requested",
        "safety.checked",
        "command.sent",
        "outcome.observed",
        "command.requested",
        "safety.checked",
        "run.ended",
    ]
    assert events[2].parent_id == events[1].event_id
    assert events[3].parent_id == events[2].event_id
    assert events[4].parent_id == events[3].event_id
    assert not denied.allowed and denied.checked.payload.rule == "requires_confirmation"
    assert blaster.sent == ["fan_power"]
    s = summarize_run(events)
    assert (s["requested"], s["denied"], s["sent"], s["success_rate"]) == (2, 1, 1, 1.0)


def test_device_error_is_logged_not_raised(runner, blaster):
    blaster.fail_next = 1
    runner.start("exp000-test")
    r = runner.request("fan.power")
    assert r.allowed and not r.ok
    assert "timeout" in r.outcome.payload.error


def test_dry_run_never_calls_the_device(runner, blaster):
    dry = Runner(runner.registry, runner.log, dry_run=True)
    dry.start("exp000-test")
    r = dry.request("fan.power")
    assert r.ok and blaster.sent == []
    events = read_log(dry.log.path)
    assert events[0].payload.null_test is True
    assert events[-1].payload.model_extra["dry_run"] is True


def test_handler_extra_fields_land_in_payload(runner):
    runner.registry.add(Tool("x.count", "count", lambda _a: {"repeats": 3}))
    runner.start("exp000-test")
    assert runner.request("x.count").outcome.payload.model_extra["repeats"] == 3
