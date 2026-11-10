"""Minimal PostgREST client for the service role. Only the lab machine holds this key."""

from __future__ import annotations

from typing import Any

import httpx


class Supabase:
    def __init__(
        self, url: str, service_key: str, *, transport: httpx.BaseTransport | None = None
    ) -> None:
        self.http = httpx.Client(
            base_url=f"{url}/rest/v1",
            headers={"apikey": service_key, "Authorization": f"Bearer {service_key}"},
            timeout=15,
            transport=transport,
        )

    def upsert(
        self, table: str, rows: list[dict[str, Any]], *, on_conflict: str, ignore: bool = False
    ) -> None:
        if not rows:
            return
        prefer = "resolution=ignore-duplicates" if ignore else "resolution=merge-duplicates"
        r = self.http.post(
            f"/{table}",
            params={"on_conflict": on_conflict},
            json=rows,
            headers={"Prefer": f"{prefer},return=minimal"},
        )
        r.raise_for_status()

    def update(self, table: str, match: dict[str, str], values: dict[str, Any]) -> None:
        r = self.http.patch(
            f"/{table}",
            params={k: f"eq.{v}" for k, v in match.items()},
            json=values,
            headers={"Prefer": "return=minimal"},
        )
        r.raise_for_status()

    def rpc(self, fn: str, args: dict[str, Any]) -> Any:
        r = self.http.post(f"/rpc/{fn}", json=args)
        r.raise_for_status()
        return r.json()
