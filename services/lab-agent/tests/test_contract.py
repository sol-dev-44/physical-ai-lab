"""The Python mirror must agree with the zod source on every shared fixture."""

import json

import pytest
from jsonschema import Draft202012Validator
from lab_agent.events import parse_event
from lab_agent.log import validate_log
from lab_agent.summary import summarize_run
from pydantic import ValidationError

from .conftest import FIXTURES

SCHEMA = json.loads((FIXTURES.parent / "schema" / "event.v0.schema.json").read_text())
VALIDATOR = Draft202012Validator(SCHEMA)


def files(sub: str):
    return sorted(p for p in (FIXTURES / sub).iterdir() if not p.name.startswith("."))


@pytest.mark.parametrize("path", files("valid"), ids=lambda p: p.name)
def test_accepts_valid(path):
    data = json.loads(path.read_text())
    parse_event(data)
    VALIDATOR.validate(data)


@pytest.mark.parametrize("path", files("invalid"), ids=lambda p: p.name)
def test_rejects_invalid(path):
    data = json.loads(path.read_text())
    with pytest.raises(ValidationError):
        parse_event(data)
    assert not VALIDATOR.is_valid(data), "generated JSON Schema should reject it too"


@pytest.mark.parametrize("path", files("logs/valid"), ids=lambda p: p.name)
def test_accepts_valid_logs(path):
    assert validate_log(path.read_text().splitlines()) == []


@pytest.mark.parametrize("path", files("logs/invalid"), ids=lambda p: p.name)
def test_rejects_invalid_logs(path):
    assert validate_log(path.read_text().splitlines())


@pytest.mark.parametrize("path", files("summaries"), ids=lambda p: p.name)
def test_summary_matches_typescript(path):
    log = FIXTURES / "logs" / "valid" / path.name.replace(".json", ".jsonl")
    events = [parse_event(line) for line in log.read_text().splitlines() if line.strip()]
    assert summarize_run(events) == json.loads(path.read_text())


def test_roundtrip_is_lossless():
    for path in files("valid"):
        data = json.loads(path.read_text())
        assert json.loads(parse_event(data).model_dump_json(exclude_none=True)) == data
