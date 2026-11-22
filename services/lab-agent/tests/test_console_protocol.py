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
