"""Settings from the environment, with an optional .env file. No secrets in code."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


@dataclass(frozen=True)
class Settings:
    events_dir: Path
    tools: str | None
    supabase_url: str | None
    supabase_service_key: str | None
    site_url: str | None
    revalidate_secret: str | None
    agent_id: str

    @classmethod
    def from_env(cls) -> Settings:
        load_dotenv()
        env = os.environ.get
        return cls(
            events_dir=Path(env("LAB_EVENTS_DIR", "events")),
            tools=env("LAB_TOOLS"),
            supabase_url=env("SUPABASE_URL"),
            supabase_service_key=env("SUPABASE_SERVICE_ROLE_KEY"),
            site_url=env("SITE_URL"),
            revalidate_secret=env("REVALIDATE_SECRET"),
            agent_id=env("LAB_AGENT_ID", os.uname().nodename),
        )

    def require_supabase(self) -> tuple[str, str]:
        if not (self.supabase_url and self.supabase_service_key):
            raise SystemExit(
                "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (services/lab-agent/.env)"
            )
        return self.supabase_url.rstrip("/"), self.supabase_service_key
