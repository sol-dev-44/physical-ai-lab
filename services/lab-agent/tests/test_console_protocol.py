import json
from pathlib import Path

import pytest
from lab_agent.console.protocol import client_message, server_message
from pydantic import ValidationError

FIXTURES = Path(__file__).resolve().parents[3] / "packages" / "schema" / "fixtures" / "console"


def _adapter(path: Path):
    if path.name.startswith("client_"):
        return client_message
    if path.name.startswith("server_"):
        return server_message
    raise AssertionError(f"fixture name must start with client_ or server_: {path.name}")


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


def _state() -> dict:
    return json.loads((FIXTURES / "valid" / "server_state.json").read_text())


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_drive_values_are_rejected(bad):
    with pytest.raises(ValidationError):
        client_message.validate_python({"type": "drive", "v": bad, "w": 0.0, "seq": 1})
    with pytest.raises(ValidationError):
        client_message.validate_python({"type": "drive", "v": 0.0, "w": bad, "seq": 1})


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_state_numbers_are_rejected(bad):
    state = _state()
    state["battery"]["volts"] = bad
    with pytest.raises(ValidationError):
        server_message.validate_python(state)


def test_json_integers_are_accepted_for_float_fields():
    client_message.validate_python({"type": "drive", "v": 0, "w": 0, "seq": 0})


def test_seq_and_token_limits():
    client_message.validate_python({"type": "heartbeat", "seq": 2**53 - 1})
    with pytest.raises(ValidationError):
        client_message.validate_python({"type": "heartbeat", "seq": 2**53})
    client_message.validate_python({"type": "hello", "token": "a" * 256})
    with pytest.raises(ValidationError):
        client_message.validate_python({"type": "hello", "token": "a" * 257})
