import json

import pytest
from lab_agent.events import new_ulid
from lab_agent.log import EventLog, read_log, validate_log
from pydantic import ValidationError


def test_ulid_shape_and_order():
    a, b = new_ulid(1_000), new_ulid(2_000)
    assert len(a) == 26 and a < b


def test_writer_assigns_seq_and_validates(tmp_path):
    log = EventLog(tmp_path / "r.jsonl", "exp000-t-r1")
    log.append("run.started", "system", {"experiment_id": "exp000-test"})
    log.append("note", "human", {"text": "hi"})
    log.append("run.ended", "system", {"status": "completed"})
    lines = (tmp_path / "r.jsonl").read_text().splitlines()
    assert [json.loads(x)["seq"] for x in lines] == [0, 1, 2]
    assert validate_log(lines) == []


def test_never_writes_invalid_event(tmp_path):
    log = EventLog(tmp_path / "r.jsonl", "exp000-t-r1")
    log.append("run.started", "system", {"experiment_id": "exp000-test"})
    with pytest.raises(ValidationError):
        log.append("note", "human", {})  # note needs text
    assert len((tmp_path / "r.jsonl").read_text().splitlines()) == 1
    assert log.seq == 1


def test_resume_and_close(tmp_path):
    path = tmp_path / "r.jsonl"
    log = EventLog(path, "exp000-t-r1")
    log.append("run.started", "system", {"experiment_id": "exp000-test"})
    resumed = EventLog(path, "exp000-t-r1")
    assert resumed.seq == 1
    resumed.append("run.ended", "system", {"status": "completed"})
    with pytest.raises(RuntimeError):
        EventLog(path, "exp000-t-r1").append("note", "human", {"text": "late"})


def test_refuses_to_resume_corrupt_log(tmp_path):
    path = tmp_path / "r.jsonl"
    path.write_text("{not json\n")
    with pytest.raises(ValueError):
        EventLog(path, "exp000-t-r1")
    with pytest.raises(ValueError):
        read_log(path)
