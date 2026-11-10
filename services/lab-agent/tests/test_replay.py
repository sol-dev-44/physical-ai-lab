from lab_agent.log import EventLog, read_log
from lab_agent.replay import replay
from lab_agent.runner import Runner


def test_replay_reissues_requests_through_the_gate(runner, registry, blaster, tmp_path):
    runner.start("exp000-test")
    runner.request("fan.power")
    runner.request("heater.power", confirmed=True)  # allowed live, by a human
    runner.end()
    assert blaster.sent == ["fan_power", "heater"]

    out = Runner(registry, EventLog(tmp_path / "replay.jsonl", "exp000-t-r1-replay"))
    results = replay(read_log(runner.log.path), out, pace=False)
    events = read_log(out.log.path)

    assert events[0].payload.forked_from == "exp000-t-r1"
    assert [r.ok for r in results] == [True, False]  # heater: manual-only, never replayed
    assert results[1].checked.payload.rule in ("manual_only", "requires_confirmation")
    assert all(e.actor in ("replay", "system") for e in events if e.type.startswith("command"))
    assert blaster.sent == ["fan_power", "heater", "fan_power"]


def test_replay_keeps_original_gaps(runner, registry, tmp_path):
    runner.start("exp000-test")
    runner.request("fan.power")
    runner.request("fan.power")
    runner.end()
    source = read_log(runner.log.path)
    gaps: list[float] = []
    out = Runner(registry, EventLog(tmp_path / "paced.jsonl", "exp000-t-r1-paced"))
    replay(source, out, sleep=gaps.append, max_gap_s=0.5)
    assert len(gaps) == 1 and 0 <= gaps[0] <= 0.5
